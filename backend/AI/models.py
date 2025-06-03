from django.db import models
from django.utils import timezone
from user.models import User


# 知识库信息
class KnowledgeBase(models.Model):
    """
    FastGPT知识库配置信息
    """
    #kb_id = models.CharField(max_length=36, unique=True)  # FastGPT知识库ID
    name = models.CharField(max_length=100)

    description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)


    ip = models.CharField(null=True, blank=True,max_length=100)

    api_key = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = "knowledge_base"

# ai对话
class AIChatSession(models.Model):
    """
    AI对话会话核心信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kb = models.ForeignKey(KnowledgeBase, on_delete=models.SET_NULL, null=True)  # 关联知识库
    #session_id = models.CharField(max_length=40, unique=True)  # FastGPT返回的sessionId
    chat_id = models.CharField(max_length=40, unique=True)  # FastGPT的chatId
    # 会话元数据
    title = models.CharField(max_length=200, default="新对话")
    created_at = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(auto_now=True)
    #is_active = models.BooleanField(default=True)
    content = models.JSONField(default=dict) # 存储FastGPT的完整上下文

    class Meta:
        db_table = "ai_chat_session"
        indexes = [
            models.Index(fields=['user', 'last_active']),
        ]
