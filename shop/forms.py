from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Product
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2', 'phone_number', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'details', 'size_or_amount', 'picture', 'isle', 'price', 'barcode']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }   

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']