"""
公告模块序列化器
"""
from rest_framework import serializers
from .models import Announcement, AnnouncementStatus


class AnnouncementListSerializer(serializers.ModelSerializer):
    """公告列表序列化器"""
    admin_name = serializers.CharField(source='admin.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Announcement
        fields = (
            'id', 'title', 'admin', 'admin_name',
            'status', 'status_display',
            'published_at', 'created_at'
        )


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    """公告详情序列化器"""
    admin_name = serializers.CharField(source='admin.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Announcement
        fields = (
            'id', 'title', 'content', 'admin', 'admin_name',
            'status', 'status_display',
            'published_at', 'created_at'
        )


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    """公告创建序列化器"""
    
    class Meta:
        model = Announcement
        fields = ('title', 'content', 'status')
    
    def create(self, validated_data):
        validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)


class AnnouncementUpdateSerializer(serializers.ModelSerializer):
    """公告更新序列化器"""
    
    class Meta:
        model = Announcement
        fields = ('title', 'content', 'status')


class PublishedAnnouncementSerializer(serializers.ModelSerializer):
    """已发布公告序列化器（读者用）"""
    
    class Meta:
        model = Announcement
        fields = ('id', 'title', 'content', 'published_at')
