import uuid
from django.db import models
from django.contrib.auth.models import User

class NotificationPreferences(models.Model):
    FREQUENCY_CHOICES = [
        ('IMMEDIATE', 'Immediate'),
        ('DAILY', 'Daily Digest'),
        ('WEEKLY', 'Weekly Digest'),
        ('DISABLED', 'Disabled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    notify_submission = models.BooleanField(default=True)
    notify_approval = models.BooleanField(default=True)
    notify_rejection = models.BooleanField(default=True)
    notify_revision_request = models.BooleanField(default=True)
    notify_obsolete = models.BooleanField(default=True)
    notify_admin_new_submission = models.BooleanField(default=True)
    notify_admin_resubmission = models.BooleanField(default=True)
    email_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='IMMEDIATE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"{self.user.username} - Email: {self.email_enabled}"

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
        ('SPAM', 'Spam'),
        ('BLOCKED', 'Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Make project field optional to handle cases where project is None
    project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.CASCADE, 
        related_name='email_logs', 
        null=True, 
        blank=True
    )
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255, blank=True)
    template_type = models.CharField(max_length=50)
    template_id = models.IntegerField(null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    brevo_message_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'email_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['recipient_email']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.template_type} to {self.recipient_email} - {self.status}"