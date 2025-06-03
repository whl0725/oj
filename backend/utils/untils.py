from backend import settings
from problem.models import ProblemTest, Problem
import logging
import json
import os
from django.core.cache import cache
from competition.models import CompetitionProblem
from judger.constants import (JUDGE_SERVER_CACHE_KEY,
                              JUDGE_SERVER_CACHE_TTL, RESULT_CACHE_TTL,
                              JUDGE_QUEUE_KEY,RESULT_CACHE_PREFIX,)
from judger.models import JudgeServer
import redis
import pickle
import requests
import time

from .serializers import SubmitSerializer,RunSerializer
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

result_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_SUBMIT_DB,
    decode_responses=True
)

problem_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_PROBLEM_DB,  # 使用专门的Redis数据库存储题目信息
    decode_responses=False  # pickle序列化对象保持为二进制
)

logger = logging.getLogger(__name__)

def judge_run_test(run_test):
    """运行测试用例"""
    test =[
        {"input":run_test}
    ]
    return test

def judge_test(problem_id):
    """获取问题的测试用例"""
    try:
        # 首先尝试从数据库获取测试用例
        test_data = ProblemTest.objects.filter(id=problem_id).first().test
        # 验证每个测试用例是否有input和output字段
        valid_test_data = []
        for i, test in enumerate(test_data):
            if not isinstance(test, dict) or 'input' not in test or 'output' not in test:
                logger.warning(f"测试用例 #{i+1} 格式无效")
                continue
            valid_test_data.append(test)

        if not valid_test_data:
            logger.error(f"问题ID {problem_id} 没有有效的测试用例")
            return []

        logger.info(f"成功获取问题ID {problem_id} 的 {len(valid_test_data)} 个测试用例")
        return valid_test_data

    except Exception as e:
        logger.error(f"获取问题ID {problem_id} 的测试用例失败: {str(e)}")
        return []

def judgment(response):
    data = response.json()
    if response.status_code == 200 :
        # 处理200成功响应
        if data["accepted_count"] == data["total_count"] :
            return {
                "status": "Accepted",
                "data":{
                    data["max_memory"],
                    data["total_time"],
                    data["total_count"],
                    data["accepted_count"]
                }
            }
        else:
            return {
                "status": "Wrong Answer",
                "data": {
                    data["max_memory"],
                    data["total_time"],
                    data["total_count"],
                    data["accepted_count"]
                }
            }
    elif response.status_code == 400:
        # 处理400错误 - 编译错误
        return {
            "status": "CompileError",
            "data":data["details"]
        }
    elif response.status_code == 401:
        return {
            "status": "Runtime error occurred",
            "data": data["details"]
        }

    elif response.status_code == 402:
        return {
            "status": "Time limit exceeded",
            "data": data["details"]
        }


def judge_submit(submit_id):
    pass



def prepare_for_json(data):
    """
    准备数据以便安全地序列化为JSON，处理各种类型
    包括日期时间、二进制数据、UUID等
    """
    if data is None:
        return None

    # 处理字典
    if isinstance(data, dict):
        return {key: prepare_for_json(value) for key, value in data.items()}

    # 处理列表或元组
    if isinstance(data, (list, tuple)):
        return [prepare_for_json(item) for item in data]

    # 处理日期时间对象
    if hasattr(data, 'isoformat'):
        return data.isoformat()

    # 处理UUID
    if hasattr(data, 'hex'):
        return str(data)

    # 处理bytes或二进制数据
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            # 如果无法解码为UTF-8，则转为Base64字符串
            import base64
            return base64.b64encode(data).decode('ascii')

    # 处理其他不能直接JSON序列化的对象
    if not isinstance(data, (str, int, float, bool)):
        return str(data)

    # 原样返回基本类型
    return data


def Choise_Judger():
    judge_servers = cache.get(JUDGE_SERVER_CACHE_KEY)
    if not judge_servers:
        judge_servers = list(JudgeServer.objects.filter(
            is_disabled=False
        ).values('id', 'server_name', 'server_ip', 'server_port', 'server_token', 'server_status'))
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

    available_server = None
    for server in judge_servers:
        if server['server_status'] == '0':
            available_server = server
            break

    return judge_servers,available_server

def process_judge_request(code,problem_id, language, problem_obj,user, submit,judge_servers, available_server=None,test=None,competition_id=None):
    import threading
    print(competition_id)
    thread = threading.Thread(
        target=process_judge_async,
        args=(code,problem_id, language, problem_obj,user, submit,judge_servers, available_server,test,competition_id)
    )
    #print(code,problem_id, language, problem_obj,user, submit,judge_servers, available_server)
    thread.daemon = True
    thread.start()

def process_judge_async(code,problem_id, language, problem_obj,user, submit,judge_servers, available_server=None,test=None,competition_id=None):
    problem_cache_key = f"problem_{problem_id}"
    problem = None
    cached_problem = problem_redis.get(problem_cache_key)
    # 还需要再看看
    if cached_problem:
        try:
            problem = pickle.loads(cached_problem)
        except Exception:
            problem = None
    if problem is None:
        print(problem_id)
        problem = Problem.objects.get(id=problem_id)
        try:
            serialized_problem = pickle.dumps(problem)
            problem_redis.setex(problem_cache_key, 3600, serialized_problem)
        except Exception as e:
            print(f"Error serializing problem: {e}")
    data = {
        'max_cpu_time': problem_obj.time_limit[language],
        'max_memory': int(problem_obj.memory_limit[language])*1024*1024 ,
        "src": code,
        'language': language,
        'test': judge_test(problem_obj.test_id),
        'test_display': 1,
    }
    if problem.Stack_memory_limit:
        data["max_stack"] = problem["Stack_memory_limit"]
    try:
        # 更新判题机情况 - 标记为忙碌
        available_server['server_status'] = '1'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='1'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '1'
                break

        # 设置缓存
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

        # 构建判题服务器URL
        judge_server_url = f"http://{available_server['server_ip']}:{available_server['server_port']}"

        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'judgertoken': available_server['server_token']
        }
        import time
        start_time = time.time()
        # 发送请求
        response = requests.post(
            judge_server_url,
            json=data,
            headers=headers,
            timeout=15  # 短超时，避免阻塞请求
        )
        end_time = time.time()  # 结束时间
        elapsed_time = end_time - start_time  # 计算运行时间
        print(f"程序运行时间：{elapsed_time}秒")
        print("发送完成")

        # 判题完成后，将判题机状态设置为空闲
        available_server['server_status'] = '0'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='0'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '0'
                break

        # 设置缓存
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
        msg = judgment(response)
        if "status" in msg:
            status = msg["status"]
            submit.status = status
            result_json = response.json()
            submit.result = json.dumps(result_json, ensure_ascii=False)
            submit.save()
            # 更新缓存
            update_result_cache(submit, msg, result_json)

        if msg.get("status") == "Accepted":
            problem_obj.accept()  # 增加通过次数
            problem_obj.summit()  # 增加提交次数
            problem_obj.save()
            #user.add_accepted(problem_obj._id) # 将通过的题目增加到数据库里面
        else:
            problem_obj.summit()  # 增加提交次数
            problem_obj.save()
        print(competition_id)
        if competition_id:
            if msg.get("status") == "Accepted":
                competition = CompetitionProblem.objects.get(id=competition_id, problem_id=problem_id)
                print(competition)
                competition.accepted_number += 1
                competition.save()

        print("test完成")
    except Exception as e:
        print(f"判题处理出错: {e}")

        # 出现异常时，确保将判题机状态恢复为空闲
        available_server['server_status'] = '0'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='0'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '0'
                break

        # 设置缓存
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)



def cache_initial_result(submit):
    """
    缓存初始提交结果到Redis，确保数据与数据库一致且不出现乱码
    """
    try:
        cache_data = SubmitSerializer(submit).data
        # 生成缓存键
        cache_key = f"{RESULT_CACHE_PREFIX}{submit.id}"

        # 设置缓存，确保使用UTF-8编码
        result_redis.setex(
            cache_key,
            RESULT_CACHE_TTL,
            json.dumps(cache_data, ensure_ascii=False)
        )
        return cache_key
    except Exception as e:
        print(f"缓存初始结果失败: {str(e)}")
        return None


def update_result_cache(submit, msg, result_json):
    """
    更新判题结果缓存
    """
    try:
        # 生成缓存键
        cache_key = f"{RESULT_CACHE_PREFIX}{submit.id}"

        cache_data = SubmitSerializer(submit).data

        cache_data["result"] = result_json
        cache_data["status"] = msg["status"]

        # 更新Redis缓存
        result_redis.setex(
            cache_key, 
            RESULT_CACHE_TTL, 
            json.dumps(cache_data, ensure_ascii=False)
        )
    except Exception as e:
        print(f"更新结果缓存失败: {str(e)}")



def process_judge_request_run(code,problem_id, language, problem_obj,user, Run_obj,judge_servers, available_server=None,test=None):
    import threading
    thread = threading.Thread(
        target=process_judge_run_async,
        args=(code, problem_id, language, problem_obj, user, Run_obj, judge_servers, available_server, test)
    )
    thread.daemon = True
    thread.start()


def process_judge_run_async(code,problem_id, language, problem_obj,user, Run_obj,judge_servers, available_server=None,test=None):
    problem_cache_key = f"problem_{problem_id}"
    problem = None
    cached_problem = problem_redis.get(problem_cache_key)

    if cached_problem:
        try:
            problem = pickle.loads(cached_problem)
        except Exception:
            problem = None
    if problem is None:
        problem = Problem.objects.get(id=problem_id)
        try:
            serialized_problem = pickle.dumps(problem)
            problem_redis.setex(problem_cache_key, 3600, serialized_problem)
        except Exception as e:
            print(f"Error serializing problem: {e}")
    data = {
        'max_cpu_time': 8000,
        'max_memory': int(problem_obj.memory_limit[language]) * 1024 * 1024,
        "src": code,
        'language': language,
        'test_display': 1,
        'test':[{
            "input":str(test),
            "output": "38 41 106 307 388 454 457 831 899 919"
        }],
        'mode':1
    }
    print(data)
    if test:
        data.update({"test":judge_run_test(test)})
    else:
        data.update({"test":problem_obj.run_test})
    try:
        # 更新判题机情况 - 标记为忙碌
        available_server['server_status'] = '1'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='1'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '1'
                break
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

        # 构建判题服务器URL
        judge_server_url = f"http://{available_server['server_ip']}:{available_server['server_port']}"
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'judgertoken': available_server['server_token']
        }
        import time
        start_time = time.time()
        # 发送请求
        response = requests.post(
            judge_server_url,
            json=data,
            headers=headers,
            timeout=15  # 短超时，避免阻塞请求
        )
        print(response.json())
        end_time = time.time()  # 结束时间
        elapsed_time = end_time - start_time  # 计算运行时间
        print(f"程序运行时间：{elapsed_time}秒")
        print("发送完成")

        # 判题完成后，将判题机状态设置为空闲
        available_server['server_status'] = '0'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='0'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '0'
                break

        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

        # 将结果保存到数据库
        print(response.json())
        Run_obj.result = response.json()
        Run_obj.status = "已完成"
        Run_obj.save()
        cache_key = f"{RESULT_CACHE_PREFIX}{Run_obj.id}"+"-run"
        cache_data = RunSerializer(Run_obj).data
        result_redis.setex(
            cache_key,
            RESULT_CACHE_TTL,
            json.dumps(cache_data, ensure_ascii=False)
        )
    except Exception as e:
        print(f"判题处理出错: {e}")

        # 出现异常时，确保将判题机状态恢复为空闲
        available_server['server_status'] = '0'

        # 先在数据库中更新判题机状态
        JudgeServer.objects.filter(id=available_server['id']).update(
            server_status='0'
        )

        # 更新缓存中的判题机列表
        for server in judge_servers:
            if server['id'] == available_server['id']:
                server['server_status'] = '0'
                break

        # 设置缓存
        cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)




def validate_email(email):
    validator = EmailValidator()
    try:
        validator(email)
        return True
    except ValidationError:
        return False