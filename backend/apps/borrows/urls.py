"""
借阅管理路由
/api/borrows/
"""
from django.urls import path
from .views import (
    BorrowListView,
    BorrowDetailView,
    BorrowCreateView,
    ReturnBookView,
    RenewBookView,
    MyBorrowListView,
    MyCurrentBorrowsView,
    OverdueBorrowsView,
    BorrowByBarcodeView,
)

urlpatterns = [
    # 我的借阅
    path('my/', MyBorrowListView.as_view(), name='my_borrows'),
    path('my/current/', MyCurrentBorrowsView.as_view(), name='my_current_borrows'),
    
    # 借阅管理（管理员）
    path('', BorrowListView.as_view(), name='borrow_list'),
    path('overdue/', OverdueBorrowsView.as_view(), name='overdue_borrows'),
    path('barcode/<str:barcode>/', BorrowByBarcodeView.as_view(), name='borrow_by_barcode'),
    
    # 借书
    path('create/', BorrowCreateView.as_view(), name='borrow_create'),
    
    # 借阅详情
    path('<int:pk>/', BorrowDetailView.as_view(), name='borrow_detail'),
    
    # 还书
    path('<int:pk>/return/', ReturnBookView.as_view(), name='return_book'),
    
    # 续借
    path('<int:pk>/renew/', RenewBookView.as_view(), name='renew_book'),
]
