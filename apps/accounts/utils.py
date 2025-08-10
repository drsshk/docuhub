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

from django.conf import settings
from django.urls import reverse

def send_account_setup_email(user, token, uid):
    """
    Sends an email to the new user with a link to set their password.
    """
    import logging
    logger = logging.getLogger('accounts')
    
    try:
        from apps.notifications.services import BrevoEmailService
        email_service = BrevoEmailService()
        
        # Generate the password setup URL
        password_setup_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        full_setup_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000') + password_setup_path
        
        # Send the email using our custom template system
        success = email_service.send_account_setup_email(user, full_setup_url)
        
        if success:
            logger.info(f"Account setup email sent successfully to {user.email}")
        else:
            logger.warning(f"Failed to send account setup email to {user.email}")
            logger.info(f"Password setup link for {user.username}: {full_setup_url}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending account setup email to {user.email}: {e}")
        return False

def send_password_reset_email(user, temp_password, is_temp_password=False):
    """
    Sends a temporary password to the user's email using custom templates.
    """
    import logging
    logger = logging.getLogger('accounts')
    
    try:
        from apps.notifications.services import BrevoEmailService
        email_service = BrevoEmailService()
        
        # Generate the login URL
        login_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/accounts/login/"
        
        # Send the email using our custom template system
        success = email_service.send_password_reset_email(user, temp_password, login_url, is_temp_password)
        
        if success:
            logger.info(f"Password reset email sent successfully to {user.email}")
        else:
            logger.warning(f"Failed to send password reset email to {user.email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {e}")
        return False