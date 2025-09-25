from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import LoginForm, RegistroForm

def registro_view(request):
    form = RegistroForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.username = usuario.email
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save()

            login(request, usuario)
            return redirect('home')
        else:
            print(form.errors)

    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    error = ''
    if request.method == 'POST' and form.is_valid():
        correo = form.cleaned_data['email']
        password = form.cleaned_data['password']
        usuario = authenticate(request, username=correo, password=password)
        if usuario:
            login(request, usuario)
            print("login exitoso, redirigiendo a home")
            return redirect('home')
        else:
            error = 'Correo o contraseña incorrectos.'
    return render(request, 'account/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def base_view(request):
    return render(request, 'base.html')