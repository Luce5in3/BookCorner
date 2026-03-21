"""
借阅模块 Admin 配置
"""
from django.contrib import admin
from .models import Borrow, Renewal


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'book_copy', 'borrow_at', 'due_at', 'return_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'book__title', 'book_copy__barcode')
    ordering = ('-borrow_at',)
    raw_id_fields = ('user', 'book', 'book_copy', 'operator')


@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ('borrow', 'renewed_at', 'new_due_at')
    ordering = ('-renewed_at',)
    raw_id_fields = ('borrow',)
