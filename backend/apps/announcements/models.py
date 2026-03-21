"""
公告模型模块
"""
from django.db import models
from django.conf import settings


class AnnouncementStatus(models.IntegerChoices):
    """公告状态枚举"""
    DRAFT = 0, '草稿'
    PUBLISHED = 1, '已发布'
    ARCHIVED = 2, '已下架'


class Announcement(models.Model):
    """
    公告模型
    """
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='announcements',
        verbose_name='发布管理员'
    )
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容', help_text='支持 HTML')
    status = models.SmallIntegerField(
        '状态',
        choices=AnnouncementStatus.choices,
        default=AnnouncementStatus.DRAFT,
        db_index=True
    )
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'announcements'
        verbose_name = '公告'
        verbose_name_plural = verbose_name
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
