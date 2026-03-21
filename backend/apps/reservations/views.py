"""
预约模块视图
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from utils.response import success_response, error_response
from utils.permissions import IsAdmin
from apps.books.models import Book
from .models import Reservation, ReservationStatus
from .serializers import (
    ReservationListSerializer,
    ReservationDetailSerializer,
    ReservationCreateSerializer,
    MyReservationSerializer,
)


class ReservationListView(generics.ListAPIView):
    """
    预约列表（管理员）
    GET /api/reservations/
    """
    queryset = Reservation.objects.select_related('user', 'book').all()
    serializer_class = ReservationListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'book', 'status']
    search_fields = ['user__username', 'user__real_name', 'book__title']
    ordering_fields = ['reserved_at', 'expire_at']
    ordering = ['-reserved_at']


class ReservationDetailView(generics.RetrieveAPIView):
    """
    预约详情
    GET /api/reservations/{id}/
    """
    queryset = Reservation.objects.select_related('user', 'book').all()
    serializer_class = ReservationDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查权限
        if instance.user != request.user and request.user.role < 1:
            return error_response(message='无权查看', code=403, status_code=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


class ReservationCreateView(APIView):
    """
    创建预约
    POST /api/reservations/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        book_id = data['book_id']
        book = Book.objects.get(pk=book_id)
        
        # 检查用户是否已预约该书（等待中状态）
        existing = Reservation.objects.filter(
            user=request.user,
            book=book,
            status=ReservationStatus.WAITING
        ).exists()
        if existing:
            return error_response(message='您已预约该图书，请勿重复预约', code=400)
        
        # 检查用户预约数量限制（最多3本）
        active_count = Reservation.objects.filter(
            user=request.user,
            status=ReservationStatus.WAITING
        ).count()
        if active_count >= 3:
            return error_response(message='预约数量已达上限（3本），请取消其他预约后再试', code=400)
        
        # 创建预约
        days = data.get('days', 7)
        expire_at = timezone.now() + timedelta(days=days)
        
        reservation = Reservation.objects.create(
            user=request.user,
            book=book,
            status=ReservationStatus.WAITING,
            expire_at=expire_at
        )
        
        return success_response(
            data=ReservationDetailSerializer(reservation).data,
            message='预约成功',
            code=201
        )


class ReservationCancelView(APIView):
    """
    取消预约
    POST /api/reservations/{id}/cancel/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.select_for_update().get(pk=pk)
        except Reservation.DoesNotExist:
            return error_response(message='预约不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查权限
        if reservation.user != request.user and request.user.role < 1:
            return error_response(message='无权操作', code=403, status_code=status.HTTP_403_FORBIDDEN)
        
        # 检查状态
        if reservation.status != ReservationStatus.WAITING:
            return error_response(message='只有等待中的预约才能取消', code=400)
        
        reservation.status = ReservationStatus.CANCELED
        reservation.cancel_at = timezone.now()
        reservation.save()
        
        return success_response(message='预约已取消')


class MyReservationListView(generics.ListAPIView):
    """
    我的预约列表
    GET /api/reservations/my/
    """
    serializer_class = MyReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-reserved_at']
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).select_related('book')


class ReservationNotifyView(APIView):
    """
    通知用户图书到馆（管理员）
    POST /api/reservations/{id}/notify/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return error_response(message='预约不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if reservation.status != ReservationStatus.WAITING:
            return error_response(message='只有等待中的预约才能通知', code=400)
        
        reservation.status = ReservationStatus.ARRIVED
        reservation.notify_at = timezone.now()
        # 延长到期时间3天，给用户取书时间
        reservation.expire_at = timezone.now() + timedelta(days=3)
        reservation.save()
        
        return success_response(
            data=ReservationDetailSerializer(reservation).data,
            message='已通知用户'
        )


class ReservationCompleteView(APIView):
    """
    完成预约（用户取书后）
    POST /api/reservations/{id}/complete/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return error_response(message='预约不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if reservation.status not in [ReservationStatus.WAITING, ReservationStatus.ARRIVED]:
            return error_response(message='该预约状态无法完成', code=400)
        
        reservation.status = ReservationStatus.COMPLETED
        reservation.save()
        
        return success_response(message='预约已完成')
