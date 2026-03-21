"""
公告管理路由
/api/announcements/
"""
from django.urls import path
from .views import (
    AnnouncementListView,
    AnnouncementDetailView,
    AnnouncementPublishView,
    AnnouncementArchiveView,
    PublishedAnnouncementListView,
    PublishedAnnouncementDetailView,
    LatestAnnouncementView,
)

urlpatterns = [
    # 公开接口（无需登录）
    path('published/', PublishedAnnouncementListView.as_view(), name='published_announcements'),
    path('published/<int:pk>/', PublishedAnnouncementDetailView.as_view(), name='published_announcement_detail'),
    path('latest/', LatestAnnouncementView.as_view(), name='latest_announcements'),
    
    # 公告管理（管理员）
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('<int:pk>/publish/', AnnouncementPublishView.as_view(), name='announcement_publish'),
    path('<int:pk>/archive/', AnnouncementArchiveView.as_view(), name='announcement_archive'),
]
