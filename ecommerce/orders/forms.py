from django import forms
from .models import Payment, SpecialShipping
from .validate import validate_number, validate_expiration_month

class CardForm(forms.ModelForm):
    method = forms.ChoiceField(
        choices= [],
        required=True,
        label='Payment Method'
    )
    card_number = forms.CharField(
        max_length=16, 
        required=True, 
        label='Card Number',
        widget=forms.TextInput(attrs={'placeholder': 'XXXX XXXX XXXX XXXX'}),
        validators=[validate_number]
    )
    card_expiration_month = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder':'MM'}),
        label='Expiration Month',
        max_length=2,
        validators=[validate_number, validate_expiration_month]
    )
    card_expiration_year =forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'YY'}),
        label='Expiration Year',
        max_length=2,
        validators=[validate_number]
    )
    card_cvc = forms.CharField(
        max_length=3, 
        required=True, 
        label='CVC',
        widget=forms.TextInput(attrs={'placeholder': 'XXX'}),
        validators=[validate_number]
    )

    class Meta:
        model = Payment
        fields = ['method']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['method'].choices = [
            (method.id, method.method) for method in Payment.objects.all()
        ]

class TemporaryShippingForm(forms.ModelForm):
    recipient_first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        label='First name'
    )
    recipient_last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
        label='Last name'
    )
    street_address = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 123 Sesame St.'}),
        label='Street address'
    )
    city = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
        label='City'
    )
    state_district = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'State/District'}),
        label='State/District'
    )
    post_code = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Postal code'}),
        label='Postal Code'
    )
    country = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'eg. USA'}),
        label='Country'
    )

    class Meta:
        model = SpecialShipping
        fields = ['recipient_first_name', 'recipient_last_name', 'street_address', 'city', 'state_district', 'post_code', 'country']