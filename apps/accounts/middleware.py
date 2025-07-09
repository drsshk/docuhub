from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserSession

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