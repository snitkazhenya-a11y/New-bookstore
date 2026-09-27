from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'address', 'city', 'state', 'zip_code']