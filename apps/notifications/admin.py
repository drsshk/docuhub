from django.contrib import admin
from django.utils.html import format_html
from .models import NotificationPreferences, EmailLog

@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'email_frequency', 'notify_submission', 
        'notify_approval', 'notify_rejection'
    ]
    list_filter = ['email_enabled', 'email_frequency', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Settings', {
            'fields': ('email_enabled', 'email_frequency')
        }),
        ('User Notifications', {
            'fields': ('notify_submission', 'notify_approval', 'notify_rejection', 
                      'notify_revision_request', 'notify_obsolete')
        }),
        ('Admin Notifications', {
            'fields': ('notify_admin_new_submission', 'notify_admin_resubmission')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_email', 'template_type', 'status_badge', 'sent_at', 
        'project_link', 'retry_count'
    ]
    list_filter = ['status', 'template_type', 'sent_at']
    search_fields = ['recipient_email', 'project__project_name', 'brevo_message_id']
    readonly_fields = [
        'sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'brevo_message_id'
    ]
    
    fieldsets = (
        ('Email Details', {
            'fields': ('project', 'recipient_email', 'recipient_name', 'template_type', 'template_id')
        }),
        ('Status & Delivery', {
            'fields': ('status', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at')
        }),
        ('Technical Details', {
            'fields': ('brevo_message_id', 'retry_count', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'SENT': 'blue',
            'DELIVERED': 'green',
            'FAILED': 'red',
            'BOUNCED': 'red',
            'SPAM': 'red',
            'BLOCKED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def project_link(self, obj):
        if obj.project:
            return format_html(
                '<a href="/admin/projects/project/{}/change/">{}</a>',
                obj.project.id, obj.project.project_name
            )
        return 'No Project'
    project_link.short_description = 'Project'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation