from datetime import time
from django import forms
from .models import Reserva
from django.core.exceptions import ValidationError
from django.utils import timezone 
from datetime import datetime, timedelta

class TimeSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        time_choices = []
        for hour in range(10, 22 + 1):
            for minute in (0, 30):
                t = time(hour, minute)
                label = t.strftime('%I:%M %p')
                value = t.strftime('%H:%M')
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
        reserva = Reserva(
            fecha=cleaned_data.get('fecha'),
            hora=cleaned_data.get('hora'),
            personas=cleaned_data.get('personas')
        )
        try:
            reserva.clean()  
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return cleaned_data
    
    def save(self, *args, **kwargs):
        pass