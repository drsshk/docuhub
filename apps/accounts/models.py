import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Role(models.Model):
    """User roles for permission management"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'accounts_role'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile information"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role.name})"
    
    def get_display_name(self):
        return self.user.get_full_name() or self.user.username


class NotificationPreferences(models.Model):
    """User notification preferences"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    submission_notifications = models.BooleanField(default=True)
    approval_notifications = models.BooleanField(default=True)
    rejection_notifications = models.BooleanField(default=True)
    revision_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class EmailLog(models.Model):
    """Telemetry of email sends (Brevo/other providers)"""
    
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('BOUNCED', 'Bounced'),
        ('OPENED', 'Opened'),
        ('CLICKED', 'Clicked'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100, blank=True)
    message_id = models.CharField(max_length=255, blank=True, help_text="Provider message ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SENT')
    
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['to_email']),
            models.Index(fields=['status']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"Email to {self.to_email} - {self.subject}"


class UserSession(models.Model):
    """Track user sessions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} session from {self.ip_address}"


class AuditLog(models.Model):
    """Cross-cutting security/audit events"""
    
    EVENT_TYPE_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('PERMISSION_CHANGED', 'Permission Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PROJECT_ACTION', 'Project Action'),
        ('SYSTEM_EVENT', 'System Event'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    object_type = models.CharField(max_length=100, blank=True, help_text="e.g., 'Project', 'Document'")
    object_id = models.CharField(max_length=255, null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['event_type']),
            models.Index(fields=['object_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else "System"
        return f"{self.event_type} by {user_info} at {self.created_at}"


# Signal handlers are now in signals.py to avoid duplication