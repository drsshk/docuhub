from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from apps.projects.models import Project, Drawing
from .models import Version, VersionImprovement
from .forms import VersionForm, VersionImprovementFormSet
import os

def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'core/home.html')

    # --- Logic for authenticated users ---
    
    # Check if user is admin/approver for role-based features
    from apps.projects.permissions import IsProjectManager
    is_admin = IsProjectManager.has_permission(request.user)
    
    # Fetch stats for the current user
    user_projects = Project.objects.filter(submitted_by=request.user)
    user_drawings = Drawing.objects.filter(project__submitted_by=request.user)
    stats = {
        'total_projects': user_projects.values('project_group_id').distinct().count(),
        'draft_projects': user_projects.filter(status='Draft').count(),
        'pending_projects': user_projects.filter(status='Pending_Approval').count(),
        'approved_projects': user_projects.filter(status='Approved').count(),
        'total_drawings': user_drawings.count(),
    }

    # Fetch recent projects for the user
    # Fetch all projects for the user, ordered by project_group_id and then by version (descending)
    # This allows easy grouping and selection of the latest version in Python
    all_user_projects = user_projects.order_by('project_group_id', '-version')

    # Manually filter to get only the latest version for each project_group_id
    seen_project_groups = set()
    recent_projects = []
    for project in all_user_projects:
        if project.project_group_id not in seen_project_groups:
            recent_projects.append(project)
            seen_project_groups.add(project.project_group_id)
    
    # Limit to the 5 most recently updated unique projects
    recent_projects = sorted(recent_projects, key=lambda p: p.updated_at, reverse=True)[:5]
    
    # Fetch admin stats if the user is a staff member or has approver role
    admin_stats = {}
    if is_admin:
        admin_stats = {
            'pending_approvals': Project.objects.filter(status='Pending_Approval').count(),
            'total_projects': Project.objects.count(),
            'total_users': User.objects.count(),
        }

    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'admin_stats': admin_stats,
        'is_admin': is_admin,
    }
    
    return render(request, 'core/dashboard.html', context)


def version_history(request):
    """Display all versions with their improvements"""
    versions = Version.objects.prefetch_related('improvements').all()
    current_version = Version.objects.filter(is_current=True).first()
    
    context = {
        'versions': versions,
        'current_version': current_version,
    }
    return render(request, 'core/version_history.html', context)


def version_detail(request, pk):
    """Display detailed view of a specific version"""
    version = get_object_or_404(Version, pk=pk)
    improvements = version.improvements.all()
    
    context = {
        'version': version,
        'improvements': improvements,
    }
    return render(request, 'core/version_detail.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_version(request):
    """Admin form to add new version with improvements"""
    if request.method == 'POST':
        form = VersionForm(request.POST)
        formset = VersionImprovementFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            version = form.save()
            formset.instance = version
            formset.save()
            
            # Update version.py file if this is marked as current
            if version.is_current:
                version_file = os.path.join(settings.BASE_DIR, 'docuhub', 'version.py')
                with open(version_file, 'w') as f:
                    f.write(f"__version__ = '{version.version_number}'\n")
            
            messages.success(request, f'Version {version.version_number} created successfully!')
            return redirect('core:version_history')
    else:
        form = VersionForm()
        formset = VersionImprovementFormSet()
    
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'core/add_version.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_version(request, pk):
    """Admin form to edit existing version"""
    version = get_object_or_404(Version, pk=pk)
    
    if request.method == 'POST':
        form = VersionForm(request.POST, instance=version)
        formset = VersionImprovementFormSet(request.POST, instance=version)
        
        if form.is_valid() and formset.is_valid():
            version = form.save()
            formset.save()
            
            # Update version.py file if this is marked as current
            if version.is_current:
                version_file = os.path.join(settings.BASE_DIR, 'docuhub', 'version.py')
                with open(version_file, 'w') as f:
                    f.write(f"__version__ = '{version.version_number}'\n")
            
            messages.success(request, f'Version {version.version_number} updated successfully!')
            return redirect('core:version_detail', pk=version.pk)
    else:
        form = VersionForm(instance=version)
        formset = VersionImprovementFormSet(instance=version)
    
    context = {
        'form': form,
        'formset': formset,
        'version': version,
        'editing': True,
    }
    return render(request, 'core/add_version.html', context)


def current_version_api(request):
    """API endpoint to get current version details"""
    try:
        current_version = Version.objects.filter(is_current=True).first()
        
        if not current_version:
            return JsonResponse({
                'error': 'No current version found',
                'version_number': '1.0.0',
                'version_type': 'major',
                'description': 'Initial release',
                'improvements': []
            })
        
        improvements = []
        for improvement in current_version.improvements.all():
            improvements.append({
                'improvement_type': improvement.improvement_type,
                'improvement_type_display': improvement.get_improvement_type_display(),
                'title': improvement.title,
                'description': improvement.description,
                'order': improvement.order
            })
        
        return JsonResponse({
            'version_number': current_version.version_number,
            'version_type': current_version.get_version_type_display(),
            'description': current_version.description,
            'release_date': current_version.release_date.isoformat(),
            'is_current': current_version.is_current,
            'improvements': improvements
        })
    
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading version details: {str(e)}'
        }, status=500)