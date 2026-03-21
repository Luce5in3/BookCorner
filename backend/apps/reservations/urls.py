"""
预约管理路由
/api/reservations/
"""
from django.urls import path
from .views import (
    ReservationListView,
    ReservationDetailView,
    ReservationCreateView,
    ReservationCancelView,
    MyReservationListView,
    ReservationNotifyView,
    ReservationCompleteView,
)

urlpatterns = [
    # 我的预约
    path('my/', MyReservationListView.as_view(), name='my_reservations'),
    
    # 预约管理（管理员）
    path('', ReservationListView.as_view(), name='reservation_list'),
    
    # 创建预约
    path('create/', ReservationCreateView.as_view(), name='reservation_create'),
    
    # 预约详情
    path('<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    
    # 取消预约
    path('<int:pk>/cancel/', ReservationCancelView.as_view(), name='reservation_cancel'),
    
    # 通知到馆（管理员）
    path('<int:pk>/notify/', ReservationNotifyView.as_view(), name='reservation_notify'),
    
    # 完成预约（管理员）
    path('<int:pk>/complete/', ReservationCompleteView.as_view(), name='reservation_complete'),
]
