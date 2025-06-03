"""
判题任务模块 - 使用 Huey 来处理异步判题任务
"""
import logging
import json
import requests
import traceback
import threading
import time
import pickle
from django.core.cache import cache
from django.db import transaction
from huey.contrib.djhuey import task, on_startup, on_shutdown, db_task
from .models import JudgeServer
from competition.models import Submit
from .constants import JUDGE_SERVER_CACHE_KEY, JUDGE_SERVER_CACHE_TTL, JUDGE_QUEUE_KEY
from utils.untils import prepare_for_json, judgment
from django.conf import settings
import redis

# 获取日志记录器
logger = logging.getLogger(__name__)

# 处理中的任务集合 - 避免重复处理
PROCESSING_TASKS = set()

# 创建 Redis 连接 - 用于判题机信息
judge_server_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,  # 使用默认的Redis数据库
    decode_responses=True  # 自动解码响应，避免JSON字符串乱码
)

# 创建 Redis 连接 - 用于提交信息（pickle序列化对象不需要解码）
submit_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_SUBMIT_DB,
    decode_responses=False
)

# Redis队列处理标志 - 避免重复启动处理线程
REDIS_QUEUE_WORKER_STARTED = False

@on_startup()
def setup_huey():
    """Huey启动时执行的函数"""
    logger.info("判题队列系统已启动")

@on_shutdown()
def teardown_huey():
    """Huey关闭时执行的函数"""
    logger.info("判题队列系统已关闭")
    # 清空处理中的任务集合
    PROCESSING_TASKS.clear()

def get_available_judge_server():
    """
    获取一个可用的判题机
    首先从缓存中查找，如果没有则从数据库加载
    """
    # 从缓存获取判题机列表
    judge_servers = cache.get(JUDGE_SERVER_CACHE_KEY)

    # 如果缓存中没有判题机列表，从数据库加载
    if not judge_servers:
        logger.info("判题机列表不在缓存中，从数据库加载")
        judge_servers = list(JudgeServer.objects.filter(
            server_status='0',
            is_disabled=False
        ).values('id', 'server_name', 'server_ip', 'server_port', 'server_token', 'server_status'))

        # 更新缓存
        if judge_servers:
            # 确保数据可以正确序列化为JSON
            cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

    # 查找空闲的判题机
    available_server = None
    for server in judge_servers:
        if server['server_status'] == '0':
            available_server = server
            # 增加当前任务并更新缓存
            server['server_status'] = '1'
            # 确保数据可以正确序列化为JSON
            cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            # 同时更新数据库
            JudgeServer.objects.filter(id=server['id']).update(
                server_status='1'
            )
            break

    return available_server, judge_servers

# 使用db_task来确保任务在数据库中持久化，固定重试延迟为10秒，最多重试3次
@db_task(retries=10, retry_delay=3)  # 重试3次，每次间隔10秒
def process_judge_task(task_data):
    """
    处理判题任务的主函数 - 最多重试3次，之后返回系统繁忙
    """
    submission_id = task_data.get('submission_id')
    retry_count = task_data.get('retry_count', 0)
    # 如果有提交ID，记录到处理中集合
    if submission_id:
        task_key = f"task_{submission_id}"
        if task_key in PROCESSING_TASKS:
            logger.info(f"任务 {submission_id} 已在处理中，跳过")
            return {
                'status': 'skipped',
                'message': '任务已在处理中'
            }
        PROCESSING_TASKS.add(task_key)
    try:
        # 获取可用判题机
        available_server, judge_servers = get_available_judge_server()
        if not available_server:
            # 从处理中集合移除
            if submission_id:
                PROCESSING_TASKS.discard(f"task_{submission_id}")
            # 如果已经重试了4次，标记为系统繁忙
            if retry_count >= 10:
                #logger.error(f"重试次后仍无可用判题机，标记为系统繁忙：{submission_id}")
                if submission_id:
                    try:
                        submit = Submit.objects.get(id=submission_id)
                        submit.status = "系统繁忙"
                        submit.result = json.dumps({"error": "判题系统繁忙，请稍后再试"})
                        submit.save()
                        submit_cache_key = f"submit_{submission_id}"
                        # 更新缓存
                        try:
                            serialized_submit = pickle.dumps(submit)
                            submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
                        except Exception as cache_error:
                            submit_redis.delete(submit_cache_key)
                    except Exception as e:
                        pass
                return {
                    'status': 'failed',
                    'error': 'busy',
                    'message': '判题系统繁忙，请稍后再试'
                }
            # 否则抛出异常以触发Huey的重试机制
            retry_count += 1
            task_data['retry_count'] = retry_count  # 保存重试次数
            #logger.warning(f"没有可用判题机，重试次数：{retry_count}")
            raise Exception("没有可用判题机")

        # 构建判题服务器URL
        judge_server_url = f"http://{available_server['server_ip']}:{available_server['server_port']}"
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'judgertoken': available_server['server_token']
        }

        # 创建判题数据的副本，移除submission_id字段和retry_count字段
        judge_data = task_data.copy()
        if 'submission_id' in judge_data:
            del judge_data['submission_id']
        if 'retry_count' in judge_data:
            del judge_data['retry_count']
        if 'stats_updated' in judge_data:
            del judge_data['stats_updated']

        # 发送判题请求前确保judge_data可以正确序列化为JSON
        sanitized_judge_data = prepare_for_json(judge_data)
        # 发送判题请求
        response = requests.post(
            judge_server_url,
            json=sanitized_judge_data,  # 使用清理后的数据，且不包含submission_id
            headers=headers,
            timeout=15  # 较长的超时时间，因为判题可能需要时间
        )

        # 处理响应
        msg = judgment(response)
        try:
            with transaction.atomic():
                # 获取提交记录
                submit = Submit.objects.get(id=submission_id)
                submit.status = msg["status"]
                # 处理数据并转换为JSON
                data_to_save = list(msg["data"])
                submit.result = json.dumps(data_to_save)
                # 保存更新
                submit.save()
                submit_cache_key = f"submit_{submission_id}"
                try:
                    serialized_submit = pickle.dumps(submit)
                    submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
                except Exception as cache_error:
                    submit_redis.delete(submit_cache_key)
                if msg["status"] == "Accepted":
                    submit.problem.accept()  # 增加通过次数
                submit.problem.summit()
                submit.problem.save()

            # 判题机状态设置为空闲
            available_server['server_status'] = '0'
            JudgeServer.objects.filter(id=available_server['id']).update(
                server_status='0'
            )
            # 更新缓存中的判题机信息
            cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)

            # 返回成功状态和结果
            return {
                'status': 'success',
                'result': msg,
            }

        except Exception as e:
            # 先处理数据库更新，再决定是否重试
            logger.error("www")
            logger.warning(f"判题机处理任务失败: {str(e)}")
            # 刷新判题机列表
            try:
                judge_servers = list(JudgeServer.objects.filter(
                    is_disabled=False
                ).values('id', 'server_name', 'server_ip', 'server_port', 'server_token', 'server_status'))
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            except Exception as refresh_error:
                logger.error(f"刷新判题机列表失败: {str(refresh_error)}")

            # 更新提交状态
            if submission_id:
                try:
                    with transaction.atomic():
                        submit = Submit.objects.get(id=submission_id)

                        # 只有在最后一次重试失败后才更新状态
                        if retry_count >= 2:  # 已尝试3次
                            if "没有可用的判题服务器" in str(e):
                                submit.status = "没有空闲"
                                submit.result = json.dumps({"error": "没有可用的判题服务器，请稍后再试"})
                            else:
                                submit.status = "判题机异常"
                                submit.result = json.dumps({"error": f"判题请求出错: {str(e)}"})
                            submit.save()

                            # 更新缓存
                            submit_cache_key = f"submit_{submission_id}"
                            try:
                                serialized_submit = pickle.dumps(submit)
                                submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
                            except Exception as cache_error:
                                submit_redis.delete(submit_cache_key)

                            logger.error(f"重试失败：提交{submission_id}已标记为'{submit.status}'")
                except Exception as update_error:
                    transaction.set_rollback(True)
                    logger.error(f"更新提交状态失败: {str(update_error)}")

            # 如果已经重试了2次（总共3次），返回失败
            if retry_count >= 3:  # 第3次尝试后结束
                return {
                    'status': 'failed',
                    'error': 'exception',
                    'message': str(e)
                }

            # 否则增加重试计数并继续重试
            task_data['retry_count'] = retry_count + 1
            logger.info(f"判题任务将进行第{retry_count+2}次尝试（共3次）")
            raise  # 重新抛出异常，触发Huey的重试机制
    except requests.Timeout:
        # 如果发生异常，确保判题机状态恢复为空闲
        if 'available_server' in locals() and available_server:
            try:
                with transaction.atomic():
                    available_server['server_status'] = '0'
                    JudgeServer.objects.filter(id=available_server['id']).update(
                        server_status='0'
                    )
                    cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
                    submit = Submit.objects.get(id=submission_id)
                    submit.status = "请求超时"
                    submit.result = json.dumps({"error": "判题请求超时"})
                    submit.save()

                    submit_cache_key = f"submit_{submission_id}"
                    try:
                        serialized_submit = pickle.dumps(submit)
                        submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
                    except Exception as cache_error:
                        submit_redis.delete(submit_cache_key)
                    retry_count = 10
            except Exception as e:
                transaction.set_rollback(True)
                retry_count = 10

        # 如果已经重试了10次，标记为系统错误
        if retry_count >= 10:  # 当前+后续重试共3次
            return {
                'status': 'failed',
                'error': 'timeout',
                'message': '判题请求超时'
            }

        # 否则继续重试
        task_data['retry_count'] = retry_count + 1
        raise Exception("判题请求超时，稍后重试")
    # except Exception as e:
    #     logger.warning("whl")
    #     logger.warning(f"判题机处理任务失败: {str(e)}")
    #     judge_servers = list(JudgeServer.objects.filter(
    #         is_disabled=False
    #     ).values('id', 'server_name', 'server_ip', 'server_port', 'server_token', 'server_status'))
    #     cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
    #     if submission_id:
    #         submit = Submit.objects.get(id=submission_id)
    #         submit.status = "没有空闲"
    #         submit.result = json.dumps({"error": f"判题请求出错: {str(e)}"})
    #         submit.save()
    #         submit_cache_key = f"submit_{submission_id}"
    #         try:
    #             serialized_submit = pickle.dumps(submit)
    #             submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
    #         except Exception as cache_error:
    #             submit_redis.delete(submit_cache_key)
    #         retry_count = 3
    #         stats_updated = True
    #     #如果已经重试了3次，标记为系统错误
    #     if retry_count >= 10:  # 当前+后续重试共3次
    #         return {
    #             'status': 'failed',
    #             'error': 'exception',
    #             'message': str(e)
    #         }
    #
    #     #否则继续重试
    #     task_data['retry_count'] = retry_count + 1
    #     logger.info(f"判题任务将进行第{retry_count+2}次尝试（共3次）")
    #     raise  # 重新抛出异常，触发Huey的重试机制

    finally:
        if submission_id:
            PROCESSING_TASKS.discard(f"task_{submission_id}")

@task()
def update_submission_status(submission_id, status, result=None):
    """
    更新提交状态的任务
    可用于在判题完成后更新数据库
    """
    logger.info(f"更新提交状态: {submission_id} -> {status}")
    try:
        # 实现更新提交状态的逻辑
        submit = Submit.objects.get(id=submission_id)
        submit.status = status
        if result:
            submit.result = json.dumps(result)
        submit.save()
        return True
    except Exception as e:
        logger.error(f"更新提交状态失败: {str(e)}")
        return False

# 添加缺失的schedule_pending_tasks_check任务定义
@task()
def schedule_pending_tasks_check():
    """
    定期检查是否有处于'队列中'状态的提交，但没有对应的任务
    这是一个空操作，只是为了满足已有的任务引用
    """
    logger.info("检查队列中的提交 - 空操作")
    # 这是一个空操作，现在使用Huey的内置重试机制来处理任务
    # 所以不需要主动重新调度 

# 处理Redis队列中的任务
def process_redis_queue():
    """
    处理Redis队列中的任务
    当Huey队列提交失败时，任务会被添加到Redis队列中
    该函数会定期检查Redis队列，并处理其中的任务
    """
    logger.info("Redis队列处理线程已启动")
    
    # 任务处理中队列 - 用于跟踪正在处理的任务
    processing_queue_key = f"{JUDGE_QUEUE_KEY}_processing"
    
    while True:
        try:
            # 检查队列长度
            queue_length = judge_server_redis.llen(JUDGE_QUEUE_KEY)
            if queue_length > 0:
                logger.info(f"Redis队列中有 {queue_length} 个待处理任务")
            
            # 从队列中获取任务（阻塞操作，超时1秒）
            # 使用BRPOPLPUSH将任务从主队列移动到处理中队列
            task_data_str = judge_server_redis.brpoplpush(
                JUDGE_QUEUE_KEY,
                processing_queue_key,
                timeout=1
            )
            
            # 如果没有任务，继续循环
            if not task_data_str:
                time.sleep(5)  # 改为5秒休眠，避免过度占用CPU
                continue
                
            # 解析任务数据
            try:
                task_data = json.loads(task_data_str)
                submission_id = task_data.get('submission_id', 'unknown')
                logger.info(f"从Redis队列获取到任务: {submission_id}")
                
                # 使用与Huey相同的处理逻辑处理任务
                result = process_judge_task_directly(task_data)
                
                # 任务成功处理，从处理中队列移除
                judge_server_redis.lrem(processing_queue_key, 1, task_data_str)
                logger.info(f"Redis任务 {submission_id} 处理完成，已从队列中移除")
                
            except json.JSONDecodeError:
                logger.error(f"Redis队列中的任务数据无效: {task_data_str[:100]}")
                # 无效任务，从处理中队列移除
                judge_server_redis.lrem(processing_queue_key, 1, task_data_str)
                continue
                
            except Exception as e:
                logger.error(f"处理Redis队列任务时出错: {str(e)}")
                logger.error(traceback.format_exc())
                
                # 如果是由于没有可用判题机导致的，任务会自动重新入队
                # 其他错误则从处理中队列移除，避免死循环
                if "没有可用判题机" not in str(e):
                    judge_server_redis.lrem(processing_queue_key, 1, task_data_str)
                
                # 休眠一段时间再继续
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Redis队列处理循环出错: {str(e)}")
            logger.error(traceback.format_exc())
            # 休眠一段时间再继续
            time.sleep(10)

# 直接处理任务（不通过Huey）- 与process_judge_task逻辑相同，但直接执行
def process_judge_task_directly(task_data):
    """
    直接处理判题任务，与process_judge_task逻辑相同
    但不通过Huey队列，而是直接在Redis队列处理线程中执行
    """
    submission_id = task_data.get('submission_id')
    retry_count = task_data.get('retry_count', 0)
    
    # 如果有提交ID，记录到处理中集合
    if submission_id:
        task_key = f"task_{submission_id}"
        if task_key in PROCESSING_TASKS:
            logger.info(f"任务 {submission_id} 已在处理中，跳过")
            return
        PROCESSING_TASKS.add(task_key)
    
    try:
        # 获取可用判题机
        available_server, judge_servers = get_available_judge_server()
        
        if not available_server:
            # 更新重试次数
            retry_count += 1
            logger.warning(f"Redis队列：没有可用判题机，尝试第 {retry_count} 次")
            
            # 从处理中集合移除
            if submission_id:
                PROCESSING_TASKS.discard(f"task_{submission_id}")
            
            # 如果已经重试了3次，标记为系统繁忙
            if retry_count >= 3:
                logger.error(f"Redis队列：重试3次后仍无可用判题机，标记为系统繁忙：{submission_id}")
                if submission_id:
                    try:
                        submit = Submit.objects.get(id=submission_id)
                        submit.status = "系统繁忙"
                        submit.result = json.dumps({"error": "判题系统繁忙，请稍后再试"})
                        submit.save()
                        logger.info(f"已更新提交 {submission_id} 的状态为系统繁忙")
                    except Exception as e:
                        logger.error(f"更新提交记录失败: {str(e)}")
                return
            
            # 否则重新加入队列，10秒后重试
            task_data['retry_count'] = retry_count
            judge_data_json = json.dumps(prepare_for_json(task_data), ensure_ascii=False)
            judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)
            logger.info(f"Redis队列：任务 {submission_id} 重新入队，10秒后重试")
            time.sleep(10)  # 延迟10秒后再继续处理下一个任务
            return
        
        # 构建判题服务器URL
        judge_server_url = f"http://{available_server['server_ip']}:{available_server['server_port']}"
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'judgertoken': available_server['server_token']
        }
        
        # 创建判题数据的副本，移除submission_id字段和retry_count字段
        judge_data = task_data.copy()
        if 'submission_id' in judge_data:
            del judge_data['submission_id']
        if 'retry_count' in judge_data:
            del judge_data['retry_count']
        
        # 发送判题请求前确保judge_data可以正确序列化为JSON
        sanitized_judge_data = prepare_for_json(judge_data)
        
        # 发送判题请求
        logger.info(f"Redis队列：发送判题请求到 {available_server['server_name']} ({judge_server_url})")
        response = requests.post(
            judge_server_url,
            json=sanitized_judge_data,
            headers=headers,
            timeout=15
        )
        
        # 处理响应
        if response.status_code == 200:
            # 解析判题结果
            try:
                result = response.json()
                # 判题完成后，将判题机状态设置为空闲
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                # 更新缓存中的判题机信息
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
                
                # 如果提交ID存在，更新提交状态
                if submission_id:
                    msg = judgment(response)
                    if msg and "status" in msg:
                        try:
                            # 使用事务包裹数据库操作
                            with transaction.atomic():
                                # 尝试更新提交记录
                                submit = Submit.objects.get(id=submission_id)
                                submit.status = msg["status"]
                                if "data" in msg:
                                    data_to_save = list(msg["data"]) if isinstance(msg["data"], set) else msg["data"]
                                    submit.result = json.dumps(data_to_save)
                                submit.save()
                                
                                # 更新题目统计
                                if msg["status"] == "Accepted":
                                    submit.problem.accept()  # 增加通过次数
                                submit.problem.summit()  # 增加提交次数
                                submit.problem.save()
                                
                                logger.info(f"Redis队列：已更新提交 {submission_id} 的状态为 {msg['status']}")
                                
                                # 将提交结果保存到Redis缓存
                                try:
                                    submit_cache_key = f"submit_{submission_id}"
                                    serialized_submit = pickle.dumps(submit)
                                    submit_redis.setex(submit_cache_key, 3600, serialized_submit)  # 缓存1小时
                                    logger.info(f"Redis队列：提交结果已保存到Redis缓存: {submit_cache_key}")
                                except Exception as cache_error:
                                    logger.error(f"Redis队列：保存提交结果到Redis缓存失败: {str(cache_error)}")
                                    submit_redis.delete(submit_cache_key)
                        except Exception as update_error:
                            # 执行事务回滚
                            transaction.set_rollback(True)
                            logger.error(f"Redis队列：更新提交记录失败，执行回滚: {str(update_error)}")
                            logger.error(traceback.format_exc())
                
            except json.JSONDecodeError:
                logger.error(f"Redis队列：解析判题结果失败: {response.text[:200]}")
                # 判题机状态恢复为空闲
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
                
                # 如果已经重试了3次，标记为系统错误
                if retry_count >= 2:
                    if submission_id:
                        try:
                            submit = Submit.objects.get(id=submission_id)
                            submit.status = "系统错误"
                            submit.result = json.dumps({"error": "判题结果解析失败"})
                            submit.save()
                        except Exception as e:
                            logger.error(f"更新提交记录失败: {str(e)}")
                    return
                
                # 否则重新加入队列，10秒后重试
                task_data['retry_count'] = retry_count + 1
                judge_data_json = json.dumps(prepare_for_json(task_data), ensure_ascii=False)
                judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)
                logger.info(f"Redis队列：任务 {submission_id} 重新入队，10秒后重试")
                time.sleep(10)
                
        else:
            logger.error(f"Redis队列：判题请求失败，状态码: {response.status_code}, 响应: {response.text}")
            # 判题失败，将判题机状态设置为空闲
            available_server['server_status'] = '0'
            JudgeServer.objects.filter(id=available_server['id']).update(
                server_status='0'
            )
            cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            
            # 如果已经重试了3次，标记为系统错误
            if retry_count >= 2:
                if submission_id:
                    try:
                        submit = Submit.objects.get(id=submission_id)
                        submit.status = "系统错误"
                        submit.result = json.dumps({"error": f"判题请求失败，状态码: {response.status_code}"})
                        submit.save()
                    except Exception as e:
                        logger.error(f"更新提交记录失败: {str(e)}")
                return
            
            # 否则重新加入队列，10秒后重试
            task_data['retry_count'] = retry_count + 1
            judge_data_json = json.dumps(prepare_for_json(task_data), ensure_ascii=False)
            judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)
            logger.info(f"Redis队列：任务 {submission_id} 重新入队，10秒后重试")
            time.sleep(10)
    
    except requests.Timeout:
        logger.error(f"Redis队列：判题请求超时")
        # 如果发生异常，确保判题机状态恢复为空闲
        if 'available_server' in locals() and available_server:
            try:
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            except Exception as e:
                logger.error(f"恢复判题机状态时出错: {str(e)}")
        
        # 如果已经重试了3次，标记为系统错误
        if retry_count >= 2:
            if submission_id:
                try:
                    submit = Submit.objects.get(id=submission_id)
                    submit.status = "系统错误"
                    submit.result = json.dumps({"error": "判题请求超时"})
                    submit.save()
                except Exception as e:
                    logger.error(f"更新提交记录失败: {str(e)}")
            return
        
        # 否则重新加入队列，10秒后重试
        task_data['retry_count'] = retry_count + 1
        judge_data_json = json.dumps(prepare_for_json(task_data), ensure_ascii=False)
        judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)
        logger.info(f"Redis队列：任务 {submission_id} 重新入队，10秒后重试")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"Redis队列：发送判题请求时出错: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 如果发生异常，确保判题机状态恢复为空闲
        if 'available_server' in locals() and available_server:
            try:
                available_server['server_status'] = '0'
                JudgeServer.objects.filter(id=available_server['id']).update(
                    server_status='0'
                )
                cache.set(JUDGE_SERVER_CACHE_KEY, prepare_for_json(judge_servers), JUDGE_SERVER_CACHE_TTL)
            except Exception as recovery_error:
                logger.error(f"恢复判题机状态时出错: {str(recovery_error)}")
        
        # 如果已经重试了3次，标记为系统错误
        if retry_count >= 2:
            if submission_id:
                try:
                    submit = Submit.objects.get(id=submission_id)
                    submit.status = "系统错误"
                    submit.result = json.dumps({"error": f"判题请求出错: {str(e)}"})
                    submit.save()
                except Exception as update_error:
                    logger.error(f"更新提交记录失败: {str(update_error)}")
            return
        
        # 否则重新加入队列，10秒后重试
        task_data['retry_count'] = retry_count + 1
        judge_data_json = json.dumps(prepare_for_json(task_data), ensure_ascii=False)
        judge_server_redis.lpush(JUDGE_QUEUE_KEY, judge_data_json)
        logger.info(f"Redis队列：任务 {submission_id} 重新入队，10秒后重试")
        time.sleep(10)
        
    finally:
        # 清理处理中标记
        if submission_id:
            PROCESSING_TASKS.discard(f"task_{submission_id}")

# 启动Redis队列处理线程
def start_judge_queue_worker():
    """
    启动Redis队列处理线程
    该函数会被apps.py中的ready方法调用
    """
    global REDIS_QUEUE_WORKER_STARTED
    
    # 避免重复启动
    if REDIS_QUEUE_WORKER_STARTED:
        return
        
    # 启动Redis队列处理线程
    redis_worker_thread = threading.Thread(target=process_redis_queue, daemon=True)
    redis_worker_thread.start()
    
    REDIS_QUEUE_WORKER_STARTED = True
    logger.info("Redis队列处理线程已启动") 