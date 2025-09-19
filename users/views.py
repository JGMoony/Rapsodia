from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegistroForm

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('login')  # Ajusta según tu ruta principal
    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        password = request.POST['password']
        usuario = authenticate(request, correo=correo, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('home')
        else:
            error = "Correo o contraseña incorrectos"
            return render(request, 'users/login.html', {'error': error})
    return render(request, 'users/login.html')