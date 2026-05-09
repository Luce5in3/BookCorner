"""
更新 books 表的 cover_url 字段
规则: https://luce5in3-buket.oss-cn-beijing.aliyuncs.com/library/{URL编码的title}.webp
"""
import os
import sys
import django
from urllib.parse import quote

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.books.models import Book

BASE_URL = 'https://luce5in3-buket.oss-cn-beijing.aliyuncs.com/library/'

books = Book.objects.all()
count = 0

for book in books:
    encoded_title = quote(book.title)
    cover_url = f'{BASE_URL}{encoded_title}.webp'
    book.cover_url = cover_url
    book.save(update_fields=['cover_url'])
    count += 1
    print(f'[{count}] {book.title} -> {cover_url}')

print(f'\n完成，共更新 {count} 本图书的封面URL。')
