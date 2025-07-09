import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from .validators import (
    validate_project_name, validate_project_description, validate_version_number,
    validate_drawing_number, validate_drawing_title, validate_url_format,
    validate_revision_number, validate_sort_order, validate_scale_ratio,
    validate_sheet_size, validate_drawing_type, validate_comments_length
)

class Project(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending_Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Revise_and_Resubmit', 'Revise and Resubmit'),
        ('Obsolete', 'Obsolete'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # This new field will link versions of the same project together.
    project_group_id = models.UUIDField(default=uuid.uuid4, editable=False, help_text="Groups different versions of the same project.")
    project_name = models.CharField(max_length=255, validators=[validate_project_name])
    project_description = models.TextField(blank=True, validators=[validate_project_description])
    version = models.IntegerField(validators=[validate_version_number])
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_projects')
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_reviewed = models.DateTimeField(null=True, blank=True)
    no_of_drawings = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Draft')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_projects')
    review_comments = models.TextField(blank=True, validators=[validate_comments_length])
    revision_notes = models.TextField(blank=True, validators=[validate_comments_length])
    client_department = models.CharField(max_length=100, blank=True)
    project_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    deadline_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_group_id']),
            models.Index(fields=['submitted_by']),
            models.Index(fields=['status']),
            models.Index(fields=['date_submitted']),
        ]

    def __str__(self):
        return f"{self.project_name} - V{self.version:03d}"

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})

    @property
    def version_display(self):
        return f"V{self.version:03d}"
    
    def is_latest_version(self):
        """
        Check if this project is the latest version in its project group
        """
        latest_project = Project.objects.filter(
            project_group_id=self.project_group_id
        ).order_by('-version').first()
        
        return latest_project and latest_project.pk == self.pk

    def get_latest_version(self):
        """
        Get the latest version of this project group
        """
        return Project.objects.filter(
            project_group_id=self.project_group_id
        ).order_by('-version').first()

    def clean(self):
        """Validate the project instance"""
        super().clean()
        
        # Validate deadline date
        if self.deadline_date:
            from django.utils import timezone
            if self.deadline_date < timezone.now().date():
                raise ValidationError('Deadline date cannot be in the past.')
        
        # Validate status transitions
        # Validate status transitions only for existing projects where status has changed
        if not self._state.adding:  # Only for existing projects
            try:
                old_project = Project.objects.get(pk=self.pk)
                if old_project.status != self.status:
                    if not self._is_valid_status_transition(old_project.status, self.status):
                        raise ValidationError(f'Invalid status transition from {old_project.status} to {self.status}.')
            except Project.DoesNotExist:
                # Should not happen if _state.adding is False, but good for robustness
                pass

    def _is_valid_status_transition(self, old_status, new_status):
        """Check if status transition is valid"""
        valid_transitions = {
            'Draft': ['Pending_Approval', 'Obsolete'],
            'Pending_Approval': ['Approved', 'Rejected', 'Revise_and_Resubmit'],
            'Approved': ['Obsolete'],
            'Rejected': ['Draft', 'Obsolete'],
            'Revise_and_Resubmit': ['Pending_Approval', 'Draft', 'Obsolete'],
            'Obsolete': []  # No transitions from obsolete
        }
        
        return new_status in valid_transitions.get(old_status, []) or old_status == new_status

    def save(self, *args, **kwargs):
        # Run clean validation
        self.full_clean()
        
        # The version is now set in the view, not automatically here.
        
        super().save(*args, **kwargs)

class Drawing(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Replaced', 'Replaced'),
        ('Obsolete', 'Obsolete'),
    ]
    
    DISCIPLINE_CHOICES = [
        ('Architectural', 'Architectural'),
        ('Structural', 'Structural'),
        ('Mechanical', 'Mechanical'),
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Civil', 'Civil'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='drawings')
    drawing_no = models.CharField(
        max_length=20,
        validators=[validate_drawing_number]
    )
    drawing_title = models.CharField(max_length=255, blank=True, validators=[validate_drawing_title])
    drawing_description = models.TextField(blank=True)
    drawing_list_link = models.URLField(max_length=500, blank=True, validators=[validate_url_format])
    drawing_type = models.CharField(max_length=50, blank=True, validators=[validate_drawing_type])
    discipline = models.CharField(max_length=50, choices=DISCIPLINE_CHOICES, blank=True)
    scale_ratio = models.CharField(max_length=20, blank=True, validators=[validate_scale_ratio])
    sheet_size = models.CharField(max_length=10, blank=True, validators=[validate_sheet_size])
    revision_number = models.IntegerField(default=0, validators=[validate_revision_number])
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    sort_order = models.IntegerField(default=0, validators=[validate_sort_order])

    class Meta:
        db_table = 'drawings'
        ordering = ['sort_order', 'drawing_no']
        # The unique constraint is removed from drawing_no per project, 
        # as different versions might have same drawing numbers.
        # unique_together = ['project', 'drawing_no'] 
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['added_by']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        """Validate the drawing instance"""
        super().clean()
        
        # Ensure drawing number is uppercase
        if self.drawing_no:
            self.drawing_no = self.drawing_no.upper()
        
        # Validate that drawing has either a title or description
        if not self.drawing_title and not self.drawing_description:
            raise ValidationError('Drawing must have either a title or description.')
        
        # Validate unique drawing number within the same project
        if self.project_id:
            existing = Drawing.objects.filter(
                project=self.project,
                drawing_no=self.drawing_no,
                status='Active'
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(f'Drawing number {self.drawing_no} already exists in this project.')

    def __str__(self):
        return f"{self.drawing_no} - {self.drawing_title}"

    def save(self, *args, **kwargs):
        # Run clean validation
        self.full_clean()
        
        super().save(*args, **kwargs)
        # Update project drawing count
        if self.project:
            self.project.save()

class ApprovalHistory(models.Model):
    ACTION_CHOICES = [
        ('Created', 'Created'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Resubmitted', 'Resubmitted'),
        ('Status_Changed', 'Status Changed'),
        ('Obsoleted', 'Obsoleted'),
        ('Version_Created', 'Version Created')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='approval_history')
    version = models.IntegerField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    performed_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, validators=[validate_comments_length])
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'approval_history'
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['performed_by']),
            models.Index(fields=['performed_at']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.action} by {self.performed_by.username}"

class ProjectHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='history_logs')
    version = models.IntegerField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_history_submissions')
    date_submitted = models.DateTimeField()
    submission_link = models.URLField(max_length=500, blank=True)
    drawing_qty = models.IntegerField(default=0)
    drawing_numbers = models.TextField(blank=True, help_text="Comma-separated list of drawing numbers")
    receipt_id = models.CharField(max_length=100, blank=True)
    approval_status = models.CharField(max_length=30, choices=Project.STATUS_CHOICES)
    
    class Meta:
        db_table = 'project_history'
        ordering = ['-date_submitted']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['submitted_by']),
            models.Index(fields=['date_submitted']),
            models.Index(fields=['approval_status']),
        ]

    def __str__(self):
        return f"History for {self.project.project_name} V{self.version} - {self.approval_status} on {self.date_submitted.strftime('%Y-%m-%d')}"
