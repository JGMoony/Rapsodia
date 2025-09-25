from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ReservaForm
from .models import Mesa, Reserva

@login_required
def crear_reserva(request):
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if "confirmar" in request.POST:
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Reserva confirmada con éxito.")
                    return redirect("lista_reservas")
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

def check_availability(request):
    date = request.GET.get('date')
    time = request.GET.get('time')

    available_tables = []

    if date and time:
        reserved_tables = Reserva.objects.filter(
            fecha=date,
            hora=time
        ).values_list('mesa_id', flat=True)

        available_tables = Mesa.objects.exclude(id__in=reserved_tables)

    return render(request, 'reservations/availability.html', {
        'available_tables': available_tables,
        'date': date,
        'time': time,
    })


def lista_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'reservations/mesas.html', {'mesas': mesas})
