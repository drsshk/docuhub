
import os
from pathlib import Path
from decouple import config
import dj_database_url
import logging.handlers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core Settings ---
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# --- Application Definition ---
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_extensions',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.projects',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'docuhub.urls'
WSGI_APPLICATION = 'docuhub.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

# --- Database ---
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', cast=int),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }


# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
USE_TZ = True

# --- Static and Media Files ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Development vs. Production Settings ---

if DEBUG:
    # --- Development Settings ---
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0','152.42.210.234']
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://152.42.210.234/"
    ]
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
    AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 4}}]
    RATELIMIT_ENABLE = False
    REST_FRAMEWORK = {} # Reset to avoid production settings
else:
    # --- Production Settings ---
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'KEY_PREFIX': 'docuhub',
            'TIMEOUT': 300,
        }
    }
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]
    RATELIMIT_ENABLE = True
    # Security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    # CSRF settings
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    # Session security
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# --- Shared Settings ---

CORS_ALLOW_CREDENTIALS = True

# Django REST Framework
REST_FRAMEWORK_BASE = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
if not DEBUG:
    REST_FRAMEWORK_BASE['DEFAULT_THROTTLE_CLASSES'] = [
        'apps.projects.permissions.ProjectUserRateThrottle',
        'apps.projects.permissions.ProjectAnonRateThrottle',
    ]
    REST_FRAMEWORK_BASE['DEFAULT_THROTTLE_RATES'] = {
        'project_user': '1000/hour',
        'project_anon': '100/hour',
        'project_admin': '2000/hour',
    }

REST_FRAMEWORK = REST_FRAMEWORK_BASE


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {asctime} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': True},
        'projects': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'accounts': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'notifications': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'core': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

if DEBUG:
    LOGGING['handlers'].update({
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'verbose',
        },
    })
    LOGGING['loggers']['django']['handlers'] = ['console', 'file']
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    for app in LOCAL_APPS:
        app_name = app.split('.')[-1]
        LOGGING['loggers'][app_name]['handlers'] = ['console', 'file', 'error_file']
        LOGGING['loggers'][app_name]['level'] = 'DEBUG'
else: # Production logging
    LOGGING['handlers'].update({
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'docuhub.log',
            'formatter': 'verbose',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'verbose',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
        },
    })
    LOGGING['loggers']['django']['handlers'] = ['console', 'file']
    LOGGING['loggers']['django.security'] = {'handlers': ['security_file'], 'level': 'WARNING', 'propagate': False}
    for app in LOCAL_APPS:
        app_name = app.split('.')[-1]
        LOGGING['loggers'][app_name]['handlers'] = ['file', 'error_file']
        LOGGING['loggers'][app_name]['level'] = 'INFO'


# Email Configuration (Brevo)
BREVO_API_KEY = config('BREVO_API_KEY', default='')
BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@docuhub.com')
BREVO_SENDER_NAME = config('BREVO_SENDER_NAME', default='DocuHub System')

# Frontend URL for email links
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:8000')

# Email Template IDs (Brevo)
EMAIL_TEMPLATES = {
    'PROJECT_SUBMITTED': config('EMAIL_TEMPLATE_PROJECT_SUBMITTED', default=1, cast=int),
    'PROJECT_APPROVED': config('EMAIL_TEMPLATE_PROJECT_APPROVED', default=2, cast=int),
    'PROJECT_REJECTED': config('EMAIL_TEMPLATE_PROJECT_REJECTED', default=3, cast=int),
    'PROJECT_REVISE_RESUBMIT': config('EMAIL_TEMPLATE_PROJECT_REVISE_RESUBMIT', default=4, cast=int),
    'PROJECT_OBSOLETE': config('EMAIL_TEMPLATE_PROJECT_OBSOLETE', default=5, cast=int),
    'ADMIN_NEW_SUBMISSION': config('EMAIL_TEMPLATE_ADMIN_NEW_SUBMISSION', default=6, cast=int),
    'ADMIN_RESUBMISSION': config('EMAIL_TEMPLATE_ADMIN_RESUBMISSION', default=7, cast=int),
}

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Sentry
if config('SENTRY_DSN', default=''):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )

    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
