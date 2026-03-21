"""
借阅模型模块
包含：借阅记录、续借记录
"""
from django.db import models
from django.conf import settings


class BorrowStatus(models.IntegerChoices):
    """借阅状态枚举"""
    RETURNED = 0, '已还'
    BORROWING = 1, '借阅中'
    OVERDUE = 2, '逾期'
    LOST = 3, '丢失'


class Borrow(models.Model):
    """
    借阅记录模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='borrows',
        verbose_name='借阅用户'
    )
    book_copy = models.ForeignKey(
        'books.BookCopy',
        on_delete=models.PROTECT,
        related_name='borrows',
        verbose_name='借出副本'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.PROTECT,
        related_name='borrows',
        verbose_name='图书',
        help_text='冗余字段，方便统计查询'
    )
    borrow_at = models.DateTimeField('借出时间', auto_now_add=True)
    due_at = models.DateTimeField('应还时间', db_index=True)
    return_at = models.DateTimeField('实际归还时间', null=True, blank=True)
    status = models.SmallIntegerField(
        '状态',
        choices=BorrowStatus.choices,
        default=BorrowStatus.BORROWING,
        db_index=True
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operated_borrows',
        verbose_name='经手管理员'
    )
    remark = models.TextField('备注', null=True, blank=True)
    
    class Meta:
        db_table = 'borrows'
        verbose_name = '借阅记录'
        verbose_name_plural = verbose_name
        ordering = ['-borrow_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book_copy', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} 借阅 {self.book.title}'


class Renewal(models.Model):
    """
    续借记录模型
    """
    borrow = models.ForeignKey(
        Borrow,
        on_delete=models.CASCADE,
        related_name='renewals',
        verbose_name='借阅记录'
    )
    renewed_at = models.DateTimeField('续借时间', auto_now_add=True)
    new_due_at = models.DateTimeField('续借后应还时间')
    
    class Meta:
        db_table = 'renewals'
        verbose_name = '续借记录'
        verbose_name_plural = verbose_name
        ordering = ['-renewed_at']
    
    def __str__(self):
        return f'{self.borrow} 续借至 {self.new_due_at}'
