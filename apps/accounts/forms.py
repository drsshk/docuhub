from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.core.exceptions import ValidationError
from .models import UserProfile, Role

# --- Helper function for styling ---

def add_tailwind_classes(fields):
    """A helper function to apply Tailwind CSS classes to form fields."""
    for field_name, field in fields.items():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.update({
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        else:
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            })

# --- Forms for Public/User-Facing Views ---




class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile."""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = [
            'department', 'job_title', 'phone_number', 
            'bio', 'location', 'email_notifications'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
        
        self.order_fields(['first_name', 'last_name', 'email'] + list(self.Meta.fields))
        add_tailwind_classes(self.fields)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class UserPasswordChangeForm(DjangoPasswordChangeForm):
    """Form for a user to change their own password, requiring the old password."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_tailwind_classes(self.fields)


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset."""
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_tailwind_classes(self.fields)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("No user is associated with this username.")
        return username


# --- Forms for Admin Views ---

class AdminUserCreationForm(forms.ModelForm):
    """A form for admins to create new users and assign roles."""
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True, empty_label="-- Select a Role --")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_tailwind_classes(self.fields)
        self.order_fields(('username', 'first_name', 'last_name', 'email', 'role'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        
        role_obj = self.cleaned_data.get('role')
        if role_obj and role_obj.name.lower() in ['admin', 'approver']:
            user.is_staff = True
            if role_obj.name.lower() == 'admin':
                user.is_superuser = True
        
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role_obj
            profile.save()
        return user


class AdminUserUpdateForm(forms.ModelForm):
    """Form for an admin to update a user's details and profile."""
    department = forms.ChoiceField(choices=UserProfile.DEPARTMENT_CHOICES, required=False)
    job_title = forms.ChoiceField(choices=UserProfile.JOB_TITLE_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True, empty_label="-- Select a Role --")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['department'].initial = profile.department
            self.fields['job_title'].initial = profile.job_title
            self.fields['role'].initial = profile.role
        add_tailwind_classes(self.fields)
        self.order_fields(('username', 'first_name', 'last_name', 'email', 'role', 'department', 'job_title', 'is_staff', 'is_active'))

    def save(self, commit=True):
        user = super().save(commit)
        if commit and hasattr(user, 'profile'):
            profile = user.profile
            profile.department = self.cleaned_data.get('department')
            profile.job_title = self.cleaned_data.get('job_title')
            profile.role = self.cleaned_data.get('role')
            profile.save()
        return user


class UserSearchForm(forms.Form):
    """Form for searching/filtering the user list in the admin view."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name, email, etc...'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="All Roles"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses'), ('active', 'Active'), ('inactive', 'Inactive'), ('staff', 'Staff')],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_tailwind_classes(self.fields)