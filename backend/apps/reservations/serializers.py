"""
预约模块序列化器
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Reservation, ReservationStatus
from apps.books.models import Book


class ReservationListSerializer(serializers.ModelSerializer):
    """预约列表序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = (
            'id', 'user', 'username', 'real_name',
            'book', 'book_title', 'book_author',
            'status', 'status_display', 'is_expired',
            'reserved_at', 'expire_at', 'notify_at', 'cancel_at'
        )
    
    def get_is_expired(self, obj):
        if obj.status == ReservationStatus.WAITING:
            return timezone.now() > obj.expire_at
        return obj.status == ReservationStatus.EXPIRED


class ReservationDetailSerializer(serializers.ModelSerializer):
    """预约详情序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_cover = serializers.URLField(source='book.cover_url', read_only=True)
    book_available = serializers.IntegerField(source='book.available_copies', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Reservation
        fields = (
            'id', 'user', 'username', 'real_name',
            'book', 'book_title', 'book_author', 'book_cover', 'book_available',
            'status', 'status_display',
            'reserved_at', 'expire_at', 'notify_at', 'cancel_at'
        )


class ReservationCreateSerializer(serializers.Serializer):
    """创建预约序列化器"""
    book_id = serializers.IntegerField()
    days = serializers.IntegerField(default=7, min_value=1, max_value=14)  # 预约有效天数
    
    def validate_book_id(self, value):
        try:
            book = Book.objects.get(pk=value)
            if book.status == 0:
                raise serializers.ValidationError('该图书已下架')
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError('图书不存在')


class MyReservationSerializer(serializers.ModelSerializer):
    """我的预约序列化器"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_cover = serializers.URLField(source='book.cover_url', read_only=True)
    book_available = serializers.IntegerField(source='book.available_copies', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = (
            'id', 'book', 'book_title', 'book_author', 'book_cover', 'book_available',
            'status', 'status_display', 'can_cancel',
            'reserved_at', 'expire_at', 'notify_at'
        )
    
    def get_can_cancel(self, obj):
        return obj.status == ReservationStatus.WAITING
