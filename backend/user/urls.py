#from backend.urls import urlpatterns
from django.urls import path,re_path
from django.views import View

from .views import (UserView, UserLoginAPI,
                    UserLogoutAPI, UserRegisterAPI,
                    UserUpdateAPI, AvatarUploadAPI,
                    UpdataEmailAPI,UpdataPasswordAPI,
                    ProflieAPI,UserSubmissionsAPI,UserInfoAPI)

urlpatterns = [
    path('login/',UserLoginAPI.as_view()),
    path('logout/',UserLogoutAPI.as_view()),
    #path('user/',UserView.as_view()),
    path('register/',UserRegisterAPI.as_view()),
    path('update/',UserUpdateAPI.as_view()),
    path('avatar/',AvatarUploadAPI.as_view()),
    path('update_password/',UpdataPasswordAPI.as_view()),
    path('update_email/',UpdataEmailAPI.as_view()),
    path('profile/',ProflieAPI.as_view()),
    path('submitions/',UserSubmissionsAPI.as_view()),
    path('info/',UserInfoAPI.as_view()),
]