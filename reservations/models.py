from django.db import models
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=6)  # cada mesa soporta hasta 6 personas
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero} (Capacidad: {self.capacidad})"


class Reserva(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    personas = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('pasada', 'Pasada')
    ], default='activa')
    creada_en = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.personas > 6:
            raise ValidationError("No se permiten más de 6 personas por reserva.")

        if self.personas > self.mesa.capacidad:
            raise ValidationError(f"La mesa solo tiene capacidad para {self.mesa.capacidad} personas.")

        inicio_reserva = datetime.combine(self.fecha, self.hora)
        fin_reserva = inicio_reserva + timedelta(hours=3)

        reservas_existentes = Reserva.objects.filter(
            mesa=self.mesa,
            fecha=self.fecha,
            estado='activa'
        ).exclude(id=self.id)

        for r in reservas_existentes:
            inicio_existente = datetime.combine(r.fecha, r.hora)
            fin_existente = inicio_existente + timedelta(hours=3)
            if (inicio_reserva < fin_existente) and (fin_reserva > inicio_existente):
                raise ValidationError("La mesa ya está reservada en este horario.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.id} - Mesa {self.mesa.numero} - {self.fecha} {self.hora} ({self.personas} personas)"
