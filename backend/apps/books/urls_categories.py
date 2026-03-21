"""
分类管理路由
/api/categories/
"""
from django.urls import path
from .views import CategoryListView, CategoryDetailView, CategoryFlatListView

urlpatterns = [
    # 分类列表（树形）
    path('', CategoryListView.as_view(), name='category_list'),
    # 分类平铺列表（下拉选择用）
    path('flat/', CategoryFlatListView.as_view(), name='category_flat'),
    # 分类详情
    path('<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
]
