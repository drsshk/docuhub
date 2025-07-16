from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
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
        
        # Check if user has project manager permission
        return (
            request.user.has_perm('projects.can_review_projects') or
            request.user.groups.filter(name='Project Managers').exists() or
            request.user.is_staff
        )


class ProjectOwnerPermission(BasePermission):
    """
    Permission that allows project owners to edit their own projects.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if user is the project owner or has admin permissions
        if hasattr(obj, 'submitted_by'):
            return (
                obj.submitted_by == request.user or
                request.user.has_perm('projects.can_manage_all_projects') or
                request.user.groups.filter(name='Project Managers').exists()
            )
        elif hasattr(obj, 'project'):
            # For drawings, check the parent project
            return (
                obj.project.submitted_by == request.user or
                request.user.has_perm('projects.can_manage_all_projects') or
                request.user.groups.filter(name='Project Managers').exists()
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
        editable_statuses = ['Draft', 'Conditional_Approval']
        
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
        versionable_statuses = ['Request_for_Revision', 'Approved_Endorsed', 'Rescinded_Revoked']
        
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
            
        return (
            user.has_perm('projects.can_review_projects') or
            user.groups.filter(name='Project Managers').exists() or
            user.is_superuser
        )


class IsProjectAdministrator:
    @staticmethod
    def has_permission(user: User) -> bool:
        """Check if user is a project administrator with full permissions"""
        if not user or not user.is_authenticated:
            return False
            
        return (
            user.has_perm('projects.can_manage_all_projects') or
            user.groups.filter(name='Project Administrators').exists() or
            user.is_superuser
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


def setup_project_permissions():
    """
    Set up custom permissions and groups for the project management system.
    This should be run as a data migration or management command.
    """
    # Get content types
    project_ct = ContentType.objects.get_for_model(Project)
    drawing_ct = ContentType.objects.get_for_model(Drawing)
    
    # Create custom permissions
    permissions = [
        ('can_review_projects', 'Can review and approve projects'),
        ('can_manage_all_projects', 'Can manage all projects'),
        ('can_bulk_operations', 'Can perform bulk operations on projects'),
        ('can_restore_projects', 'Can restore obsoleted projects'),
        ('view_approved_projects', 'Can view all approved projects'),
        ('can_manage_drawings', 'Can manage all drawings'),
    ]
    
    created_permissions = []
    for codename, name in permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=project_ct,
            defaults={'name': name}
        )
        if created:
            created_permissions.append(permission)
    
    # Create user groups
    groups_permissions = {
        'Project Users': [
            'projects.add_project',
            'projects.change_project',
            'projects.view_project',
            'projects.add_drawing',
            'projects.change_drawing',
            'projects.view_drawing',
            'projects.view_approved_projects',
        ],
        'Project Managers': [
            'projects.add_project',
            'projects.change_project',
            'projects.view_project',
            'projects.add_drawing',
            'projects.change_drawing',
            'projects.view_drawing',
            'projects.can_review_projects',
            'projects.can_bulk_operations',
            'projects.view_approved_projects',
        ],
        'Project Administrators': [
            'projects.add_project',
            'projects.change_project',
            'projects.delete_project',
            'projects.view_project',
            'projects.add_drawing',
            'projects.change_drawing',
            'projects.delete_drawing',
            'projects.view_drawing',
            'projects.can_review_projects',
            'projects.can_manage_all_projects',
            'projects.can_bulk_operations',
            'projects.can_restore_projects',
            'projects.view_approved_projects',
            'projects.can_manage_drawings',
        ],
    }
    
    created_groups = []
    for group_name, permission_codenames in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            created_groups.append(group)
        
        # Assign permissions to group
        for codename in permission_codenames:
            try:
                app_label, perm_codename = codename.split('.')
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type__app_label=app_label
                )
                group.permissions.add(permission)
            except (ValueError, Permission.DoesNotExist):
                # Skip invalid permissions
                pass
    
    return created_permissions, created_groups