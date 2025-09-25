from django.urls import path
from . import views

urlpatterns = [
    path("reservar/", views.crear_reserva, name="crear_reserva"),
    path("lista/", views.lista_reservas, name="lista_reservas"),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path('availability/', views.check_availability, name='check_availability'),
    path('mesas/', views.lista_mesas, name='lista_mesas'),
]