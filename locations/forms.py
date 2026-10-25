from django import forms
from .models import Location


class LocationForm(forms.ModelForm):
    """
    Form used for creating or associating addresses.
    Reuses existing locations using get_or_create logic in services/views.
    Postal code has been removed.
    """
    class Meta:
        model = Location
        fields = ['address', 'area', 'city', 'latitude', 'longitude']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. House #, Road #, Street name'}),
            'area': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Dhanmondi / Banani / Mirpur / Uttara'}),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Dhaka, Gazipur, Barishal, Savar',
                'list': 'city-suggestions',
                'autocomplete': 'off'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()
        if not address:
            raise forms.ValidationError("Address is required.")
        return address

    def clean_area(self):
        area = self.cleaned_data.get('area', '').strip()
        if not area:
            raise forms.ValidationError("Area is required.")
        return area

    def clean_city(self):
        city = self.cleaned_data.get('city', '').strip()
        if not city:
            raise forms.ValidationError("City is required.")
        return city
