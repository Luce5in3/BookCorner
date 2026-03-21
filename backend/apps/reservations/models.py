"""
预约模型模块
"""
from django.db import models
from django.conf import settings


class ReservationStatus(models.IntegerChoices):
    """预约状态枚举"""
    CANCELED = 0, '已取消'
    WAITING = 1, '等待中'
    ARRIVED = 2, '已到馆'
    COMPLETED = 3, '已完成'
    EXPIRED = 4, '已过期'


class Reservation(models.Model):
    """
    预约记录模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reservations',
        verbose_name='预约用户'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.PROTECT,
        related_name='reservations',
        verbose_name='预约图书'
    )
    status = models.SmallIntegerField(
        '状态',
        choices=ReservationStatus.choices,
        default=ReservationStatus.WAITING,
        db_index=True
    )
    reserved_at = models.DateTimeField('预约时间', auto_now_add=True)
    expire_at = models.DateTimeField('预约到期时间')
    notify_at = models.DateTimeField('到馆通知时间', null=True, blank=True)
    cancel_at = models.DateTimeField('取消时间', null=True, blank=True)
    
    class Meta:
        db_table = 'reservations'
        verbose_name = '预约记录'
        verbose_name_plural = verbose_name
        ordering = ['-reserved_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} 预约 {self.book.title}'
