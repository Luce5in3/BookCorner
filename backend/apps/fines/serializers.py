"""
罚款模块序列化器
"""
from rest_framework import serializers
from .models import Fine, FineStatus


class FineListSerializer(serializers.ModelSerializer):
    """罚款列表序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='borrow.book.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Fine
        fields = (
            'id', 'user', 'username', 'real_name',
            'borrow', 'book_title',
            'amount', 'reason', 'status', 'status_display',
            'created_at', 'paid_at'
        )


class FineDetailSerializer(serializers.ModelSerializer):
    """罚款详情序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='borrow.book.title', read_only=True)
    book_author = serializers.CharField(source='borrow.book.author', read_only=True)
    barcode = serializers.CharField(source='borrow.book_copy.barcode', read_only=True)
    borrow_at = serializers.DateTimeField(source='borrow.borrow_at', read_only=True)
    due_at = serializers.DateTimeField(source='borrow.due_at', read_only=True)
    return_at = serializers.DateTimeField(source='borrow.return_at', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Fine
        fields = (
            'id', 'user', 'username', 'real_name',
            'borrow', 'book_title', 'book_author', 'barcode',
            'borrow_at', 'due_at', 'return_at',
            'amount', 'reason', 'status', 'status_display',
            'created_at', 'paid_at'
        )


class FineUpdateSerializer(serializers.ModelSerializer):
    """罚款更新序列化器（管理员）"""
    
    class Meta:
        model = Fine
        fields = ('status',)
    
    def validate_status(self, value):
        if value not in [FineStatus.PAID, FineStatus.EXEMPTED]:
            raise serializers.ValidationError('只能标记为已缴或已免除')
        return value


class MyFineSerializer(serializers.ModelSerializer):
    """我的罚款序列化器"""
    book_title = serializers.CharField(source='borrow.book.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Fine
        fields = (
            'id', 'borrow', 'book_title',
            'amount', 'reason', 'status', 'status_display',
            'created_at', 'paid_at'
        )
