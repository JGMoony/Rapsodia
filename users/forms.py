from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'nombre', 'apellido', 'password1', 'password2']

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError("La contraseña debe contener letras y números.")
        return password