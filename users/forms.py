from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User

class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "nombre", 
            "apellido", 
            "email", 
            "password1", 
            "password2"
            )
        
class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nombre", "apellido", "email"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }