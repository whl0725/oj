from django.http import StreamingHttpResponse
from django.template.defaultfilters import title
from httpcore import stream
from pyexpat.errors import messages

from .models import AIChatSession, KnowledgeBase
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
import logging
import uuid
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from user.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.views.decorators.http import condition
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import AIChatSessionSerializer
logger = logging.getLogger(__name__)

class SSERenderer:
    media_type = 'text/event-stream'
    format = 'sse'
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

@csrf_exempt
@api_view(['POST'])
@renderer_classes([SSERenderer, JSONRenderer])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        #print(data)
        user_id = data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=404)
        message = data.get('message')
        chat_id = data.get('chat_id')
        kb_id = data.get('kb_id')
        # 获取或创建会话
        if chat_id:
            chat_session = AIChatSession.objects.get(chat_id=chat_id)
            # 获取现有内容
            existing_content = chat_session.content or {}
            messages = existing_content.get('messages', [])
        else:
            chat_id = str(uuid.uuid4())
            chat_session = AIChatSession.objects.create(
                user=user,
                chat_id=chat_id,
                kb_id=kb_id,
                created_at=timezone.now(),
                content={'messages': []},
                title = message[0:10]
            )
            messages = []

        # 添加用户消息到历史记录
        messages.append({
            'role': 'user',
            'content': message,
            'timestamp': timezone.now().isoformat()
        })
        # 构造请求FastGPT的数据
        fastgpt_data = {
            'chatId': chat_id,
            "model": "Qwen-plus",
            'messages': messages,  # 发送完整的历史消息
            'stream': True,
            'detail': False
        }
        
        # 获取知识库配置
        fastgpt = KnowledgeBase.objects.get(id=kb_id)
        fastgpt_key = fastgpt.api_key
        fastgpt_url = fastgpt.ip
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {fastgpt_key}'
        }
        
        def event_stream():
            try:
                response = requests.post(
                    fastgpt_url,
                    headers=headers,
                    json=fastgpt_data,
                    stream=True
                )
                response.raise_for_status()
                
                # 用于收集完整的AI响应
                ai_response_content = []
                
                for line in response.iter_lines(decode_unicode=True):
                    # 检查行是否非空
                    if line:
                        yield f"{line}\n\n"
                        # 收集AI响应内容
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if data.get('choices') and data['choices'][0].get('delta', {}).get('content'):
                                    ai_response_content.append(data['choices'][0]['delta']['content'])
                            except json.JSONDecodeError:
                                continue
                # 保存完整的对话历史
                if ai_response_content:
                    ai_message = {
                        'role': 'assistant',
                        'content': ''.join(ai_response_content),
                        'timestamp': timezone.now().isoformat()
                    }
                    messages.append(ai_message)
                    chat_session.content = {'messages': messages}
                    chat_session.save()
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"FastGPT请求失败: {str(e)}")
                yield f"data: {json.dumps({'error': 'FastGPT请求失败'})}\n\n".encode('utf-8')
            except Exception as e:
                logger.error(f"处理流式响应时发生错误: {str(e)}")
                yield f"data: {json.dumps({'error': '处理响应时发生错误'})}\n\n".encode('utf-8')
        
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Expose-Headers'] = 'X-Chat-ID'
        response['X-Chat-ID'] = chat_id
        return response
    except Exception as e:
        logger.exception(f"处理AI聊天请求时发生错误: {str(e)}")
        return Response({
            'error': f'处理请求时发生错误: {str(e)}',
            'success': False
        }, status=500)



class ChatHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
            user = request.user
            # 获取用户最近的10条聊天记录，按创建时间降序排序
            chat_sessions = AIChatSession.objects.filter(user=user.id,kb=1).order_by('-created_at')[:10]
            # 构建响应数据
            history = []
            for session in chat_sessions:
                history.append({
                    'chat_id': session.chat_id,
                    'title': session.title,
                })
            
            return Response({
                'history': history,
                'success': True
            }, status=200)


class ChatDetailsAPI(APIView):

    def post(self,request):
        chat_id = request.data.get('chat_id')
        print(chat_id)
        chat_session = AIChatSession.objects.get(chat_id=chat_id,kb=1)
        messages = AIChatSessionSerializer(chat_session)
        #print(messages.data['content']['messages'])
        return Response({
            "chat_id": chat_id,
            'messages': messages.data['content']['messages'],
        })


class ChatDetailsProcessAPI(APIView):
    def post(self,request):
        chat_id = request.data.get('chat_id')
        print(chat_id)
        chat_session = AIChatSession.objects.get(chat_id=chat_id,kb=1)
        messages = AIChatSessionSerializer(chat_session)
        print(messages.data['content']['messages'])
        return Response({
            "chat_id": chat_id,
            'messages': messages.data['content']['messages'],
        })