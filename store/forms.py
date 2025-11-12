from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'street_address', 'city', 'state', 'postal_code', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'street_address': forms.Textarea(attrs={'placeholder': 'Enter complete address', 'rows': 3}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter state'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Enter PIN code'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
        }

class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[('card', 'Credit/Debit Card'), ('cod', 'Cash on Delivery')],
        widget=forms.RadioSelect
    )