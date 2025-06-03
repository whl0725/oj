from rest_framework import serializers
from .models import Announcement
from blog.models import Blog
from user.serializers import UserProfileSerializer

class  HomePageSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    #content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = ['id', 'title','create_time',
                  'last_update_time','created_by']
        read_only_fields = ['create_time', 'last_update_time']
    
    def get_content_preview(self, obj):
        # 返回内容预览，去除HTML标签
        from django.utils.html import strip_tags
        content = strip_tags(obj.content)
        return content[:200] + '...' if len(content) > 200 else content

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['content']