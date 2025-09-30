from datetime import time, datetime
from django import forms
from .models import Reserva
from django.core.exceptions import ValidationError

class TimeSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        time_choices = []
        for hour in range(10, 23):  # de 10 a 22
            for minute in (0, 30):
                t = time(hour, minute)
                label = t.strftime('%I:%M %p')  # formato 12h
                value = t.strftime('%H:%M')      # formato 24h
                time_choices.append((value, label))
        super().__init__(choices=time_choices, *args, **kwargs)

class ReservaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Fecha de la reserva"
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        label="Hora de la reserva"
    )

    class Meta:
        model = Reserva
        fields = ['cliente', 'mesa', 'fecha', 'hora', 'personas']
        labels = {
            'cliente': 'Cliente',
            'mesa': 'Mesa',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'personas': 'Número de personas',
        }

class DisponibilidadForm(forms.Form):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        }),
        label="Fecha"
    )
    hora = forms.TimeField(widget=TimeSelectWidget(), label="Hora")
    personas = forms.IntegerField(min_value=1, max_value=6, label="Número de personas")

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        personas = cleaned_data.get('personas')

        # Validar que fecha y hora existan
        if not fecha:
            raise forms.ValidationError("La fecha es requerida.")
        if not hora:
            raise forms.ValidationError("La hora es requerida.")
        if not personas:
            raise forms.ValidationError("El número de personas es requerido.")

        # Convertir hora a objeto time si viene como string
        if isinstance(hora, str):
            try:
                hora = datetime.strptime(hora, "%H:%M").time()
            except ValueError:
                raise forms.ValidationError("Formato de hora inválido (HH:MM).")

        # Crear un objeto Reserva temporal para validar modelo
        reserva = Reserva(fecha=fecha, hora=hora, personas=personas)
        try:
            reserva.clean()
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        # Actualizar hora en cleaned_data
        cleaned_data['hora'] = hora
        return cleaned_data