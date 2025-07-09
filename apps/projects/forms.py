import bleach
from django import forms
from django.contrib.auth.models import User
from .models import Project, Drawing

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name', 'project_description', 'client_department', 
            'project_priority', 'deadline_date', 'project_folder_link'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter project name'
            }),
            'project_description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Enter project description (optional)'
            }),
            'client_department': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter client or department'
            }),
            'project_priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'deadline_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'project_folder_link': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://example.com/project-folder-link'
            })
        }

    def clean_project_name(self):
        project_name = self.cleaned_data['project_name']
        return bleach.clean(project_name, tags=[], attributes={}, strip=True)

    def clean_project_description(self):
        project_description = self.cleaned_data['project_description']
        return bleach.clean(project_description, tags=[], attributes={}, strip=True)


class DrawingForm(forms.ModelForm):
    class Meta:
        model = Drawing
        fields = [
            'drawing_no', 'drawing_title', 'drawing_description', 
            'discipline', 'drawing_type'
        ]
        widgets = {
            'drawing_no': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., A001, M001, E001',
                'maxlength': '4'
            }),
            'drawing_title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter drawing title'
            }),
            'drawing_description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter drawing description (optional)'
            }),
            'discipline': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'drawing_type': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., Floor Plan, Section, Detail'
            })
        }

class ReviewForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('revise', 'Request Revision')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'mr-2'
        })
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 4,
            'placeholder': 'Enter review comments (required for rejection and revision requests)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        comments = cleaned_data.get('comments')
        
        if action in ['reject', 'revise'] and not comments:
            raise forms.ValidationError('Comments are required when rejecting a project or requesting revision.')
        
        return cleaned_data

class BulkActionForm(forms.Form):
    """Form for bulk operations on projects"""
    ACTION_CHOICES = [
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
        ('revise', 'Request Revision for Selected'),
        ('obsolete', 'Mark as Obsolete'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter comments for bulk action (optional)'
        })
    )
    project_ids = forms.CharField(widget=forms.HiddenInput())
    
    def clean_project_ids(self):
        project_ids = self.cleaned_data.get('project_ids', '')
        if not project_ids:
            raise forms.ValidationError('No projects selected for bulk action.')
        
        try:
            # Convert comma-separated string to list of UUIDs
            ids = [id.strip() for id in project_ids.split(',') if id.strip()]
            if not ids:
                raise forms.ValidationError('No valid project IDs provided.')
            return ids
        except Exception:
            raise forms.ValidationError('Invalid project IDs format.')

class ProjectRestoreForm(forms.Form):
    """Form for restoring obsoleted projects"""
    restore_to_status = forms.ChoiceField(
        choices=[
            ('Draft', 'Draft'),
            ('Approved', 'Approved'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    restore_comments = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter reason for restoring this project'
        })
    )