from django.db import models
from users.models import User
from django.utils import timezone

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero} ({'Disponible' if self.disponible else 'Ocupada'})"

class Reserva(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('pasada', 'Pasada')
    ], default='activa')
    creada_en = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reserva {self.id} - Mesa {self.mesa.numero} - {self.fecha} {self.hora}"