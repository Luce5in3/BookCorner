"""
副本管理路由
/api/copies/
"""
from django.urls import path
from .views import (
    BookCopyListView,
    BookCopyDetailView,
    BookCopyBatchCreateView,
    BookCopyByBarcodeView,
)

urlpatterns = [
    # 副本列表
    path('', BookCopyListView.as_view(), name='copy_list'),
    # 批量入库
    path('batch/', BookCopyBatchCreateView.as_view(), name='copy_batch_create'),
    # 通过条形码查询
    path('barcode/<str:barcode>/', BookCopyByBarcodeView.as_view(), name='copy_by_barcode'),
    # 副本详情
    path('<int:pk>/', BookCopyDetailView.as_view(), name='copy_detail'),
]
