from datetime import datetime, timedelta
from .forms import EditarReservaForm, ReservaForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DisponibilidadForm
from .models import Mesa, Reserva

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
                capacidad__gte=personas
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
            personas = request.POST.get("personas")
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
    reserva.save()
    messages.info(request, "Reserva cancelada.")
    return redirect("perfil_usuario")

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