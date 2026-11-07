from django import forms
from .models import Property, PropertyImage, Amenity


class PropertyForm(forms.ModelForm):
    """
    Form for creating and updating rental property listings.
    """
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'status', 'description',
            'rent_amount', 'security_deposit', 'bedrooms', 'bathrooms',
            'area_sqft', 'furnished_status', 'pet_friendly', 'available_from',
            'address', 'city', 'state', 'postal_code',
            'amenities', 'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Luxury 2-Bedroom Apartment in Downtown'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide a detailed overview of the property, floor plan, views, etc.'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '20'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20'}),
            'area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'min': '50'}),
            'furnished_status': forms.Select(attrs={'class': 'form-select'}),
            'pet_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main Street, Apt 4B'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP / Postal Code'}),
            'amenities': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PropertyImageForm(forms.ModelForm):
    """
    Form for adding extra photos to a property's gallery.
    """
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Master Bedroom, Living Room'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

