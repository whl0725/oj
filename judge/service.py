import os
import schedule
import time
import requests
import logging
import threading
from _judge.config import loger

# 配置日志


# 这个文件用于定义服务类，向后端发送心跳请求
class JudgeService:
    def __init__(self):
        # 从环境变量获取配置
        self.BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.SERVICE_URL = os.getenv('SERVICE_URL', 'http://localhost:5000')
        self._thread = None
        self._running = False
     
    def _request(self, data):
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f"{self.BACKEND_URL}",
                json=data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                loger.info("Heartbeat sent successfully")
            else:
                loger.error(f"Failed to send heartbeat. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            loger.error(f"Error sending heartbeat: {str(e)}")

    def send_heartbeat(self):
        data = {
            "active": "heartbeat",
            "service_url": self.SERVICE_URL
        }
        self._request(data)

    def _run_schedule(self):
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        if self._thread is not None:
            return

        self._running = True
        # 立即发送一次心跳
        self.send_heartbeat()
        # 设置定时任务
        schedule.every(5).seconds.do(self.send_heartbeat)
        
        # 在新线程中运行定时任务
        self._thread = threading.Thread(target=self._run_schedule)
        self._thread.daemon = True  # 设置为守护线程
        self._thread.start()
        
        loger.info("Heartbeat service started")

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        schedule.clear()
        loger.info("Heartbeat service stopped")

def run_service():
    # 检查是否启用心跳检测
    if not os.getenv('ENABLE_HEARTBEAT'):
        loger.info("Heartbeat service is disabled")
        return

    try:
        service = JudgeService()
        
        # 立即发送一次心跳
        service.send_heartbeat()
        
        # 设置定时任务，固定为1分钟
        schedule.every(60).seconds.do(service.send_heartbeat)
        
        loger.info("Service started. Sending heartbeat every 60 seconds")
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except Exception as e:
        loger.error(f"Service error: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        run_service()
    except KeyboardInterrupt:
        loger.info("Service stopped by user")
    except Exception as e:
        loger.error(f"Service crashed: {str(e)}")