from decimal import Decimal
from datetime import timedelta
from django import forms
from django.conf import settings
from django.utils import timezone
from .models import FoodListing, FoodPhoto
from django.core.validators import FileExtensionValidator

def validate_food_image(image):
    if image.size > 5 * 1024 * 1024:
        raise forms.ValidationError(
            "Image size must not exceed 5 MB."
        )

    uploaded_image = getattr(image, 'image', None)

    if uploaded_image is not None:
        if uploaded_image.format not in ['JPEG', 'PNG', 'WEBP']:
            raise forms.ValidationError(
                "Only JPG, PNG and WebP images are allowed."
            )

class FoodListingForm(forms.ModelForm):
    """
    Form for creating and updating surplus Food Listings by Donors.
    Includes embedded location fields to allow custom pickup spots.
    Quantity uses manual decimal input (no spinners or steppers).
    """
    photo = forms.ImageField(
        required=False,
        label="Food Photo (Optional)",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp']
            ),
            validate_food_image,
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/jpeg,image/png,image/webp',
            'id': 'id_food_photo',
        }),
        help_text="JPG, PNG or WebP. Maximum 5 MB."
    )

    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street address for pickup'})
    )
    area = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Dhanmondi / Banani / Mirpur / Uttara'})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Dhaka, Gazipur, Barishal, Savar',
            'list': 'city-suggestions',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = FoodListing
        fields = ['food_name', 'description', 'quantity', 'unit', 'expires_at']
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 50 Lunch Boxes (Rice & Chicken)'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Food condition, ingredients, allergen info, packaging details...'}),
            'quantity': forms.TextInput(attrs={'class': 'form-input', 'inputmode': 'decimal', 'placeholder': 'e.g. 25'}),
            'unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. meals, kg, portions, boxes'}),
            'expires_at': forms.DateTimeInput(
                attrs={'class': 'form-input', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise forms.ValidationError("Quantity is required.")
        try:
            quantity = Decimal(str(quantity))
        except Exception:
            raise forms.ValidationError("Quantity must be a valid number.")
        if not quantity.is_finite() or quantity <= Decimal('0.00'):
            raise forms.ValidationError("Quantity must be a valid number greater than zero.")
        return quantity.quantize(Decimal('0.01'))

    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if not expires_at:
            raise forms.ValidationError("Expiry date and time is required.")

        now = timezone.now()
        conf = getattr(settings, 'FOODFLOW_SETTINGS', {})
        min_minutes = conf.get('MIN_EXPIRY_MINUTES', 30)
        max_hours = conf.get('MAX_EXPIRY_HOURS', 72)

        min_allowed = now + timedelta(minutes=min_minutes)
        max_allowed = now + timedelta(hours=max_hours)

        if expires_at <= now:
            raise forms.ValidationError("Expiry date/time must be in the future.")

        if expires_at < min_allowed:
            raise forms.ValidationError(f"Expiry must be at least {min_minutes} minutes into the future to allow sufficient time for pickup.")

        if expires_at > max_allowed:
            raise forms.ValidationError(f"Expiry cannot exceed {max_hours} hours ({max_hours // 24} days) from now.")

        return expires_at

class FoodPhotoForm(forms.ModelForm):
    image = forms.ImageField(
        label="Food Photo",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp']
            ),
            validate_food_image,
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/jpeg,image/png,image/webp',
        }),
        help_text="JPG, PNG or WebP. Maximum 5 MB."
    )

    class Meta:
        model = FoodPhoto
        fields = ['image', 'caption']

        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Short description of the photo',
            }),
        }