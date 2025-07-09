from django.shortcuts import render
from django.contrib.auth.models import User
from apps.projects.models import Project, Drawing

def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'core/home.html')

    # --- Logic for authenticated users ---
    
    # Fetch stats for the current user
    user_projects = Project.objects.filter(submitted_by=request.user)
    user_drawings = Drawing.objects.filter(project__submitted_by=request.user)
    stats = {
        'total_projects': user_projects.count(),
        'draft_projects': user_projects.filter(status='Draft').count(),
        'pending_projects': user_projects.filter(status='Pending_Approval').count(),
        'approved_projects': user_projects.filter(status='Approved').count(),
        'total_drawings': user_drawings.count(),
    }

    # Fetch recent projects for the user
    recent_projects = user_projects.order_by('-updated_at')[:5]
    
    # Fetch admin stats if the user is a staff member
    admin_stats = {}
    if request.user.is_staff:
        admin_stats = {
            'pending_approvals': Project.objects.filter(status='Pending_Approval').count(),
            'total_projects': Project.objects.count(),
            'total_users': User.objects.count(),
        }

    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'admin_stats': admin_stats,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'core/dashboard.html', context)