from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator
from .models import Claim


class ClaimForm(forms.Form):
    """
    Form used by verified Recipients to claim a quantity of food.
    Uses manual decimal text typing (no spin buttons or automatic step increments).
    """
    claimed_quantity = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'inputmode': 'decimal',
            'id': 'id_claimed_quantity',
            'placeholder': 'Enter quantity to claim (e.g. 5)'
        }),
        label="Quantity to Claim"
    )

    def __init__(self, *args, max_available=None, unit="units", **kwargs):
        super().__init__(*args, **kwargs)
        if max_available is not None:
            try:
                self.max_available = Decimal(str(max_available)).quantize(Decimal('0.01'))
            except Exception:
                self.max_available = None
        else:
            self.max_available = None

        if self.max_available is not None:
            self.fields['claimed_quantity'].help_text = (
                f"Minimum claim: 0.10 {unit}. "
                f"Available: {self.max_available:.2f} {unit}."
            )

    def clean_claimed_quantity(self):
        val = self.cleaned_data.get('claimed_quantity', '').strip()

        if not val:
            raise forms.ValidationError("Please enter a quantity to claim.")

        try:
            qty = Decimal(val)
        except Exception:
            raise forms.ValidationError("Please enter a valid numeric quantity.")

        if not qty.is_finite() or qty < Decimal('0.10'):
            raise forms.ValidationError("Minimum claim quantity is 0.10.")

        try:
            qty = qty.quantize(Decimal('0.01'))
        except Exception:
            raise forms.ValidationError("Please enter a valid numeric quantity.")

        if self.max_available is not None and qty > self.max_available:
            raise forms.ValidationError(
                f"Cannot claim more than the available quantity "
                f"({self.max_available:.2f})."
            )

        return qty


class PickupVerificationForm(forms.Form):
    """
    Form used by Donors to verify the 8-character pickup code presented by the recipient.
    """
    pickup_code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-input code-input',
            'placeholder': '8-CHAR CODE (e.g. 4F9B2C1A)',
            'style': 'text-transform: uppercase; letter-spacing: 0.15em; font-family: monospace; font-size: 1.25rem; text-align: center;'
        }),
        label="Enter Recipient's Pickup Code"
    )

    def clean_pickup_code(self):
        code = self.cleaned_data.get('pickup_code', '').strip().upper()
        if len(code) != 8:
            raise forms.ValidationError("Pickup code must be exactly 8 characters long.")
        return code
