# 判题相关常量定义
JUDGE_SERVER_CACHE_KEY = "judge_servers_list"  # 缓存中存储判题机列表的键名
JUDGE_SERVER_CACHE_TTL = 60 * 10  # 缓存过期时间，10分钟
JUDGE_QUEUE_KEY = "judge_tasks_queue"  # Redis列表用作消息队列



# 判题结果
RESULT_CACHE_PREFIX = "judge_result:"
RESULT_CACHE_TTL = 3600  # 结果缓存1小时