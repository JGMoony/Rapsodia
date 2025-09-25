from django.contrib import admin
from .models import Reserva, Mesa

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'mesa', 'fecha', 'hora', 'personas', 'estado')
    list_filter = ('estado', 'fecha', 'mesa')
    search_fields = ('cliente__email', 'mesa__numero')
    ordering = ('-fecha', 'hora')

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidad', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('numero',)