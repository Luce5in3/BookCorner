"""
全局权限类模块
"""
from rest_framework.permissions import BasePermission


class IsReader(BasePermission):
    """普通读者权限（role >= 0）"""
    message = '需要读者权限'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """管理员权限（role >= 1）"""
    message = '需要管理员权限'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role >= 1
        )


class IsSuperAdmin(BasePermission):
    """超级管理员权限（role = 2）"""
    message = '需要超级管理员权限'
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 2
        )


class IsAdminOrReadOnly(BasePermission):
    """管理员可写，其他只读"""
    message = '需要管理员权限才能执行此操作'
    
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role >= 1
        )
