"""
图书模块视图
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.conf import settings
import requests as http_requests

from utils.response import success_response, error_response
from utils.permissions import IsAdmin, IsAdminOrReadOnly
from utils.oss import upload_file_to_oss
from .models import Category, Book, BookCopy, BookCopyStatus
from .serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
    BookListSerializer,
    BookDetailSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
    BookCopyListSerializer,
    BookCopyDetailSerializer,
    BookCopyCreateSerializer,
    BookCopyUpdateSerializer,
    BookCopyBatchCreateSerializer,
)


# ==================== 分类视图 ====================

class CategoryListView(APIView):
    """
    分类列表
    GET /api/categories/ - 获取树形分类列表
    POST /api/categories/ - 创建分类（管理员）
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get(self, request):
        """获取树形分类列表"""
        root_categories = Category.get_root_nodes()
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        """创建分类"""
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return success_response(
            data=CategorySerializer(category).data,
            message='分类创建成功',
            code=201
        )


class CategoryDetailView(APIView):
    """
    分类详情
    GET /api/categories/{id}/ - 获取分类详情
    PUT /api/categories/{id}/ - 更新分类（管理员）
    DELETE /api/categories/{id}/ - 删除分类（管理员）
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None
    
    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message='分类不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 返回分类及其子分类
        serializer = CategoryTreeSerializer(category)
        return success_response(data=serializer.data)
    
    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message='分类不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = CategoryUpdateSerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(data=CategorySerializer(category).data, message='更新成功')
    
    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return error_response(message='分类不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        # 检查是否有关联图书
        if category.books.exists():
            return error_response(message='该分类下有图书，无法删除', code=400)
        
        # 检查是否有子分类
        if category.get_children().exists():
            return error_response(message='该分类有子分类，无法删除', code=400)
        
        category.delete()
        return success_response(message='删除成功')


class CategoryFlatListView(APIView):
    """
    分类平铺列表（下拉选择用）
    GET /api/categories/flat/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Category.objects.all().order_by('path')
        data = []
        for cat in categories:
            # 添加层级前缀
            prefix = '　' * (cat.depth - 1) + ('└ ' if cat.depth > 1 else '')
            data.append({
                'id': cat.id,
                'name': cat.name,
                'display_name': f'{prefix}{cat.name}',
                'code': cat.code,
                'depth': cat.depth
            })
        return success_response(data=data)


# ==================== 图书视图 ====================


class BookCoverUploadView(APIView):
    """
    上传图书封面图片到 OSS
    POST /api/books/upload-cover/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return error_response(message='请选择要上传的图片', code=400)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if file.content_type not in allowed_types:
            return error_response(message='仅支持 JPG/PNG/WebP/GIF 格式的图片', code=400)

        # 验证文件大小（5MB）
        if file.size > 5 * 1024 * 1024:
            return error_response(message='图片大小不能超过 5MB', code=400)

        try:
            url = upload_file_to_oss(file, folder='covers')
            return success_response(data={'url': url}, message='上传成功')
        except Exception as e:
            return error_response(message=f'上传失败：{str(e)}', code=500,
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookGenerateDescriptionView(APIView):
    """
    AI 生成图书简介
    POST /api/books/{id}/generate-description/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            book = Book.objects.select_related('category').get(pk=pk)
        except Book.DoesNotExist:
            return error_response(message='图书不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)

        # 检查 API Key 是否配置
        if not settings.AI_API_KEY or settings.AI_API_KEY == 'your-ai-api-key-here':
            return error_response(message='AI 服务未配置，请联系管理员', code=503, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 获取用户关注的关键词
        keywords = request.data.get('keywords', '').strip()

        # 构建提示词
        prompt = self._build_prompt(book, keywords)

        try:
            resp = http_requests.post(
                f'{settings.AI_BASE_URL}/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {settings.AI_API_KEY}',
                },
                json={
                    'model': settings.AI_MODEL,
                    'messages': [
                        {'role': 'system', 'content': '你是一位专业的图书编辑，擅长撰写简洁准确的图书简介。请用中文回答。'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            description = data['choices'][0]['message']['content'].strip()
        except http_requests.exceptions.Timeout:
            return error_response(message='AI 服务响应超时，请稍后重试', code=504, status_code=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return error_response(message=f'AI 服务调用失败：{str(e)}', code=500, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 保存到数据库
        book.description = description
        book.save(update_fields=['description'])

        return success_response(data={'description': description}, message='简介生成成功')

    @staticmethod
    def _build_prompt(book, keywords=''):
        """构建 AI 提示词"""
        parts = ['请为以下图书撰写一段约300字的简介：']
        parts.append(f'书名：《{book.title}》')
        parts.append(f'作者：{book.author}')
        if book.publisher:
            parts.append(f'出版社：{book.publisher}')
        if book.isbn:
            parts.append(f'ISBN：{book.isbn}')
        if book.category:
            parts.append(f'分类：{book.category.name}')
        if keywords:
            parts.append(f'请重点关注以下方面：{keywords}')
        parts.append('要求：内容客观，语言流畅，约300字左右。')
        return '\n'.join(parts)


class BookListView(generics.ListCreateAPIView):
    """
    图书列表
    GET /api/books/ - 获取图书列表（支持搜索、筛选、分页）
    POST /api/books/ - 创建图书（管理员）
    """
    queryset = Book.objects.select_related('category').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'language']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    ordering_fields = ['created_at', 'title', 'available_copies']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookCreateSerializer
        return BookListSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        return success_response(
            data=BookDetailSerializer(book).data,
            message='图书创建成功',
            code=201
        )


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    图书详情
    GET /api/books/{id}/ - 获取图书详情
    PUT /api/books/{id}/ - 更新图书（管理员）
    DELETE /api/books/{id}/ - 删除图书（管理员）
    """
    queryset = Book.objects.select_related('category').prefetch_related('copies').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookUpdateSerializer
        return BookDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BookDetailSerializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = BookUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=BookDetailSerializer(instance).data, message='更新成功')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # 检查是否有副本
        if instance.copies.exists():
            return error_response(message='该图书有副本，无法删除', code=400)
        
        instance.delete()
        return success_response(message='删除成功')


class BookToggleStatusView(APIView):
    """
    切换图书上下架状态
    POST /api/books/{id}/toggle-status/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return error_response(message='图书不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        book.status = 0 if book.status == 1 else 1
        book.save(update_fields=['status'])
        
        return success_response(
            data={'status': book.status, 'status_display': book.get_status_display()},
            message=f'图书已{"上架" if book.status == 1 else "下架"}'
        )


# ==================== 副本视图 ====================

class BookCopyListView(generics.ListCreateAPIView):
    """
    副本列表
    GET /api/copies/ - 获取副本列表
    POST /api/copies/ - 创建副本（入库）
    """
    queryset = BookCopy.objects.select_related('book').all()
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['book', 'status', 'condition']
    search_fields = ['barcode', 'book__title', 'book__isbn']
    ordering_fields = ['created_at', 'barcode']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookCopyCreateSerializer
        return BookCopyListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        copy = serializer.save()
        return success_response(
            data=BookCopyDetailSerializer(copy).data,
            message='入库成功',
            code=201
        )


class BookCopyDetailView(generics.RetrieveUpdateAPIView):
    """
    副本详情
    GET /api/copies/{id}/ - 获取副本详情
    PUT /api/copies/{id}/ - 更新副本
    """
    queryset = BookCopy.objects.select_related('book').all()
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookCopyUpdateSerializer
        return BookCopyDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BookCopyDetailSerializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        
        serializer = BookCopyUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 如果状态变化，更新图书可借数量
        new_status = instance.status
        if old_status != new_status:
            book = instance.book
            # 从可借变为不可借
            if old_status == BookCopyStatus.IN_LIBRARY and new_status != BookCopyStatus.IN_LIBRARY:
                book.available_copies = max(0, book.available_copies - 1)
                book.save(update_fields=['available_copies'])
            # 从不可借变为可借
            elif old_status != BookCopyStatus.IN_LIBRARY and new_status == BookCopyStatus.IN_LIBRARY:
                book.available_copies += 1
                book.save(update_fields=['available_copies'])
        
        return success_response(data=BookCopyDetailSerializer(instance).data, message='更新成功')


class BookCopyBatchCreateView(APIView):
    """
    批量入库
    POST /api/copies/batch/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @transaction.atomic
    def post(self, request):
        serializer = BookCopyBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        copies = serializer.save()
        
        return success_response(
            data={'count': len(copies)},
            message=f'成功入库 {len(copies)} 册',
            code=201
        )


class BookCopyByBarcodeView(APIView):
    """
    通过条形码查询副本
    GET /api/copies/barcode/{barcode}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, barcode):
        try:
            copy = BookCopy.objects.select_related('book').get(barcode=barcode)
        except BookCopy.DoesNotExist:
            return error_response(message='副本不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = BookCopyDetailSerializer(copy)
        return success_response(data=serializer.data)


class BookCopiesByBookView(generics.ListAPIView):
    """
    获取某本书的所有副本
    GET /api/books/{book_id}/copies/
    """
    serializer_class = BookCopyListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'condition']
    ordering = ['-created_at']
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return BookCopy.objects.filter(book_id=book_id).select_related('book')
    
    def list(self, request, *args, **kwargs):
        # 验证图书是否存在
        book_id = self.kwargs.get('book_id')
        if not Book.objects.filter(pk=book_id).exists():
            return error_response(message='图书不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class BookAISearchView(APIView):
    """
    AI 智能检索图书
    POST /api/books/ai-search/
    用户用自然语言描述需求，AI 在馆藏中检索匹配的图书
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query', '').strip()
        if not query:
            return error_response(message='请输入检索内容', code=400)

        # 检查 AI 服务配置
        if not settings.AI_API_KEY or settings.AI_API_KEY == 'your-ai-api-key-here':
            return error_response(message='AI 服务未配置，请联系管理员', code=503,
                                  status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 获取馆藏图书列表（上架中的）
        books_qs = Book.objects.filter(status=1).select_related('category')
        book_list = []
        for b in books_qs[:500]:
            info = f'《{b.title}》 作者:{b.author}'
            if b.category:
                info += f' 分类:{b.category.name}'
            if b.description:
                info += f' 简介:{b.description[:60]}'
            book_list.append({'id': b.id, 'text': info, 'title': b.title, 'author': b.author})

        # 构建 prompt
        book_texts = '\n'.join([f"{i+1}. {item['text']}" for i, item in enumerate(book_list)])
        prompt = (
            f'以下是图书馆的馆藏书目清单：\n{book_texts}\n\n'
            f'读者的需求是：「{query}」\n\n'
            f'请根据读者需求，从上面的书目清单中找出最相关的图书（最多推荐5本）。'
            f'如果找到相关图书，请用以下JSON格式返回：'
            f'{{"found": true, "books": [{{"title": "书名", "author": "作者", "reason": "推荐理由"}}]}}\n'
            f'如果没有找到任何相关图书，请返回：'
            f'{{"found": false, "message": "未查询到该类图书"}}\n'
            f'注意：只返回JSON，不要包含其他内容。'
        )

        try:
            import json
            resp = http_requests.post(
                f'{settings.AI_BASE_URL}/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {settings.AI_API_KEY}',
                },
                json={
                    'model': settings.AI_MODEL,
                    'messages': [
                        {'role': 'system', 'content': '你是一位图书馆智能检索助手，帮助读者从馆藏中找到需要的图书。只返回JSON格式结果。'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 800,
                    'temperature': 0.3,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data['choices'][0]['message']['content'].strip()

            # 兼容 AI 可能返回 markdown 代码块
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            result = json.loads(content)

            return success_response(data=result)

        except http_requests.exceptions.Timeout:
            return error_response(message='AI 服务响应超时，请稍后重试', code=504,
                                  status_code=status.HTTP_504_GATEWAY_TIMEOUT)
        except (ValueError, KeyError, IndexError):
            return success_response(data={'found': False, 'message': 'AI 返回格式异常，请重试'})
        except Exception as e:
            return error_response(message=f'AI 检索失败：{str(e)}', code=500,
                                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
