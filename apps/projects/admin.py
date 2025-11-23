from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Document, ProjectGroup, ApprovalHistory, ProjectHistory

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
    fields = ['document_number', 'title', 'discipline', 'status', 'file_path']

class ApprovalHistoryInline(admin.TabularInline):
    model = ApprovalHistory
    extra = 0
    readonly_fields = ['performed_at', 'performed_by', 'action', 'comment']
    fields = ['action', 'performed_by', 'performed_at', 'comment']
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_name', 'version_display', 'created_by', 'is_latest', 
        'created_at'
    ]
    list_filter = ['is_latest', 'project_priority', 'created_at']
    search_fields = ['project_name', 'created_by__username', 'project_group__name']
    readonly_fields = [
        'id', 'version_number', 'created_at', 'updated_at'
    ]
    inlines = [DocumentInline, ApprovalHistoryInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project_name', 'project_description', 
                      'project_priority', 'deadline_date')
        }),
        ('Version & Project Group', {
            'fields': ('project_group', 'version_number', 'is_latest')
        }),
        ('Creation Info', {
            'fields': ('created_by',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    
    def version_display(self, obj):
        return obj.version_display
    version_display.short_description = 'Version'

@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'client_name', 'created_by', 'created_at']
    list_filter = ['created_at', 'client_name']
    search_fields = ['name', 'code', 'client_name', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Project Group Information', {
            'fields': ('name', 'code', 'client_name', 'created_by')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_number', 'title', 'project', 'discipline',
        'status', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'discipline', 'created_at']
    search_fields = ['document_number', 'title', 'project__project_name']
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('project', 'document_number', 'title', 'description')
        }),
        ('Technical Details', {
            'fields': ('discipline', 'revision', 'file_path')
        }),
        ('Status & Workflow', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ApprovalHistory)
class ApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'document', 'action', 'performed_by', 'performed_at'
    ]
    list_filter = ['action', 'performed_at']
    search_fields = ['project__project_name', 'document__document_number', 'performed_by__username']
    readonly_fields = [f.name for f in ApprovalHistory._meta.fields]
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProjectHistory)
class ProjectHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'version', 'approval_status', 'submitted_by', 'date_submitted'
    ]
    list_filter = ['approval_status', 'date_submitted']
    search_fields = ['project__project_name', 'receipt_id', 'submitted_by__username']
    readonly_fields = [f.name for f in ProjectHistory._meta.fields]
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
