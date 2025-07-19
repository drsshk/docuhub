from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

# URL patterns - Django receives /docuhub/ prefix
urlpatterns = [
    path('docuhub/admin/', admin.site.urls),
    path('docuhub/', core_views.dashboard, name='dashboard'),
    path('docuhub/core/', include('apps.core.urls')),
    path('docuhub/notifications/', include('apps.notifications.urls')),
    path('docuhub/api/', include('apps.projects.api_urls')),
    path('docuhub/accounts/', include('apps.accounts.urls')),
    path('docuhub/projects/', include('apps.projects.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)