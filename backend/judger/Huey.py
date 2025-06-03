import logging
import json
import requests
import pickle
from django.core.cache import cache
from django.db import transaction
from huey.contrib.djhuey import task, on_startup, on_shutdown, db_task
from .models import JudgeServer
from competition.models import Submit
from .constants import JUDGE_SERVER_CACHE_KEY, JUDGE_SERVER_CACHE_TTL, JUDGE_QUEUE_KEY,RESULT_CACHE_PREFIX
from utils.untils import prepare_for_json, judgment
from django.conf import settings
import redis

from utils.serializers import SubmitSerializer


logger = logging.getLogger(__name__)
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
        judge_servers = list(JudgeServer.objects.filter(
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
@db_task(retries=1, retry_delay=30)  # 重试3次，每次间隔10秒
def process_judge_task(task_data):
    """
    处理判题任务的主函数 - 最多重试30次，之后返回系统繁忙
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
    available_server, judge_servers = get_available_judge_server()
    if not available_server:
        retry_count += 1
        # 从处理中集合移除
        if submission_id:
            PROCESSING_TASKS.discard(f"task_{submission_id}")
        # 如果已经重试了30次，标记为系统繁忙
        if retry_count >= 30:
            # logger.error(f"重试次后仍无可用判题机，标记为系统繁忙：{submission_id}")
            if submission_id:
                try:
                    submit = Submit.objects.get(id=submission_id)
                    submit.status = "系统繁忙"
                    submit.result = json.dumps({"error": "判题系统繁忙，请稍后再试"})
                    submit.save()
                    cache_key = f"{RESULT_CACHE_PREFIX}{submit.id}"
                    #submit_cache_key = f"submit_{submission_id}"

                    # 更新缓存
                    try:
                        #serialized_submit = pickle.dumps(submit)
                        serialized_submit = SubmitSerializer(submit).data
                        submit_redis.setex(cache_key, 3600, serialized_submit)  # 缓存1小时
                    except Exception as cache_error:
                        submit_redis.delete(cache_key)
                except Exception as e:
                    pass
            return {
                'status': 'failed',
                'error': 'busy',
                'message': '判题系统繁忙，请稍后再试'
            }
        # 否则抛出异常以触发Huey的重试机制
        task_data['retry_count'] = retry_count  # 保存重试次数
        raise Exception("没有可用判题机")

    try:
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

                submit.result = response.json()
                # 保存更新
                submit.save()
                cache_key = f"{RESULT_CACHE_PREFIX}{submit.id}"
                try:
                    serialized_submit = SubmitSerializer(submit).data
                    submit.status = msg["status"]
                    submit.result = response.json()
                    submit_redis.setex(cache_key, 3600, serialized_submit)  # 缓存1小时
                except Exception as cache_error:
                    submit_redis.delete(cache_key)
                if msg["status"] == "Accepted":
                    submit.problem.accept()  # 增加通过次数

                submit.problem.summit()
                submit.problem.save()

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

            # 返回成功状态和结果
            return {
                'status': 'success',
                'result': msg,
            }

        except Exception as e:
            # 先处理数据库更新，再决定是否重试
            logger.warning(f"判题机处理任务失败: {str(e)}")
            # 刷新判题机列表
            try:
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
            except Exception as refresh_error:
                logger.error(f"刷新判题机列表失败: {str(refresh_error)}")

            # 更新提交状态
            if submission_id:
                try:
                    with transaction.atomic():
                        submit = Submit.objects.get(id=submission_id)

                        # 只有在最后一次重试失败后才更新状态
                        if retry_count >= 30:  # 已尝试3次
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
            if retry_count >= 30:  # 第3次尝试后结束
                return {
                    'status': 'failed',
                    'error': 'exception',
                    'message': str(e)
                }

            # 否则增加重试计数并继续重试
            task_data['retry_count'] = retry_count + 1
            logger.info(f"判题任务将进行第{retry_count + 2}次尝试（共3次）")
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

    finally:
        if submission_id:
            PROCESSING_TASKS.discard(f"task_{submission_id}")