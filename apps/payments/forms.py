from django import forms
from .models import Payment


class PaymentInitiateForm(forms.ModelForm):
    """
    Form to initialize an invoice or rent obligation for a lease.
    """
    class Meta:
        model = Payment
        fields = ['payment_type', 'amount', 'description', 'due_date']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., November 2026 Monthly Rent'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class SimulatedCheckoutForm(forms.Form):
    """
    Simulated sandbox payment checkout form.
    Explicitly identified as Sandbox / Demo payment simulation.
    """
    payment_method = forms.ChoiceField(
        choices=[
            ('CARD', 'Credit / Debit Card (Simulated)'),
            ('UPI', 'UPI Virtual ID (Simulated)'),
            ('BANK_TRANSFER', 'Simulated Direct Net Banking'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'paymentMethodSelect'})
    )
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4242 &bull;&bull;&bull;&bull; &bull;&bull;&bull;&bull; 4242', 'id': 'cardNumberInput'})
    )
    card_expiry = forms.CharField(
        required=False,
        max_length=7,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY', 'id': 'cardExpiryInput'})
    )
    card_cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV', 'id': 'cardCvvInput'})
    )
    upi_id = forms.CharField(
        required=False,
        max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username@bank or phone@upi', 'id': 'upiIdInput'})
    )

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        if method == 'CARD':
            card_num = cleaned_data.get('card_number')
            if not card_num or len(card_num.replace(' ', '')) < 12:
                # Default to demo card if blank for ease of college grading demo
                cleaned_data['card_number'] = '4242-4242-4242-4242'
        elif method == 'UPI':
            upi = cleaned_data.get('upi_id')
            if not upi:
                cleaned_data['upi_id'] = 'tenant@okaxis'
        return cleaned_data

