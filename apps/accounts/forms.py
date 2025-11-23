import logging
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from .models import UserProfile

logger = logging.getLogger(__name__)

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
            'department', 'phone_number'
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
        """Save user profile with error handling"""
        try:
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
        except IntegrityError as e:
            logger.error(f"IntegrityError saving user profile: {e}")
            raise ValidationError("There was an error saving your profile. Please check your information and try again.")
        except DatabaseError as e:
            logger.error(f"DatabaseError saving user profile: {e}")
            raise ValidationError("Database error occurred. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error saving user profile: {e}")
            raise ValidationError("An unexpected error occurred. Please try again.")


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
    role = forms.ModelChoiceField(queryset=None, required=True)
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Role
        self.fields['role'].queryset = Role.objects.all()
        add_tailwind_classes(self.fields)
        self.order_fields(('username', 'first_name', 'last_name', 'email', 'role'))

    def save(self, commit=True):
        """Save admin user creation with error handling"""
        try:
            user = super().save(commit=False)
            user.set_unusable_password()
            
            role = self.cleaned_data.get('role')
            if role and role.name in ['Admin', 'Approver']:
                user.is_staff = True
                if role.name == 'Admin':
                    user.is_superuser = True
            
            if commit:
                user.save()
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = role
                profile.save()
            return user
        except IntegrityError as e:
            logger.error(f"IntegrityError creating admin user: {e}")
            raise ValidationError("There was an error creating the user. Please check that the username and email are unique.")
        except DatabaseError as e:
            logger.error(f"DatabaseError creating admin user: {e}")
            raise ValidationError("Database error occurred. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error creating admin user: {e}")
            raise ValidationError("An unexpected error occurred. Please try again.")


class AdminUserUpdateForm(forms.ModelForm):
    """Form for an admin to update a user's details and profile."""
    department = forms.CharField(max_length=100, required=False)
    role = forms.ModelChoiceField(queryset=None, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Role
        self.fields['role'].queryset = Role.objects.all()
        
        if hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['department'].initial = profile.department
            self.fields['role'].initial = profile.role
        add_tailwind_classes(self.fields)
        self.order_fields(('username', 'first_name', 'last_name', 'email', 'role', 'department', 'is_staff', 'is_active'))

    def save(self, commit=True):
        """Save admin user update with error handling"""
        try:
            user = super().save(commit)
            if commit and hasattr(user, 'profile'):
                profile = user.profile
                profile.department = self.cleaned_data.get('department')
                profile.role = self.cleaned_data.get('role')
                profile.save()
            return user
        except IntegrityError as e:
            logger.error(f"IntegrityError updating admin user: {e}")
            raise ValidationError("There was an error updating the user. Please check that the email is unique.")
        except DatabaseError as e:
            logger.error(f"DatabaseError updating admin user: {e}")
            raise ValidationError("Database error occurred. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error updating admin user: {e}")
            raise ValidationError("An unexpected error occurred. Please try again.")


class UserSearchForm(forms.Form):
    """Form for searching/filtering the user list in the admin view."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name, email, etc...'})
    )
    role = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Roles"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses'), ('active', 'Active'), ('inactive', 'Inactive'), ('staff', 'Staff')],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Role
        self.fields['role'].queryset = Role.objects.all()
        add_tailwind_classes(self.fields)