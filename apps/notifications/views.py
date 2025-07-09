from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import NotificationPreferences, EmailLog
from .forms import NotificationPreferencesForm

@login_required
def notification_preferences(request):
    """User notification preferences"""
    preferences, created = NotificationPreferences.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('notifications:preferences')
    else:
        form = NotificationPreferencesForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)

@user_passes_test(lambda u: u.is_staff)
def email_logs(request):
    """Admin view for email logs"""
    logs = EmailLog.objects.all().order_by('-sent_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status=status)
    
    # Filter by template type
    template_type = request.GET.get('template_type')
    if template_type:
        logs = logs.filter(template_type=template_type)
    
    # Search by email or project
    search = request.GET.get('search')
    if search:
        logs = logs.filter(
            Q(recipient_email__icontains=search) |
            Q(project__project_name__icontains=search) |
            Q(recipient_name__icontains=search)
        )
    
    # Get unique template types for filter dropdown
    template_types = EmailLog.objects.values_list('template_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Email statistics
    stats = {
        'total_emails': EmailLog.objects.count(),
        'sent_emails': EmailLog.objects.filter(status='SENT').count(),
        'delivered_emails': EmailLog.objects.filter(status='DELIVERED').count(),
        'failed_emails': EmailLog.objects.filter(status='FAILED').count(),
    }
    
    context = {
        'logs': page_obj,
        'current_status': status,
        'current_template_type': template_type,
        'current_search': search,
        'template_types': template_types,
        'stats': stats,
    }
    return render(request, 'notifications/email_logs.html', context)

@user_passes_test(lambda u: u.is_staff)
def email_statistics(request):
    """Admin view for email statistics"""
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Overall statistics
    total_emails = EmailLog.objects.count()
    
    # Status breakdown
    status_stats = EmailLog.objects.values('status').annotate(
        count=Count('status')
    ).order_by('status')
    
    # Template type breakdown
    template_stats = EmailLog.objects.values('template_type').annotate(
        count=Count('template_type')
    ).order_by('-count')
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_emails = EmailLog.objects.filter(sent_at__gte=thirty_days_ago)
    
    # Daily email counts for the last 7 days
    daily_stats = []
    for i in range(7):
        date = datetime.now().date() - timedelta(days=i)
        count = EmailLog.objects.filter(sent_at__date=date).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_stats.reverse()
    
    context = {
        'total_emails': total_emails,
        'status_stats': status_stats,
        'template_stats': template_stats,
        'recent_count': recent_emails.count(),
        'daily_stats': daily_stats,
    }
    return render(request, 'notifications/email_statistics.html', context)