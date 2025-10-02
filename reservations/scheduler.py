from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Reserva
from datetime import timedelta,datetime
from apscheduler.schedulers.background import BackgroundScheduler

def enviar_recordatorios():
    ahora = timezone.now()
    reservas = Reserva.objects.filter(estado="activa")

    for reserva in reservas:
        inicio = datetime.combine(reserva.fecha, reserva.hora)
        inicio = timezone.make_aware(inicio, timezone.get_current_timezone())
        tiempo_restante = inicio - ahora

        if timedelta(minutes=0) < tiempo_restante <= timedelta(hours=1):
            if reserva.cliente and reserva.cliente.email:
                send_mail(
                    subject="Recordatorio de tu reserva en Rapsodia",
                    message=(
                        f"Hola {reserva.cliente.nombre}, recuerda tu reserva:\n\n"
                        f"Mesa: {reserva.mesa.numero}\n"
                        f"Fecha: {reserva.fecha}\n"
                        f"Hora: {reserva.hora}\n"
                        f"Personas: {reserva.personas}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reserva.cliente.email],
                    fail_silently=False,
                )

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(enviar_recordatorios, "interval", minutes=30)
    scheduler.start()
