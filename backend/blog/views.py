from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Blog
from .serializers import BlogSerializer

# Create your views here.

class BlogViewSet(viewsets.ModelViewSet):
    # 定义查询集，获取所有Blog对象
    queryset = Blog.objects.all()
    # 定义序列化器类，用于将Blog对象转换为JSON格式
    serializer_class = BlogSerializer
    # 定义权限类，只有认证用户或只读用户才能访问
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # 在创建Blog对象时，将作者设置为当前请求的用户
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        # 获取当前请求的Blog对象
        blog = self.get_object()
        # 增加Blog的点赞数
        blog.likes += 1
        # 保存修改后的Blog对象
        blog.save()
        # 返回新的点赞数
        return Response({'likes': blog.likes})
    
    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        # 获取当前请求的Blog对象
        blog = self.get_object()
        # 增加Blog的浏览次数
        blog.views += 1
        # 保存修改后的Blog对象
        blog.save()
        # 返回新的浏览次数
        return Response({'views': blog.views})
