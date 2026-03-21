"""
预约模块 Admin 配置
"""
from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'reserved_at', 'expire_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'book__title')
    ordering = ('-reserved_at',)
    raw_id_fields = ('user', 'book')
