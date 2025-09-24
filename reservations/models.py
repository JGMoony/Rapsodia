from django.db import models
from users.models import User
from django.utils import timezone


class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=6)  # cada mesa soporta hasta 6 personas
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero} (Capacidad: {self.capacidad})"


class Reserva(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    personas = models.IntegerField(default=1)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activa', 'Activa'),
            ('cancelada', 'Cancelada'),
            ('pasada', 'Pasada'),
        ],
        default='activa'
    )
    creada_en = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reserva {self.id} - Mesa {self.mesa.numero} - {self.fecha} {self.hora}"

    class Meta:
        unique_together = ('mesa', 'fecha', 'hora')  # 🔒 evita doble reserva misma mesa/fecha/hora
