"""
图书模块 Admin 配置
"""
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category, Book, BookCopy


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_display = ('name', 'code', 'sort_order', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'status')
    list_filter = ('status', 'category', 'language')
    search_fields = ('title', 'author', 'isbn', 'publisher')
    ordering = ('-created_at',)


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'book', 'condition', 'status', 'location')
    list_filter = ('status', 'condition')
    search_fields = ('barcode', 'book__title')
    ordering = ('-created_at',)
