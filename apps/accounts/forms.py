from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, TenantDocument


class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password, role, and contact information.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit public self-registration roles strictly to OWNER and TENANT
        self.fields['role'].choices = [
            (CustomUser.Role.TENANT, 'Tenant (Looking to rent)'),
            (CustomUser.Role.OWNER, 'Property Owner (Looking to list properties)'),
        ]
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users in Django Admin.
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'profile_picture', 'is_verified', 'bio',
            'address', 'city', 'state', 'postal_code', 'occupation',
            'company_name', 'emergency_contact_name', 'emergency_contact_phone'
        )


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for users to edit their own profile and personal details.
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'profile_picture', 'bio', 'address', 'city', 'state',
            'postal_code', 'occupation', 'company_name',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Software Engineer, Architect, etc.'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TenantDocumentUploadForm(forms.ModelForm):
    """
    Form for tenants to upload identification and lease verification documents.
    """
    class Meta:
        model = TenantDocument
        fields = ['document_type', 'title', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Passport, State ID, March 2026 Payslip'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
