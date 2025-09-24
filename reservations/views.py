from django.shortcuts import render
from .models import Mesa, Reserva


def check_availability(request):
    date = request.GET.get('date')
    time = request.GET.get('time')

    available_tables = []

    if date and time:
        # mesas ocupadas en esa fecha/hora
        reserved_tables = Reserva.objects.filter(
            fecha=date,
            hora=time
        ).values_list('mesa_id', flat=True)

        # todas las demás quedan disponibles
        available_tables = Mesa.objects.exclude(id__in=reserved_tables)

    return render(request, 'reservations/availability.html', {
        'available_tables': available_tables,
        'date': date,
        'time': time,
    })


def lista_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'reservations/mesas.html', {'mesas': mesas})
