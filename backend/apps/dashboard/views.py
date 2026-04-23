from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from utils.response import success_response
from apps.books.models import Book
from apps.users.models import User, UserRole
from apps.borrows.models import Borrow, BorrowStatus
from apps.reservations.models import Reservation, ReservationStatus
from apps.announcements.models import Announcement, AnnouncementStatus


class DashboardStatsView(APIView):
    """
    仪表盘统计数据视图
    GET /api/dashboard/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取仪表盘统计数据
        """
        stats = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.filter(role=UserRole.READER).count(),
            'active_borrows': Borrow.objects.filter(status=BorrowStatus.BORROWING).count(),
            'pending_reservations': Reservation.objects.filter(status=ReservationStatus.WAITING).count(),
        }
        return success_response(stats)


class DashboardRecentView(APIView):
    """
    仪表盘最近数据视图
    GET /api/dashboard/recent/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取最近借阅记录和公告
        """
        # 最近10条借阅记录
        recent_borrows = Borrow.objects.select_related('user', 'book').order_by('-borrow_at')[:10]
        borrows_data = [
            {
                'id': b.id,
                'user_name': b.user.real_name,
                'book_title': b.book.title,
                'borrow_date': b.borrow_at.strftime('%Y-%m-%d'),
                'status': b.status,
                'status_display': b.get_status_display(),
            }
            for b in recent_borrows
        ]
        
        # 最近5条已发布公告
        recent_announcements = Announcement.objects.filter(
            status=AnnouncementStatus.PUBLISHED
        ).order_by('-published_at')[:5]
        announcements_data = [
            {
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'created_at': a.published_at.strftime('%Y-%m-%d') if a.published_at else '',
            }
            for a in recent_announcements
        ]
        
        data = {
            'recent_borrows': borrows_data,
            'recent_announcements': announcements_data,
        }
        return success_response(data)
