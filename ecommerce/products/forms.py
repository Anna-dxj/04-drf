from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        label='Product name',
        widget=forms.TextInput(attrs={'placeholder': 'eg. Product'})
    )
    price = forms.DecimalField(
        required=True,
        label='Product price',
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 10.00'})
    )
    description = forms.CharField(
        required=True,
        label='Product description',
        widget=forms.Textarea(attrs={'placeholder': 'Description'})
    )
    stock = forms.IntegerField(
        required=True,
        label='Stock available',
        widget=forms.TextInput(attrs={'placeholder': 'eg. 500'})
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Product Category (choose at least one. cntrl+click to select multiple)',
        widget=forms.SelectMultiple
    )
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'stock', 'category']

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='')