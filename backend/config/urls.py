"""
URL configuration for BookCorner project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 路由
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.urls_users')),
    path('api/categories/', include('apps.books.urls_categories')),
    path('api/books/', include('apps.books.urls_books')),
    path('api/copies/', include('apps.books.urls_copies')),
    path('api/borrows/', include('apps.borrows.urls')),
    path('api/reservations/', include('apps.reservations.urls')),
    path('api/fines/', include('apps.fines.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    
    # API 文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# 开发环境媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
