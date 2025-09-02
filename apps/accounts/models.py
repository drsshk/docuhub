import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Role(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Approver', 'Approver'),
        ('Submitter', 'Submitter'),
        ('Viewer', 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Architecture', 'Architecture'),
        ('Construction', 'Construction'),
        ('Planning', 'Planning'),
        ('Quality Assurance', 'Quality Assurance'),
        ('Project Management', 'Project Management'),
        ('Administration', 'Administration'),
        ('Other', 'Other'),
    ]
    
    JOB_TITLE_CHOICES = [
        ('Engineer', 'Engineer'),
        ('Senior Engineer', 'Senior Engineer'),
        ('Principal Engineer', 'Principal Engineer'),
        ('Architect', 'Architect'),
        ('Senior Architect', 'Senior Architect'),
        ('Project Manager', 'Project Manager'),
        ('Team Lead', 'Team Lead'),
        ('Supervisor', 'Supervisor'),
        ('Manager', 'Manager'),
        ('Director', 'Director'),
        ('Technician', 'Technician'),
        ('Draftsperson', 'Draftsperson'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, choices=JOB_TITLE_CHOICES, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    bio = models.TextField(blank=True, help_text='Brief description about yourself')
    location = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='subordinates', help_text='Direct manager/supervisor'
    )
    hire_date = models.DateField(null=True, blank=True)
    is_active_employee = models.BooleanField(default=True)
    
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class AuditLog(models.Model):
    """Model to log user actions for audit trail."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100, help_text="e.g., 'user_login', 'project_create'")
    description = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_actions_performed'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    additional_data = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.action} by {self.performed_by.username if self.performed_by else 'System'} at {self.created_at}"


# Signal handlers to create/update user profiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)