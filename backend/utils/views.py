from rest_framework.views import APIView
from rest_framework.response import Response
from captcha.models import CaptchaStore
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from captcha.image import ImageCaptcha  # 确保导入路径正确
import os  # 导入 os 模块以处理文件路径
import base64  # 导入 base64 模块以处理图像数据
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import random
import string
from django.core.cache import cache

User = get_user_model()

def captcha_image_url(hashkey):
    # 生成验证码图像的URL
    # 这里可以根据您的需求实现图像生成逻辑
    return f"{settings.STATIC_URL}captcha/{hashkey}.png"  # 示例返回URL            

def verify(hashkey, response):
    # 检查hashkey和response是否为空
    if not hashkey or not response:
        # 如果参数不完整，返回错误信息
        return {'valid': False, 'message': '参数不完整'}
    CaptchaStore.remove_expired()
    try:
        # 根据hashkey从CaptchaStore中获取对应的验证码对象
        captcha = CaptchaStore.objects.get(hashkey=hashkey)
        # 将用户输入的response转换为小写并与存储的response进行比较
        if captcha.response == response.lower():
            # 如果验证码正确，删除该验证码对象
            captcha.delete()  # 验证成功后删除
            # 返回验证成功的JSON响应
            return True
        else:
            # 如果验证码错误，返回错误信息
            return {'valid': False, 'message': '验证码错误'}
    except CaptchaStore.DoesNotExist:
        # 如果验证码对象不存在（可能已过期），返回错误信息
        return {'valid': False, 'message': '验证码已过期'}

class CaptchaAPIView(APIView):
    """
    验证码API
    """
    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        # image_url = captcha_image_url(hashkey)
        
        # 生成并保存验证码图片
        captcha = CaptchaStore.objects.get(hashkey=hashkey)
        image = ImageCaptcha()
        data = image.generate(captcha.response)
        # datas= image.generate(captcha.response)
        # image_path = os.path.join(settings.STATIC_CAPTCHA, 'captcha', f'{hashkey}.png')
        image_base64 = base64.b64encode(data.read()).decode('utf-8')

        #确保目录存在
        # os.makedirs(os.path.dirname(image_path), exist_ok=True)
        # with open(image_path, 'wb') as f:
        #     f.write(data.read())
        return Response({
            'hashkey': hashkey,
            # 'image_url': image_url,
            'image_base64': image_base64
        })


class TokenRefreshAPI(APIView):
    def post(self, request):

        refresh_token = request.data.get('refresh_token')
        # 使用refresh_token获取新的token
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        new_refresh_token = str(refresh)

        # 返回新的token
        return Response({
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        })
    
class SendResetCodeAPI(APIView):

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                "code":401,
                'message': '邮箱不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "code":404,
                'message': '该邮箱未注册'
            })
        # 生成6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))
        # 将验证码存储在缓存中，设置1分钟过期
        cache.set(f'reset_code_{email}', code, 60)
        # 发送邮件
        subject = '重置密码验证码'
        message = f'您的重置密码验证码是：{code}，验证码有效期为5分钟。'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
            return Response({
                'message': '验证码已发送'
            })
        except Exception as e:
            return Response({
                'message': '验证码发送失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResetPasswordAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('password')
        
        if not all([email, code, new_password]):
            return Response({
                'message': '参数不完整'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 验证验证码
        cached_code = cache.get(f'reset_code_{email}')
        if not cached_code or cached_code != code:
            return Response({
                'message': '验证码错误或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 删除验证码缓存
            cache.delete(f'reset_code_{email}')
            return Response({
                'message': '密码重置成功'
            })
        except User.DoesNotExist:
            return Response({
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)