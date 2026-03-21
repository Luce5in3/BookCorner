"""
公告模块 Admin 配置
"""
from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin', 'status', 'published_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    raw_id_fields = ('admin',)
