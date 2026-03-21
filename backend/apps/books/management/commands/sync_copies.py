"""
同步图书副本统计
更新 books 表的 total_copies 和 available_copies
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from apps.books.models import Book, BookCopy, BookCopyStatus


class Command(BaseCommand):
    help = '同步图书副本统计（total_copies 和 available_copies）'

    def handle(self, *args, **options):
        # 获取所有图书的副本统计
        books = Book.objects.all()
        updated_count = 0
        
        for book in books:
            # 统计总副本数（排除注销的）
            total = BookCopy.objects.filter(
                book=book
            ).exclude(status=BookCopyStatus.CANCELED).count()
            
            # 统计可借副本数（只统计在馆的）
            available = BookCopy.objects.filter(
                book=book,
                status=BookCopyStatus.IN_LIBRARY
            ).count()
            
            # 更新图书记录
            if book.total_copies != total or book.available_copies != available:
                book.total_copies = total
                book.available_copies = available
                book.save(update_fields=['total_copies', 'available_copies', 'updated_at'])
                updated_count += 1
                self.stdout.write(f'  {book.title}: 总数={total}, 可借={available}')
        
        self.stdout.write(self.style.SUCCESS(f'同步完成，更新了 {updated_count} 本图书的库存信息'))
