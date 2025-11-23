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

from .models import Project, Document, ProjectGroup, ApprovalHistory, ProjectHistory
from .forms import ProjectForm, DocumentForm, ReviewForm, BulkActionForm, ProjectRestoreForm, HistoryFilterForm
from .permissions import IsProjectManager, CanEditProject
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

from .models import Project, Document, ProjectGroup, ApprovalHistory, ProjectHistory
from .forms import ProjectForm, DocumentForm, ReviewForm, BulkActionForm, ProjectRestoreForm, HistoryFilterForm
from .permissions import IsProjectManager, CanEditProject
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

from .models import Project, Document, ProjectGroup, ApprovalHistory, ProjectHistory
from .forms import ProjectForm, DocumentForm, ReviewForm, BulkActionForm, ProjectRestoreForm, HistoryFilterForm
from .permissions import IsProjectManager, CanEditProject
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
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
from apps.accounts.models import UserProfile # Import UserProfile

def is_admin_or_approver(user):
    """Helper function to check if a user is an Admin or Approver."""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role.name in ['Admin', 'Approver']
    except AttributeError:
        return False

@login_required
@user_passes_test(is_admin_or_approver)
@csrf_protect
@never_cache
def rescind_revoke_project(request, pk):
    """Rescind or revoke an approved project."""
    project = get_object_or_404(Project, pk=pk)

    if project.status != 'Approved_Endorsed':
        messages.error(request, 'Only approved projects can be rescinded or revoked.')
        return redirect('projects:detail', pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                old_status = project.status
                project.status = 'Rescinded_Revoked'
                project.reviewed_by = None
                project.date_reviewed = None
                project.review_comments = ""
                project.save()

                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Rescinded_Revoked',
                    performed_by=request.user,
                    comments="Project status changed to Rescinded & Revoked.",
                    previous_status=old_status,
                    new_status='Rescinded_Revoked',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                messages.success(request, f'Project "{project.project_name}" has been Rescinded & Revoked.')
        except Exception as e:
            messages.error(request, f'Failed to rescind/revoke project: {str(e)}')

        return redirect('projects:detail', pk=pk)
    
    # If not POST, render a confirmation page or redirect
    messages.error(request, 'Invalid request method for this action.')
    return redirect('projects:detail', pk=pk)

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
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        status = self.request.GET.get('status')
        if status:
            base_queryset = base_queryset.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            base_queryset = base_queryset.filter(
                Q(project_name__icontains=search) |
                Q(project_description__icontains=search) |
                Q(submitted_by__first_name__icontains=search) |
                Q(submitted_by__last_name__icontains=search)
            )

        latest_versions_pks = base_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)

        queryset = Project.objects.filter(pk__in=latest_versions_pks).select_related(
            'submitted_by', 'reviewed_by'
        ).prefetch_related('drawings')

        # Apply sorting
        sort = self.request.GET.get('sort')
        if sort:
            if sort in ['-created_at', 'created_at', 'project_name', '-project_name', '-updated_at']:
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by('-updated_at')
        else:
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = IsProjectManager.has_permission(self.request.user)
        
        # Get base queryset for statistics (before pagination)
        user = self.request.user
        if IsProjectManager.has_permission(user):
            stats_queryset = Project.objects.exclude(status='Draft')
        else:
            stats_queryset = Project.objects.filter(
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        # Get latest versions for statistics
        latest_versions_pks = stats_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)
        
        stats_projects = Project.objects.filter(pk__in=latest_versions_pks)
        
        # Calculate statistics
        stats = {
            'draft_projects': stats_projects.filter(status='Draft').count(),
            'pending_projects': stats_projects.filter(status='Pending_Approval').count(),
            'approved_projects': stats_projects.filter(status='Approved_Endorsed').count(),
        }
        context['stats'] = stats
        
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
        
        # If user is viewing their own project, always redirect to the latest version
        if self.object.submitted_by == request.user:
            latest_version = Project.objects.filter(
                project_group_id=self.object.project_group_id,
                project_name=self.object.project_name,
                submitted_by=self.object.submitted_by
            ).order_by('-version').first()
            
            if latest_version and latest_version.pk != self.object.pk:
                return redirect('projects:detail', pk=latest_version.pk)
             
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_admin = IsProjectManager.has_permission(self.request.user)
        context['can_edit'] = CanEditProject.has_permission(self.request.user, self.object)
        context['can_create_new_version'] = CanCreateNewVersion.has_permission(self.request.user, self.object)
        context['can_review'] = is_admin and (self.object.status == 'Pending_Approval')
        context['is_review_page'] = False
        context['drawings'] = self.object.drawings.select_related('added_by')

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
@method_decorator(ratelimit(key='user', rate='5/h', method='POST', block=True), name='dispatch')
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
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def submit_project(request, pk):
    """Submit project for approval"""
    project = get_object_or_404(Project, pk=pk)
    
    if project.submitted_by != request.user:
        return HttpResponseForbidden("You don't have permission to submit this project.")
    
    if project.status not in ['Draft', 'Conditional_Approval']:
        messages.error(request, 'Only drafts or conditionally approved projects can be submitted.')
        return redirect('projects:detail', pk=pk)
    
    if not project.drawings.exists():
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
@ratelimit(key='user', rate='20/m', method='POST', block=True)
def review_project(request, pk):
    """Admin review project"""
    project = get_object_or_404(Project, pk=pk)
    drawings = project.drawings.order_by('sort_order', 'drawing_no')
    
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
    
    is_admin = IsProjectManager.has_permission(request.user)
    context = {
        'project': project,
        'form': form,
        'drawings': drawings,
        'can_review': is_admin and (project.status == 'Pending_Approval'),
        'can_edit': CanEditProject.has_permission(request.user, project),
        'is_review_page': True,
        'project_versions': Project.objects.filter(
            project_group_id=project.project_group_id,
            project_name=project.project_name,
            submitted_by=project.submitted_by
        ).select_related('submitted_by', 'reviewed_by').order_by('-version'),
        'full_activity_log': ApprovalHistory.objects.filter(
            project__project_group_id=project.project_group_id,
            project__project_name=project.project_name,
            project__submitted_by=project.submitted_by
        ).select_related('performed_by', 'project').order_by('-performed_at'),
    }
    return render(request, 'projects/project_review.html', context)

@login_required
def add_drawing(request, project_pk):
    """Add drawing to project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not CanEditProject.has_permission(request.user, project):
        messages.error(request, "Drawings can only be added to 'Draft' or 'Conditional Approval' projects.")
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
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
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

@login_required
def edit_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to edit this drawing.")

    if request.method == 'POST':
        form = DrawingForm(request.POST, instance=drawing)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
                can_edit = CanEditProject.has_permission(request.user, project)
                list_html = render_to_string(
                    'projects/partials/drawing_list.html',
                    {'drawings': drawings, 'project': project, 'can_edit': can_edit},
                    request=request
                )
                oob_list_html = f'<div id="drawing-list" hx-swap-oob="true">{list_html}</div>'
                feedback_script = (
                    '<script>'
                    f" alert('Drawing {drawing.drawing_no} updated successfully!');"
                    " const modal = document.getElementById('modal');"
                    " if (modal) { modal.style.display = 'none'; }"
                    " const modalContent = document.getElementById('modal-content');"
                    " if (modalContent) { modalContent.innerHTML = ''; }"
                    '</script>'
                )
                return HttpResponse(oob_list_html + feedback_script)
            messages.success(request, f'Drawing {drawing.drawing_no} updated successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = DrawingForm(instance=drawing)
    return render(request, 'projects/drawing_form.html', {'form': form, 'project': project, 'drawing': drawing})

@login_required
@csrf_protect
def delete_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to delete this drawing.")

    if request.method == 'POST':
        drawing_no = drawing.drawing_no
        drawing.delete()
        project.no_of_drawings = project.drawings.count()
        project.save()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=200) # HTMX will remove the element
        messages.success(request, f'Drawing {drawing_no} deleted successfully.')
        return redirect('projects:detail', pk=project.pk)
    return HttpResponseForbidden("Invalid request method.")


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
@ratelimit(key='user', rate='5/m', method='POST', block=True)
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
@ratelimit(key='user', rate='10/m', method='POST', block=True)
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
@ratelimit(key='user', rate='10/m', method='POST', block=True)
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
        # Pre-populate form with original project data
        form = ProjectForm(initial={
            'project_name': original_project.project_name,
            'project_description': original_project.project_description,
            'project_priority': original_project.project_priority,
            'deadline_date': original_project.deadline_date,
            'project_folder_link': original_project.project_folder_link,
        })

    context = {
        'form': form,
        'project': original_project
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def history_log(request):
    """History log view: Users see their own, approvers/viewers see all."""
    from itertools import chain
    from django.db.models import Q
    from datetime import datetime
    
    # Initialize filter form
    filter_form = HistoryFilterForm(request.GET, user=request.user)
    
    # Base querysets
    if IsProjectManager.has_permission(request.user):
        project_history = ProjectHistory.objects.all()
        approval_history = ApprovalHistory.objects.all()
    else:
        project_history = ProjectHistory.objects.filter(submitted_by=request.user)
        approval_history = ApprovalHistory.objects.filter(performed_by=request.user)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        
        # Project filter
        if filters.get('project'):
            project_history = project_history.filter(project=filters['project'])
            approval_history = approval_history.filter(project=filters['project'])
        
        # User filter
        if filters.get('user'):
            project_history = project_history.filter(submitted_by=filters['user'])
            approval_history = approval_history.filter(performed_by=filters['user'])
        
        # Status filter
        if filters.get('status'):
            project_history = project_history.filter(approval_status=filters['status'])
            approval_history = approval_history.filter(
                Q(previous_status=filters['status']) | Q(new_status=filters['status'])
            )
        
        # Date range filters
        if filters.get('date_from'):
            project_history = project_history.filter(date_submitted__date__gte=filters['date_from'])
            approval_history = approval_history.filter(performed_at__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            project_history = project_history.filter(date_submitted__date__lte=filters['date_to'])
            approval_history = approval_history.filter(performed_at__date__lte=filters['date_to'])
        
        # Type filter (submission or change)
        if filters.get('entry_type') == 'submission':
            approval_history = ApprovalHistory.objects.none()  # Empty queryset
        elif filters.get('entry_type') == 'change':
            project_history = ProjectHistory.objects.none()  # Empty queryset
    
    # Apply sorting
    sort_by = filter_form.cleaned_data.get('sort_by', '-date') if filter_form.is_valid() else '-date'
    
    if sort_by == 'project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower()
        )
    elif sort_by == '-project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower(),
            reverse=True
        )
    elif sort_by == 'user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower()
        )
    elif sort_by == '-user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower(),
            reverse=True
        )
    elif sort_by == 'type':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: 'submission' if hasattr(x, 'receipt_id') and x.receipt_id else 'change'
        )
    elif sort_by == 'date':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None)
        )
    else:  # Default: '-date'
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None),
            reverse=True
        )
    
    # Pagination
    paginator = Paginator(combined_history, 25)  # 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'history': page_obj,
        'filter_form': filter_form,
        'total_count': len(combined_history)
    }
    
    return render(request, 'projects/history_log.html', context)

@login_required
@user_passes_test(lambda u: IsProjectManager.has_permission(u))
def quick_action(request, pk):
    """Quick action endpoint for approve/reject/revise from admin pending page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk)
    
    if project.status != 'Pending_Approval':
        return JsonResponse({'error': 'Only pending projects can be reviewed'}, status=400)
    
    action = request.POST.get('action')
    if action not in ['approve', 'reject', 'revise']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # Use the same service as the regular review function
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    success = False
    message = ''
    
    if action == 'approve':
        success = submission_service.approve_project(project, request.user, 'Quick approval', request_meta)
        message = 'Project approved successfully!'
    elif action == 'reject':
        success = submission_service.reject_project(project, request.user, 'Quick rejection', request_meta)
        message = 'Project rejected.'
    elif action == 'revise':
        success = submission_service.request_revision(project, request.user, 'Quick revision request', request_meta)
        message = 'Project sent back for revision.'
    
    if success:
        messages.success(request, message)
        return redirect('projects:admin_pending')
    else:
        messages.error(request, 'Failed to process review. Please try again.')
        return redirect('projects:admin_pending')


@user_passes_test(is_admin_check)
@csrf_protect
def update_drawing_status(request, pk):
    """Update drawing status - only during review for project managers"""
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project
    
    # Check if user is project manager
    if not IsProjectManager.has_permission(request.user):
        return HttpResponseForbidden("Only project managers can update drawing status.")
    
    # Check if project is in review status (Pending_Approval)
    if project.status != 'Pending_Approval':
        return HttpResponseForbidden("Drawing status can only be updated during project review.")
    
    if request.method == 'POST':
        new_status = request.POST.get('drawing_status_' + str(pk))
        if new_status and new_status in [choice[0] for choice in Document.STATUS_CHOICES]:
            drawing.status = new_status
            drawing.save()
            
            if request.headers.get('HX-Request'):
                # Return the updated row for HTMX
                context = {
                    'drawing': drawing,
                    'project': project,
                    'can_review': IsProjectManager.has_permission(request.user) and project.status == 'Pending_Approval',
                    'can_edit': CanEditProject.has_permission(request.user, project),
                    'is_review_page': True,
                }
                return render(request, 'projects/partials/drawing_row.html', context)
            
            messages.success(request, f'Drawing {drawing.drawing_no} status updated to {drawing.get_status_display()}.')
            return redirect('projects:detail', pk=project.pk)
    
    return HttpResponseForbidden("Invalid request method.")

@login_required
def get_project_versions(request, project_group_id):
    """API endpoint to get all versions of a project"""
    try:
        project_group_uuid = uuid.UUID(project_group_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid project group ID format'}, status=400)
    
    versions = Project.objects.filter(
        project_group_id=project_group_uuid
    ).select_related('submitted_by').order_by('-version')
    
    # Permission check: user must be able to see at least one project in the group
    can_view = any(CanViewProject.has_permission(request.user, p) for p in versions)
    if not can_view:
        return JsonResponse({'error': 'You do not have permission to view these projects.'}, status=403)
    
    data = {
        'versions': [
            {
                'id': str(v.id),
                'version': v.version_display,
                'status': v.get_status_display(),
                'date_submitted': v.date_submitted.strftime('%Y-%m-%d %H:%M') if v.date_submitted else 'N/A',
                'submitted_by': v.submitted_by.get_full_name() or v.submitted_by.username,
                'url': reverse('projects:detail', kwargs={'pk': v.pk})
            } for v in versions
        ]
    }
    
    return JsonResponse(data)


def is_admin_or_approver(user):
    """Helper function to check if a user is an Admin or Approver."""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role.name in ['Admin', 'Approver']
    except AttributeError:
        return False

@login_required
@user_passes_test(is_admin_or_approver)
@csrf_protect
@never_cache
def rescind_revoke_project(request, pk):
    """Rescind or revoke an approved project."""
    project = get_object_or_404(Project, pk=pk)

    if project.status != 'Approved_Endorsed':
        messages.error(request, 'Only approved projects can be rescinded or revoked.')
        return redirect('projects:detail', pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                old_status = project.status
                project.status = 'Rescinded_Revoked'
                project.reviewed_by = None
                project.date_reviewed = None
                project.review_comments = ""
                project.save()

                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Rescinded_Revoked',
                    performed_by=request.user,
                    comments="Project status changed to Rescinded & Revoked.",
                    previous_status=old_status,
                    new_status='Rescinded_Revoked',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                messages.success(request, f'Project "{project.project_name}" has been Rescinded & Revoked.')
        except Exception as e:
            messages.error(request, f'Failed to rescind/revoke project: {str(e)}')

        return redirect('projects:detail', pk=pk)
    
    # If not POST, render a confirmation page or redirect
    messages.error(request, 'Invalid request method for this action.')
    return redirect('projects:detail', pk=pk)

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
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        status = self.request.GET.get('status')
        if status:
            base_queryset = base_queryset.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            base_queryset = base_queryset.filter(
                Q(project_name__icontains=search) |
                Q(project_description__icontains=search) |
                Q(submitted_by__first_name__icontains=search) |
                Q(submitted_by__last_name__icontains=search)
            )

        latest_versions_pks = base_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)

        queryset = Project.objects.filter(pk__in=latest_versions_pks).select_related(
            'submitted_by', 'reviewed_by'
        ).prefetch_related('drawings')

        # Apply sorting
        sort = self.request.GET.get('sort')
        if sort:
            if sort in ['-created_at', 'created_at', 'project_name', '-project_name', '-updated_at']:
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by('-updated_at')
        else:
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = IsProjectManager.has_permission(self.request.user)
        
        # Get base queryset for statistics (before pagination)
        user = self.request.user
        if IsProjectManager.has_permission(user):
            stats_queryset = Project.objects.exclude(status='Draft')
        else:
            stats_queryset = Project.objects.filter(
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        # Get latest versions for statistics
        latest_versions_pks = stats_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)
        
        stats_projects = Project.objects.filter(pk__in=latest_versions_pks)
        
        # Calculate statistics
        stats = {
            'draft_projects': stats_projects.filter(status='Draft').count(),
            'pending_projects': stats_projects.filter(status='Pending_Approval').count(),
            'approved_projects': stats_projects.filter(status='Approved_Endorsed').count(),
        }
        context['stats'] = stats
        
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
        
        # If user is viewing their own project, always redirect to the latest version
        if self.object.submitted_by == request.user:
            latest_version = Project.objects.filter(
                project_group_id=self.object.project_group_id,
                project_name=self.object.project_name,
                submitted_by=self.object.submitted_by
            ).order_by('-version').first()
            
            if latest_version and latest_version.pk != self.object.pk:
                return redirect('projects:detail', pk=latest_version.pk)
             
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_admin = IsProjectManager.has_permission(self.request.user)
        context['can_edit'] = CanEditProject.has_permission(self.request.user, self.object)
        context['can_create_new_version'] = CanCreateNewVersion.has_permission(self.request.user, self.object)
        context['can_review'] = is_admin and (self.object.status == 'Pending_Approval')
        context['is_review_page'] = False
        context['drawings'] = self.object.drawings.select_related('added_by')

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
    
    if project.status not in ['Draft', 'Conditional_Approval']:
        messages.error(request, 'Only drafts or conditionally approved projects can be submitted.')
        return redirect('projects:detail', pk=pk)
    
    if not project.drawings.exists():
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
    drawings = project.drawings.order_by('sort_order', 'drawing_no')
    
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
    
    is_admin = IsProjectManager.has_permission(request.user)
    context = {
        'project': project,
        'form': form,
        'drawings': drawings,
        'can_review': is_admin and (project.status == 'Pending_Approval'),
        'can_edit': CanEditProject.has_permission(request.user, project),
        'is_review_page': True,
        'project_versions': Project.objects.filter(
            project_group_id=project.project_group_id,
            project_name=project.project_name,
            submitted_by=project.submitted_by
        ).select_related('submitted_by', 'reviewed_by').order_by('-version'),
        'full_activity_log': ApprovalHistory.objects.filter(
            project__project_group_id=project.project_group_id,
            project__project_name=project.project_name,
            project__submitted_by=project.submitted_by
        ).select_related('performed_by', 'project').order_by('-performed_at'),
    }
    return render(request, 'projects/project_review.html', context)

@login_required
def add_drawing(request, project_pk):
    """Add drawing to project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not CanEditProject.has_permission(request.user, project):
        messages.error(request, "Drawings can only be added to 'Draft' or 'Conditional Approval' projects.")
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
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
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

@login_required
def edit_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to edit this drawing.")

    if request.method == 'POST':
        form = DrawingForm(request.POST, instance=drawing)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
                can_edit = CanEditProject.has_permission(request.user, project)
                list_html = render_to_string(
                    'projects/partials/drawing_list.html',
                    {'drawings': drawings, 'project': project, 'can_edit': can_edit},
                    request=request
                )
                oob_list_html = f'<div id="drawing-list" hx-swap-oob="true">{list_html}</div>'
                feedback_script = (
                    '<script>'
                    f" alert('Drawing {drawing.drawing_no} updated successfully!');"
                    " const modal = document.getElementById('modal');"
                    " if (modal) { modal.style.display = 'none'; }"
                    " const modalContent = document.getElementById('modal-content');"
                    " if (modalContent) { modalContent.innerHTML = ''; }"
                    '</script>'
                )
                return HttpResponse(oob_list_html + feedback_script)
            messages.success(request, f'Drawing {drawing.drawing_no} updated successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = DrawingForm(instance=drawing)
    return render(request, 'projects/drawing_form.html', {'form': form, 'project': project, 'drawing': drawing})

@login_required
@csrf_protect
def delete_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to delete this drawing.")

    if request.method == 'POST':
        drawing_no = drawing.drawing_no
        drawing.delete()
        project.no_of_drawings = project.drawings.count()
        project.save()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=200) # HTMX will remove the element
        messages.success(request, f'Drawing {drawing_no} deleted successfully.')
        return redirect('projects:detail', pk=project.pk)
    return HttpResponseForbidden("Invalid request method.")


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
        # Pre-populate form with original project data
        form = ProjectForm(initial={
            'project_name': original_project.project_name,
            'project_description': original_project.project_description,
            'project_priority': original_project.project_priority,
            'deadline_date': original_project.deadline_date,
            'project_folder_link': original_project.project_folder_link,
        })

    context = {
        'form': form,
        'project': original_project
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def history_log(request):
    """History log view: Users see their own, approvers/viewers see all."""
    from itertools import chain
    from django.db.models import Q
    from datetime import datetime
    
    # Initialize filter form
    filter_form = HistoryFilterForm(request.GET, user=request.user)
    
    # Base querysets
    if IsProjectManager.has_permission(request.user):
        project_history = ProjectHistory.objects.all()
        approval_history = ApprovalHistory.objects.all()
    else:
        project_history = ProjectHistory.objects.filter(submitted_by=request.user)
        approval_history = ApprovalHistory.objects.filter(performed_by=request.user)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        
        # Project filter
        if filters.get('project'):
            project_history = project_history.filter(project=filters['project'])
            approval_history = approval_history.filter(project=filters['project'])
        
        # User filter
        if filters.get('user'):
            project_history = project_history.filter(submitted_by=filters['user'])
            approval_history = approval_history.filter(performed_by=filters['user'])
        
        # Status filter
        if filters.get('status'):
            project_history = project_history.filter(approval_status=filters['status'])
            approval_history = approval_history.filter(
                Q(previous_status=filters['status']) | Q(new_status=filters['status'])
            )
        
        # Date range filters
        if filters.get('date_from'):
            project_history = project_history.filter(date_submitted__date__gte=filters['date_from'])
            approval_history = approval_history.filter(performed_at__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            project_history = project_history.filter(date_submitted__date__lte=filters['date_to'])
            approval_history = approval_history.filter(performed_at__date__lte=filters['date_to'])
        
        # Type filter (submission or change)
        if filters.get('entry_type') == 'submission':
            approval_history = ApprovalHistory.objects.none()  # Empty queryset
        elif filters.get('entry_type') == 'change':
            project_history = ProjectHistory.objects.none()  # Empty queryset
    
    # Apply sorting
    sort_by = filter_form.cleaned_data.get('sort_by', '-date') if filter_form.is_valid() else '-date'
    
    if sort_by == 'project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower()
        )
    elif sort_by == '-project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower(),
            reverse=True
        )
    elif sort_by == 'user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower()
        )
    elif sort_by == '-user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower(),
            reverse=True
        )
    elif sort_by == 'type':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: 'submission' if hasattr(x, 'receipt_id') and x.receipt_id else 'change'
        )
    elif sort_by == 'date':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None)
        )
    else:  # Default: '-date'
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None),
            reverse=True
        )
    
    # Pagination
    paginator = Paginator(combined_history, 25)  # 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'history': page_obj,
        'filter_form': filter_form,
        'total_count': len(combined_history)
    }
    
    return render(request, 'projects/history_log.html', context)

@login_required
@user_passes_test(lambda u: IsProjectManager.has_permission(u))
def quick_action(request, pk):
    """Quick action endpoint for approve/reject/revise from admin pending page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk)
    
    if project.status != 'Pending_Approval':
        return JsonResponse({'error': 'Only pending projects can be reviewed'}, status=400)
    
    action = request.POST.get('action')
    if action not in ['approve', 'reject', 'revise']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # Use the same service as the regular review function
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    success = False
    message = ''
    
    if action == 'approve':
        success = submission_service.approve_project(project, request.user, 'Quick approval', request_meta)
        message = 'Project approved successfully!'
    elif action == 'reject':
        success = submission_service.reject_project(project, request.user, 'Quick rejection', request_meta)
        message = 'Project rejected.'
    elif action == 'revise':
        success = submission_service.request_revision(project, request.user, 'Quick revision request', request_meta)
        message = 'Project sent back for revision.'
    
    if success:
        messages.success(request, message)
        return redirect('projects:admin_pending')
    else:
        messages.error(request, 'Failed to process review. Please try again.')
        return redirect('projects:admin_pending')


@user_passes_test(is_admin_check)
@csrf_protect
def update_drawing_status(request, pk):
    """Update drawing status - only during review for project managers"""
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project
    
    # Check if user is project manager
    if not IsProjectManager.has_permission(request.user):
        return HttpResponseForbidden("Only project managers can update drawing status.")
    
    # Check if project is in review status (Pending_Approval)
    if project.status != 'Pending_Approval':
        return HttpResponseForbidden("Drawing status can only be updated during project review.")
    
    if request.method == 'POST':
        new_status = request.POST.get('drawing_status_' + str(pk))
        if new_status and new_status in [choice[0] for choice in Document.STATUS_CHOICES]:
            drawing.status = new_status
            drawing.save()
            
            if request.headers.get('HX-Request'):
                # Return the updated row for HTMX
                context = {
                    'drawing': drawing,
                    'project': project,
                    'can_review': IsProjectManager.has_permission(request.user) and project.status == 'Pending_Approval',
                    'can_edit': CanEditProject.has_permission(request.user, project),
                    'is_review_page': True,
                }
                return render(request, 'projects/partials/drawing_row.html', context)
            
            messages.success(request, f'Drawing {drawing.drawing_no} status updated to {drawing.get_status_display()}.')
            return redirect('projects:detail', pk=project.pk)
    
    return HttpResponseForbidden("Invalid request method.")

@login_required
def get_project_versions(request, project_group_id):
    """API endpoint to get all versions of a project"""
    try:
        project_group_uuid = uuid.UUID(project_group_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid project group ID format'}, status=400)
    
    versions = Project.objects.filter(
        project_group_id=project_group_uuid
    ).select_related('submitted_by').order_by('-version')
    
    # Permission check: user must be able to see at least one project in the group
    can_view = any(CanViewProject.has_permission(request.user, p) for p in versions)
    if not can_view:
        return JsonResponse({'error': 'You do not have permission to view these projects.'}, status=403)
    
    data = {
        'versions': [
            {
                'id': str(v.id),
                'version': v.version_display,
                'status': v.get_status_display(),
                'date_submitted': v.date_submitted.strftime('%Y-%m-%d %H:%M') if v.date_submitted else 'N/A',
                'submitted_by': v.submitted_by.get_full_name() or v.submitted_by.username,
                'url': reverse('projects:detail', kwargs={'pk': v.pk})
            } for v in versions
        ]
    }
    
    return JsonResponse(data)


def is_admin_or_approver(user):
    """Helper function to check if a user is an Admin or Approver."""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role.name in ['Admin', 'Approver']
    except AttributeError:
        return False

@login_required
@user_passes_test(is_admin_or_approver)
@csrf_protect
@never_cache
def rescind_revoke_project(request, pk):
    """Rescind or revoke an approved project."""
    project = get_object_or_404(Project, pk=pk)

    if project.status != 'Approved_Endorsed':
        messages.error(request, 'Only approved projects can be rescinded or revoked.')
        return redirect('projects:detail', pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                old_status = project.status
                project.status = 'Rescinded_Revoked'
                project.reviewed_by = None
                project.date_reviewed = None
                project.review_comments = ""
                project.save()

                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Rescinded_Revoked',
                    performed_by=request.user,
                    comments="Project status changed to Rescinded & Revoked.",
                    previous_status=old_status,
                    new_status='Rescinded_Revoked',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                messages.success(request, f'Project "{project.project_name}" has been Rescinded & Revoked.')
        except Exception as e:
            messages.error(request, f'Failed to rescind/revoke project: {str(e)}')

        return redirect('projects:detail', pk=pk)
    
    # If not POST, render a confirmation page or redirect
    messages.error(request, 'Invalid request method for this action.')
    return redirect('projects:detail', pk=pk)

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
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        status = self.request.GET.get('status')
        if status:
            base_queryset = base_queryset.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            base_queryset = base_queryset.filter(
                Q(project_name__icontains=search) |
                Q(project_description__icontains=search) |
                Q(submitted_by__first_name__icontains=search) |
                Q(submitted_by__last_name__icontains=search)
            )

        latest_versions_pks = base_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)

        queryset = Project.objects.filter(pk__in=latest_versions_pks).select_related(
            'submitted_by', 'reviewed_by'
        ).prefetch_related('drawings')

        # Apply sorting
        sort = self.request.GET.get('sort')
        if sort:
            if sort in ['-created_at', 'created_at', 'project_name', '-project_name', '-updated_at']:
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by('-updated_at')
        else:
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = IsProjectManager.has_permission(self.request.user)
        
        # Get base queryset for statistics (before pagination)
        user = self.request.user
        if IsProjectManager.has_permission(user):
            stats_queryset = Project.objects.exclude(status='Draft')
        else:
            stats_queryset = Project.objects.filter(
                Q(submitted_by=user) | Q(status='Approved_Endorsed')
            ).distinct()
        
        # Get latest versions for statistics
        latest_versions_pks = stats_queryset.values('project_group_id').annotate(
            latest_pk=Max('pk')
        ).values_list('latest_pk', flat=True)
        
        stats_projects = Project.objects.filter(pk__in=latest_versions_pks)
        
        # Calculate statistics
        stats = {
            'draft_projects': stats_projects.filter(status='Draft').count(),
            'pending_projects': stats_projects.filter(status='Pending_Approval').count(),
            'approved_projects': stats_projects.filter(status='Approved_Endorsed').count(),
        }
        context['stats'] = stats
        
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
        
        # If user is viewing their own project, always redirect to the latest version
        if self.object.submitted_by == request.user:
            latest_version = Project.objects.filter(
                project_group_id=self.object.project_group_id,
                project_name=self.object.project_name,
                submitted_by=self.object.submitted_by
            ).order_by('-version').first()
            
            if latest_version and latest_version.pk != self.object.pk:
                return redirect('projects:detail', pk=latest_version.pk)
             
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

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
        context['is_review_page'] = False
        context['drawings'] = self.object.drawings.select_related('added_by')

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
    
    if project.status not in ['Draft', 'Conditional_Approval']:
        messages.error(request, 'Only drafts or conditionally approved projects can be submitted.')
        return redirect('projects:detail', pk=pk)
    
    if not project.drawings.exists():
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
    drawings = project.drawings.order_by('sort_order', 'drawing_no')
    
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
    
    is_admin = IsProjectManager.has_permission(request.user)
    context = {
        'project': project,
        'form': form,
        'drawings': drawings,
        'can_review': is_admin and (project.status == 'Pending_Approval'),
        'can_edit': CanEditProject.has_permission(request.user, project),
        'is_review_page': True,
        'project_versions': Project.objects.filter(
            project_group_id=project.project_group_id,
            project_name=project.project_name,
            submitted_by=project.submitted_by
        ).select_related('submitted_by', 'reviewed_by').order_by('-version'),
        'full_activity_log': ApprovalHistory.objects.filter(
            project__project_group_id=project.project_group_id,
            project__project_name=project.project_name,
            project__submitted_by=project.submitted_by
        ).select_related('performed_by', 'project').order_by('-performed_at'),
    }
    return render(request, 'projects/project_review.html', context)



@login_required
def add_drawing(request, project_pk):
    """Add drawing to project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not CanEditProject.has_permission(request.user, project):
        messages.error(request, "Drawings can only be added to 'Draft' or 'Conditional Approval' projects.")
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
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
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



@login_required
def add_drawing(request, project_pk):
    """Add drawing to project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not CanEditProject.has_permission(request.user, project):
        messages.error(request, "Drawings can only be added to 'Draft' or 'Conditional Approval' projects.")
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
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
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

@login_required
def edit_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to edit this drawing.")

    if request.method == 'POST':
        form = DrawingForm(request.POST, instance=drawing)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                drawings = project.drawings.order_by('sort_order', 'drawing_no')
                can_edit = CanEditProject.has_permission(request.user, project)
                list_html = render_to_string(
                    'projects/partials/drawing_list.html',
                    {'drawings': drawings, 'project': project, 'can_edit': can_edit},
                    request=request
                )
                oob_list_html = f'<div id="drawing-list" hx-swap-oob="true">{list_html}</div>'
                feedback_script = (
                    '<script>'
                    f" alert('Drawing {drawing.drawing_no} updated successfully!');"
                    " const modal = document.getElementById('modal');"
                    " if (modal) { modal.style.display = 'none'; }"
                    " const modalContent = document.getElementById('modal-content');"
                    " if (modalContent) { modalContent.innerHTML = ''; }"
                    '</script>'
                )
                return HttpResponse(oob_list_html + feedback_script)
            messages.success(request, f'Drawing {drawing.drawing_no} updated successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = DrawingForm(instance=drawing)
    return render(request, 'projects/drawing_form.html', {'form': form, 'project': project, 'drawing': drawing})

@login_required
@csrf_protect
def delete_drawing(request, pk):
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project

    if not CanEditProject.has_permission(request.user, project):
        return HttpResponseForbidden("You don't have permission to delete this drawing.")

    if request.method == 'POST':
        drawing_no = drawing.drawing_no
        drawing.delete()
        project.no_of_drawings = project.drawings.count()
        project.save()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=200) # HTMX will remove the element
        messages.success(request, f'Drawing {drawing_no} deleted successfully.')
        return redirect('projects:detail', pk=project.pk)
    return HttpResponseForbidden("Invalid request method.")


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
        # Pre-populate form with original project data
        form = ProjectForm(initial={
            'project_name': original_project.project_name,
            'project_description': original_project.project_description,
            'project_priority': original_project.project_priority,
            'deadline_date': original_project.deadline_date,
            'project_folder_link': original_project.project_folder_link,
        })

    context = {
        'form': form,
        'project': original_project
    }
    return render(request, 'projects/project_form.html', context)

@login_required
def history_log(request):
    """History log view: Users see their own, approvers/viewers see all."""
    from itertools import chain
    from django.db.models import Q
    from datetime import datetime
    
    # Initialize filter form
    filter_form = HistoryFilterForm(request.GET, user=request.user)
    
    # Base querysets
    if IsProjectManager.has_permission(request.user):
        project_history = ProjectHistory.objects.all()
        approval_history = ApprovalHistory.objects.all()
    else:
        project_history = ProjectHistory.objects.filter(submitted_by=request.user)
        approval_history = ApprovalHistory.objects.filter(performed_by=request.user)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        
        # Project filter
        if filters.get('project'):
            project_history = project_history.filter(project=filters['project'])
            approval_history = approval_history.filter(project=filters['project'])
        
        # User filter
        if filters.get('user'):
            project_history = project_history.filter(submitted_by=filters['user'])
            approval_history = approval_history.filter(performed_by=filters['user'])
        
        # Status filter
        if filters.get('status'):
            project_history = project_history.filter(approval_status=filters['status'])
            approval_history = approval_history.filter(
                Q(previous_status=filters['status']) | Q(new_status=filters['status'])
            )
        
        # Date range filters
        if filters.get('date_from'):
            project_history = project_history.filter(date_submitted__date__gte=filters['date_from'])
            approval_history = approval_history.filter(performed_at__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            project_history = project_history.filter(date_submitted__date__lte=filters['date_to'])
            approval_history = approval_history.filter(performed_at__date__lte=filters['date_to'])
        
        # Type filter (submission or change)
        if filters.get('entry_type') == 'submission':
            approval_history = ApprovalHistory.objects.none()  # Empty queryset
        elif filters.get('entry_type') == 'change':
            project_history = ProjectHistory.objects.none()  # Empty queryset
    
    # Apply sorting
    sort_by = filter_form.cleaned_data.get('sort_by', '-date') if filter_form.is_valid() else '-date'
    
    if sort_by == 'project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower()
        )
    elif sort_by == '-project':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: x.project.project_name.lower(),
            reverse=True
        )
    elif sort_by == 'user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower()
        )
    elif sort_by == '-user':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: (getattr(x, 'submitted_by', None) or getattr(x, 'performed_by', None)).username.lower(),
            reverse=True
        )
    elif sort_by == 'type':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: 'submission' if hasattr(x, 'receipt_id') and x.receipt_id else 'change'
        )
    elif sort_by == 'date':
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None)
        )
    else:  # Default: '-date'
        combined_history = sorted(
            chain(project_history, approval_history),
            key=lambda x: getattr(x, 'date_submitted', None) or getattr(x, 'performed_at', None),
            reverse=True
        )
    
    # Pagination
    paginator = Paginator(combined_history, 25)  # 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'history': page_obj,
        'filter_form': filter_form,
        'total_count': len(combined_history)
    }
    
    return render(request, 'projects/history_log.html', context)

@login_required
@user_passes_test(lambda u: IsProjectManager.has_permission(u))
def quick_action(request, pk):
    """Quick action endpoint for approve/reject/revise from admin pending page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk)
    
    if project.status != 'Pending_Approval':
        return JsonResponse({'error': 'Only pending projects can be reviewed'}, status=400)
    
    action = request.POST.get('action')
    if action not in ['approve', 'reject', 'revise']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # Use the same service as the regular review function
    submission_service = ProjectSubmissionService()
    request_meta = {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }
    
    success = False
    message = ''
    
    if action == 'approve':
        success = submission_service.approve_project(project, request.user, 'Quick approval', request_meta)
        message = 'Project approved successfully!'
    elif action == 'reject':
        success = submission_service.reject_project(project, request.user, 'Quick rejection', request_meta)
        message = 'Project rejected.'
    elif action == 'revise':
        success = submission_service.request_revision(project, request.user, 'Quick revision request', request_meta)
        message = 'Project sent back for revision.'
    
    if success:
        messages.success(request, message)
        return redirect('projects:admin_pending')
    else:
        messages.error(request, 'Failed to process review. Please try again.')
        return redirect('projects:admin_pending')


@user_passes_test(is_admin_check)
@csrf_protect
def update_drawing_status(request, pk):
    """Update drawing status - only during review for project managers"""
    drawing = get_object_or_404(Drawing, pk=pk)
    project = drawing.project
    
    # Check if user is project manager
    if not IsProjectManager.has_permission(request.user):
        return HttpResponseForbidden("Only project managers can update drawing status.")
    
    # Check if project is in review status (Pending_Approval)
    if project.status != 'Pending_Approval':
        return HttpResponseForbidden("Drawing status can only be updated during project review.")
    
    if request.method == 'POST':
        new_status = request.POST.get('drawing_status_' + str(pk))
        if new_status and new_status in [choice[0] for choice in Document.STATUS_CHOICES]:
            drawing.status = new_status
            drawing.save()
            
            if request.headers.get('HX-Request'):
                # Return the updated row for HTMX
                context = {
                    'drawing': drawing,
                    'project': project,
                    'can_review': IsProjectManager.has_permission(request.user) and project.status == 'Pending_Approval',
                    'can_edit': CanEditProject.has_permission(request.user, project),
                    'is_review_page': True,
                }
                return render(request, 'projects/partials/drawing_row.html', context)
            
            messages.success(request, f'Drawing {drawing.drawing_no} status updated to {drawing.get_status_display()}.')
            return redirect('projects:detail', pk=project.pk)
    
    return HttpResponseForbidden("Invalid request method.")