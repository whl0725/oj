from django.urls import path,re_path
from django.views import View
from .views import (PasswordAPI, CompetitionAPI,DescriptionAPI,
                    PasswordAPI,AnnouncementAPI,ProblemListAPI,
                    ProblemDetails,SubmissionListAPI)

urlpatterns = [
    path('match/', PasswordAPI.as_view()),
    path('list/', CompetitionAPI.as_view()),
    path('description/<int:id>/', DescriptionAPI.as_view()),
    path('password/', PasswordAPI.as_view()),
    path('announcements/<int:id>/',AnnouncementAPI.as_view()),
    path('problemslist/<int:id>/',ProblemListAPI.as_view()),
    path('problemslist/<int:competition_id>/problem/<int:problem_id>/', ProblemDetails.as_view(), name='competition-problem-details'),

    path('submissions/',SubmissionListAPI.as_view())
]




