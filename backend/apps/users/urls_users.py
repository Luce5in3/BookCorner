"""
用户管理路由
/api/users/
"""
from django.urls import path
from .views import (
    UserProfileView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
    UserStatusToggleView,
)

urlpatterns = [
    # 当前用户
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/password/', ChangePasswordView.as_view(), name='change_password'),
    
    # 用户管理（管理员）
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/toggle-status/', UserStatusToggleView.as_view(), name='user_toggle_status'),
]
