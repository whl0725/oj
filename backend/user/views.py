from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User,UserProfile
from .serializers import (UserSerializer, UserLoginSerializer,
                          UserRegisterSerializer,UserUpdateSerializer,
                          UserProfileSerializer,UserSubmissionsSerializer)
from rest_framework import status
from django.contrib import auth
from utils.api import validate_serializer
from django.views.decorators.csrf import csrf_exempt
from utils.views import verify
from utils.untils import validate_email
from rest_framework_simplejwt.tokens import RefreshToken
import os
from django.conf import settings
from competition.models import Submit
from django.core.paginator import Paginator

class UserView(APIView):

    def get(self,request):
        content = User.objects.all()
        serializers= UserSerializer(content, many=True)
        return Response(serializers.data)

    def post(self,request):
        obj = UserSerializer(data=request.data)
        try:
            if obj.is_valid():
                obj.save()
                user_data = {
                    'username':request.data['username'],
                    'password':request.data['password'],
                    'user_img':"/static/1,json.jpg",
                }
                return Response(user_data)
            else:
                return Response(obj.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(obj.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPI(APIView):

    @validate_serializer(UserLoginSerializer)
    def post(self, request, validated=None):

        data = request.data
        if validate_email(data["username"]):
            user_obj = User.objects.filter(email=data["username"])
            username = user_obj.get().username
            user = auth.authenticate(username=username, password=data["password"])
        else:
            user = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            if not user.is_active:
                return Response("Your account cannot be used")
            else:
                # 生成JWT
                refresh = RefreshToken.for_user(user)
                userprofile = UserProfile.objects.get(user_id=user.id)
                avatar = userprofile.avatar
                email = user.email
                return Response({
                    "id":user.id,
                    "username": user.username,
                    "refresh_token": str(refresh),#刷新token（长期）
                    "access_token": str(refresh.access_token),#访问token（短期）
                    "avatar": avatar,
                    "email": email,
                    "code": 200
                })
        else:
            return Response({
                "code": 401,
                "message":"Invalid username or password"
            })

class UserLogoutAPI(APIView):
    def post(self, request):
        """
        User logout api
        :param request:
        :return:"Succeeded Logout"
        """
        auth.logout(request)
        return Response("Succeeded Logout")

class UserRegisterAPI(APIView):
    """
    User register api
    """
    def post(self, request):
        data = request.data
        data["username"] = data["username"].lower()
        data["email"] = data["email"]
        if not verify(data["hashkey"],data["captcha"]):
            return Response("Invalid captcha")
        if User.objects.filter(username=data["username"]).exists():
            return Response("Username already exists")
        if User.objects.filter(email=data["email"]).exists():
            return Response("Email already exists")
        user = User.objects.create(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        user.save()
        avatar=UserProfile.objects.create(user=user).avatar
        data_file = {
            "avatar":avatar,
            "state":"Succeeded"
        }
        return Response(data_file)

class UserUpdateAPI(APIView):
    """
    User update api
    使用序列化器，做到部分更新
    """
    def put(self, request):
        try:
            # 获取用户ID
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    "code": 1,
                    "message": "缺少用户ID"
                }, status=status.HTTP_400_BAD_REQUEST)

            # 获取用户profile
            try:
                user_profile = UserProfile.objects.get(user_id=user_id)
            except UserProfile.DoesNotExist:
                return Response({
                    "code": 1,
                    "message": "用户不存在"
                }, status=status.HTTP_404_NOT_FOUND)

            # 使用序列化器进行更新
            data = request.data.copy()  # 创建数据的副本
            data.pop("user_id", None)  # 移除user_id字段
            
            print("处理后的数据:", data)  # 打印处理后的数据
            
            serializer = UserProfileSerializer(
                user_profile,
                data=data,
                partial=True
            )
            
            # 先验证数据
            if not serializer.is_valid():
                print("验证错误:", serializer.errors)  # 打印验证错误
                return Response({
                    "code": 1,
                    "message": "数据验证失败",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证通过后保存数据
            serializer.save()
            
            # 现在可以安全地访问 serializer.data
            return Response({
                "code": 0,
                "message": "更新成功",
                "data": serializer.data
            })

        except Exception as e:
            print("发生错误:", str(e))  # 打印具体错误
            return Response({
                "code": 1,
                "message": f"服务器错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvatarUploadAPI(APIView):
    """
    用户上传头像API
    """
    def post(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return Response({
                'code': 1,
                'message': '没有上传文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 确保 user/static 目录存在
        static_dir = os.path.join(settings.BASE_DIR, 'user', 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        # 保存文件
        file_path = os.path.join(static_dir, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        # 返回相对路径
        avatar_url = f'/static/{file.name}'
        # 更新用户头像
        data = request.data
        id = data.get("id")
        user = User.objects.get(id=id)
        userprofile = UserProfile.objects.get(user_id=user.id)
        userprofile.avatar = avatar_url
        userprofile.save()
        return Response({
            'code': 0,
            'message': '上传成功',
            'url': avatar_url
        })


class UpdataPasswordAPI(APIView):
    """
    用户更新密码API
    需要提供：
    - username: 用户名
    - old_password: 旧密码
    - new_password: 新密码
    API --
    code 400 - 数据不足
    """
    def post(self, request):
        data = request.data
        username = data.get("username")
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        print(data)
        # 验证必要参数
        if not all([username, old_password, new_password]):
            return Response({
                "code": 400,
                "message": "请提供用户名、旧密码和新密码"
            })

        user = User.objects.get(username=username)

        # 验证旧密码
        if not user.check_password(old_password):
            return Response({
                "code": 400,
                "message": "旧密码错误"
            })

        # 更新密码
        user.set_password(new_password)
        user.save()

        # 生成新的token
        refresh = RefreshToken.for_user(user)

        return Response({
            "code": 200,
            "message": "密码更新成功",
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token)
        })


class UpdataEmailAPI(APIView):
    """
    用户更新邮箱API
    需要提供：
    - username: 用户名
    - old_password: 旧密码
    - new_email: 新邮箱
    API --
    code 400 - 数据不足
    """
    def post(self, request):
        data = request.data
        username = data.get("username")
        old_password = data.get("old_password")
        new_email = data.get("new_email")
        print(data)
        # 验证必要参数
        if not all([username, old_password, new_email]):
            return Response({
                "code":400,
                "message": "请提供用户名、旧密码和新邮箱"
            })
        user = User.objects.get(username=username)
        # 验证旧密码
        if not user.check_password(old_password):
            return Response({
                "code": 400,
                "message": "旧密码错误"
            })
        # 更新邮箱
        user.email = new_email
        user.save()
        return Response({
            "code": 200,
            "message": "邮箱更新成功"
        })


class ProflieAPI(APIView):
    """
    User profile api
    修改个人资料
    """
    def post(self,request):
        data = request.data
        id = data.get("id")
        user = User.objects.get(id=id)

        return Response("User profile api")


class UserSubmissionsAPI(APIView):

    def post(self,request):
        user_id = request.data.get("id")
        page = request.data.get("page", 1)  # 当前页码，默认1
        page_size = request.data.get("page_size", 10)  # 每页大小，默认10
        
        # 获取所有数据并按提交时间倒序排序
        data = Submit.objects.filter(user_id=user_id).select_related('problem').order_by('-submit_time')
        
        # 创建分页器
        paginator = Paginator(data, page_size)
        # 获取当前页的数据
        current_page_data = paginator.get_page(page)
        
        # 序列化当前页数据
        serializer = UserSubmissionsSerializer(current_page_data, many=True)
        submissions_data = serializer.data

        # 为每条记录添加题目名称
        for item in submissions_data:
            submit = next((s for s in current_page_data if s.id == item['id']), None)
            if submit and submit.problem:
                item['problem_title'] = submit.problem.title
            else:
                item['problem_title'] = ''

        return Response({
            'code': 0,
            'data': {
                'submissions': submissions_data,
                'total': paginator.count,  # 总记录数
                'total_pages': paginator.num_pages,  # 总页数
                'current_page': page,  # 当前页
                'page_size': page_size  # 每页大小
            },
            'message': 'success'
        })

class UserInfoAPI(APIView):

    def post(self, request):
        user_id = request.data.get("id")
        try:
            # 获取用户基本信息
            user = User.objects.get(id=user_id)
            # 获取用户详细信息
            user_profile = UserProfile.objects.get(user_id=user_id)
            
            return Response({
                'code': 0,
                'data': {
                    'real_name': user_profile.real_name,
                    'username': user.username,
                    'email': user.email,
                    'avatar': user_profile.avatar,
                    'school': user_profile.school,
                    'major': user_profile.major,
                    'create_time': user.create_time,
                    'blog': user_profile.blog,
                    'github': user_profile.github,
                    'mood': user_profile.mood,
                    'language': user_profile.language
                },
                'message': 'success'
            })
            
        except User.DoesNotExist:
            return Response({
                'code': 1,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({
                'code': 1,
                'message': f'获取用户信息失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)