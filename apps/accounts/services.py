"""
Business logic services for user account management
"""
import logging
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone

from .models import UserProfile, UserSession, AuditLog
from .utils import get_client_ip, send_account_setup_email

logger = logging.getLogger('accounts')


class UserAccountService:
    """Service for user account management operations"""
    
    @staticmethod
    def create_user_with_profile(user_data: Dict[str, Any], 
                               profile_data: Dict[str, Any],
                               created_by: User) -> Optional[User]:
        """Create a new user with profile and send setup email"""
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=user_data.get('is_active', True),
                    is_staff=user_data.get('is_staff', False)
                )
                
                # Update profile
                profile = user.profile
                for key, value in profile_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                profile.save()
                
                # Generate password reset token and send email
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                send_account_setup_email(user, token, uid)
                
                # Log the action
                AuditLog.objects.create(
                    user=user,
                    action='user_created',
                    description=f"User account created by admin: {created_by.username}",
                    performed_by=created_by
                )
                
                logger.info(f"User created: {user.username} by {created_by.username}")
                return user
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    @staticmethod
    def update_user_profile(user: User, profile_data: Dict[str, Any], 
                          updated_by: User) -> bool:
        """Update user profile information"""
        try:
            with transaction.atomic():
                profile = user.profile
                changes = []
                
                for key, value in profile_data.items():
                    if hasattr(profile, key):
                        old_value = getattr(profile, key)
                        if old_value != value:
                            setattr(profile, key, value)
                            changes.append(f"{key}: {old_value} -> {value}")
                
                if changes:
                    profile.save()
                    
                    # Log the changes
                    AuditLog.objects.create(
                        user=user,
                        action='profile_updated',
                        description=f"Profile updated: {', '.join(changes)}",
                        performed_by=updated_by
                    )
                    
                    logger.info(f"Profile updated for {user.username} by {updated_by.username}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to update profile for {user.username}: {e}")
            return False
    
    @staticmethod
    def toggle_user_status(user: User, field: str, admin: User, 
                          request_meta: Optional[Dict] = None) -> bool:
        """Toggle user active or staff status"""
        try:
            if field not in ['is_active', 'is_staff']:
                raise ValueError(f"Invalid field: {field}")
            
            if user == admin:
                raise ValueError("Cannot modify own status")
            
            with transaction.atomic():
                old_value = getattr(user, field)
                new_value = not old_value
                setattr(user, field, new_value)
                user.save(update_fields=[field])
                
                # Log the action
                action_name = f"user_{'activated' if new_value else 'deactivated'}" if field == 'is_active' else f"staff_{'granted' if new_value else 'revoked'}"
                
                AuditLog.objects.create(
                    user=user,
                    action=action_name,
                    description=f"{field} changed from {old_value} to {new_value}",
                    performed_by=admin,
                    ip_address=request_meta.get('ip_address') if request_meta else None
                )
                
                logger.info(f"User {user.username} {field} changed to {new_value} by {admin.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to toggle {field} for {user.username}: {e}")
            return False


class UserSessionService:
    """Service for user session management"""
    
    @staticmethod
    def create_session(user: User, session_key: str, request_meta: Dict) -> UserSession:
        """Create or update user session"""
        session, created = UserSession.objects.get_or_create(
            user=user,
            session_key=session_key,
            defaults={
                'ip_address': request_meta.get('ip_address'),
                'user_agent': request_meta.get('user_agent', '')
            }
        )
        
        if not created:
            session.last_activity = timezone.now()
            session.is_active = True
            session.save()
        
        # Log login
        AuditLog.objects.create(
            user=user,
            action='user_login',
            description=f"User logged in from {request_meta.get('ip_address')}",
            performed_by=user,
            ip_address=request_meta.get('ip_address')
        )
        
        logger.info(f"User session created: {user.username} from {request_meta.get('ip_address')}")
        return session
    
    @staticmethod
    def end_session(user: User, session_key: str) -> bool:
        """End user session"""
        try:
            session = UserSession.objects.get(
                user=user,
                session_key=session_key,
                is_active=True
            )
            session.is_active = False
            session.logout_time = timezone.now()
            session.save()
            
            # Log logout
            AuditLog.objects.create(
                user=user,
                action='user_logout',
                description="User logged out",
                performed_by=user
            )
            
            logger.info(f"User session ended: {user.username}")
            return True
            
        except UserSession.DoesNotExist:
            return False
    
    @staticmethod
    def cleanup_old_sessions(days: int = 30) -> int:
        """Clean up old inactive sessions"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        updated_count = UserSession.objects.filter(
            last_activity__lt=cutoff_date,
            is_active=True
        ).update(
            is_active=False,
            logout_time=timezone.now()
        )
        
        logger.info(f"Cleaned up {updated_count} old sessions")
        return updated_count
    
    @staticmethod
    def get_active_sessions(user: User) -> List[UserSession]:
        """Get all active sessions for a user"""
        return UserSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-last_activity')


class UserStatsService:
    """Service for user statistics and analytics"""
    
    @staticmethod
    def get_comprehensive_user_stats(user: User) -> Dict[str, Any]:
        """Get comprehensive statistics for a user"""
        stats = {}
        
        # Basic profile info
        profile = getattr(user, 'profile', None)
        if profile:
            fields = ['department', 'job_title', 'phone_number', 'employee_id', 'location', 'bio']
            filled_fields = sum(1 for field in fields if getattr(profile, field))
            stats['profile_completeness'] = (filled_fields / len(fields)) * 100
        else:
            stats['profile_completeness'] = 0
        
        # Session statistics
        stats['sessions'] = {
            'total_sessions': UserSession.objects.filter(user=user).count(),
            'active_sessions': UserSession.objects.filter(user=user, is_active=True).count(),
            'last_login': user.last_login,
            'recent_sessions': UserSession.objects.filter(user=user).order_by('-created_at')[:5]
        }
        
        # Project statistics (if available)
        try:
            stats['projects'] = {
                'total': user.submitted_projects.count(),
                'draft': user.submitted_projects.filter(status='Draft').count(),
                'pending': user.submitted_projects.filter(status='Pending_Approval').count(),
                'approved': user.submitted_projects.filter(status='Approved').count(),
                'rejected': user.submitted_projects.filter(status='Rejected').count(),
            }
        except AttributeError:
            stats['projects'] = {
                'total': 0, 'draft': 0, 'pending': 0, 'approved': 0, 'rejected': 0
            }
        
        # Activity statistics
        stats['activity'] = {
            'total_actions': AuditLog.objects.filter(user=user).count(),
            'recent_actions': AuditLog.objects.filter(user=user).order_by('-created_at')[:10]
        }
        
        return stats
    
    @staticmethod
    def get_department_statistics() -> List[Dict[str, Any]]:
        """Get user statistics by department"""
        from django.db.models import Count
        
        return list(UserProfile.objects.values('department').annotate(
            user_count=Count('user')
        ).order_by('-user_count'))
    
    @staticmethod
    def get_system_user_stats() -> Dict[str, Any]:
        """Get system-wide user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        # Recent activity
        recent_logins = AuditLog.objects.filter(
            action='user_login',
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'staff_users': staff_users,
            'recent_logins_week': recent_logins,
            'active_sessions': UserSession.objects.filter(is_active=True).count()
        }