"""
Development settings for DocuHub project.
"""
from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),  
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", cast=int),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}

# CORS Settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Development logging with file output
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

# Update loggers for development
LOGGING['loggers'].update({
    'django': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'projects': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'accounts': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'notifications': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'DEBUG',
        'propagate': False,
    },
})

# Development email backend (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (if installed)
if 'debug_toolbar' in INSTALLED_APPS:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Development cache (dummy)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Less strict password validation for development
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
]