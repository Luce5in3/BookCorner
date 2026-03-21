"""
用户模块序列化器
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'real_name', 'email', 'phone')
        extra_kwargs = {
            'real_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义登录序列化器，返回用户信息"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 检查用户状态
        if self.user.status == 0:
            raise serializers.ValidationError('账号已被禁用')
        
        # 添加用户信息到响应
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'real_name': self.user.real_name,
            'email': self.user.email,
            'phone': self.user.phone,
            'role': self.user.role,
            'role_display': self.user.get_role_display(),
            'avatar_url': self.user.avatar_url,
        }
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'real_name', 'email', 'phone',
            'role', 'role_display', 'status', 'status_display',
            'avatar_url', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'username', 'role', 'status', 'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    
    class Meta:
        model = User
        fields = ('real_name', 'email', 'phone', 'avatar_url')
    
    def validate_email(self, value):
        user = self.context['request'].user
        if value and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被使用')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次密码不一致'})
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器（管理员用）"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'real_name', 'email', 'phone',
            'role', 'role_display', 'status', 'status_display',
            'avatar_url', 'created_at'
        )


class UserAdminSerializer(serializers.ModelSerializer):
    """用户管理序列化器（管理员用）"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'real_name', 'email', 'phone',
            'role', 'role_display', 'status', 'status_display',
            'avatar_url', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'username', 'created_at', 'updated_at')
