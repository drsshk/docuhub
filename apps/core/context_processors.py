from django.conf import settings
import docuhub

def site_settings(request):
    """Add site-wide settings to template context"""
    return {
        'SITE_NAME': 'DocuHub',
        'SITE_DESCRIPTION': 'Drawing Version Management System',
        'DEBUG': settings.DEBUG,
        'APP_VERSION': docuhub.__version__,
    }