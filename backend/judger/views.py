from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.conf import settings
import logging
from django.core.cache import cache
import uuid
import time
from .models import JudgeServer
import redis
import pickle
import traceback
from .constants import JUDGE_SERVER_CACHE_KEY, JUDGE_SERVER_CACHE_TTL, JUDGE_QUEUE_KEY
from utils.untils import prepare_for_json,judge_test,judgment
from problem.models import Problem,Run
from competition.models import Submit,CompetitionProblem
from django.contrib.auth import get_user_model
from utils.untils import Choise_Judger,process_judge_request,cache_initial_result,process_judge_run_async,judge_run_test
from user.models import UserProfile

logger = logging.getLogger(__name__)
User = get_user_model()  # 获取当前项目使用的User模型

# 创建 Redis 连接 - 用于判题机信息
judge_server_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,  # 使用默认的Redis数据库
    decode_responses=True  # 自动解码响应，避免JSON字符串乱码
)

# 创建 Redis 连接 - 用于题目信息（pickle序列化对象不需要解码）
problem_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_PROBLEM_DB,  # 使用专门的Redis数据库存储题目信息
    decode_responses=False  # pickle序列化对象保持为二进制
)

# 创建 Redis 连接 - 用于提交信息（pickle序列化对象不需要解码）
submit_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_SUBMIT_DB,
    decode_responses=False
)

# 创建Redis连接 - 用于结果缓存（JSON格式，需要解码）
result_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_SUBMIT_DB,
    decode_responses=True
)

# 延迟导入以避免循环导入
def get_process_judge_task():
    """
    延迟导入process_judge_task函数，避免循环导入
    """
    from .tasks import process_judge_task
    return process_judge_task

# 判题结果缓存相关常量
RESULT_CACHE_PREFIX = "judge_result:"
RESULT_CACHE_TTL = 3600  # 结果缓存1小时

class HomePageAPI(APIView):
    """
    首页 API，返回公告
    """
    
    def get(self, request):
        data = {
            'code': 200,
            'msg': 'ok',
        }

        return Response(data)

class Judger_HeartAPI(APIView):
    def get(self, request):
        pass
    def post(self, request):
        print(request.data)
        return Response({'msg': 'ok'})


class RunResultAPI(APIView):

    def post(self, request):
        data = request.data
        run_id = data.get('run_id')

        if not run_id:
            return Response({
                'code': 400,
                'msg': '参数不完整，请提供run_id'
            })

        # 从Redis缓存中获取提交结果
        cache_key = cache_key = f"{RESULT_CACHE_PREFIX}{run_id}"+"-run"
        cached_result = result_redis.get(cache_key)
        cached_result = json.loads(cached_result)
        print(cached_result)
        if cached_result:
            if cached_result["status"] == "队列中" or cached_result["status"] == "处理中":
                return Response({
                    'code': 201,
                    'msg': 'await'
                })
            if cached_result["status"] == "已完成":
                data = cached_result["result"]
                code = data.get('code')
                print(data)
                print(cached_result["result"])
                if code == 400:
                    return Response({
                    'code': 400,
                    'msg':cached_result["result"]
                })
                if data["test_cases"][0]["error"] == -1:
                    print(1)
                    return Response({
                        'code': 401,
                        'msg':cached_result["result"]["test_cases"]
                    })
                return Response({
                    'code': 200,
                    'msg':cached_result["result"]["test_cases"]
                })
            return Response({
                'code': 201,
                'data': cached_result
            })



class SubmitResultAPI(APIView):
    """
    获取判题结果的API，用于前端轮询
    code - 400 参数不完整
    code
    """
    def post(self, request):
        data = request.data
        submit_id = data.get('submit_id')

        if not submit_id:
            return Response({
                'code': 400,
                'msg': '参数不完整，请提供submit_id'
            })

        # 从Redis缓存中获取提交结果
        cache_key = f"{RESULT_CACHE_PREFIX}{submit_id}"
        cached_result = result_redis.get(cache_key)
        cached_result = json.loads(cached_result)
        if cached_result:
            if cached_result["status"] == "队列中" or cached_result["status"] == "处理中":
                return Response({
                    'code': 201,
                    'msg': 'await'
                })
            if cached_result["status"] == "Wrong Answer":
                return Response({
                    'code': 202,
                    'msg': 'Wrong Answer',
                    'src': cached_result["code"]
                })
            if cached_result["status"] == "Time Limit Exceeded":
                return Response({
                    'code': 203,
                    'msg': 'Time Limit Exceeded',
                    'src': cached_result["code"]
                })
            if cached_result["status"] == "CompileError":
                return Response({
                    'code': 204,
                    'msg': 'CompileError',
                    'data': cached_result["result"],
                    'src': cached_result["code"]
                })
            if cached_result["status"] == "Accepted":
                return Response({
                    'code': 200,
                    'msg': 'Accepted',
                    'src':cached_result["code"]
                })
            return Response({
                'code': 201,
                'data':cached_result
            })
        # 缓存不存在或已过期，从数据库获取
        submit = Submit.objects.get(id=submit_id)
        if submit.status == "队列中" or submit.status == "队列中":
            return Response({
                'code': 201,
                'msg': 'await'
            })
        elif submit.status == "Wrong Answer":
            return Response({
                'code': 202,
                'msg': 'Wrong Answer',
                'src': submit.code
            })
        elif submit.status == "Time Limit Exceeded":
            return Response({
                'code': 203,
                'msg': 'Time Limit Exceeded',
                'src': submit.code
            })
        elif submit.status == "CompileError":
            return Response({
                'code': 204,
                'msg': 'CompileError',
                'data': submit.result,
                'src': submit.code
            })
        if submit.status == "Accepted":
            return Response({
                'code': 200,
                'msg': 'Accepted',
                'src': submit.code
            })
        return Response({
            'code': 201,
            'msg': 'await'
        })




class JudgeServerAPI(APIView):
    def get(self, request):
        pass
    def post(self, request):
        pass

class SubmitAPI(APIView):
    """
    测试API
    code - 600 请求数据不完整
    code - 601 用户不存在
    code - 602 题目不存在
    code - 603 提交失败
    code - 200 提交成功
    """
    def post(self, request):
        # 获取请求中的数据
        data = request.data
        code = data.get('code')
        problem_id = data.get('problem_id')
        language = data.get('language')
        user = data.get('user_id')
        competition_id = data.get('competition_id')
        #print(data)
        if not code or not problem_id or not language or not user:
            return Response({
                'code': 600,
                'msg': '参数不完整',
            })
        try :
            user_obj = User.objects.get(username=user)
            problem_obj = Problem.objects.get(_id=problem_id)
            submit = Submit.objects.create(
                code=code,
                problem=problem_obj,
                language=language,
                user=user_obj,
                status = "处理中"  # 初始状态设置为处理中
            )
            if competition_id:
                submit.competition_id = competition_id
                submit.save()
                competition =CompetitionProblem.objects.get(competition_id=competition_id,problem_id=problem_id)
                competition.submission_number += 1
                competition.save()
                problem_id = competition.competition.id
        except User.DoesNotExist:
            return Response({
                'code': 601,
                'msg': '用户不存在',
            })
        except Problem.DoesNotExist:
            return Response({
                'code': 602,
                'msg': '题目不存在',
            })
        #try:
        judge_servers,available_server = Choise_Judger()
        cache_key = cache_initial_result(submit)
        if available_server:
            print(competition_id)
            process_judge_request(code, problem_id,language,problem_obj ,user,submit,judge_servers, available_server,competition_id=competition_id)
        else:
            self._add_to_queue(problem_obj=problem_obj,code=code,language=language,submit=submit)

        return Response({
            'code': 200,
            'msg': '提交成功',
            'submit_id': submit.id
        })
        # except Exception as e:
        #     self._add_to_queue(problem_obj=problem_obj, code=code, language=language, submit=submit)
        #     return Response({
        #         'code': 200,
        #         'msg': '提交到huey成功',
        #     })


    def _add_to_queue(self, problem_obj, code, language, submit):
        """使用 Huey 将判题任务加入队列"""
        judge_data = {
            'max_cpu_time': problem_obj.time_limit[language],
            'max_memory': problem_obj.memory_limit[language] * 1024 * 1024,
            "src": code,
            'language': language,
            'test': judge_test(problem_obj.test_id),
            'test_display': 1,
        }
        try:
            # 确保提交ID存在于判题数据中
            if submit and submit.id:
                judge_data['submission_id'] = submit.id
            # 初始化重试计数为0
            judge_data['retry_count'] = 0
            # 使用延迟导入获取任务函数
            process_judge_task = get_process_judge_task()
            # 将任务提交到 Huey 队列
            result = process_judge_task(judge_data)

            # 更新提交状态为"队列中"
            if submit:
                submit.status = "队列中"
                submit.save()

            return True

        except Exception as e:
            # 记录错误但不中断处理
            print(f"加入队列失败: {e}")
            return False


class TestAPI(APIView):
    """
    处理代码提交并调度判题服务的API
    """

    def post(self, request):
        try:
            # 1. 获取并验证提交的代码和问题信息
            data = request.data
            code = data.get('code')
            problem_id = data.get('problem_id')
            language = data.get('language')
            user = data.get('user_id')

            # 验证必要参数
            if not code or not problem_id or not language or not user:
                return Response({
                    'code': 200,
                    'msg': '参数不完整',
                })

            try:
                user_obj = User.objects.get(username=user)  # 使用新的User模型
                problem_obj = Problem.objects.get(_id=problem_id)
                submit = Submit.objects.create(
                    code=code,
                    problem=problem_obj,
                    language=language,
                    user=user_obj
                )

            except User.DoesNotExist:
                return Response({
                    'code': 404,
                    'msg': '用户不存在',
                })
            except Problem.DoesNotExist:
                return Response({
                    'code': 404,
                    'msg': '题目不存在',
                })

            # 从缓存中寻找判题机和题目信息
            judge_servers = cache.get(JUDGE_SERVER_CACHE_KEY)
            if not judge_servers:
                judge_servers = list(JudgeServer.objects.filter(
                    # server_status='0',
                    is_disabled=False
                ).values('id', 'server_name', 'server_ip', 'server_port', 'server_token', 'server_status'))

                if judge_servers:
                    cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            problem_cache_key = f"problem_{problem_id}"
            cached_problem = problem_redis.get(problem_cache_key)
            if cached_problem:
                try:
                    problem = pickle.loads(cached_problem)
                except Exception as e:
                    cached_problem = None

            if not cached_problem:
                problem = Problem.objects.get(_id=problem_id)
                try:
                    serialized_problem = pickle.dumps(problem)
                    problem_redis.setex(problem_cache_key, 3600, serialized_problem)
                except Exception as e:
                    print(f"Error serializing problem: {e}")

            # 建立发送数据
            judge_data = {
                'max_cpu_time': problem_obj.time_limit[language],
                "max_memory": problem.memory_limit[language] * 1024 * 1024,
                'src': code,
                'language': language,
                'test_display': 1,
                'test': judge_test(problem_id),
            }

            if problem.Stack_memory_limit:
                judge_data["max_stack"] = problem["Stack_memory_limit"]

            # 检查是否有可用判题机
            available_server = None
            for server in judge_servers:
                if server['server_status'] == '0':
                    available_server = server
                    break

            # 如果没有可用判题机，直接加入队列
            if not available_server:
                # 直接将任务加入Huey队列
                queue_result = self._add_to_queue(judge_data, submit)

                if queue_result:
                    return Response({
                        'code': 200,
                        'msg': '提交成功，已加入判题队列',
                    })
                else:
                    return Response({
                        'code': 500,
                        'msg': '提交失败，无法加入判题队列',
                    })

            # 有可用判题机，尝试直接判题
            try:
                # 标记判题机为忙碌状态
                available_server['server_status'] = '1'
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='1'
                )
                # 构建判题服务器URL
                judge_server_url = f"http://{available_server['server_ip']}:{available_server['server_port']}"

                # 设置请求头
                headers = {
                    'Content-Type': 'application/json',
                    'judgertoken': available_server['server_token']
                }

                # 发送请求
                response = requests.post(
                    judge_server_url,
                    json=judge_data,
                    headers=headers,
                    timeout=15  # 短超时，避免阻塞请求
                )

                # 判题完成后，将判题机状态设置为空闲
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

                # 根据返回的数据结果进行判断题目
                msg = judgment(response)
                # 更新提交记录
                if msg:
                    # 更新提交状态
                    if "status" in msg:
                        submit.status = msg["status"]

                    # 保存完整的响应数据
                    try:
                        # 保存完整的response数据而不仅仅是部分数据
                        submit.result = json.dumps(response.json(), ensure_ascii=False)
                        submit.save()
                    except Exception as e:
                        print(f"保存结果时出错: {e}")

                # 增加题目数据 - 标记统计已更新
                if msg.get("status") == "Accepted":
                    problem_obj.accept()  # 增加通过次数
                    problem_obj.summit()  # 增加提交次数
                    problem_obj.save()
                else:
                    problem_obj.summit()  # 增加提交次数
                    problem_obj.save()

                    # 返回完整的判题结果，以便前端展示
                return Response({
                    'code': 200,
                    'msg': 'Accepted',
                    'src':submit.code
                })

            except Exception as e:
                # 发送失败，将判题机状态设置为空闲
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

                # 加入队列 - 传递题目统计更新状态
                queue_result = self._add_to_queue(judge_data, submit)
                if queue_result:
                    return Response({
                        'code': 200,
                        'msg': '提交成功，已加入判题队列',
                    })
                else:
                    return Response({
                        'code': 500,
                        'msg': '提交失败，无法加入判题队列',
                    })

        except Exception as e:
            return Response({
                'code': 500,
                'msg': '提交处理失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _add_to_queue(self, judge_data, submit=None):
        """使用 Huey 将判题任务加入队列"""
        try:
            # 确保提交ID存在于判题数据中
            if submit and submit.id:
                judge_data['submission_id'] = submit.id
            # 初始化重试计数为0
            judge_data['retry_count'] = 0
            # 使用延迟导入获取任务函数
            process_judge_task = get_process_judge_task()
            # print(process_judge_task)
            # 将任务提交到 Huey 队列 - 使用10秒重试间隔，最多重试3次
            result = process_judge_task(judge_data)

            # 更新提交状态为"队列中"
            if submit:
                submit.status = "队列中"
                submit.save()

            return True

        except Exception as e:
            pass
            # logger.error(f"Huey队列提交失败: {str(e)}")

            # # 作为备用方案，使用 Redis 队列
            # try:
            #     # 序列化数据为JSON字符串
            #     judge_data_json = json.dumps(prepare_for_json(judge_data), ensure_ascii=False)
            #     # 添加到队列 - 使用判题机Redis
            #     judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)

            #     # 更新提交状态为"队列中"
            #     if submit:
            #         submit.status = "队列中"
            #         submit.save()

            #     logger.info(f"成功将判题任务加入Redis备用队列")
            #     return True
            # except Exception as backup_error:
            #     logger.error(f"Redis备用队列提交也失败: {str(backup_error)}")
            #     return False



class RunAPI(APIView):
    '''
    运行代码API，但是判题机没有将运行结果返回，还需要更改判题机
    250404-判题机已改
    '''
    def post(self,request):
        data = request.data
        code = data.get('code')
        problem_id = data.get('problem_id')
        language = data.get('language')
        user = data.get('user_id')
        test = data.get('test')
        if not code or not problem_id or not language or not user:
            return Response({
                'code': 600,
                'msg': '参数不完整',
            })
        try :
            user_obj = User.objects.get(username=user)
            problem_obj = Problem.objects.get(_id=problem_id)
            Run_obj = Run.objects.create(
                code=code,
                problem=problem_obj,
                language=language,
                user=user_obj,
                status = "处理中"  # 初始状态设置为处理中
            )
        except User.DoesNotExist:
            return Response({
                'code': 601,
                'msg': '用户不存在',
            })
        except Problem.DoesNotExist:
            return Response({
                'code': 602,
                'msg': '题目不存在',
            })
        judge_servers, available_server = Choise_Judger()
        if available_server:
            process_judge_run_async(code, problem_id, language, problem_obj, user, Run_obj, judge_servers,
                                  available_server,test)
        else:
            self._add_to_queue(problem_obj=problem_obj,code=code,language=language,Run_obj=Run_obj,test=test)

        return Response({
            'code': 200,
            'msg': '提交成功',
            'run_id': Run_obj.id
        })

    def _add_to_run_queue(self, problem_obj,code,language, Run_obj=None,test=None):
        """使用 Huey 将判题任务加入队列"""
        judge_data = {
            'max_cpu_time': problem_obj.time_limit[language],
            'max_memory': problem_obj.memory_limit[language] * 1024 * 1024,
            "src": code,
            'language': language,
            'test_display': 1,
            'test': [],
            'mode': 1
        }
        if test:
            judge_data.update({"test": judge_run_test(test)})
        else:
            judge_data.update({"test": problem_obj.run_test})
        try:
            # 确保提交ID存在于判题数据中
            if Run_obj and Run_obj.id:
                judge_data['run_id'] = Run_obj.id
            # 初始化重试计数为0
            judge_data['retry_count'] = 0
            # 使用延迟导入获取任务函数
            process_judge_task = get_process_judge_task()
            # print(process_judge_task)
            # 将任务提交到 Huey 队列 - 使用10秒重试间隔，最多重试3次
            result = process_judge_task(judge_data)

            # 更新提交状态为"队列中"
            if Run_obj:
                Run_obj.status = "队列中"
                Run_obj.save()

            return True
        except Exception as e:
            pass



