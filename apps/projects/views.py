import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from django.db import transaction

from .models import Project, Drawing, ApprovalHistory, ProjectHistory
from .forms import ProjectForm, DrawingForm, ReviewForm, BulkActionForm, ProjectRestoreForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
# from django_ratelimit.decorators import ratelimit  # Temporarily disabled until package is installed
from .permissions import (
    CanEditProject, CanCreateNewVersion, IsProjectManager, 
    IsProjectAdministrator, CanViewProject
)
from .services import (
    ProjectStatsService, ProjectSubmissionService, ProjectVersionService,
    ProjectBulkOperationsService, ProjectRestoreService
)
from apps.accounts.views import is_admin_role_user
from apps.accounts.utils import get_client_ip

@login_required
def dashboard(request):
    """User dashboard showing project summary"""
    # Use service for user project stats
    stats = ProjectStatsService.get_user_project_stats(request.user)
    
    # Get admin stats if user is project manager
    admin_stats = {}
    is_admin = IsProjectManager.has_permission(request.user)
    if is_admin:
        admin_stats = ProjectStatsService.get_admin_dashboard_stats()
    
    context = {
        'stats': stats,
        'recent_projects': stats['recent_projects'],
        'admin_stats': admin_stats,
        'is_admin': is_admin,
    }
    
    return render(request, 'projects/dashboard.html', context)

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Filter projects based on user permissions:
        - Approver can see all except draft
        - Submitter can view his own projects (any status) and all approved projects
        """
        user = self.request.user
        
        if IsProjectManager.has_permission(user):
            # Approvers can see all projects except Draft status
            base_queryset = Project.objects.exclude(status='Draft')
        else:
            # Submitters can see:
            # 1. Their own projects (any status)
            # 2. All approved projects from anyone
            base_queryset = Project.objects.filter(
                Q(submitted_by=user) | Q(status='Approved')
            ).distinct()
        
        status = self.request.GET.get('status')
        if status:
            base_queryset = base_queryset.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            base_queryset = base_queryset.filter(
                Q(project_name__icontains=search)
            )

        latest_versions_pks = base_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)

        return Project.objects.filter(pk__in=latest_versions_pks).select_related(
            'submitted_by', 'reviewed_by'
        ).prefetch_related('drawings').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = IsProjectManager.has_permission(self.request.user)
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        print(f"DEBUG: ProjectDetailView received PK: {pk}")
        obj = get_object_or_404(
            Project.objects.select_related('submitted_by', 'reviewed_by'),
            pk=pk
        )
        print(f"DEBUG: ProjectDetailView found object: {obj.pk}")
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Use proper permission checking
        if not CanViewProject.has_permission(self.request.user, self.object):
            return HttpResponseForbidden("You do not have permission to view this project.")
             
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_admin = IsProjectManager.has_permission(self.request.user)
        context['can_edit'] = CanEditProject.has_permission(self.request.user, self.object)
        context['can_create_new_version'] = CanCreateNewVersion.has_permission(self.request.user, self.object)
        context['can_review'] = is_admin and (self.object.status == 'Pending_Approval')
        context['drawings'] = self.object.drawings.filter(status='Active').select_related('added_by')

        # Get all project versions for the version history sidebar
        # Only get versions that belong to the same project group
        context['project_versions'] = Project.objects.filter(
            project_group_id=self.object.project_group_id,
            project_name=self.object.project_name,
            submitted_by=self.object.submitted_by
        ).select_related('submitted_by', 'reviewed_by').order_by('-version')
        
        # Get the complete activity log for ALL versions of this specific project group
        context['full_activity_log'] = ApprovalHistory.objects.filter(
            project__project_group_id=self.object.project_group_id,
            project__project_name=self.object.project_name,
            project__submitted_by=self.object.submitted_by
        ).select_related('performed_by', 'project').order_by('-performed_at')
        
        # Get the detailed project history log
        context['project_history_logs'] = ProjectStatsService.get_project_history_log(self.object)
        
        # Log project access for audit trail
        if self.request.user.is_staff:
            import logging
            logger = logging.getLogger('projects')
            logger.info(
                f"Project detail accessed by admin {self.request.user.username}: "
                f"Project {self.object.project_name} (Group: {self.object.project_group_id}), "
                f"Found {context['project_versions'].count()} versions"
            )
        
        return context

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
# @method_decorator(ratelimit(key='user', rate='5/h', method='POST', block=True), name='dispatch')  # Temporarily disabled
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    @transaction.atomic
    def form_valid(self, form):
        project_name = form.cleaned_data.get('project_name')
        
        # Check for duplicate project names by the same user (excluding obsolete ones)
        if Project.objects.filter(
            submitted_by=self.request.user,
            project_name__iexact=project_name
        ).exclude(status='Obsolete').exists():
            form.add_error('project_name', 'You already have an active project with this name. Please choose a different name.')
            return self.form_invalid(form)

        form.instance.submitted_by = self.request.user
        form.instance.status = 'Draft'
        form.instance.version = 1
        # Each new project gets a unique project_group_id
        form.instance.project_group_id = uuid.uuid4()
        response = super().form_valid(form)
        
        ApprovalHistory.objects.create(
            project=form.instance,
            version=form.instance.version,
            action='Created',
            performed_by=self.request.user,
            comments=f"Project created as V{form.instance.version:03d}."
        )
        
        messages.success(self.request, f'Project "{form.instance.project_name}" created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def test_func(self):
        project = self.get_object()
        # Only submitters can edit their own projects
        # Check if user can edit or create new version of this project
        can_edit = CanEditProject.has_permission(self.request.user, project)
        can_create_version = CanCreateNewVersion.has_permission(self.request.user, project)
        
        return can_edit or can_create_version

    def get_object(self, queryset=None):
        return get_object_or_404(Project, pk=self.kwargs['pk'])

    @transaction.atomic
    def form_valid(self, form):
        messages.success(self.request, f'Project "{self.get_object().project_name}" updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.object.pk})

@login_required
@csrf_protect
@never_cache
# # @ratelimit(key='user', rate='10/m', method='POST', block=True)  # Temporarily disabled  # Temporarily disabled
def submit_project(request, pk):
    """Submit project for approval"""
    project = get_object_or_404(Project, pk=pk)
    
    if project.submitted_by != request.user:
        return HttpResponseForbidden("You don't have permission to submit this project.")
    
    if project.status not in ['Draft', 'Revise_and_Resubmit']:
        messages.error(request, 'Only drafts or projects needing revision can be submitted.')
        return redirect('projects:detail', pk=pk)
    
    if not project.drawings.filter(status='Active').exists():
        messages.error(request, 'Project must have at least one drawing before submission.')
        return redirect('projects:detail', pk=pk)
    
    # Use service for submission
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    if submission_service.submit_for_approval(project, request.user, request_meta):
        messages.success(request, 'Project submitted for approval successfully!')
    else:
        messages.error(request, 'Failed to submit project. Please try again.')
    
    return redirect('projects:detail', pk=pk)

def is_admin_check(user):
    """Helper function for user_passes_test decorator"""
    return IsProjectManager.has_permission(user)

@user_passes_test(is_admin_check)
@csrf_protect
@never_cache
# @ratelimit(key='user', rate='20/m', method='POST', block=True)  # Temporarily disabled
def review_project(request, pk):
    """Admin review project"""
    project = get_object_or_404(Project, pk=pk)
    drawings = project.drawings.filter(status='Active').order_by('sort_order', 'drawing_no')
    
    if project.status != 'Pending_Approval':
        messages.error(request, 'Only pending projects can be reviewed.')
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            comments = form.cleaned_data.get('comments', '')
            
            # Use service for review actions
            submission_service = ProjectSubmissionService()
            request_meta = {
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
            
            success = False
            if action == 'approve':
                success = submission_service.approve_project(project, request.user, comments, request_meta)
                if success:
                    messages.success(request, 'Project approved successfully!')
            elif action == 'reject':
                success = submission_service.reject_project(project, request.user, comments, request_meta)
                if success:
                    messages.warning(request, 'Project rejected.')
            else:  # revise
                success = submission_service.request_revision(project, request.user, comments, request_meta)
                if success:
                    messages.warning(request, 'Project sent back for revision.')
            
            if not success:
                messages.error(request, 'Failed to process review. Please try again.')
            
            return redirect('projects:detail', pk=pk)
    else:
        form = ReviewForm()
    
    context = {'project': project, 'form': form, 'drawings': drawings}
    return render(request, 'projects/project_review.html', context)

@login_required
def add_drawing(request, project_pk):
    """Add drawing to project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not CanEditProject.has_permission(request.user, project):
        messages.error(request, "Drawings can only be added to 'Draft' or 'Revise and Resubmit' projects.")
        return HttpResponseForbidden("You don't have permission to add drawings to this project at its current state.")
    
    if request.method == 'POST':
        form = DrawingForm(request.POST)
        if form.is_valid():
            drawing = form.save(commit=False)
            drawing.project = project
            drawing.added_by = request.user
            
            if Drawing.objects.filter(project=project, drawing_no=drawing.drawing_no).exists():
                messages.error(request, f'Drawing number {drawing.drawing_no} already exists in this project version.')
                return render(request, 'projects/drawing_form.html', {'form': form, 'project': project})
            
            drawing.save()
            
            if request.headers.get('HX-Request'):
                # For an HTMX request, we return a response that uses an "Out of Band" (OOB)
                # swap to update the drawing list on the main page, and also includes
                # a script to close the modal and provide user feedback.

                # 1. Prepare the updated drawing list HTML.
                drawings = project.drawings.filter(status='Active').order_by('sort_order', 'drawing_no')
                can_edit = CanEditProject.has_permission(request.user, project)
                list_html = render_to_string(
                    'projects/partials/drawing_list.html',
                    {'drawings': drawings, 'project': project, 'can_edit': can_edit},
                    request=request
                )
                
                # 2. Wrap the list HTML for the OOB swap. This targets the #drawing-list div.
                oob_list_html = f'<div id="drawing-list" hx-swap-oob="true">{list_html}</div>'

                # 3. Create a script to close the modal and show a confirmation message.
                # This becomes the main part of the response, which replaces the form in the modal.
                feedback_script = (
                    '<script>'
                    f" alert('Drawing {drawing.drawing_no} added successfully!');"
                    " const modal = document.getElementById('modal');"
                    " if (modal) { modal.style.display = 'none'; }"
                    " const modalContent = document.getElementById('modal-content');"
                    " if (modalContent) { modalContent.innerHTML = ''; }"
                    '</script>'
                )

                # 4. Combine and return the full response.
                return HttpResponse(oob_list_html + feedback_script)
            
            # Fallback for non-HTMX submissions
            messages.success(request, f'Drawing {drawing.drawing_no} added successfully!')
            return redirect('projects:detail', pk=project_pk)
    else:
        form = DrawingForm()
    
    return render(request, 'projects/drawing_form.html', {'form': form, 'project': project})

@user_passes_test(is_admin_check)
@never_cache
def admin_pending_projects(request):
    """Admin view for pending projects"""
    pending_projects = Project.objects.filter(status='Pending_Approval').select_related(
        'submitted_by'
    ).prefetch_related('drawings').order_by('date_submitted')
    
    paginator = Paginator(pending_projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'total_pending': pending_projects.count(),
        'bulk_form': BulkActionForm(),
    }
    
    return render(request, 'projects/admin_pending.html', context)

@user_passes_test(is_admin_check)
@csrf_protect
@never_cache
# @ratelimit(key='user', rate='5/m', method='POST', block=True)  # Temporarily disabled
def bulk_action_projects(request):
    """Handle bulk actions on projects"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('projects:admin_pending')
    
    form = BulkActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid form data.')
        return redirect('projects:admin_pending')
    
    action = form.cleaned_data['action']
    comments = form.cleaned_data['comments']
    project_ids = form.cleaned_data['project_ids']
    
    bulk_service = ProjectBulkOperationsService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    results = None
    if action == 'approve':
        results = bulk_service.bulk_approve_projects(project_ids, request.user, comments, request_meta)
    elif action == 'reject':
        results = bulk_service.bulk_reject_projects(project_ids, request.user, comments, request_meta)
    elif action == 'revise':
        results = bulk_service.bulk_request_revision(project_ids, request.user, comments, request_meta)
    
    if results:
        if results['success']:
            messages.success(request, f"Successfully processed {len(results['success'])} projects: {', '.join(results['success'])}")
        if results['errors']:
            messages.error(request, f"Errors occurred: {'; '.join(results['errors'])}")
    else:
        messages.error(request, 'Failed to process bulk action.')
    
    return redirect('projects:admin_pending')

@user_passes_test(is_admin_check)
@csrf_protect
@never_cache
# @ratelimit(key='user', rate='10/m', method='POST', block=True)  # Temporarily disabled
def restore_project(request, pk):
    """Restore an obsoleted project"""
    project = get_object_or_404(Project, pk=pk)
    
    if project.status != 'Obsolete':
        messages.error(request, 'Only obsolete projects can be restored.')
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectRestoreForm(request.POST)
        if form.is_valid():
            restore_to_status = form.cleaned_data['restore_to_status']
            restore_comments = form.cleaned_data['restore_comments']
            
            restore_service = ProjectRestoreService()
            request_meta = {
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
            
            if restore_service.restore_project(project, request.user, restore_to_status, restore_comments, request_meta):
                messages.success(request, f'Project "{project.project_name}" restored to {restore_to_status} status.')
            else:
                messages.error(request, 'Failed to restore project. Please try again.')
            
            return redirect('projects:detail', pk=pk)
    else:
        form = ProjectRestoreForm()
    
    context = {
        'project': project,
        'form': form
    }
    return render(request, 'projects/project_restore.html', context)

@login_required
@csrf_protect
@never_cache
# @ratelimit(key='user', rate='10/m', method='POST', block=True)  # Temporarily disabled
def recover_draft(request, pk):
    """Recover a deleted draft project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Only allow recovery if user is the owner or admin
    if not (project.submitted_by == request.user or IsProjectManager.has_permission(request.user)):
        return HttpResponseForbidden("You don't have permission to recover this project.")
    
    # Only allow recovery of drafts that were recently "deleted" (status changed)
    if project.status not in ['Rejected', 'Obsolete']:
        messages.error(request, 'Only rejected or obsolete projects can be recovered as drafts.')
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                old_status = project.status
                project.status = 'Draft'
                project.reviewed_by = None
                project.date_reviewed = None
                project.review_comments = ""
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Status_Changed',
                    performed_by=request.user,
                    comments=f"Project recovered as draft from {old_status} status.",
                    previous_status=old_status,
                    new_status='Draft',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'Project "{project.project_name}" recovered as draft.')
                
        except Exception as e:
            messages.error(request, f'Failed to recover project: {str(e)}')
        
        return redirect('projects:detail', pk=pk)
    
    context = {'project': project}
    return render(request, 'projects/project_recover.html', context)

@login_required
def create_new_version(request, pk):
    """Create a new version of an existing project"""
    original_project = get_object_or_404(Project, pk=pk)
    
    if not CanCreateNewVersion.has_permission(request.user, original_project):
        messages.error(request, "You don't have permission to create a new version of this project.")
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        # The form is not used to update the original_project, but to pass the revision_notes
        form = ProjectForm(request.POST)
        if form.is_valid():
            revision_notes = form.cleaned_data.get('revision_notes', '')
            version_service = ProjectVersionService()
            new_project = version_service.create_new_version(original_project, request.user, revision_notes)
            
            if new_project:
                messages.success(request, f'New version (V{new_project.version:03d}) created successfully.')
                return redirect('projects:detail', pk=new_project.pk)
            else:
                messages.error(request, 'Failed to create a new version.')
                return redirect('projects:detail', pk=pk)
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'project': original_project
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def history_log(request):
    """History log view: Users see their own, approvers/viewers see all."""
    if IsProjectManager.has_permission(request.user):
        history = ProjectHistory.objects.all().order_by('-date_submitted')
    else:
        history = ProjectHistory.objects.filter(submitted_by=request.user).order_by('-date_submitted')
    
    return render(request, 'projects/history_log.html', {'history': history})