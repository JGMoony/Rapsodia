from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from reservations.models import Reserva, Mesa
from users.forms import LoginForm, RegistroForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils.timezone import now, timedelta
import datetime


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
            print("login exitoso")
            # Redirige según tipo de usuario
            if usuario.is_staff or usuario.is_superuser:
                print("usuario admin, redirigiendo a dashboard")
                return redirect('admin_dashboard')  # nombre de tu dashboard de admin
            else:
                print("usuario normal, redirigiendo a home")
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


def home(request):
    return render(request, 'home.html')


# ==============================
# 🚀 Dashboard del administrador
# ==============================
@login_required
def admin_dashboard(request):
    # Estadísticas generales
    reservas_activas = Reserva.objects.filter(estado="activa").count()
    reservas_canceladas = Reserva.objects.filter(estado="cancelada").count()
    reservas_pasadas = Reserva.objects.filter(estado="pasada").count()

    # Filtro de fechas (semana o mes)
    filtro = request.GET.get("filtro", "semana")
    hoy = now().date()

    if filtro == "mes":
        fecha_inicio = hoy - timedelta(days=30)
    else:  # por defecto semana
        fecha_inicio = hoy - timedelta(days=7)

    reservas = Reserva.objects.filter(fecha__gte=fecha_inicio)

    # 📊 Datos para gráfico de reservas en el tiempo
    labels = []
    data = []
    rango_fechas = [fecha_inicio + timedelta(days=i) for i in range((hoy - fecha_inicio).days + 1)]
    for dia in rango_fechas:
        labels.append(dia.strftime("%d-%m"))
        data.append(reservas.filter(fecha=dia).count())

    # 📊 Datos para gráfico de días más concurridos
    dias_labels = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dias_data = [0] * 7

    reservas_por_dia = reservas.values("fecha").annotate(total=Count("id"))
    for r in reservas_por_dia:
        dia_semana = r["fecha"].weekday()  # 0=lunes, 6=domingo
        dias_data[dia_semana] += r["total"]

    # Listado de mesas
    mesas = Mesa.objects.all()

    return render(request, "dashboard/admin_dashboard.html", {
        "reservas_activas": reservas_activas,
        "reservas_canceladas": reservas_canceladas,
        "reservas_pasadas": reservas_pasadas,
        "labels": labels,
        "data": data,
        "dias_labels": dias_labels,
        "dias_data": dias_data,
        "reservas": reservas,
        "mesas": mesas,
        "filtro": filtro,
    })
