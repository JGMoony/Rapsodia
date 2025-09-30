from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DisponibilidadForm
from .models import Mesa, Reserva

@login_required
def disponibilidad_y_reserva(request):
    form = DisponibilidadForm(request.POST or None)
    mesas_disponibles = None
    reserva_confirmada = None
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
        elif "reservar" in request.POST:
            mesa_id = request.POST.get("mesa_id")
            mesa = get_object_or_404(Mesa, id=mesa_id)
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            personas = request.POST.get("personas")

            reserva_confirmada = Reserva.objects.create(
                mesa=mesa,
                fecha=fecha,
                hora=hora,
                personas=personas,
                cliente=request.user
            )

            messages.success(request, "Reserva creada exitosamente.")

    return render(request, "reservations/availability.html", {
        "form": form,
        "mesas_disponibles": mesas_disponibles,
        "reserva_confirmada": reserva_confirmada,
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
    })


@login_required
def lista_reservas(request):
    reservas = Reserva.objects.all().order_by("-fecha", "-hora")
    return render(request, "reservations/lista_reservas.html", {"reservas": reservas})


@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado = "cancelada"
    reserva.save()
    messages.info(request, "Reserva cancelada.")
    return redirect("lista_reservas")


@login_required
def lista_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, "reservations/mesas.html", {"mesas": mesas})
