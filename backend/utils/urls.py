from django.urls import path,re_path
from .views import (CaptchaAPIView, TokenRefreshAPI,
                    SendResetCodeAPI, ResetPasswordAPI)

urlpatterns = [
   path('captcha/', CaptchaAPIView.as_view()),
   path('token/refresh/',TokenRefreshAPI.as_view()),
   path('send-reset-code/', SendResetCodeAPI.as_view()),
   path('reset-password/', ResetPasswordAPI.as_view())
]