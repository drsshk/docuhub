from django import forms
from django.forms import inlineformset_factory
from .models import Version, VersionImprovement


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['version_number', 'version_type', 'description', 'is_current']
        widgets = {
            'version_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1.2.0'
            }),
            'version_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this version...'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class VersionImprovementForm(forms.ModelForm):
    class Meta:
        model = VersionImprovement
        fields = ['improvement_type', 'title', 'description', 'order']
        widgets = {
            'improvement_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for this improvement...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Detailed description...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0,
                'min': 0
            })
        }


# Create an inline formset for version improvements
VersionImprovementFormSet = inlineformset_factory(
    Version,
    VersionImprovement,
    form=VersionImprovementForm,
    extra=3,
    can_delete=True
)