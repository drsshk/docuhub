from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Drawing, ApprovalHistory

class DrawingInline(admin.TabularInline):
    model = Drawing
    extra = 0
    readonly_fields = ['date_added', 'added_by']
    fields = ['drawing_no', 'drawing_title', 'discipline', 'drawing_list_link', 'status']

class ApprovalHistoryInline(admin.TabularInline):
    model = ApprovalHistory
    extra = 0
    readonly_fields = ['performed_at', 'performed_by', 'action', 'comments', 'version']
    fields = ['action', 'performed_by', 'performed_at', 'version', 'comments']
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_name', 'version_display', 'submitted_by', 'status_badge', 
        'no_of_drawings', 'date_created', 'date_submitted'
    ]
    list_filter = ['status', 'project_priority', 'date_created', 'date_submitted']
    search_fields = ['project_name', 'submitted_by__username', 'project_group_id']
    readonly_fields = [
        'id', 'project_group_id', 'version', 'date_created', 'date_submitted', 'date_reviewed', 
        'no_of_drawings', 'created_at', 'updated_at'
    ]
    inlines = [DrawingInline, ApprovalHistoryInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project_name', 'project_description', 
                      'project_priority', 'deadline_date')
        }),
        ('Status & Workflow', {
            'fields': ('status', 'submitted_by', 'reviewed_by', 'review_comments', 'revision_notes')
        }),
        ('Metadata', {
            'fields': ('id', 'project_group_id', 'version', 'no_of_drawings', 'date_created', 'date_submitted', 
                      'date_reviewed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'Draft': '#6c757d',
            'Pending_Approval': '#ffc107',
            'Approved': '#28a745',
            'Rejected': '#dc3545',
            'Revise_and_Resubmit': '#007bff',
            'Obsolete': '#343a40'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 5px; font-size: 12px; font-weight: 500;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def version_display(self, obj):
        return obj.version_display
    version_display.short_description = 'Version'

@admin.register(Drawing)
class DrawingAdmin(admin.ModelAdmin):
    list_display = [
        'drawing_no', 'drawing_title', 'project', 'discipline', 
        'status', 'added_by', 'date_added'
    ]
    list_filter = ['discipline', 'status', 'date_added']
    search_fields = ['drawing_no', 'drawing_title', 'project__project_name']
    readonly_fields = ['date_added', 'added_by']
    
    fieldsets = (
        ('Drawing Information', {
            'fields': ('project', 'drawing_no', 'drawing_title', 'drawing_description')
        }),
        ('Technical Details', {
            'fields': ('discipline', 'drawing_type', 'scale_ratio', 'sheet_size')
        }),
        ('Links & Status', {
            'fields': ('drawing_list_link', 'status', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('revision_number', 'added_by', 'date_added'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ApprovalHistory)
class ApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'action', 'performed_by', 'performed_at', 'version'
    ]
    list_filter = ['action', 'performed_at', 'version']
    search_fields = ['project__project_name', 'performed_by__username']
    readonly_fields = [f.name for f in ApprovalHistory._meta.fields]
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
