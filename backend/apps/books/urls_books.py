"""
图书管理路由
/api/books/
"""
from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    BookToggleStatusView,
    BookGenerateDescriptionView,
    BookCopiesByBookView,
    BookCoverUploadView,
    BookAISearchView,
)

urlpatterns = [
    # 上传封面（必须在 <int:pk>/ 之前）
    path('upload-cover/', BookCoverUploadView.as_view(), name='book_upload_cover'),
    # AI 智能检索
    path('ai-search/', BookAISearchView.as_view(), name='book_ai_search'),
    # 图书列表
    path('', BookListView.as_view(), name='book_list'),
    # 图书详情
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    # AI 生成图书简介
    path('<int:pk>/generate-description/', BookGenerateDescriptionView.as_view(), name='book_generate_description'),
    # 切换上下架状态
    path('<int:pk>/toggle-status/', BookToggleStatusView.as_view(), name='book_toggle_status'),
    # 获取图书的所有副本
    path('<int:book_id>/copies/', BookCopiesByBookView.as_view(), name='book_copies'),
]
