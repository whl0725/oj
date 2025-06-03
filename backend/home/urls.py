from django.urls import path
from .views import HomePageAPI, Announcement_Content

urlpatterns = [
    path('', HomePageAPI.as_view(), name='home'),
    path('announcement/',Announcement_Content.as_view(), name='announcement'),
] 