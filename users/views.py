from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegistroForm
from .models import User

def registro_view(request):
    form = RegistroForm(request.POST or None)
    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.username = usuario.email 
        usuario.save()
        login(request, usuario)
        return redirect('home')  
    return render(request, 'account/register.html', {'form': form})

def login_view(request):
    error = ''
    try:
        if request.method == 'POST':
            correo = request.POST.get('email')
            password = request.POST.get('password')
            usuario = authenticate(request, username=correo, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
            else:
                error = 'Correo o contraseña incorrectos.'
    except Exception as e:
        error = f"Error interno: {e}"
    return render(request, 'account/login.html', {'error': error})


def base_view(request):
    return render(request, 'base.html')