import logging
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.db import IntegrityError, DatabaseError, OperationalError
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from .models import UserSession

logger = logging.getLogger(__name__)

class UserActivityMiddleware:
    """Middleware to track user activity and update session records"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before processing the request
        if request.user.is_authenticated and hasattr(request, 'session'):
            try:
                session = UserSession.objects.get(
                    user=request.user,
                    session_key=request.session.session_key,
                    is_active=True
                )
                session.last_activity = timezone.now()
                session.save(update_fields=['last_activity'])
            except UserSession.DoesNotExist:
                # Create session record if it doesn't exist
                UserSession.objects.create(
                    user=request.user,
                    session_key=request.session.session_key,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    is_active=True
                )

        response = self.get_response(request)
        
        # After processing the request
        return response

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware:
    """Middleware for session security enhancements"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for session hijacking indicators
        if request.user.is_authenticated:
            stored_user_agent = request.session.get('user_agent')
            current_user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            if stored_user_agent is None:
                # First time - store user agent
                request.session['user_agent'] = current_user_agent
            elif stored_user_agent != current_user_agent:
                # User agent changed - potential session hijacking
                # You could log this event or force logout
                pass

        response = self.get_response(request)
        return response


class DatabaseErrorMiddleware(MiddlewareMixin):
    """Middleware to handle database errors gracefully across the application"""

    def process_exception(self, request, exception):
        """Handle database-related exceptions"""
        
        if isinstance(exception, IntegrityError):
            logger.error(f"IntegrityError: {exception} - User: {getattr(request.user, 'username', 'anonymous')} - Path: {request.path}")
            
            # Handle specific integrity errors
            error_message = str(exception).lower()
            if 'duplicate entry' in error_message:
                if 'user_profiles.user_id' in error_message:
                    messages.error(request, "User profile already exists. Please contact support if this persists.")
                elif 'username' in error_message:
                    messages.error(request, "This username is already taken. Please choose a different one.")
                elif 'email' in error_message:
                    messages.error(request, "This email address is already registered. Please use a different email.")
                else:
                    messages.error(request, "This information is already in use. Please check your input and try again.")
            else:
                messages.error(request, "There was an error with your request. Please check your information and try again.")
            
            # Return to the same page or a safe fallback
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META['HTTP_REFERER'])
            else:
                return render(request, 'error.html', {
                    'error_title': 'Database Error',
                    'error_message': 'There was an issue processing your request. Please try again.'
                }, status=400)

        elif isinstance(exception, (OperationalError, DatabaseError)):
            logger.error(f"DatabaseError: {exception} - User: {getattr(request.user, 'username', 'anonymous')} - Path: {request.path}")
            
            # Check for specific schema mismatches
            error_message = str(exception).lower()
            if 'unknown column' in error_message:
                # Schema mismatch error
                logger.critical(f"Schema mismatch detected: {exception}")
                messages.error(request, "System configuration error. Please contact support.")
            elif 'table' in error_message and "doesn't exist" in error_message:
                # Missing table error
                logger.critical(f"Missing table detected: {exception}")
                messages.error(request, "System configuration error. Please contact support.")
            else:
                messages.error(request, "Database connection issue. Please try again in a moment.")
            
            return render(request, 'error.html', {
                'error_title': 'Database Connection Error',
                'error_message': 'We are experiencing technical difficulties. Please try again later or contact support if the problem persists.'
            }, status=500)

        elif isinstance(exception, ValidationError):
            # ValidationError from forms - let Django handle normally
            logger.warning(f"ValidationError: {exception} - User: {getattr(request.user, 'username', 'anonymous')} - Path: {request.path}")
            return None

        # Return None to let Django handle other exceptions normally
        return None


class UserProfileMiddleware(MiddlewareMixin):
    """Middleware to ensure user profile exists for authenticated users"""

    def process_request(self, request):
        """Ensure authenticated users have required profile objects"""
        if request.user.is_authenticated:
            try:
                # Check if user has a profile
                if not hasattr(request.user, 'profile'):
                    logger.warning(f"User {request.user.username} missing profile, creating...")
                    from .models import UserProfile, Role
                    default_role, _ = Role.objects.get_or_create(
                        name='User',
                        defaults={'description': 'Default user role'}
                    )
                    UserProfile.objects.get_or_create(
                        user=request.user,
                        defaults={'role': default_role}
                    )
                
                # Check if user has notification preferences
                if not hasattr(request.user, 'notification_preferences'):
                    logger.warning(f"User {request.user.username} missing notification preferences, creating...")
                    from .models import NotificationPreferences
                    NotificationPreferences.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'email_enabled': True,
                            'submission_notifications': True,
                            'approval_notifications': True,
                            'rejection_notifications': True,
                            'revision_notifications': True
                        }
                    )
                    
            except (IntegrityError, DatabaseError) as e:
                logger.error(f"Error ensuring user profile for {request.user.username}: {e}")
                # Continue processing - the DatabaseErrorMiddleware will handle any subsequent errors
            except Exception as e:
                logger.error(f"Unexpected error ensuring user profile for {request.user.username}: {e}")

        return None