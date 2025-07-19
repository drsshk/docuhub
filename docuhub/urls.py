from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views
from django.http import JsonResponse

def debug_view(request):
    return JsonResponse({
        'path': request.path,
        'full_path': request.get_full_path(),
        'absolute_uri': request.build_absolute_uri(),
        'static_url': settings.STATIC_URL,
        'script_name': request.META.get('SCRIPT_NAME'),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('debug/', debug_view),
    path('core/', include('apps.core.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/', include('apps.projects.api_urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('projects/', include('apps.projects.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)