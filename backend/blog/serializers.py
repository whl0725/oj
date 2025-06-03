from rest_framework import serializers
from .models import Blog, Comment
from user.serializers import UserProfileSerializer

class BlogSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    content = serializers.CharField()  # 处理富文本内容
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'created_at', 
                 'updated_at', 'is_public', 'views', 'likes']
        read_only_fields = ['views', 'likes', 'created_at', 'updated_at'] 