from datetime import time, datetime, timedelta
from django import forms
from .models import Reserva
from django.core.exceptions import ValidationError

class TimeSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        time_choices = []
        for hour in range(10, 23): 
            for minute in (0, 30):
                t = time(hour, minute)
                label = t.strftime('%I:%M %p')
                value = t.strftime('%H:%M')
                time_choices.append((value, label))
        super().__init__(choices=time_choices, *args, **kwargs)

class EditarReservaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Fecha de la reserva"
    )
    hora = forms.TimeField(
        widget=TimeSelectWidget(),
        label="Hora de la reserva"
    )
    personas = forms.IntegerField(
        min_value=1,
        max_value=6,
        label="Número de personas",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Reserva
        fields = ['mesa', 'fecha', 'hora', 'personas']
        labels = {
            'mesa': 'Mesa',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'personas': 'Número de personas',
        }
        widgets = {
            'mesa': forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            dt_reserva = datetime.combine(fecha, hora)
            dt_actual = datetime.now()
            if dt_reserva - dt_actual < timedelta(hours=24):
                raise ValidationError("Solo puedes editar la reserva con al menos 24 horas de anticipación.")

        return cleaned_data

class ReservaForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        if fecha and hora:
            from datetime import datetime, timedelta
            dt_reserva = datetime.combine(fecha, hora)
            dt_actual = datetime.now()
            if dt_reserva - dt_actual < timedelta(hours=24):
                raise ValidationError("Solo puedes editar o cancelar la reserva con al menos 24 horas de anticipación.")
        return cleaned_data
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

        if not fecha:
            raise forms.ValidationError("La fecha es requerida.")
        if not hora:
            raise forms.ValidationError("La hora es requerida.")
        if not personas:
            raise forms.ValidationError("El número de personas es requerido.")

        if isinstance(hora, str):
            try:
                hora = datetime.strptime(hora, "%H:%M").time()
            except ValueError:
                raise forms.ValidationError("Formato de hora inválido (HH:MM).")

        reserva = Reserva(fecha=fecha, hora=hora, personas=personas)
        try:
            reserva.clean()
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        cleaned_data['hora'] = hora
        return cleaned_data