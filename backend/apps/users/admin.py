"""
用户模块 Admin 配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'real_name', 'email', 'role', 'status', 'created_at')
    list_filter = ('role', 'status', 'is_staff')
    search_fields = ('username', 'real_name', 'email', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('real_name', 'email', 'phone', 'avatar_url')}),
        ('权限', {'fields': ('role', 'status', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'real_name', 'password1', 'password2', 'role', 'status'),
        }),
    )
