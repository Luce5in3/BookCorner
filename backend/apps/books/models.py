"""
图书模型模块
包含：分类、图书、图书副本
"""
from django.db import models
from treebeard.mp_tree import MP_Node


class Category(MP_Node):
    """
    图书分类模型（树形结构）
    使用 django-treebeard 的 Materialized Path 实现
    """
    name = models.CharField('分类名称', max_length=50)
    code = models.CharField(
        '分类编号',
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text='如 TP312'
    )
    sort_order = models.PositiveIntegerField('排序权重', default=0, help_text='越小越靠前')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    node_order_by = ['sort_order', 'name']
    
    class Meta:
        db_table = 'categories'
        verbose_name = '图书分类'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


class BookStatus(models.IntegerChoices):
    """图书状态枚举"""
    OFF_SHELF = 0, '下架'
    ON_SHELF = 1, '上架'


class Book(models.Model):
    """
    图书信息模型（逻辑书）
    """
    isbn = models.CharField(
        'ISBN',
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    title = models.CharField('书名', max_length=255, db_index=True)
    author = models.CharField('作者', max_length=255)
    publisher = models.CharField(
        '出版社',
        max_length=100,
        null=True,
        blank=True
    )
    cover_url = models.URLField(
        '封面图片',
        max_length=255,
        null=True,
        blank=True
    )
    description = models.TextField('简介', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='分类'
    )
    total_copies = models.PositiveIntegerField('馆藏总册数', default=0)
    available_copies = models.PositiveIntegerField(
        '可借册数',
        default=0,
        help_text='冗余字段，事务维护'
    )
    price = models.DecimalField(
        '定价',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    publish_date = models.DateField('出版日期', null=True, blank=True)
    language = models.CharField('语言', max_length=20, default='zh')
    status = models.SmallIntegerField(
        '状态',
        choices=BookStatus.choices,
        default=BookStatus.ON_SHELF,
        db_index=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = '图书'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.author}'


class BookCopyCondition(models.IntegerChoices):
    """图书副本品相枚举"""
    NEW = 1, '全新'
    GOOD = 2, '良好'
    FAIR = 3, '一般'
    DAMAGED = 4, '破损'


class BookCopyStatus(models.IntegerChoices):
    """图书副本状态枚举"""
    CANCELED = 0, '注销'
    IN_LIBRARY = 1, '在馆'
    BORROWED = 2, '借出'
    RESERVED = 3, '预约锁定'
    LOST = 4, '丢失'


class BookCopy(models.Model):
    """
    图书副本模型（实体书）
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='copies',
        verbose_name='所属图书'
    )
    barcode = models.CharField(
        '条形码',
        max_length=50,
        unique=True
    )
    condition = models.SmallIntegerField(
        '品相',
        choices=BookCopyCondition.choices,
        default=BookCopyCondition.NEW
    )
    status = models.SmallIntegerField(
        '状态',
        choices=BookCopyStatus.choices,
        default=BookCopyStatus.IN_LIBRARY,
        db_index=True
    )
    location = models.CharField(
        '书架位置',
        max_length=50,
        null=True,
        blank=True,
        help_text='如 A区-03-2'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'book_copies'
        verbose_name = '图书副本'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.book.title} [{self.barcode}]'
