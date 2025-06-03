import logging
import os
import multiprocessing
# 日志配置
log_url = 'log'
loger = logging.getLogger(__name__)
handler = logging.FileHandler(log_url)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
loger.addHandler(handler)
loger.setLevel(logging.INFO)

def load_config():
    """加载配置，如果环境变量不存在则使用默认值"""
    config = {}
    
    # 使用 os.getenv 替代 os.environ
    config['TOKEN'] = os.getenv('TOKEN', '123456')
    config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8000/api/heart_judger/')
    config['MAX_WORKERS'] = int(os.getenv('JUDGE_MAX_WORKERS', 
                           max(1, multiprocessing.cpu_count() // 6)))
    config['BATCH_SIZE'] = int(os.getenv('JUDGE_BATCH_SIZE', 1))
    
    # 记录获取到的环境变量值
    loger.info(f"Loaded TOKEN from env: {config['TOKEN']}")
    loger.info(f"Loaded BACKEND_URL from env: {config['BACKEND_URL']}")
    
    # 工作目录配置
    config['JUDGER_WORKSPACE'] = "compile/"
    
    return config

# 加载配置
config = load_config()

# 导出配置变量
TOKEN = config['TOKEN']
BACKEND_URL = config['BACKEND_URL']
JUDGER_WORKSPACE = config['JUDGER_WORKSPACE']
MAX_WORKERS = config['MAX_WORKERS']
BATCH_SIZE = config['BATCH_SIZE']

# 记录最终使用的配置
loger.info(f"Using configuration: TOKEN={TOKEN}, BACKEND_URL={BACKEND_URL}, JUDGER_WORKSPACE={JUDGER_WORKSPACE}, MAX_WORKERS={MAX_WORKERS}, BATCH_SIZE={BATCH_SIZE}")
