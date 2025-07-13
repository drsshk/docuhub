from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import UserProfile, UserSession, AuditLog
import re

def validate_employee_id(employee_id):
    """Validate employee ID format"""
    if not employee_id:
        return True  # Employee ID is optional
    
    # Example validation: must be alphanumeric, 3-10 characters
    if not re.match(r'^[A-Za-z0-9]{3,10}$', employee_id):
        raise ValidationError(
            'Employee ID must be 3-10 alphanumeric characters'
        )
    return True

def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Basic phone validation - adjust pattern as needed
    phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
    if not re.match(phone_pattern, phone):
        raise ValidationError(
            'Please enter a valid phone number'
        )
    return True

def get_user_full_name(user):
    """Get user's full name or username as fallback"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return user.username

def create_user_profile(user, **kwargs):
    """Create or update user profile with given data"""
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults=kwargs
    )
    
    if not created:
        # Update existing profile
        for key, value in kwargs.items():
            setattr(profile, key, value)
        profile.save()
    
    return profile

def log_user_action(user, action, description="", performed_by=None, ip_address=None, **kwargs):
    """Log user action for audit purposes"""
    try:
        from .models import AuditLog
        AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            performed_by=performed_by or user,
            ip_address=ip_address,
            additional_data=kwargs
        )
    except Exception as e:
        # Don't let audit logging break the main functionality
        import logging
        logger = logging.getLogger('accounts')
        logger.error(f"Failed to log user action: {e}")

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def cleanup_inactive_sessions(days=30):
    """Clean up old inactive sessions"""
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    # Mark old sessions as inactive
    updated_count = UserSession.objects.filter(
        last_activity__lt=cutoff_date,
        is_active=True
    ).update(
        is_active=False,
        logout_time=timezone.now()
    )
    
    return updated_count

def get_user_statistics(user):
    """Get comprehensive user statistics"""
    stats = {}
    
    # Project statistics (if projects app is available)
    try:
        stats['projects'] = {
            'total': user.submitted_projects.count(),
            'draft': user.submitted_projects.filter(status='Draft').count(),
            'pending': user.submitted_projects.filter(status='Pending_Approval').count(),
            'approved': user.submitted_projects.filter(status='Approved').count(),
            'rejected': user.submitted_projects.filter(status='Rejected').count(),
        }
    except AttributeError:
        # Projects app not available or not set up yet
        stats['projects'] = {
            'total': 0, 'draft': 0, 'pending': 0, 'approved': 0, 'rejected': 0
        }
    
    # Session statistics
    stats['sessions'] = {
        'total_sessions': UserSession.objects.filter(user=user).count(),
        'active_sessions': UserSession.objects.filter(user=user, is_active=True).count(),
        'last_login': user.last_login,
    }
    
    # Profile completeness
    profile = getattr(user, 'profile', None)
    if profile:
        fields = ['department', 'job_title', 'phone_number', 'employee_id', 'location', 'bio']
        filled_fields = sum(1 for field in fields if getattr(profile, field))
        stats['profile_completeness'] = (filled_fields / len(fields)) * 100
    else:
        stats['profile_completeness'] = 0
    
    return stats

def is_user_admin(user):
    """Check if user has admin privileges"""
    return user.is_staff or user.is_superuser

def is_admin_role_user(user):
    """Check if user has admin role (for decorator use)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def format_user_display_name(user):
    """Format user name for display purposes"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return user.username

def get_users_by_department(department):
    """Get all users in a specific department"""
    return User.objects.filter(
        profile__department=department,
        is_active=True
    ).select_related('profile')

def get_department_statistics():
    """Get statistics by department"""
    from django.db.models import Count
    
    return UserProfile.objects.values('department').annotate(
        user_count=Count('user')
    ).order_by('-user_count')

import requests
from django.conf import settings
from django.urls import reverse

def send_account_setup_email(user, token, uid):
    """
    Sends an email to the new user with a link to set their password.
    """
    import logging
    logger = logging.getLogger('accounts')
    
    # --- FIX: Added 'accounts:' namespace to the reverse() call ---
    password_setup_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    
    # The rest of the function remains the same
    full_setup_url = settings.FRONTEND_URL + password_setup_path

    # Brevo API details from settings.py
    api_key = settings.BREVO_API_KEY
    api_url = settings.BREVO_API_URL
    sender_email = settings.DEFAULT_FROM_EMAIL
    sender_name = settings.BREVO_SENDER_NAME

    if not api_key:
        logger.warning(f"BREVO_API_KEY not set. Email not sent for user {user.username}")
        logger.info(f"Password setup link for {user.username}: {full_setup_url}")
        return False

    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }

    data = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": user.email, "name": user.get_full_name()}],
        "subject": "Welcome to DocuHub - Set Up Your Account",
        "htmlContent": (
            f"<html><body>"
            f"<h2>Welcome to DocuHub, {user.first_name}!</h2>"
            f"<p>An account has been created for you. Please set your password by clicking the link below:</p>"
            f'<p><a href="{full_setup_url}" style="padding: 10px 20px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px;">Set Your Password</a></p>'
            f"<p>This link is valid for 24 hours.</p>"
            f"<p>If you did not expect this, please ignore this email.</p>"
            f"</body></html>"
        )
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Account setup email sent successfully via Brevo to {user.email}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send account setup email to {user.email}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Brevo API response: {e.response.text}")
        return False

def send_password_reset_email(user, temp_password):
    """
    Sends a temporary password to the user's email via Brevo API only.
    """
    import logging
    logger = logging.getLogger('accounts')
    
    api_key = settings.BREVO_API_KEY
    api_url = settings.BREVO_API_URL
    sender_email = settings.DEFAULT_FROM_EMAIL
    sender_name = settings.BREVO_SENDER_NAME

    if not api_key:
        logger.error(f"BREVO_API_KEY not set. Password reset email cannot be sent for user {user.username}")
        return False

    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }

    data = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": user.email, "name": user.get_full_name()}],
        "subject": "DocuHub Password Reset",
        "htmlContent": (
            f"<html><body>"
            f"<h2>Hello {user.first_name or user.username},</h2>"
            f"<p>Your password for DocuHub has been reset.</p>"
            f"<p>Your temporary password is: <strong>{temp_password}</strong></p>"
            f"<p>Please log in with this temporary password and change it immediately for security reasons.</p>"
            f'<p><a href="{settings.FRONTEND_URL}/accounts/login/" style="padding: 10px 20px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px;">Login to DocuHub</a></p>'
            f"<p>If you did not request this password reset, please contact support immediately.</p>"
            f"</body></html>"
        )
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Password reset email sent successfully via Brevo to {user.email}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send password reset email via Brevo to {user.email}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Brevo API response: {e.response.text}")
        return False