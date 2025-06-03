from django.urls import path
from .views import (
    HomePageAPI, SubmitResultAPI, SubmitAPI, Judger_HeartAPI,
    JudgeServerAPI,TestAPI,RunAPI,RunResultAPI
)

urlpatterns = [
    path('', HomePageAPI.as_view()),
    path('submit/', SubmitAPI.as_view(), name='submit'),
    #path('run/',RunAPI.as_view(),name='run'),
    path('test/', TestAPI.as_view()),
    path('result/', SubmitResultAPI.as_view()),
    path('run/', RunAPI.as_view(), name='run'),
    path('run_result/', RunResultAPI.as_view()),
]