"""
仪表盘统计视图
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from utils.response import success_response
from utils.permissions import IsAdmin
from apps.users.models import User
from apps.books.models import Book
from apps.borrows.models import Borrow, BorrowStatus
from apps.reservations.models import Reservation, ReservationStatus
from apps.announcements.models import Announcement, AnnouncementStatus


class DashboardStatsView(APIView):
    """
    仪表盘统计数据
    GET /api/dashboard/stats/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        stats = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.filter(role=0).count(),
            'active_borrows': Borrow.objects.filter(status=BorrowStatus.BORROWING).count(),
            'pending_reservations': Reservation.objects.filter(status=ReservationStatus.WAITING).count(),
        }
        return success_response(data=stats)


class DashboardRecentView(APIView):
    """
    最近数据
    GET /api/dashboard/recent/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # 最近借阅记录
        recent_borrows = Borrow.objects.select_related(
            'user', 'book_copy', 'book_copy__book', 'book'
        ).order_by('-borrow_at')[:10]
        
        borrows_data = [{
            'id': b.id,
            'user_name': b.user.real_name or b.user.username,
            'book_title': b.book.title if b.book else '-',
            'borrow_date': b.borrow_at.strftime('%Y-%m-%d') if b.borrow_at else '-',
            'status': b.status,
            'status_display': b.get_status_display(),
        } for b in recent_borrows]
        
        # 最新公告
        recent_announcements = Announcement.objects.filter(
            status=AnnouncementStatus.PUBLISHED
        ).order_by('-published_at', '-created_at')[:5]
        
        announcements_data = [{
            'id': a.id,
            'title': a.title,
            'created_at': a.created_at.strftime('%Y-%m-%d'),
        } for a in recent_announcements]
        
        return success_response(data={
            'recent_borrows': borrows_data,
            'recent_announcements': announcements_data,
        })
