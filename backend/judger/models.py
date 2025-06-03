from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class JudgeServer(models.Model):
    # server_id = models.CharField(max_length=100, unique=True)
    server_name = models.CharField(max_length=100)
    server_ip = models.CharField(max_length=100)
    server_port = models.IntegerField()
    server_status = models.CharField(max_length=100, choices=[('0', '空闲'), ('1', '繁忙'), ('2', '离线')])
    server_create_time = models.DateTimeField(auto_now_add=True)
    server_token = models.CharField(max_length=100)
    server_HeartTime = models.DateTimeField(auto_now=True)
    is_disabled = models.BooleanField(default=False,
                                      help_text='是否禁用')
    
    HEARTBEAT_TIMEOUT = 30  # 心跳超时时间（秒）
    
    class Meta:
        db_table = "judge_server"
    
    def is_alive(self):
        """检查判题机是否存活"""
        if self.is_disabled:
            return False
        
        # 检查最后心跳时间是否超时
        timeout_threshold = timezone.now() - timedelta(seconds=self.HEARTBEAT_TIMEOUT)
        return self.server_HeartTime >= timeout_threshold
    
    def update_status(self):
        """更新判题机状态"""
        if not self.is_alive():
            self.server_status = '2'  # 设置为离线
            self.save()
        return self.server_status
    
    def __str__(self):
        return f"{self.server_name} ({self.get_server_status_display()})"
    



