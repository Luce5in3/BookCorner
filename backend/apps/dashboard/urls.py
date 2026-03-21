"""
仪表盘路由
/api/dashboard/
"""
from django.urls import path
from .views import DashboardStatsView, DashboardRecentView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('recent/', DashboardRecentView.as_view(), name='dashboard_recent'),
]
