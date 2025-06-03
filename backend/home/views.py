from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Announcement
from .serializers import AnnouncementSerializer, HomePageSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

class HomePageAPI(APIView):
    """
    首页 API，返回分页后的公告
    """
    def get(self, request):
        try:
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 5)
            
            # 获取最新的公告（只获取可见的）
            announcements = Announcement.objects.filter(visible=True).order_by('-create_time')
            
            # 使用Django的分页器
            paginator = Paginator(announcements, page_size)
            
            try:
                current_page = paginator.page(page)
            except PageNotAnInteger:
                current_page = paginator.page(1)
            except EmptyPage:
                current_page = paginator.page(paginator.num_pages)
            
            # 使用序列化器处理数据
            serializer = HomePageSerializer(current_page.object_list, many=True)
            
            return Response({
                "code": 0,
                "data": {
                    "announcements": serializer.data,
                    "total": paginator.count,
                    "total_pages": paginator.num_pages,
                    "current_page": int(page)
                },
                "message": "success"
            })
            
        except Exception as e:
            return Response({
                "code": 1,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Announcement_Content(APIView):
    """
    公告 API，返回对应的公告
    """
    def get(self, request):
        announcement_id = request.GET.get('id')
        try:
            # 获取对应的公告
            announcement = Announcement.objects.get(id=announcement_id)
            # 使用序列化器处理数据
            serializer = AnnouncementSerializer(announcement)
            return Response({
                "code": 0,
                "data": {
                    "announcement": serializer.data
                },
                "message": "success"
            })
        except Exception as e:
            return Response({
                "code": 1,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)