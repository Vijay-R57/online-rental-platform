from django import forms
from .models import RentalApplication, Booking, Lease


class RentalApplicationForm(forms.ModelForm):
    """
    Form for tenants to submit an application for a rental listing.
    """
    class Meta:
        model = RentalApplication
        fields = [
            'employment_status', 'employer_name', 'annual_income',
            'credit_score_range', 'occupants_count', 'has_pets',
            'pets_description', 'proposed_move_in', 'lease_term_months',
            'message_to_landlord'
        ]
        widgets = {
            'employment_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Full-Time Employed, Self-Employed, Student'}),
            'employer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or Institution name'}),
            'annual_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '100', 'min': '0'}),
            'credit_score_range': forms.Select(attrs={'class': 'form-select'}),
            'occupants_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '15'}),
            'has_pets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 Golden Retriever, vaccinated'}),
            'proposed_move_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lease_term_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '36'}),
            'message_to_landlord': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Introduce yourself and any special preferences to the property owner...'}),
        }


class ApplicationReviewForm(forms.ModelForm):
    """
    Form for landlords to approve or decline a rental application.
    """
    class Meta:
        model = RentalApplication
        fields = ['status', 'owner_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'owner_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide feedback or terms for the applicant...'}),
        }


class LeaseCreationForm(forms.ModelForm):
    """
    Form for landlords to initialize and formalize a lease agreement for an approved booking.
    """
    class Meta:
        model = Lease
        fields = [
            'start_date', 'end_date', 'monthly_rent', 'security_deposit',
            'rent_due_day', 'terms', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rent_due_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '28'}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

