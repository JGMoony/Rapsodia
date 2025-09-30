from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from reservations.models import Reserva
from users.forms import LoginForm, RegistroForm
from django.contrib.auth.decorators import login_required

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


@login_required
def perfil_usuario(request):
    reservas = Reserva.objects.filter(cliente=request.user).order_by("-fecha", "-hora")
    return render(request, "account/perfil.html", {"reservas": reservas})

def editar_perfil(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=request.user)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.username = usuario.email
            if form.cleaned_data['password1']:
                usuario.set_password(form.cleaned_data['password1'])
            usuario.save()
            login(request, usuario) 
            return redirect('perfil_usuario')
    else:
        form = RegistroForm(instance=request.user)

    return render(request, 'account/editar_perfil.html', {'form': form})

def editar_reserva(request, reserva_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        reserva = Reserva.objects.get(id=reserva_id, cliente=request.user)
    except Reserva.DoesNotExist:
        return redirect('perfil_usuario')

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        num_personas = request.POST.get('num_personas')

        reserva.fecha = fecha
        reserva.hora = hora
        reserva.num_personas = num_personas
        reserva.save()
        return redirect('perfil_usuario')

    return render(request, 'reservations/editar_reserva.html', {'reserva': reserva})

def base_view(request):
    return render(request, 'base.html')