import bleach
from django import forms
from django.contrib.auth.models import User
from .models import Project, Document

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name', 'project_description', 
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




class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'document_number', 'title', 'description', 'discipline', 'revision', 'file_path'
        ]
        widgets = {
            'document_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., A001, M001, E001',
                'maxlength': '20'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter document title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter document description (optional)'
            }),
            'discipline': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., Architecture, Engineering, MEP'
            }),
            'revision': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., A, B, C or 01, 02, 03'
            }),
            'file_path': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }

class ReviewForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approved & Endorsed'),
            ('conditional', 'Conditional Approval'),
            ('revise', 'Request for Revision'),
            ('reject', 'Rejected')
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:focus:border-indigo-400 transition-all duration-200 appearance-none cursor-pointer',
            'required': True
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
            ('Approved_Endorsed', 'Approved & Endorsed'),
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

class HistoryFilterForm(forms.Form):
    TYPE_CHOICES = [
        ('', 'All Types'),
        ('submission', 'Submissions'),
        ('change', 'Changes'),
    ]
    
    SORT_CHOICES = [
        ('-date', 'Date (Newest First)'),
        ('date', 'Date (Oldest First)'),
        ('project', 'Project Name (A-Z)'),
        ('-project', 'Project Name (Z-A)'),
        ('user', 'User (A-Z)'),
        ('-user', 'User (Z-A)'),
        ('type', 'Type'),
    ]
    
    # Project filter
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    # User filter
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    # Type filter
    entry_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    # Status filter
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Document.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    # Date range filters
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    # Sort field
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-date',
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Limit project choices based on user permissions
            if not getattr(user, 'profile', None) or user.profile.role.name not in ['Admin', 'Approver']:
                self.fields['project'].queryset = Project.objects.filter(submitted_by=user)
                self.fields['user'].queryset = User.objects.filter(id=user.id)