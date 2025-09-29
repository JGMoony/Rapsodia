from django.db import models
from Rapsodia import settings
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from datetime import datetime, timedelta

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=6)  
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
        # Validación que NO requiere la mesa:
        if self.personas > 6:
            raise ValidationError("No se permiten más de 6 personas por reserva.")

        # Validación que SI requiere la mesa (CORRECCIÓN CRÍTICA):
        if self.mesa:
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

    def __str__(self):
        # Si self.mesa es None, usamos un valor por defecto para no fallar
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
        
        # Corrección: Verificar self.mesa antes de acceder a sus propiedades
        if self.estado == 'activa' and self.mesa:
            self.mesa.disponible = False
            self.mesa.save()
            send_mail(
                subject='Confirmación de reserva en Rapsodia',
                message=f"Hola {self.cliente.nombre}, tu reserva está confirmada:\n\n"
                        f"Mesa: {self.mesa.numero}\n"
                        f"Fecha: {self.fecha}\n"
                        f"Hora: {self.hora}\n"
                        f"Personas: {self.personas}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.cliente.email],
                fail_silently=False,
            )