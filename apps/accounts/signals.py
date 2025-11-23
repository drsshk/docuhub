import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.db import IntegrityError, DatabaseError
from .models import UserProfile, UserSession, NotificationPreferences

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create a user profile when a new user is created, and save it on updates.
    Handles database errors gracefully to prevent user creation failures.
    """
    if created:
        try:
            # Get or create default role
            from .models import Role
            default_role, _ = Role.objects.get_or_create(
                name='User',
                defaults={'description': 'Default user role'}
            )
            
            # Create user profile with default role
            profile, profile_created = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'role': default_role, 'department': '', 'phone_number': ''}
            )
            
            if profile_created:
                logger.info(f"Created UserProfile for user {instance.username}")
            
            # Create notification preferences
            prefs, prefs_created = NotificationPreferences.objects.get_or_create(
                user=instance,
                defaults={
                    'email_enabled': True,
                    'submission_notifications': True,
                    'approval_notifications': True,
                    'rejection_notifications': True,
                    'revision_notifications': True
                }
            )
            
            if prefs_created:
                logger.info(f"Created NotificationPreferences for user {instance.username}")
                
        except IntegrityError as e:
            logger.warning(f"IntegrityError creating profile for user {instance.username}: {e}")
            # Profile already exists, continue gracefully
        except DatabaseError as e:
            logger.error(f"DatabaseError creating profile for user {instance.username}: {e}")
            # Log error but don't prevent user creation
        except Exception as e:
            logger.error(f"Unexpected error creating profile for user {instance.username}: {e}")
    
    # Save profile if it exists
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except (IntegrityError, DatabaseError) as e:
        logger.warning(f"Error saving profile for user {instance.username}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error saving profile for user {instance.username}: {e}")

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Handle user login - create session record with error handling"""
    try:
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Ensure we have a session key
        if not request.session.session_key:
            request.session.create()
        
        # Create session record
        session, created = UserSession.objects.get_or_create(
            user=user,
            session_key=request.session.session_key,
            defaults={
                'ip_address': ip,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
            }
        )
        
        if created:
            logger.info(f"Created session record for user {user.username} from {ip}")
        else:
            # Update existing session to active
            session.is_active = True
            session.last_active_at = timezone.now()
            session.save()
            
    except IntegrityError as e:
        logger.warning(f"IntegrityError creating session for user {user.username}: {e}")
    except DatabaseError as e:
        logger.error(f"DatabaseError creating session for user {user.username}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating session for user {user.username}: {e}")

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """Handle user logout - mark session as inactive with error handling"""
    try:
        if user and hasattr(request, 'session') and request.session.session_key:
            updated_count = UserSession.objects.filter(
                user=user,
                session_key=request.session.session_key,
                is_active=True
            ).update(is_active=False, logout_time=timezone.now())
            
            if updated_count > 0:
                logger.info(f"Marked session inactive for user {user.username}")
                
    except DatabaseError as e:
        logger.error(f"DatabaseError updating session for user logout {user.username if user else 'unknown'}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error updating session for user logout {user.username if user else 'unknown'}: {e}")

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up related data when user is deleted with error handling"""
    try:
        # Marking sessions as inactive is a good non-destructive practice.
        updated_count = UserSession.objects.filter(user=instance).update(
            is_active=False,
            logout_time=timezone.now()
        )
        
        if updated_count > 0:
            logger.info(f"Cleaned up {updated_count} sessions for deleted user {instance.username}")
            
    except DatabaseError as e:
        logger.error(f"DatabaseError cleaning up data for deleted user {instance.username}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error cleaning up data for deleted user {instance.username}: {e}")