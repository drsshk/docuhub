"""
Custom middleware for security enhancements and rate limiting.
"""
import logging
from django.http import HttpResponseTooManyRequests, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import hashlib

logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # HSTS header (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Custom rate limiting middleware for form submissions and sensitive operations.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return None
        
        # Define rate limits for different endpoints
        rate_limits = {
            # Authentication endpoints
            '/accounts/login/': {'limit': 5, 'window': 300},  # 5 attempts per 5 minutes
            '/accounts/register/': {'limit': 3, 'window': 3600},  # 3 attempts per hour
            
            # Project submission endpoints
            '/projects/': {'limit': 100, 'window': 3600},  # 100 requests per hour
            '/api/projects/': {'limit': 200, 'window': 3600},  # 200 API requests per hour
            
            # Admin endpoints
            '/admin/': {'limit': 1000, 'window': 3600},  # 1000 requests per hour for admin
            
            # Bulk operations (more restrictive)
            '/projects/admin/bulk-action/': {'limit': 10, 'window': 600},  # 10 bulk operations per 10 minutes
        }
        
        # Check if this path should be rate limited
        path = request.path
        rate_config = None
        
        for pattern, config in rate_limits.items():
            if path.startswith(pattern):
                rate_config = config
                break
        
        if not rate_config:
            return None
        
        # Create unique key for user/IP combination
        if request.user.is_authenticated:
            key_base = f"rate_limit:{request.user.id}:{path}"
        else:
            ip = self.get_client_ip(request)
            key_base = f"rate_limit:ip:{ip}:{path}"
        
        # Hash the key to ensure consistent length
        key = hashlib.md5(key_base.encode()).hexdigest()
        
        # Check current count
        current_count = cache.get(key, 0)
        
        if current_count >= rate_config['limit']:
            logger.warning(
                f"Rate limit exceeded for {key_base}. "
                f"Count: {current_count}, Limit: {rate_config['limit']}"
            )
            
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f"Too many requests. Limit: {rate_config['limit']} per {rate_config['window']} seconds."
                }, status=429)
            else:
                return HttpResponseTooManyRequests(
                    "Too many requests. Please try again later."
                )
        
        # Increment counter
        cache.set(key, current_count + 1, rate_config['window'])
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant events and suspicious activities.
    """
    
    def process_request(self, request):
        # Log potentially suspicious requests
        suspicious_patterns = [
            'admin',
            'wp-admin',
            'phpmyadmin',
            '.php',
            '../',
            'eval(',
            'script>',
            'SELECT',
            'UNION',
            'DROP',
        ]
        
        path = request.path.lower()
        query = request.GET.urlencode().lower()
        
        for pattern in suspicious_patterns:
            if pattern in path or pattern in query:
                logger.warning(
                    f"Suspicious request detected: {request.method} {request.path} "
                    f"from {self.get_client_ip(request)} "
                    f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
                )
                break
        
        return None
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if (request.path.startswith('/accounts/login/') and 
            response.status_code in [400, 401, 403]):
            logger.warning(
                f"Failed login attempt from {self.get_client_ip(request)} "
                f"for path {request.path}"
            )
        
        # Log admin access
        if (request.path.startswith('/admin/') and 
            response.status_code == 200 and 
            request.user.is_authenticated):
            logger.info(
                f"Admin access: {request.user.username} accessed {request.path} "
                f"from {self.get_client_ip(request)}"
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFLoggingMiddleware(MiddlewareMixin):
    """
    Log CSRF failures for security monitoring.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # This will be called for each view
        return None
    
    def process_exception(self, request, exception):
        # Log CSRF failures
        if hasattr(exception, '__class__') and 'Csrf' in exception.__class__.__name__:
            logger.warning(
                f"CSRF failure: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"User: {getattr(request.user, 'username', 'Anonymous')} "
                f"Referer: {request.META.get('HTTP_REFERER', 'None')}"
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip