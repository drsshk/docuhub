from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from .models import Project, ApprovalHistory

# Only import if notifications app is available
try:
    from apps.notifications.services import BrevoEmailService
    email_service = BrevoEmailService()
    HAS_EMAIL_SERVICE = True
except ImportError:
    HAS_EMAIL_SERVICE = False

@receiver(pre_save, sender=Project)
def track_project_changes(sender, instance, **kwargs):
    """Track project status changes for approval history"""
    if instance.pk:
        try:
            old_instance = Project.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Project.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Project)
def project_status_changed(sender, instance, created, **kwargs):
    """Handle project status changes and send appropriate emails"""
    
    if created:
        # Create approval history for new project
        ApprovalHistory.objects.create(
            project=instance,
            version=instance.version,
            action='Created',
            performed_by=instance.submitted_by,
            new_status=instance.status
        )
        return
    
    # Get old status
    old_status = getattr(instance, '_old_status', None)
    
    # Only proceed if status actually changed
    if old_status == instance.status:
        return
    
    # Create approval history entry
    ApprovalHistory.objects.create(
        project=instance,
        version=instance.version,
        action=instance.status.replace('_', ' ').title(),
        performed_by=instance.reviewed_by or instance.submitted_by,
        previous_status=old_status,
        new_status=instance.status,
        comments=instance.review_comments
    )
    
    # Handle email notifications if email service is available
    if not HAS_EMAIL_SERVICE:
        return
    
    user = instance.submitted_by
    
    if instance.status == 'Pending_Approval' and old_status == 'Draft':
        # Project submitted - notify user and admins
        if instance.date_submitted:
            email_service.notify_project_submitted(instance, user)
            
            # Notify all admin and approver users
            from apps.accounts.models import Role
            from django.db import models as db_models
            admin_users = User.objects.filter(is_active=True).filter(
                db_models.Q(is_staff=True) | 
                db_models.Q(profile__role__name__in=['Approver', 'Admin'])
            ).distinct()
            if admin_users.exists():
                email_service.notify_admin_new_submission(instance, admin_users)
    
    elif instance.status == 'Pending_Approval' and old_status in ['Rejected', 'Revise_and_Resubmit']:
        # Project resubmitted - notify admins
        admin_users = User.objects.filter(is_active=True).filter(
            db_models.Q(is_staff=True) | 
            db_models.Q(profile__role__name__in=['Approver', 'Admin'])
        ).distinct()
        if admin_users.exists():
            email_service.notify_admin_new_submission(instance, admin_users)
    
    elif instance.status == 'Approved_Endorsed':
        # Project approved - notify user
        if instance.reviewed_by:
            email_service.notify_project_approved(instance, user, instance.reviewed_by)
    
    elif instance.status == 'Rejected':
        # Project rejected - notify user
        if instance.reviewed_by:
            email_service.notify_project_rejected(instance, user, instance.reviewed_by)
    
    elif instance.status == 'Revise_and_Resubmit':
        # Admin requires revision - notify user
        if instance.reviewed_by:
            email_service.notify_revision_required(instance, user, instance.reviewed_by)
    
    elif instance.status == 'Obsolete':
        # Project marked obsolete - notify user
        email_service.notify_project_obsolete(instance, user)