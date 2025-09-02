from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import Project, Drawing
from .serializers import ProjectSerializer, DrawingSerializer
from .permissions import (
    CanEditProject, ProjectManagerPermission, ProjectOwnerPermission,
    ProjectUserRateThrottle, ProjectAdminRateThrottle, IsProjectManager
)
from .services import ProjectSubmissionService
from apps.accounts.utils import get_client_ip

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ProjectOwnerPermission]
    throttle_classes = [ProjectUserRateThrottle]
    
    def get_queryset(self):
        # Use proper permission checking instead of is_staff
        if IsProjectManager.has_permission(self.request.user):
            return Project.objects.all().select_related('submitted_by', 'reviewed_by')
        return Project.objects.filter(submitted_by=self.request.user).select_related('submitted_by', 'reviewed_by')
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)
    
    def get_throttles(self):
        """Use admin throttle for privileged users"""
        if IsProjectManager.has_permission(self.request.user):
            self.throttle_classes = [ProjectAdminRateThrottle]
        return super().get_throttles()

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class DrawingViewSet(viewsets.ModelViewSet):
    serializer_class = DrawingSerializer
    permission_classes = [IsAuthenticated, ProjectOwnerPermission]
    throttle_classes = [ProjectUserRateThrottle]
    
    def get_queryset(self):
        # Use proper permission checking instead of is_staff
        if IsProjectManager.has_permission(self.request.user):
            return Drawing.objects.all().select_related('project', 'added_by')
        return Drawing.objects.filter(
            project__submitted_by=self.request.user
        ).select_related('project', 'added_by')
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
    
    def get_throttles(self):
        """Use admin throttle for privileged users"""
        if IsProjectManager.has_permission(self.request.user):
            self.throttle_classes = [ProjectAdminRateThrottle]
        return super().get_throttles()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ProjectUserRateThrottle])
@csrf_protect
@never_cache
def submit_project_api(request, pk):
    """Submit project for approval via API"""
    project = get_object_or_404(Project, pk=pk)
    
    if project.submitted_by != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if project.status not in ['Draft', 'Revise_and_Resubmit']:
        return Response({'error': 'Only draft or revision projects can be submitted'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not project.drawings.filter(status='Active').exists():
        return Response({'error': 'Project must have at least one drawing'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Use service for proper submission handling
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    if submission_service.submit_for_approval(project, request.user, request_meta):
        return Response({'message': 'Project submitted successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Failed to submit project'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated, ProjectManagerPermission])
@throttle_classes([ProjectAdminRateThrottle])
@csrf_protect
@never_cache
def review_project_api(request, pk):
    """Review project via API (project managers and admins only)"""
    # Use proper permission checking
    if not IsProjectManager.has_permission(request.user):
        return Response({'error': 'Project manager access required'}, status=status.HTTP_403_FORBIDDEN)
    
    project = get_object_or_404(Project, pk=pk)
    
    if project.status != 'Pending_Approval':
        return Response({'error': 'Only pending projects can be reviewed'}, status=status.HTTP_400_BAD_REQUEST)
    
    action = request.data.get('action')
    comments = request.data.get('comments', '')
    
    if action not in ['approve', 'reject', 'revise']:
        return Response({'error': 'Invalid action. Must be approve, reject, or revise'}, status=status.HTTP_400_BAD_REQUEST)
    
    if action in ['reject', 'revise'] and not comments:
        return Response({'error': 'Comments required for rejection or revision requests'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Use service for proper review handling
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    success = False
    if action == 'approve':
        success = submission_service.approve_project(project, request.user, comments, request_meta)
    elif action == 'reject':
        success = submission_service.reject_project(project, request.user, comments, request_meta)
    elif action == 'revise':
        success = submission_service.request_revision(project, request.user, comments, request_meta)
    
    if success:
        return Response({'message': f'Project {action}d successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': f'Failed to {action} project'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)