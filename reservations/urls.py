from django.urls import path
from . import views

urlpatterns = [
    path("reservar/", views.disponibilidad_y_reserva, name="crear_reserva"),
    path("confirmar_reserva/", views.confirmar_reserva, name="confirmar_reserva"),
    path("editar/<int:reserva_id>/", views.editar_reserva, name="editar_reserva"),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path('', views.disponibilidad_y_reserva, name='disponibilidad_y_reserva'),
]