"""
仪表盘统计路由
/api/dashboard/
"""
from django.urls import path
from .views import DashboardStatsView, DashboardRecentView

urlpatterns = [
    # 仪表盘统计数据
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    # 最近数据
    path('recent/', DashboardRecentView.as_view(), name='dashboard_recent'),
]
