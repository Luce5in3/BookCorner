"""
认证相关路由
/api/auth/
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileView, ChangePasswordView

urlpatterns = [
    # 注册
    path('register/', RegisterView.as_view(), name='register'),
    # 登录
    path('login/', LoginView.as_view(), name='login'),
    # JWT Token 刷新
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 当前用户信息
    path('me/', UserProfileView.as_view(), name='user_profile'),
    # 修改密码
    path('password/', ChangePasswordView.as_view(), name='change_password'),
]
