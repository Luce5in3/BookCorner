"""
借阅模块序列化器
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Borrow, Renewal, BorrowStatus
from apps.books.models import BookCopy, BookCopyStatus
from apps.books.serializers import BookCopyBriefSerializer


class BorrowListSerializer(serializers.ModelSerializer):
    """借阅列表序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    barcode = serializers.CharField(source='book_copy.barcode', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrow
        fields = (
            'id', 'user', 'username', 'real_name',
            'book', 'book_title', 'book_author',
            'book_copy', 'barcode',
            'borrow_at', 'due_at', 'return_at',
            'status', 'status_display', 'is_overdue', 'remark'
        )
    
    def get_is_overdue(self, obj):
        """是否逾期"""
        if obj.status == BorrowStatus.BORROWING:
            return timezone.now() > obj.due_at
        return obj.status == BorrowStatus.OVERDUE


class BorrowDetailSerializer(serializers.ModelSerializer):
    """借阅详情序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    barcode = serializers.CharField(source='book_copy.barcode', read_only=True)
    copy_location = serializers.CharField(source='book_copy.location', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True, default=None)
    renewals = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    overdue_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrow
        fields = (
            'id', 'user', 'username', 'real_name',
            'book', 'book_title', 'book_author', 'book_isbn',
            'book_copy', 'barcode', 'copy_location',
            'borrow_at', 'due_at', 'return_at',
            'status', 'status_display', 'is_overdue', 'overdue_days',
            'operator', 'operator_name', 'remark', 'renewals'
        )
    
    def get_renewals(self, obj):
        """获取续借记录"""
        renewals = obj.renewals.all()
        return RenewalSerializer(renewals, many=True).data
    
    def get_is_overdue(self, obj):
        if obj.status == BorrowStatus.BORROWING:
            return timezone.now() > obj.due_at
        return obj.status == BorrowStatus.OVERDUE
    
    def get_overdue_days(self, obj):
        """逾期天数"""
        if obj.status in [BorrowStatus.BORROWING, BorrowStatus.OVERDUE]:
            if timezone.now() > obj.due_at:
                return (timezone.now() - obj.due_at).days
        return 0


class BorrowCreateSerializer(serializers.Serializer):
    """借书序列化器"""
    book_copy_id = serializers.IntegerField(required=False)
    barcode = serializers.CharField(required=False, max_length=50)
    user_id = serializers.IntegerField(required=False)  # 管理员帮用户借书时使用
    days = serializers.IntegerField(default=30, min_value=1, max_value=90)  # 借阅天数
    remark = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, attrs):
        # 必须提供 book_copy_id 或 barcode
        if not attrs.get('book_copy_id') and not attrs.get('barcode'):
            raise serializers.ValidationError('请提供副本ID或条形码')
        return attrs


class ReturnBookSerializer(serializers.Serializer):
    """还书序列化器"""
    remark = serializers.CharField(required=False, allow_blank=True, max_length=500)


class RenewalSerializer(serializers.ModelSerializer):
    """续借记录序列化器"""
    
    class Meta:
        model = Renewal
        fields = ('id', 'renewed_at', 'new_due_at')


class RenewBookSerializer(serializers.Serializer):
    """续借序列化器"""
    days = serializers.IntegerField(default=14, min_value=1, max_value=30)  # 续借天数


class MyBorrowListSerializer(serializers.ModelSerializer):
    """我的借阅列表序列化器"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_cover = serializers.URLField(source='book.cover_url', read_only=True)
    barcode = serializers.CharField(source='book_copy.barcode', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    can_renew = serializers.SerializerMethodField()
    renewal_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrow
        fields = (
            'id', 'book', 'book_title', 'book_author', 'book_cover',
            'book_copy', 'barcode',
            'borrow_at', 'due_at', 'return_at',
            'status', 'status_display', 'is_overdue',
            'can_renew', 'renewal_count'
        )
    
    def get_is_overdue(self, obj):
        if obj.status == BorrowStatus.BORROWING:
            return timezone.now() > obj.due_at
        return obj.status == BorrowStatus.OVERDUE
    
    def get_can_renew(self, obj):
        """是否可以续借（最多续借2次，且未逾期）"""
        if obj.status != BorrowStatus.BORROWING:
            return False
        if timezone.now() > obj.due_at:
            return False
        return obj.renewals.count() < 2
    
    def get_renewal_count(self, obj):
        """已续借次数"""
        return obj.renewals.count()
