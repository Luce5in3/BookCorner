"""
罚款模块视图
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum

from utils.response import success_response, error_response
from utils.permissions import IsAdmin
from .models import Fine, FineStatus
from .serializers import (
    FineListSerializer,
    FineDetailSerializer,
    FineUpdateSerializer,
    MyFineSerializer,
)


class FineListView(generics.ListAPIView):
    """
    罚款列表（管理员）
    GET /api/fines/
    """
    queryset = Fine.objects.select_related('user', 'borrow__book').all()
    serializer_class = FineListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'status']
    search_fields = ['user__username', 'user__real_name', 'borrow__book__title']
    ordering_fields = ['created_at', 'amount', 'paid_at']
    ordering = ['-created_at']


class FineDetailView(generics.RetrieveAPIView):
    """
    罚款详情
    GET /api/fines/{id}/
    """
    queryset = Fine.objects.select_related('user', 'borrow__book', 'borrow__book_copy').all()
    serializer_class = FineDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查权限
        if instance.user != request.user and request.user.role < 1:
            return error_response(message='无权查看', code=403, status_code=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


class FinePayView(APIView):
    """
    标记罚款已缴（管理员）
    POST /api/fines/{id}/pay/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            fine = Fine.objects.get(pk=pk)
        except Fine.DoesNotExist:
            return error_response(message='罚款记录不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if fine.status != FineStatus.PENDING:
            return error_response(message='该罚款记录不是待缴状态', code=400)
        
        fine.status = FineStatus.PAID
        fine.paid_at = timezone.now()
        fine.save()
        
        return success_response(
            data=FineDetailSerializer(fine).data,
            message='已标记为已缴'
        )


class FineExemptView(APIView):
    """
    免除罚款（管理员）
    POST /api/fines/{id}/exempt/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            fine = Fine.objects.get(pk=pk)
        except Fine.DoesNotExist:
            return error_response(message='罚款记录不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if fine.status != FineStatus.PENDING:
            return error_response(message='该罚款记录不是待缴状态', code=400)
        
        fine.status = FineStatus.EXEMPTED
        fine.paid_at = timezone.now()
        fine.save()
        
        return success_response(
            data=FineDetailSerializer(fine).data,
            message='已免除罚款'
        )


class MyFineListView(generics.ListAPIView):
    """
    我的罚款列表
    GET /api/fines/my/
    """
    serializer_class = MyFineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Fine.objects.filter(user=self.request.user).select_related('borrow__book')


class MyFineStatsView(APIView):
    """
    我的罚款统计
    GET /api/fines/my/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        fines = Fine.objects.filter(user=request.user)
        
        # 待缴罚款
        pending = fines.filter(status=FineStatus.PENDING)
        pending_count = pending.count()
        pending_amount = pending.aggregate(total=Sum('amount'))['total'] or 0
        
        # 已缴罚款
        paid = fines.filter(status=FineStatus.PAID)
        paid_count = paid.count()
        paid_amount = paid.aggregate(total=Sum('amount'))['total'] or 0
        
        return success_response(data={
            'pending_count': pending_count,
            'pending_amount': float(pending_amount),
            'paid_count': paid_count,
            'paid_amount': float(paid_amount),
        })


class PendingFinesView(generics.ListAPIView):
    """
    待缴罚款列表（管理员）
    GET /api/fines/pending/
    """
    serializer_class = FineListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'user__real_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Fine.objects.filter(status=FineStatus.PENDING).select_related('user', 'borrow__book')


class UserFinesView(generics.ListAPIView):
    """
    查询指定用户的罚款（管理员）
    GET /api/fines/user/{user_id}/
    """
    serializer_class = FineListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Fine.objects.filter(user_id=user_id).select_related('user', 'borrow__book')
