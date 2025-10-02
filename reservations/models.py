from django.db import models
from Rapsodia import settings
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from datetime import datetime


class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=6)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero} (Capacidad: {self.capacidad})"


class Reserva(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('pasada', 'Pasada')
    ]

    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    personas = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activa')
    creada_en = models.DateTimeField(default=timezone.now)

    def clean(self):
        if isinstance(self.fecha, str):
            try:
                self.fecha = datetime.strptime(self.fecha, "%d-%m-%Y").date()
            except ValueError:
                raise ValidationError("Formato de fecha inválido (YYYY-MM-DD).")

        if isinstance(self.hora, str):
            try:
                try:
                    self.hora = datetime.strptime(self.hora, "%H:%M").time()
                except ValueError:
                    self.hora = datetime.strptime(self.hora, "%H:%M:%S").time()
            except ValueError:
                raise ValidationError("Formato de hora inválido (HH:MM o HH:MM:SS).")

        if self.mesa_id and self.personas and self.mesa and self.personas > self.mesa.capacidad:
            raise ValidationError(
                f"La mesa {self.mesa.numero} tiene capacidad máxima de {self.mesa.capacidad} personas."
            )

    def __str__(self):
        mesa_str = f"Mesa {self.mesa.numero}" if self.mesa else "Mesa NO ASIGNADA"
        return f"Reserva {self.id} - {mesa_str} - {self.fecha} {self.hora} ({self.personas} personas)"

    def actualizar_estado(self):
        ahora = timezone.now()
        inicio = datetime.combine(self.fecha, self.hora)
        if self.estado == 'activa' and inicio < ahora:
            self.estado = 'pasada'
            self.save()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        if self.estado == 'activa' and self.mesa:
            self.mesa.disponible = False
            self.mesa.save()

            if self.cliente and self.cliente.email:
                send_mail(
                    subject='Confirmación de reserva en Rapsodia',
                    message=(
                        f"Hola {self.cliente.nombre}, tu reserva está confirmada:\n\n"
                        f"Mesa: {self.mesa.numero}\n"
                        f"Fecha: {self.fecha}\n"
                        f"Hora: {self.hora}\n"
                        f"Personas: {self.personas}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.cliente.email],
                    fail_silently=False,
                )
        elif self.estado == 'cancelada' or self.estado == 'pasada' and self.mesa:
            self.mesa.disponible = True
            self.mesa.save(update_fields=["disponible"])
