"""
图书模块序列化器
"""
from rest_framework import serializers
from .models import Category, Book, BookCopy, BookStatus, BookCopyStatus, BookCopyCondition


# ==================== 分类序列化器 ====================

class CategorySerializer(serializers.ModelSerializer):
    """分类基础序列化器"""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'code', 'sort_order', 'depth', 'created_at')
        read_only_fields = ('id', 'depth', 'created_at')


class CategoryTreeSerializer(serializers.ModelSerializer):
    """分类树形序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'code', 'sort_order', 'depth', 'children')
    
    def get_children(self, obj):
        children = obj.get_children()
        return CategoryTreeSerializer(children, many=True).data


class CategoryCreateSerializer(serializers.ModelSerializer):
    """分类创建序列化器"""
    parent_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Category
        fields = ('name', 'code', 'sort_order', 'parent_id')
    
    def validate_code(self, value):
        if value and Category.objects.filter(code=value).exists():
            raise serializers.ValidationError('分类编号已存在')
        return value
    
    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        
        if parent_id:
            try:
                parent = Category.objects.get(pk=parent_id)
                category = parent.add_child(**validated_data)
            except Category.DoesNotExist:
                raise serializers.ValidationError({'parent_id': '父分类不存在'})
        else:
            category = Category.add_root(**validated_data)
        
        return category


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """分类更新序列化器"""
    
    class Meta:
        model = Category
        fields = ('name', 'code', 'sort_order')
    
    def validate_code(self, value):
        instance = self.instance
        if value and Category.objects.exclude(pk=instance.pk).filter(code=value).exists():
            raise serializers.ValidationError('分类编号已存在')
        return value


# ==================== 图书序列化器 ====================

class BookListSerializer(serializers.ModelSerializer):
    """图书列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Book
        fields = (
            'id', 'isbn', 'title', 'author', 'publisher', 'cover_url',
            'category', 'category_name', 'total_copies', 'available_copies',
            'price', 'publish_date', 'status', 'status_display', 'created_at'
        )


class BookDetailSerializer(serializers.ModelSerializer):
    """图书详情序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    copies = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'isbn', 'title', 'author', 'publisher', 'cover_url',
            'description', 'category', 'category_name',
            'total_copies', 'available_copies', 'price', 'publish_date',
            'language', 'status', 'status_display', 'copies',
            'created_at', 'updated_at'
        )
    
    def get_copies(self, obj):
        """获取副本列表（简要信息）"""
        copies = obj.copies.all()[:10]  # 最多显示10个
        return BookCopyBriefSerializer(copies, many=True).data


class BookCreateSerializer(serializers.ModelSerializer):
    """图书创建序列化器"""
    
    class Meta:
        model = Book
        fields = (
            'isbn', 'title', 'author', 'publisher', 'cover_url',
            'description', 'category', 'price', 'publish_date', 'language', 'status'
        )
    
    def validate_isbn(self, value):
        if value and Book.objects.filter(isbn=value).exists():
            raise serializers.ValidationError('ISBN 已存在')
        return value


class BookUpdateSerializer(serializers.ModelSerializer):
    """图书更新序列化器"""
    
    class Meta:
        model = Book
        fields = (
            'isbn', 'title', 'author', 'publisher', 'cover_url',
            'description', 'category', 'price', 'publish_date', 'language', 'status'
        )
    
    def validate_isbn(self, value):
        instance = self.instance
        if value and Book.objects.exclude(pk=instance.pk).filter(isbn=value).exists():
            raise serializers.ValidationError('ISBN 已存在')
        return value


# ==================== 副本序列化器 ====================

class BookCopyBriefSerializer(serializers.ModelSerializer):
    """副本简要序列化器"""
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BookCopy
        fields = ('id', 'barcode', 'condition', 'condition_display', 'status', 'status_display', 'location')


class BookCopyListSerializer(serializers.ModelSerializer):
    """副本列表序列化器"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BookCopy
        fields = (
            'id', 'book', 'book_title', 'book_author', 'barcode',
            'condition', 'condition_display', 'status', 'status_display',
            'location', 'created_at', 'updated_at'
        )


class BookCopyDetailSerializer(serializers.ModelSerializer):
    """副本详情序列化器"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BookCopy
        fields = (
            'id', 'book', 'book_title', 'book_author', 'book_isbn',
            'barcode', 'condition', 'condition_display',
            'status', 'status_display', 'location',
            'created_at', 'updated_at'
        )


class BookCopyCreateSerializer(serializers.ModelSerializer):
    """副本创建序列化器（入库）"""
    
    class Meta:
        model = BookCopy
        fields = ('book', 'barcode', 'condition', 'location')
    
    def validate_barcode(self, value):
        if BookCopy.objects.filter(barcode=value).exists():
            raise serializers.ValidationError('条形码已存在')
        return value
    
    def create(self, validated_data):
        copy = super().create(validated_data)
        # 更新图书的馆藏总数和可借数量
        book = copy.book
        book.total_copies += 1
        book.available_copies += 1
        book.save(update_fields=['total_copies', 'available_copies'])
        return copy


class BookCopyUpdateSerializer(serializers.ModelSerializer):
    """副本更新序列化器"""
    
    class Meta:
        model = BookCopy
        fields = ('condition', 'status', 'location')


class BookCopyBatchCreateSerializer(serializers.Serializer):
    """批量入库序列化器"""
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    barcodes = serializers.ListField(
        child=serializers.CharField(max_length=50),
        min_length=1,
        max_length=100
    )
    condition = serializers.ChoiceField(
        choices=BookCopyCondition.choices,
        default=BookCopyCondition.NEW
    )
    location = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_barcodes(self, value):
        # 检查是否有重复
        if len(value) != len(set(value)):
            raise serializers.ValidationError('条形码列表中存在重复')
        # 检查是否已存在
        existing = BookCopy.objects.filter(barcode__in=value).values_list('barcode', flat=True)
        if existing:
            raise serializers.ValidationError(f'以下条形码已存在: {", ".join(existing)}')
        return value
    
    def create(self, validated_data):
        book = validated_data['book']
        barcodes = validated_data['barcodes']
        condition = validated_data.get('condition', BookCopyCondition.NEW)
        location = validated_data.get('location', '')
        
        copies = []
        for barcode in barcodes:
            copies.append(BookCopy(
                book=book,
                barcode=barcode,
                condition=condition,
                location=location,
                status=BookCopyStatus.IN_LIBRARY
            ))
        
        BookCopy.objects.bulk_create(copies)
        
        # 更新图书的馆藏总数和可借数量
        count = len(barcodes)
        book.total_copies += count
        book.available_copies += count
        book.save(update_fields=['total_copies', 'available_copies'])
        
        return copies
