from django.contrib import admin
from django.utils.html import format_html
from .models import Version, VersionImprovement


class VersionImprovementInline(admin.TabularInline):
    model = VersionImprovement
    extra = 1
    fields = ('improvement_type', 'title', 'description', 'order')
    ordering = ('order', 'created_at')


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('version_number', 'version_type', 'release_date', 'is_current', 'improvement_count')
    list_filter = ('version_type', 'release_date', 'is_current')
    search_fields = ('version_number', 'description')
    readonly_fields = ('release_date',)
    inlines = [VersionImprovementInline]
    
    fieldsets = (
        ('Version Information', {
            'fields': ('version_number', 'version_type', 'is_current', 'release_date')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    def improvement_count(self, obj):
        count = obj.improvements.count()
        if count > 0:
            return format_html(
                '<span style="color: green;">{} improvements</span>',
                count
            )
        return format_html('<span style="color: red;">No improvements</span>')
    improvement_count.short_description = 'Improvements'
    
    def save_model(self, request, obj, form, change):
        # Update version.py file when version is marked as current
        if obj.is_current:
            import os
            from django.conf import settings
            
            version_file = os.path.join(settings.BASE_DIR, 'docuhub', 'version.py')
            with open(version_file, 'w') as f:
                f.write(f"__version__ = '{obj.version_number}'\n")
        
        super().save_model(request, obj, form, change)


@admin.register(VersionImprovement)
class VersionImprovementAdmin(admin.ModelAdmin):
    list_display = ('version', 'improvement_type', 'title', 'created_at', 'order')
    list_filter = ('improvement_type', 'version__version_number', 'created_at')
    search_fields = ('title', 'description', 'version__version_number')
    list_editable = ('order',)
    
    fieldsets = (
        ('Improvement Details', {
            'fields': ('version', 'improvement_type', 'title', 'description')
        }),
        ('Display Options', {
            'fields': ('order',)
        }),
    )