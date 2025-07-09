from django import forms
from .models import NotificationPreferences

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = [
            'email_enabled', 'email_frequency', 'notify_submission',
            'notify_approval', 'notify_rejection', 'notify_revision_request',
            'notify_obsolete', 'notify_admin_new_submission', 'notify_admin_resubmission'
        ]
        widgets = {
            'email_enabled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'email_frequency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notify_submission': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'notify_approval': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'
            }),
            'notify_rejection': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded'
            }),
            'notify_revision_request': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded'
            }),
            'notify_obsolete': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded'
            }),
            'notify_admin_new_submission': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'notify_admin_resubmission': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        
        labels = {
            'email_enabled': 'Enable Email Notifications',
            'email_frequency': 'Email Frequency',
            'notify_submission': 'Project submission confirmations',
            'notify_approval': 'Project approvals',
            'notify_rejection': 'Project rejections',
            'notify_revision_request': 'Revision requests',
            'notify_obsolete': 'Project marked as obsolete',
            'notify_admin_new_submission': 'New project submissions (Admin)',
            'notify_admin_resubmission': 'Project resubmissions (Admin)',
        }
        
        help_texts = {
            'email_frequency': 'How often you want to receive email notifications',
            'notify_submission': 'Get notified when you submit a project for approval',
            'notify_approval': 'Get notified when your project is approved',
            'notify_rejection': 'Get notified when your project is rejected',
            'notify_revision_request': 'Get notified when admin requests revisions',
            'notify_obsolete': 'Get notified when your project is marked as obsolete',
            'notify_admin_new_submission': 'Admin: Get notified of new project submissions',
            'notify_admin_resubmission': 'Admin: Get notified of project resubmissions',
        }