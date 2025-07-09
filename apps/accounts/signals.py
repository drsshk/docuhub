from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import UserProfile, UserSession

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create a user profile when a new user is created, and save it on updates.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Handle user login - create session record"""
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Create session record
    UserSession.objects.get_or_create(
        user=user,
        session_key=request.session.session_key,
        defaults={
            'ip_address': ip,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_active': True,
        }
    )

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """Handle user logout - mark session as inactive"""
    if user and hasattr(request, 'session'):
        UserSession.objects.filter(
            user=user,
            session_key=request.session.session_key,
            is_active=True
        ).update(is_active=False, logout_time=timezone.now())

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up related data when user is deleted"""
    # Marking sessions as inactive is a good non-destructive practice.
    UserSession.objects.filter(user=instance).update(
        is_active=False,
        logout_time=timezone.now()
    )