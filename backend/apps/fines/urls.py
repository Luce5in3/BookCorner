"""
罚款管理路由
/api/fines/
"""
from django.urls import path
from .views import (
    FineListView,
    FineDetailView,
    FinePayView,
    FineExemptView,
    MyFineListView,
    MyFineStatsView,
    PendingFinesView,
    UserFinesView,
)

urlpatterns = [
    # 我的罚款
    path('my/', MyFineListView.as_view(), name='my_fines'),
    path('my/stats/', MyFineStatsView.as_view(), name='my_fine_stats'),
    
    # 罚款管理（管理员）
    path('', FineListView.as_view(), name='fine_list'),
    path('pending/', PendingFinesView.as_view(), name='pending_fines'),
    path('user/<int:user_id>/', UserFinesView.as_view(), name='user_fines'),
    
    # 罚款详情
    path('<int:pk>/', FineDetailView.as_view(), name='fine_detail'),
    
    # 标记已缴
    path('<int:pk>/pay/', FinePayView.as_view(), name='fine_pay'),
    
    # 免除罚款
    path('<int:pk>/exempt/', FineExemptView.as_view(), name='fine_exempt'),
]
