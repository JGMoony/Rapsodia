from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ReservaForm
from .models import Reserva

@login_required
def crear_reserva(request):
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if "confirmar" in request.POST:
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Reserva confirmada con éxito.")
                    return redirect("lista_reservas")  # Debes definir esta vista
                except Exception as e:
                    messages.error(request, str(e))
            return render(request, "reservations/crear_reserva.html", {"form": form})

        elif form.is_valid():
            datos = form.cleaned_data
            return render(request, "reservations/confirmar_reserva.html", {"form": form, "datos": datos})

    else:
        form = ReservaForm()
    return render(request, "reservations/crear_reserva.html", {"form": form})

@login_required
def lista_reservas(request):
    reservas = Reserva.objects.all().order_by("-fecha", "-hora")
    return render(request, "reservations/lista_reservas.html", {"reservas": reservas})

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado = "cancelada"
    reserva.save()
    return redirect("lista_reservas")