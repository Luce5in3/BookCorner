"""
用户模块视图
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from utils.response import success_response, error_response
from utils.permissions import IsAdmin, IsSuperAdmin
from .serializers import (
    UserRegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
    UserAdminSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    用户注册
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(
            data={
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
            },
            message='注册成功',
            code=201
        )


class LoginView(TokenObtainPairView):
    """
    用户登录
    POST /api/auth/login/
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return error_response(message='用户名或密码错误', code=401, status_code=status.HTTP_401_UNAUTHORIZED)
        
        return success_response(
            data=serializer.validated_data,
            message='登录成功'
        )


class UserProfileView(APIView):
    """
    当前用户信息
    GET /api/users/me/ - 获取个人信息
    PUT /api/users/me/ - 更新个人信息
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)
    
    def put(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 返回更新后的完整信息
        profile_serializer = UserProfileSerializer(request.user)
        return success_response(data=profile_serializer.data, message='更新成功')


class ChangePasswordView(APIView):
    """
    修改密码
    POST /api/users/me/password/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return success_response(message='密码修改成功')


class UserListView(generics.ListAPIView):
    """
    用户列表（管理员）
    GET /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'status']
    search_fields = ['username', 'real_name', 'email', 'phone']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    用户详情（管理员）
    GET /api/users/{id}/
    PUT/PATCH /api/users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 超级管理员才能修改角色
        if 'role' in request.data and not request.user.is_super_admin:
            return error_response(message='只有超级管理员才能修改用户角色', code=403, status_code=status.HTTP_403_FORBIDDEN)
        
        # 不能修改超级管理员的角色和状态
        if instance.is_super_admin and instance != request.user:
            if 'role' in request.data or 'status' in request.data:
                return error_response(message='不能修改超级管理员的角色或状态', code=403, status_code=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(data=serializer.data, message='更新成功')


class UserStatusToggleView(APIView):
    """
    切换用户状态（管理员）
    POST /api/users/{id}/toggle-status/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return error_response(message='用户不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 不能禁用自己
        if user == request.user:
            return error_response(message='不能修改自己的状态', code=400)
        
        # 不能禁用超级管理员
        if user.is_super_admin:
            return error_response(message='不能修改超级管理员的状态', code=403, status_code=status.HTTP_403_FORBIDDEN)
        
        # 切换状态
        user.status = 0 if user.status == 1 else 1
        user.save()
        
        return success_response(
            data={'status': user.status, 'status_display': user.get_status_display()},
            message=f'用户已{"启用" if user.status == 1 else "禁用"}'
        )
