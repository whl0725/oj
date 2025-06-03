from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class JudgerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'judger'
    
    def ready(self):
        """
        当应用准备好时调用的方法
        """
        logger.info("判题应用已启动")
        
        # 启动Redis队列处理线程
        try:
            # 避免在Django reload过程中重复启动
            import sys
            if not any(arg.endswith('manage.py') for arg in sys.argv) or ('runserver' in sys.argv):
                from .tasks import start_judge_queue_worker
                start_judge_queue_worker()
                logger.info("Redis备用队列处理线程已启动")
        except Exception as e:
            logger.error(f"启动Redis备用队列处理线程失败: {str(e)}")
        
        # 不要在这里启动Huey消费者进程
        # Huey消费者应该使用命令行单独启动: python manage.py run_huey
