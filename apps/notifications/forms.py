import logging
from django import forms
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError
from apps.accounts.models import NotificationPreferences

logger = logging.getLogger(__name__)

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = [
            'email_enabled', 'submission_notifications', 'approval_notifications', 
            'rejection_notifications', 'revision_notifications'
        ]
        widgets = {
            'email_enabled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'submission_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'approval_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'
            }),
            'rejection_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded'
            }),
            'revision_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded'
            })
        }
        
        labels = {
            'email_enabled': 'Enable email notifications',
            'submission_notifications': 'Project submission confirmations',
            'approval_notifications': 'Project approvals',
            'rejection_notifications': 'Project rejections',
            'revision_notifications': 'Revision requests'
        }
        
        help_texts = {
            'email_enabled': 'Enable or disable all email notifications',
            'submission_notifications': 'Get notified when you submit a project for approval',
            'approval_notifications': 'Get notified when your project is approved',
            'rejection_notifications': 'Get notified when your project is rejected',
            'revision_notifications': 'Get notified when admin requests revisions'
        }

    def save(self, commit=True):
        """Save notification preferences with error handling"""
        try:
            return super().save(commit=commit)
        except IntegrityError as e:
            logger.error(f"IntegrityError saving notification preferences: {e}")
            raise ValidationError("There was an error saving your notification preferences. Please try again.")
        except DatabaseError as e:
            logger.error(f"DatabaseError saving notification preferences: {e}")
            raise ValidationError("Database error occurred. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error saving notification preferences: {e}")
            raise ValidationError("An unexpected error occurred. Please try again.")