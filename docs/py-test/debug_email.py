#!/usr/bin/env python
"""
Email Configuration Debug Script for DocuHub
Run this to diagnose password reset email issues
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docuhub.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from apps.accounts.utils import send_password_reset_email

def check_email_config():
    """Check email configuration"""
    print("=== DocuHub Email Configuration Debug ===\n")
    
    print("1. Django Email Settings:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    if not settings.DEBUG:
        print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER[:5]}***" if settings.EMAIL_HOST_USER else "   EMAIL_HOST_USER: Not set")
        print(f"   EMAIL_HOST_PASSWORD: {'***set***' if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    
    print(f"\n2. Brevo API Configuration:")
    print(f"   BREVO_API_KEY: {'***set***' if settings.BREVO_API_KEY else 'NOT SET'}")
    print(f"   BREVO_API_URL: {settings.BREVO_API_URL}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   BREVO_SENDER_NAME: {settings.BREVO_SENDER_NAME}")
    print(f"   FRONTEND_URL: {settings.FRONTEND_URL}")
    
    print(f"\n3. Environment Variables Check:")
    env_vars = [
        'BREVO_API_KEY', 'DEFAULT_FROM_EMAIL', 'BREVO_SENDER_NAME', 
        'FRONTEND_URL', 'EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'
    ]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                print(f"   {var}: ***set***")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: NOT SET")

def test_password_reset_email():
    """Test password reset email function"""
    print(f"\n4. Testing Password Reset Email Function:")
    
    # Find a test user
    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("   ERROR: No active users found for testing")
            return
        
        print(f"   Testing with user: {user.username} ({user.email})")
        
        if not user.email:
            print("   ERROR: Test user has no email address")
            return
        
        # Test the function
        temp_password = "test123temp"
        print(f"   Attempting to send password reset email...")
        
        send_password_reset_email(user, temp_password)
        print("   Password reset email function completed (check logs for success/failure)")
        
    except Exception as e:
        print(f"   ERROR: Failed to test password reset email: {e}")

def provide_solutions():
    """Provide potential solutions"""
    print(f"\n5. Potential Solutions:")
    
    if not settings.BREVO_API_KEY:
        print("   • CRITICAL: BREVO_API_KEY is not set!")
        print("     - Copy .env.example to .env and update the values")
        print("     - Set BREVO_API_KEY in your .env file")
        print("     - Get API key from: https://app.brevo.com/settings/keys/api")
    else:
        print("   • BREVO_API_KEY is set, but getting API errors:")
        print("     - Verify the API key is valid and not expired")
        print("     - Check Brevo account status and credits")
        print("     - Ensure sender email is verified in Brevo")
    
    if settings.DEBUG:
        print("   • Currently in DEBUG mode:")
        print("     - Django emails will appear in console")
        print("     - Brevo API calls still work in debug mode")
        print("     - Check console output for detailed error messages")
    
    print("   • Setup Instructions:")
    print("     1. Copy .env.example to .env")
    print("     2. Add your Brevo API key to BREVO_API_KEY")
    print("     3. Update DEFAULT_FROM_EMAIL with verified sender")
    print("     4. Restart the Django server")
    
    print("   • Check Django logs for detailed errors:")
    print("     - Location: logs/development.log or logs/errors.log")
    print("   • Verify user has a valid email address")
    print("   • Test with Brevo API directly: https://developers.brevo.com/reference/sendtransacemail")

if __name__ == "__main__":
    check_email_config()
    test_password_reset_email()
    provide_solutions()
    
    print(f"\n=== Debug Complete ===")