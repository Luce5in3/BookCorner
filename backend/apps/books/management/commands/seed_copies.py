"""
批量添加图书副本数据
python manage.py seed_copies
"""
import random
from django.core.management.base import BaseCommand
from apps.books.models import Book, BookCopy, BookCopyStatus, BookCopyCondition


class Command(BaseCommand):
    help = '为现有图书添加副本数据'

    def handle(self, *args, **options):
        books = Book.objects.all()
        
        if not books.exists():
            self.stdout.write(self.style.WARNING('没有图书数据，请先运行 seed_books'))
            return
        
        created_count = 0
        locations = ['A区', 'B区', 'C区', 'D区']
        
        for book in books:
            # 每本书生成 2-5 个副本
            copy_count = random.randint(2, 5)
            
            for i in range(copy_count):
                # 生成唯一条形码
                barcode = f'BC{book.id:04d}{i+1:02d}'
                
                # 检查是否已存在
                if BookCopy.objects.filter(barcode=barcode).exists():
                    continue
                
                # 随机状态，大部分在馆
                status_choices = [
                    (BookCopyStatus.IN_LIBRARY, 0.7),  # 70% 在馆
                    (BookCopyStatus.BORROWED, 0.2),    # 20% 借出
                    (BookCopyStatus.RESERVED, 0.05),   # 5% 预约锁定
                    (BookCopyStatus.LOST, 0.05),       # 5% 丢失
                ]
                rand = random.random()
                cumulative = 0
                status = BookCopyStatus.IN_LIBRARY
                for s, prob in status_choices:
                    cumulative += prob
                    if rand < cumulative:
                        status = s
                        break
                
                # 随机品相
                condition = random.choice([
                    BookCopyCondition.NEW,
                    BookCopyCondition.GOOD,
                    BookCopyCondition.GOOD,
                    BookCopyCondition.FAIR,
                ])
                
                # 随机位置
                location = f'{random.choice(locations)}-{random.randint(1,10):02d}-{random.randint(1,5)}'
                
                BookCopy.objects.create(
                    book=book,
                    barcode=barcode,
                    status=status,
                    condition=condition,
                    location=location
                )
                created_count += 1
        
        # 更新图书的副本统计
        for book in books:
            total = book.copies.count()
            available = book.copies.filter(status=BookCopyStatus.IN_LIBRARY).count()
            book.total_copies = total
            book.available_copies = available
            book.save(update_fields=['total_copies', 'available_copies'])
        
        self.stdout.write(self.style.SUCCESS(f'成功添加 {created_count} 个副本'))
