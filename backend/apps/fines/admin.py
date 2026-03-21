"""
罚款模块 Admin 配置
"""
from django.contrib import admin
from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('user', 'borrow', 'amount', 'reason', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'borrow')
