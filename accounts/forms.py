from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from config.forms import BootstrapFormMixin

from .models import User


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(label='Электронная почта')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
