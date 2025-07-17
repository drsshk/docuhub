from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import Project, Drawing


class ProjectUserRateThrottle(UserRateThrottle):
    """Rate throttling for authenticated users on project operations"""
    scope = 'project_user'


class ProjectAnonRateThrottle(AnonRateThrottle):
    """Rate throttling for anonymous users"""
    scope = 'project_anon'


class ProjectAdminRateThrottle(UserRateThrottle):
    """Rate throttling for admin operations"""
    scope = 'project_admin'


class ProjectManagerPermission(BasePermission):
    """
    Custom permission for project managers.
    Project managers can review and approve projects.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has approver or admin role
        user_role = getattr(request.user.profile, 'role', None) if hasattr(request.user, 'profile') else None
        return (
            request.user.is_staff or
            request.user.is_superuser or
            (user_role and user_role.name in ['Admin', 'Approver'])
        )


class ProjectOwnerPermission(BasePermission):
    """
    Permission that allows project owners to edit their own projects.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if user is the project owner or has admin permissions
        user_role = getattr(request.user.profile, 'role', None) if hasattr(request.user, 'profile') else None
        is_admin_or_approver = user_role and user_role.name in ['Admin', 'Approver']
        
        if hasattr(obj, 'submitted_by'):
            return (
                obj.submitted_by == request.user or
                request.user.is_staff or
                request.user.is_superuser or
                is_admin_or_approver
            )
        elif hasattr(obj, 'project'):
            # For drawings, check the parent project
            return (
                obj.project.submitted_by == request.user or
                request.user.is_staff or
                request.user.is_superuser or
                is_admin_or_approver
            )
        
        return False


class CanEditProject:
    @staticmethod
    def has_permission(user, project):
        """
        Permission check for project editing based on requirements:
        - Admins can edit any project.
        - Submitters can edit their own projects in certain statuses.
        """
        if not user or not project:
            return False

        # Admins can always edit
        if IsProjectAdministrator.has_permission(user):
            return True
            
        # Define which statuses are editable for non-admins
        # Conditional_Approval should not be directly editable - users must create new version
        editable_statuses = ['Draft']
        
        is_owner = (project.submitted_by == user)
        is_editable_status = (project.status in editable_statuses)
        
        # Check if this is the latest version
        is_latest_version = project.is_latest_version()
        
        # Only the project owner can edit their own projects (latest version only)
        return is_owner and is_editable_status and is_latest_version


class CanCreateNewVersion:
    @staticmethod
    def has_permission(user, project):
        """
        Permission check for creating new project versions based on requirements:
        - Only submitters can create new versions of their own projects
        """
        if not user or not project:
            return False
            
        # Define which statuses allow creating new versions
        versionable_statuses = ['Request_for_Revision', 'Approved_Endorsed', 'Rescinded_Revoked', 'Conditional_Approval']
        
        is_owner = (project.submitted_by == user)
        is_versionable_status = (project.status in versionable_statuses)
        
        # Check if this is the latest version
        is_latest_version = project.is_latest_version()
        
        # Only the project owner can create new versions of their own projects
        # Removed admin override to enforce "submitter can only edit own projects" rule
        return is_latest_version and is_versionable_status and is_owner


class IsProjectManager:
    @staticmethod
    def has_permission(user: User) -> bool:
        """Check if user is a project manager with proper permissions"""
        if not user or not user.is_authenticated:
            return False
        
        user_role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None
        return (
            user.is_superuser or
            user.is_staff or
            (user_role and user_role.name in ['Admin', 'Approver'])
        )


class IsProjectAdministrator:
    @staticmethod
    def has_permission(user: User) -> bool:
        """Check if user is a project administrator with full permissions"""
        if not user or not user.is_authenticated:
            return False
        
        user_role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None
        return (
            user.is_superuser or
            user.is_staff or
            (user_role and user_role.name == 'Admin')
        )


class CanViewProject:
    @staticmethod
    def has_permission(user: User, project: Project) -> bool:
        """
        Enhanced permission check for viewing projects based on requirements:
        - Approver can see all except draft
        - Submitter can view his own projects (any status) and all approved projects
        """
        if not user or not user.is_authenticated:
            return False
            
        # Superusers can view everything
        if user.is_superuser:
            return True
            
        # Check if user is an approver (Project Manager)
        is_approver = IsProjectManager.has_permission(user)
        
        if is_approver:
            # Approvers can see all projects except Draft status
            return project.status != 'Draft'
        
        # For regular users (submitters)
        is_owner = project.submitted_by == user
        
        if is_owner:
            # Submitters can view their own projects (any status)
            return True
        
        # Submitters can view ALL approved projects (not just their own)
        if project.status == 'Approved_Endorsed':
            return True
            
        return False


def setup_project_roles():
    """
    Set up roles for the project management system.
    This should be run as a data migration or management command.
    """
    from apps.accounts.models import Role
    
    # Create roles if they don't exist
    roles = [
        ('Admin', 'Full system administrator with all permissions'),
        ('Approver', 'Can review and approve projects'),
        ('Submitter', 'Can submit and manage own projects'),
        ('Viewer', 'Can view approved projects only'),
    ]
    
    created_roles = []
    for name, description in roles:
        role, created = Role.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        if created:
            created_roles.append(role)
    
    return created_roles