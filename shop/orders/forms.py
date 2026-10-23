from django import forms

from config.forms import BootstrapFormMixin

from .models import Order


class OrderForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'comment']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 ...'}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
