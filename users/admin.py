from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import CustomUser

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

# Override the default admin login form globally
admin.site.login_form = EmailAuthenticationForm

# Register CustomUser if not already registered
admin.site.register(CustomUser)
