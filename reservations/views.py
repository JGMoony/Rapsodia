from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import EditarReservaForm, ReservaForm, DisponibilidadForm
from .models import Mesa, Reserva
from users.models import User
import json
from calendar import month_name


# ------------------------------
#  VISTAS DE RESERVAS CLIENTE
# ------------------------------

@login_required
def disponibilidad_y_reserva(request):
    form = DisponibilidadForm(request.POST or None)
    mesas_disponibles = None
    fecha = hora = personas = None

    if request.method == "POST":
        if "consultar" in request.POST and form.is_valid():
            fecha = form.cleaned_data["fecha"]
            hora = form.cleaned_data["hora"]
            personas = form.cleaned_data["personas"]

            mesas_disponibles = Mesa.objects.filter(
                capacidad__gte=personas, disponible=True
            ).exclude(
                reserva__fecha=fecha,
                reserva__hora=hora,
                reserva__estado="activa"
            )

            return render(request, "reservations/availability.html", {
                "form": form,
                "mesas_disponibles": mesas_disponibles,
                "fecha": fecha,
                "hora": hora,
                "personas": personas,
            })

        elif "reservar" in request.POST:
            mesa_id = request.POST.get("mesa_id")
            mesa = get_object_or_404(Mesa, id=mesa_id)
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            personas = request.POST.get("personas")

            datos = {
                "mesa": mesa.numero,
                "capacidad": mesa.capacidad,
                "fecha": fecha,
                "hora": hora,
                "personas": personas,
                "cliente": request.user.get_full_name(),
            }
            return render(request, "reservations/confirmar_reserva.html", {
                "datos": datos,
                "mesa_id": mesa.id,
                "fecha": fecha,
                "hora": hora,
                "personas": personas,
            })

    return render(request, "reservations/availability.html", {
        "form": form,
        "mesas_disponibles": mesas_disponibles,
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
    })

@login_required
def confirmar_reserva(request):
    if request.method == "POST":
        if "confirmar" in request.POST:
            mesa_id = request.POST.get("mesa_id")
            mesa = get_object_or_404(Mesa, id=mesa_id)
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            personas = int(request.POST.get("personas"))  # ✅ Convertir a entero
            cliente = request.user

            reserva = Reserva.objects.create(
                mesa=mesa,
                fecha=fecha,
                hora=hora,
                personas=personas,
                cliente=cliente
            )
            return render(request, "reservations/reserva_confirmada.html", {"reserva": reserva})

        elif "editar" in request.POST:
            form = DisponibilidadForm(initial={
                "fecha": request.POST.get("fecha"),
                "hora": request.POST.get("hora"),
                "personas": request.POST.get("personas")
            })
            return render(request, "reservations/availability.html", {"form": form})

        elif "cancelar" in request.POST:
            return redirect("disponibilidad_y_reserva")

    return redirect("disponibilidad_y_reserva")



@login_required
def perfil_usuario(request):
    reservas = Reserva.objects.filter(cliente=request.user).order_by("-fecha", "-hora")
    return render(request, "account/perfil.html", {"reservas": reservas})


@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    dt_reserva = datetime.combine(reserva.fecha, reserva.hora)
    dt_actual = datetime.now()

    if dt_reserva - dt_actual < timedelta(hours=24):
        messages.error(request, "Solo puedes cancelar la reserva con al menos 24 horas de anticipación.")
        return redirect("perfil_usuario")

    reserva.estado = "cancelada"
    reserva.mesa.disponible = True
    reserva.save()
    messages.info(request, "Reserva cancelada.")
    return redirect("perfil_usuario")


@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if request.method == "POST":
        form = EditarReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva actualizada correctamente.")
            return redirect("perfil_usuario")
    else:
        form = EditarReservaForm(instance=reserva)

    return render(request, "reservations/editar_reserva.html", {"form": form})


# ------------------------------
#  DASHBOARD ADMINISTRATIVO
# ------------------------------
@user_passes_test(lambda u: u.is_staff)  # Solo admin puede ver el panel
def admin_dashboard(request):
    clientes = User.objects.all()
    mesas = Mesa.objects.all()
    reservas = Reserva.objects.all().order_by("-fecha", "-hora")

    filtro = request.GET.get("filtro", "semana")
    mes = request.GET.get("mes")  # 👈 filtro por mes
    hoy = now()

    # --- Filtro de mes ---
    if mes:
        reservas = reservas.filter(fecha__month=mes)

    # --- Gráfica principal: reservas en el tiempo ---
    if filtro == "semana":
        inicio = hoy - timedelta(days=7)
        data = (
            reservas.filter(fecha__gte=inicio)
            .extra({"day": "date(fecha)"})
            .values("day")
            .annotate(total=Count("id"))
        )
        labels = [str(d["day"]) for d in data]
        values = [d["total"] for d in data]
    else:
        inicio = hoy - timedelta(days=30)
        data = (
            reservas.filter(fecha__gte=inicio)
            .extra({"month": "strftime('%%m', fecha)"})
            .values("month")
            .annotate(total=Count("id"))
        )
        labels = [f"Mes {d['month']}" for d in data]
        values = [d["total"] for d in data]

    # --- Días más concurridos ---
    dias_semana = (
        reservas.extra({"dow": "strftime('%%w', fecha)"})
        .values("dow")
        .annotate(total=Count("id"))
        .order_by("dow")
    )

    nombres_dias = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    dias_dict = {i: 0 for i in range(7)}
    for d in dias_semana:
        dias_dict[int(d["dow"])] = d["total"]

    dias_labels = [nombres_dias[i] for i in range(7)]
    dias_counts = [dias_dict[i] for i in range(7)]

    # --- Meses disponibles para el select ---
    meses_disponibles = (
        Reserva.objects.dates("fecha", "month")
        .distinct()
        .values_list("fecha__month", flat=True)
    )

    MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                 ]

    meses_contexto = [
        {"mes": m, "nombre": MESES_ES[m]} for m in sorted(set(meses_disponibles))
    ]

    context = {
        "clientes": clientes,
        "mesas": mesas,
        "reservas": reservas,
        "labels": json.dumps(labels if labels else []),
        "data": json.dumps(values if values else []),
        "filtro": filtro,
        "reservas_activas": reservas.filter(estado="activa").count(),
        "reservas_canceladas": reservas.filter(estado="cancelada").count(),
        "reservas_pasadas": reservas.filter(estado="pasada").count(),
        "dias_labels": json.dumps(dias_labels),
        "dias_counts": json.dumps(dias_counts),
        "meses_disponibles": meses_contexto,
        "mes_seleccionado": int(mes) if mes else None,
    }
    return render(request, "reservations/admin_dashboard.html", context)
# ------------------------------
#  CRUD DE MESAS (CBV)
# ------------------------------

class MesaListView(ListView):
    model = Mesa
    template_name = "reservations/mesa_list.html"


class MesaCreateView(CreateView):
    model = Mesa
    fields = ["numero", "capacidad", "disponible"]
    template_name = "reservations/mesa_form.html"
    success_url = reverse_lazy("mesa_list")


class MesaUpdateView(UpdateView):
    model = Mesa
    fields = ["numero", "capacidad", "disponible"]
    template_name = "reservations/mesa_form.html"
    success_url = reverse_lazy("mesa_list")


class MesaDeleteView(DeleteView):
    model = Mesa
    template_name = "reservations/mesa_confirm_delete.html"
    success_url = reverse_lazy("mesa_list")

    def get(self, request, *args, **kwargs):
        print("kwargs:", kwargs)
        return super().get(request, *args, **kwargs)

