from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

# URL prefix for the application
URL_PREFIX = 'docuhub/'

# Core application patterns
app_patterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('core/', include('apps.core.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/', include('apps.projects.api_urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('projects/', include('apps.projects.urls')),
]

# Apply URL prefix to all patterns
urlpatterns = [
    path(URL_PREFIX, include(app_patterns)),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)