from django import forms
from .models import MaintenanceRequest
from apps.properties.models import Property


class MaintenanceRequestCreateForm(forms.ModelForm):
    """
    Form for tenants to file a repair ticket.
    """
    class Meta:
        model = MaintenanceRequest
        fields = ['property', 'title', 'category', 'priority', 'description', 'attachment']
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Master bathroom sink pipe leaking'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe where the issue is located, when it started, and any symptoms...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_admin_role:
            # Filter properties to only those where tenant has an active lease or booking
            leased_properties = Property.objects.filter(leases__tenant=user).distinct()
            if leased_properties.exists():
                self.fields['property'].queryset = leased_properties
            else:
                self.fields['property'].queryset = Property.objects.all()


class MaintenanceRequestUpdateForm(forms.ModelForm):
    """
    Form for landlords to update repair status and document technician dispatch.
    """
    class Meta:
        model = MaintenanceRequest
        fields = ['status', 'landlord_response']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'landlord_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide status update, technician schedule, or completion notes for the tenant...'}),
        }

