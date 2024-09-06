from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Shipping, Customer, Vendor
from django.contrib.auth.models import User
from .validate import validate_passwords_match

class CreateCustomerForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    street_address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 123 Sesame Rd.'})
    )
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City'})
    )
    state_district = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'State/District'}),
        label='State/District'
    )
    post_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 12345'})
    )
    country = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. USA'})
    )

    class Meta:
        model = Shipping
        fields = ['street_address', 'city', 'state_district', 'post_code', 'country']

class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'password123'})
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Must match password'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    email= forms.CharField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'eg. example@email.com'})
    )
    is_vendor = forms.BooleanField(
        required=False,
        label='I am a vendor'

    )
    class Meta: 
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user=super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('password_confirm')

        if password and confirm_password:
            validate_passwords_match(password, confirm_password)


class VendorForm(forms.ModelForm):
    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'company name'})
    )
    customer_service_email = forms.CharField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'eg. customerservice@email.com'}),
        label='Customer Service Email'
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'company description...'})
    )
    class Meta:
        model = Vendor
        fields = ['company_name', 'customer_service_email', 'description']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'password'})
    )

class UpdateVendorForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    email= forms.CharField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'eg. example@email.com'})
    )
    class Meta: 
        model = User
        fields = ['username', 'email']

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    email= forms.CharField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'eg. example@email.com'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    class Meta: 
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class UpdatePasswordForm(forms.Form):
    old_password = forms.CharField(
        required=True,
        label='Old password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Old password'})
    )
    new_password = forms.CharField(
        required=True,
        label='New password',
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Must match password'}),
        required=True,
        label='Confirm password'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        user = self.user
        cleaned_data = super().clean()

        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        password_confirm = cleaned_data.get('password_confirm')

        if not user.check_password(old_password):
            self.add_error('old_password', 'Incorrect password')
        
        if user.check_password(new_password):
            self.add_error('new_password', 'New password cannot be the same as old password')
        
        if new_password != password_confirm: 
            self.add_error('password_confirm', 'Passwords must match')

class ShippingForm(forms.ModelForm):
    street_address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 123 Sesame Rd.'})
    )
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City'})
    )
    state_district = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'State/District'}),
        label='State/District'
    )
    post_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 12345'})
    )
    country = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. USA'})
    )

    class Meta:
        model = Shipping
        fields = ['street_address', 'city', 'state_district', 'post_code', 'country']