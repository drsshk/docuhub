import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from .validators import (
    validate_project_name, validate_project_description, validate_version_number,
    validate_drawing_number, validate_drawing_title, validate_url_format,
    validate_revision_number, validate_sort_order, validate_scale_ratio,
    validate_sheet_size, validate_drawing_type, validate_comments_length
)


class ProjectGroup(models.Model):
    """Logical family for all versions of the same project"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, blank=True, help_text="Human-readable project code")
    name = models.CharField(max_length=255, validators=[validate_project_name])
    client_name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_project_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_groups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['client_name']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_latest_project(self):
        """Get the latest version of this project group"""
        return self.projects.filter(is_latest=True).first()


class Project(models.Model):
    """One version of a project. No status field - status lives on Documents."""
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='projects')
    version_number = models.IntegerField(validators=[validate_version_number])
    is_latest = models.BooleanField(default=True)
    
    # Metadata snapshot for this version
    project_name = models.CharField(max_length=255, validators=[validate_project_name])
    client_name = models.CharField(max_length=255, blank=True)
    project_description = models.TextField(blank=True, validators=[validate_project_description])
    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    project_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    deadline_date = models.DateField(null=True, blank=True)
    project_folder_link = models.URLField(max_length=500, blank=True, validators=[validate_url_format])
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        unique_together = ['project_group', 'version_number']
        indexes = [
            models.Index(fields=['project_group']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_latest']),
        ]

    def __str__(self):
        return f"{self.project_name} - V{self.version_number:03d}"

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})

    @property
    def version_display(self):
        return f"V{self.version_number:03d}"
    
    def set_as_latest(self):
        """Set this project as the latest version and unmark others"""
        Project.objects.filter(project_group=self.project_group).update(is_latest=False)
        self.is_latest = True
        self.save(update_fields=['is_latest'])
    
    def update_document_count(self):
        """Update the document count for this project"""
        self.no_of_documents = self.documents.count()
        self.save(update_fields=['updated_at'])

    def clean(self):
        """Validate the project instance"""
        super().clean()
        
        # Validate deadline date
        if self.deadline_date:
            if self.deadline_date < timezone.now().date():
                raise ValidationError('Deadline date cannot be in the past.')
        
        # Validate unique latest version per project group
        if self.is_latest and self.project_group_id:
            existing_latest = Project.objects.filter(
                project_group=self.project_group,
                is_latest=True
            ).exclude(pk=self.pk)
            
            if existing_latest.exists():
                raise ValidationError('Only one project can be marked as latest per project group.')


class Document(models.Model):
    """Document/Drawing entity - This is where the workflow status lives"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION_REQUIRED', 'Revision Required'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    document_number = models.CharField(
        max_length=20,
        validators=[validate_drawing_number],
        help_text="Document/Drawing number"
    )
    title = models.CharField(max_length=255, blank=True, validators=[validate_drawing_title])
    description = models.TextField(blank=True)
    discipline = models.CharField(max_length=100, blank=True)
    revision = models.CharField(max_length=10, blank=True)
    file_path = models.FileField(upload_to='documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_documents')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['document_number']
        unique_together = ['project', 'document_number']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['created_by']),
            models.Index(fields=['status']),
            models.Index(fields=['discipline']),
        ]

    def clean(self):
        """Validate the document instance"""
        super().clean()
        
        # Ensure document number is uppercase
        if self.document_number:
            self.document_number = self.document_number.upper()
        
        # Validate that document has either a title or description
        if not self.title and not self.description:
            raise ValidationError('Document must have either a title or description.')
        
        # Validate unique document number within the same project
        if self.project_id:
            existing = Document.objects.filter(
                project=self.project,
                document_number=self.document_number
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(f'Document number {self.document_number} already exists in this project.')

    def __str__(self):
        return f"{self.document_number} - {self.title}"

    def save(self, *args, **kwargs):
        # Run clean validation
        self.full_clean()
        super().save(*args, **kwargs)


class ApprovalHistory(models.Model):
    """Logs every decision/action taken on a submission"""
    
    ACTION_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION_REQUESTED', 'Revision Requested'),
        ('RESCINDED', 'Rescinded'),
        ('OBSOLETED', 'Made Obsolete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='approval_history')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, related_name='approval_history')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    from_status = models.CharField(max_length=30, blank=True, null=True)
    to_status = models.CharField(max_length=30)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    performed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, validators=[validate_comments_length])
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'approval_history'
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['document']),
            models.Index(fields=['performed_by']),
            models.Index(fields=['performed_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.action} by {self.performed_by.username}"


class ProjectHistory(models.Model):
    """Audit of project/document metadata & submissions"""
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION_REQUIRED', 'Revision Required'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='history_logs')
    version = models.IntegerField()
    date_submitted = models.DateTimeField()
    submission_link = models.URLField(max_length=500, blank=True)
    drawing_qty = models.IntegerField(default=0)
    drawing_numbers = models.TextField(blank=True)
    receipt_id = models.CharField(max_length=100, unique=True)
    approval_status = models.CharField(max_length=30, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_submissions')
    
    class Meta:
        db_table = 'project_history'
        ordering = ['-date_submitted']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['submitted_by']),
            models.Index(fields=['approval_status']),
        ]

    def __str__(self):
        return f"Submission {self.receipt_id} - {self.project.project_name} v{self.version} by {self.submitted_by.username}"