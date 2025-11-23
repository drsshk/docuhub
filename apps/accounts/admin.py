# In accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserSession, AuditLog, NotificationPreferences, EmailLog

# Unregister the provided UserAdmin
admin.site.unregister(User)

# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'submission_notifications', 'approval_notifications')
    list_filter = ('email_enabled', 'submission_notifications')
    search_fields = ('user__username',)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'to_email', 'subject', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('to_email', 'subject', 'user__username')
    readonly_fields = ('sent_at', 'opened_at', 'clicked_at')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'last_active_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'session_key', 'ip_address', 'user_agent', 'login_at', 'last_active_at', 'logout_time')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'event_type', 'user', 'object_type')
    list_filter = ('event_type', 'created_at')
    search_fields = ('user__username', 'event_type', 'object_type')
    readonly_fields = ('user', 'event_type', 'object_type', 'object_id', 'ip_address', 'payload', 'created_at')