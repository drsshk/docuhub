# In accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Role, UserSession, AuditLog

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

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'last_activity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity', 'logout_time')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'performed_by', 'description')
    list_filter = ('action', 'created_at')
    search_fields = ('performed_by__username', 'description')
    readonly_fields = ('user', 'action', 'description', 'performed_by', 'ip_address', 'additional_data', 'created_at')