from django.urls import path
from . import views
from .views import ChatHistoryAPI, ChatDetailsAPI,ChatDetailsProcessAPI

urlpatterns = [
    path('', views.ai_chat, name='ai_chat'),
    path('history/', ChatHistoryAPI.as_view(), name='chat_history'),
    path('details/',ChatDetailsAPI.as_view(), name='chat_details'),
    path('details_process/',ChatDetailsProcessAPI.as_view(), name='chat_details_process'),
]

