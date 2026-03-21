"""
公告模块视图
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from utils.response import success_response, error_response
from utils.permissions import IsAdmin
from .models import Announcement, AnnouncementStatus
from .serializers import (
    AnnouncementListSerializer,
    AnnouncementDetailSerializer,
    AnnouncementCreateSerializer,
    AnnouncementUpdateSerializer,
    PublishedAnnouncementSerializer,
)


class AnnouncementListView(generics.ListCreateAPIView):
    """
    公告列表（管理员）
    GET /api/announcements/ - 所有公告
    POST /api/announcements/ - 创建公告
    """
    queryset = Announcement.objects.select_related('admin').all()
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'admin']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnnouncementCreateSerializer
        return AnnouncementListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        announcement = serializer.save()
        
        # 如果状态是发布，设置发布时间
        if announcement.status == AnnouncementStatus.PUBLISHED:
            announcement.published_at = timezone.now()
            announcement.save(update_fields=['published_at'])
        
        return success_response(
            data=AnnouncementDetailSerializer(announcement).data,
            message='公告创建成功',
            code=201
        )


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    公告详情（管理员）
    GET /api/announcements/{id}/
    PUT /api/announcements/{id}/
    DELETE /api/announcements/{id}/
    """
    queryset = Announcement.objects.select_related('admin').all()
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AnnouncementUpdateSerializer
        return AnnouncementDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AnnouncementDetailSerializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 如果从非发布变为发布，设置发布时间
        if old_status != AnnouncementStatus.PUBLISHED and instance.status == AnnouncementStatus.PUBLISHED:
            instance.published_at = timezone.now()
            instance.save(update_fields=['published_at'])
        
        return success_response(
            data=AnnouncementDetailSerializer(instance).data,
            message='更新成功'
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='删除成功')


class AnnouncementPublishView(APIView):
    """
    发布公告
    POST /api/announcements/{id}/publish/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return error_response(message='公告不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if announcement.status == AnnouncementStatus.PUBLISHED:
            return error_response(message='公告已发布', code=400)
        
        announcement.status = AnnouncementStatus.PUBLISHED
        announcement.published_at = timezone.now()
        announcement.save()
        
        return success_response(
            data=AnnouncementDetailSerializer(announcement).data,
            message='公告已发布'
        )


class AnnouncementArchiveView(APIView):
    """
    下架公告
    POST /api/announcements/{id}/archive/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return error_response(message='公告不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        if announcement.status == AnnouncementStatus.ARCHIVED:
            return error_response(message='公告已下架', code=400)
        
        announcement.status = AnnouncementStatus.ARCHIVED
        announcement.save()
        
        return success_response(
            data=AnnouncementDetailSerializer(announcement).data,
            message='公告已下架'
        )


class PublishedAnnouncementListView(generics.ListAPIView):
    """
    已发布公告列表（所有用户，包括未登录）
    GET /api/announcements/published/
    """
    serializer_class = PublishedAnnouncementSerializer
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter]
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Announcement.objects.filter(status=AnnouncementStatus.PUBLISHED)


class PublishedAnnouncementDetailView(APIView):
    """
    已发布公告详情（所有用户）
    GET /api/announcements/published/{id}/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk, status=AnnouncementStatus.PUBLISHED)
        except Announcement.DoesNotExist:
            return error_response(message='公告不存在', code=404, status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = PublishedAnnouncementSerializer(announcement)
        return success_response(data=serializer.data)


class LatestAnnouncementView(APIView):
    """
    最新公告（首页用）
    GET /api/announcements/latest/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        count = int(request.query_params.get('count', 5))
        count = min(count, 10)  # 最多10条
        
        announcements = Announcement.objects.filter(
            status=AnnouncementStatus.PUBLISHED
        ).order_by('-published_at')[:count]
        
        serializer = PublishedAnnouncementSerializer(announcements, many=True)
        return success_response(data=serializer.data)
