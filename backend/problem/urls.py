from django.urls import path
from .views import ProblemDetails, ProblemSubminAPI,Problem_Tag,ProblemList

urlpatterns = [
    path('submit/', ProblemSubminAPI.as_view(), name='problem-submit'),
    #path('<int:problem_id>/', ProblemDetailAPI.as_view(), name='problem-detail'),
    path('details/', ProblemDetails.as_view(), name='problem-details'),
    path('tag/', Problem_Tag.as_view(), name='problem-tag'),
    path('list/', ProblemList.as_view(), name='problem-list'),
]