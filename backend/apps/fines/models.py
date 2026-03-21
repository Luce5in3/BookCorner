"""
罚款模型模块
"""
from django.db import models
from django.conf import settings


class FineStatus(models.IntegerChoices):
    """罚款状态枚举"""
    PENDING = 0, '待缴'
    PAID = 1, '已缴'
    EXEMPTED = 2, '已免除'


class Fine(models.Model):
    """
    罚款记录模型
    """
    borrow = models.ForeignKey(
        'borrows.Borrow',
        on_delete=models.PROTECT,
        related_name='fines',
        verbose_name='关联借阅'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='fines',
        verbose_name='欠款用户'
    )
    amount = models.DecimalField(
        '罚款金额',
        max_digits=8,
        decimal_places=2
    )
    reason = models.CharField(
        '原因',
        max_length=100,
        default='逾期还书'
    )
    status = models.SmallIntegerField(
        '状态',
        choices=FineStatus.choices,
        default=FineStatus.PENDING,
        db_index=True
    )
    created_at = models.DateTimeField('生成时间', auto_now_add=True)
    paid_at = models.DateTimeField('缴清时间', null=True, blank=True)
    
    class Meta:
        db_table = 'fines'
        verbose_name = '罚款记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} 罚款 {self.amount}元'
