"""
借阅模块视图
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from decimal import Decimal

from utils.response import success_response, error_response
from utils.permissions import IsAdmin
from apps.users.permissions import IsOwnerOrAdmin
from apps.books.models import Book, BookCopy, BookCopyStatus
from apps.fines.models import Fine, FineStatus
from .models import Borrow, Renewal, BorrowStatus
from .serializers import (
    BorrowListSerializer,
    BorrowDetailSerializer,
    BorrowCreateSerializer,
    ReturnBookSerializer,
    RenewBookSerializer,
    MyBorrowListSerializer,
)

User = get_user_model()

# 逾期罚款单价（元/天）
OVERDUE_FINE_PER_DAY = Decimal('0.50')


class BorrowListView(generics.ListAPIView):
    """
    借阅列表（管理员）
    GET /api/borrows/
    """
    queryset = Borrow.objects.select_related('user', 'book', 'book_copy').all()
    serializer_class = BorrowListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'book', 'status']
    search_fields = ['user__username', 'user__real_name', 'book__title', 'book_copy__barcode']
    ordering_fields = ['borrow_at', 'due_at', 'return_at']
    ordering = ['-borrow_at']


class BorrowDetailView(generics.RetrieveAPIView):
    """
    借阅详情
    GET /api/borrows/{id}/
    """
    queryset = Borrow.objects.select_related('user', 'book', 'book_copy', 'operator').prefetch_related('renewals').all()
    serializer_class = BorrowDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)


class BorrowCreateView(APIView):
    """
    借书
    POST /api/borrows/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = BorrowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # 获取副本
        book_copy = None
        if data.get('book_copy_id'):
            try:
                book_copy = BookCopy.objects.select_for_update().get(pk=data['book_copy_id'])
            except BookCopy.DoesNotExist:
                return error_response(message='副本不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        elif data.get('barcode'):
            try:
                book_copy = BookCopy.objects.select_for_update().get(barcode=data['barcode'])
            except BookCopy.DoesNotExist:
                return error_response(message='副本不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查副本状态
        if book_copy.status != BookCopyStatus.IN_LIBRARY:
            status_msg = book_copy.get_status_display()
            return error_response(message=f'该副本当前状态为"{status_msg}"，无法借出', code=400)
        
        # 确定借阅用户
        if data.get('user_id') and request.user.role >= 1:
            # 管理员帮用户借书
            try:
                borrower = User.objects.get(pk=data['user_id'])
            except User.DoesNotExist:
                return error_response(message='用户不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        else:
            borrower = request.user
        
        # 检查用户状态
        if borrower.status == 0:
            return error_response(message='该用户已被禁用，无法借书', code=400)
        
        # 检查用户是否有未缴罚款
        if Fine.objects.filter(user=borrower, status=FineStatus.PENDING).exists():
            return error_response(message='有未缴罚款，请先缴清后再借书', code=400)
        
        # 检查用户当前借阅数量（限制最多借5本）
        current_borrows = Borrow.objects.filter(
            user=borrower,
            status__in=[BorrowStatus.BORROWING, BorrowStatus.OVERDUE]
        ).count()
        if current_borrows >= 5:
            return error_response(message='已达到最大借阅数量（5本），请先归还后再借', code=400)
        
        # 获取图书并检查
        book = book_copy.book
        if book.status == 0:
            return error_response(message='该图书已下架，无法借出', code=400)
        
        # 创建借阅记录
        days = data.get('days', 30)
        due_at = timezone.now() + timedelta(days=days)
        
        borrow = Borrow.objects.create(
            user=borrower,
            book_copy=book_copy,
            book=book,
            due_at=due_at,
            status=BorrowStatus.BORROWING,
            operator=request.user if request.user != borrower else None,
            remark=data.get('remark', '')
        )
        
        # 更新副本状态
        book_copy.status = BookCopyStatus.BORROWED
        book_copy.save(update_fields=['status', 'updated_at'])
        
        # 更新图书可借数量
        book.available_copies = max(0, book.available_copies - 1)
        book.save(update_fields=['available_copies', 'updated_at'])
        
        return success_response(
            data=BorrowDetailSerializer(borrow).data,
            message='借书成功',
            code=201
        )


class ReturnBookView(APIView):
    """
    还书
    POST /api/borrows/{id}/return/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @transaction.atomic
    def post(self, request, pk):
        try:
            borrow = Borrow.objects.select_for_update().select_related('book_copy', 'book', 'user').get(pk=pk)
        except Borrow.DoesNotExist:
            return error_response(message='借阅记录不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查状态
        if borrow.status not in [BorrowStatus.BORROWING, BorrowStatus.OVERDUE]:
            return error_response(message='该借阅记录不在借阅中状态', code=400)
        
        serializer = ReturnBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        now = timezone.now()
        
        # 检查是否逾期，生成罚款
        fine_created = False
        if now > borrow.due_at:
            overdue_days = (now - borrow.due_at).days + 1
            fine_amount = OVERDUE_FINE_PER_DAY * overdue_days
            
            Fine.objects.create(
                borrow=borrow,
                user=borrow.user,
                amount=fine_amount,
                reason=f'逾期还书 {overdue_days} 天',
                status=FineStatus.PENDING
            )
            fine_created = True
        
        # 更新借阅记录
        borrow.return_at = now
        borrow.status = BorrowStatus.RETURNED
        borrow.operator = request.user
        if serializer.validated_data.get('remark'):
            borrow.remark = (borrow.remark or '') + '\n还书备注：' + serializer.validated_data['remark']
        borrow.save()
        
        # 更新副本状态
        book_copy = borrow.book_copy
        book_copy.status = BookCopyStatus.IN_LIBRARY
        book_copy.save(update_fields=['status', 'updated_at'])
        
        # 更新图书可借数量
        book = borrow.book
        book.available_copies += 1
        book.save(update_fields=['available_copies', 'updated_at'])
        
        message = '还书成功'
        if fine_created:
            message += f'，因逾期产生罚款，请提醒读者缴费'
        
        return success_response(
            data=BorrowDetailSerializer(borrow).data,
            message=message
        )


class RenewBookView(APIView):
    """
    续借
    POST /api/borrows/{id}/renew/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        try:
            borrow = Borrow.objects.select_for_update().select_related('user').prefetch_related('renewals').get(pk=pk)
        except Borrow.DoesNotExist:
            return error_response(message='借阅记录不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查权限：只能续借自己的或管理员可续借任何人的
        if borrow.user != request.user and request.user.role < 1:
            return error_response(message='无权操作', code=403, status_code=status.HTTP_403_FORBIDDEN)
        
        # 检查状态
        if borrow.status != BorrowStatus.BORROWING:
            return error_response(message='只有借阅中的记录才能续借', code=400)
        
        # 检查是否已逾期
        if timezone.now() > borrow.due_at:
            return error_response(message='已逾期，无法续借，请先还书', code=400)
        
        # 检查续借次数
        renewal_count = borrow.renewals.count()
        if renewal_count >= 2:
            return error_response(message='已达到最大续借次数（2次）', code=400)
        
        serializer = RenewBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        days = serializer.validated_data.get('days', 14)
        new_due_at = borrow.due_at + timedelta(days=days)
        
        # 创建续借记录
        Renewal.objects.create(
            borrow=borrow,
            new_due_at=new_due_at
        )
        
        # 更新借阅记录的应还时间
        borrow.due_at = new_due_at
        borrow.save(update_fields=['due_at'])
        
        return success_response(
            data=BorrowDetailSerializer(borrow).data,
            message=f'续借成功，新的应还日期为 {new_due_at.strftime("%Y-%m-%d")}'
        )


class MyBorrowListView(generics.ListAPIView):
    """
    我的借阅记录
    GET /api/borrows/my/
    """
    serializer_class = MyBorrowListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['borrow_at', 'due_at']
    ordering = ['-borrow_at']
    
    def get_queryset(self):
        return Borrow.objects.filter(user=self.request.user).select_related('book', 'book_copy').prefetch_related('renewals')


class MyCurrentBorrowsView(APIView):
    """
    我当前借阅中的图书
    GET /api/borrows/my/current/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        borrows = Borrow.objects.filter(
            user=request.user,
            status__in=[BorrowStatus.BORROWING, BorrowStatus.OVERDUE]
        ).select_related('book', 'book_copy').prefetch_related('renewals').order_by('due_at')
        
        serializer = MyBorrowListSerializer(borrows, many=True)
        return success_response(data=serializer.data)


class OverdueBorrowsView(generics.ListAPIView):
    """
    逾期借阅列表（管理员）
    GET /api/borrows/overdue/
    """
    serializer_class = BorrowListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'user__real_name', 'book__title']
    ordering = ['due_at']
    
    def get_queryset(self):
        # 获取所有逾期的借阅（包括状态为逾期的，以及借阅中但已过期的）
        now = timezone.now()
        return Borrow.objects.filter(
            status__in=[BorrowStatus.BORROWING, BorrowStatus.OVERDUE],
            due_at__lt=now
        ).select_related('user', 'book', 'book_copy')


class BorrowByBarcodeView(APIView):
    """
    通过条形码查询当前借阅
    GET /api/borrows/barcode/{barcode}/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, barcode):
        try:
            book_copy = BookCopy.objects.get(barcode=barcode)
        except BookCopy.DoesNotExist:
            return error_response(message='副本不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 查找当前借阅记录
        borrow = Borrow.objects.filter(
            book_copy=book_copy,
            status__in=[BorrowStatus.BORROWING, BorrowStatus.OVERDUE]
        ).select_related('user', 'book', 'book_copy', 'operator').first()
        
        if not borrow:
            return success_response(
                data={
                    'book_copy': {
                        'id': book_copy.id,
                        'barcode': book_copy.barcode,
                        'status': book_copy.status,
                        'status_display': book_copy.get_status_display(),
                        'book_title': book_copy.book.title,
                    },
                    'borrow': None
                },
                message='该副本当前无借阅记录'
            )
        
        return success_response(data=BorrowDetailSerializer(borrow).data)
