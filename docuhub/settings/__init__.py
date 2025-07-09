"""
Settings module for DocuHub project.

This module dynamically loads the appropriate settings based on the 
DJANGO_SETTINGS_MODULE environment variable or defaults to development.
"""
import os
from decouple import config

# Determine which settings to use
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'staging':
    # You can create staging.py if needed
    from .production import *
    DEBUG = True  # Override for staging
else:
    from .development import *