from django.db import models
from django.urls import reverse


class Version(models.Model):
    """Track application versions and their improvements"""
    
    VERSION_TYPES = [
        ('major', 'Major Release'),
        ('minor', 'Minor Release'),
        ('patch', 'Patch Release'),
        ('beta', 'Beta Release'),
    ]
    
    version_number = models.CharField(max_length=20, unique=True, help_text="e.g., 1.0.0")
    version_type = models.CharField(max_length=10, choices=VERSION_TYPES, default='minor')
    release_date = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False, help_text="Mark as current version")
    description = models.TextField(blank=True, help_text="Brief description of this version")
    
    class Meta:
        ordering = ['-release_date']
        verbose_name = "Version"
        verbose_name_plural = "Versions"
    
    def __str__(self):
        return f"v{self.version_number}"
    
    def get_absolute_url(self):
        return reverse('core:version_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # If this version is marked as current, unmark all others
        if self.is_current:
            Version.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class VersionImprovement(models.Model):
    """Track improvements made in each version"""
    
    IMPROVEMENT_TYPES = [
        ('feature', 'New Feature'),
        ('enhancement', 'Enhancement'),
        ('bugfix', 'Bug Fix'),
        ('security', 'Security Fix'),
        ('performance', 'Performance Improvement'),
        ('ui', 'UI/UX Improvement'),
        ('api', 'API Change'),
        ('documentation', 'Documentation'),
    ]
    
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='improvements')
    improvement_type = models.CharField(max_length=20, choices=IMPROVEMENT_TYPES, default='feature')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Version Improvement"
        verbose_name_plural = "Version Improvements"
    
    def __str__(self):
        return f"{self.version} - {self.title}"