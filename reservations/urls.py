from django.urls import path
from . import views
from .views import (
    admin_dashboard,
    MesaListView, MesaCreateView, MesaUpdateView, MesaDeleteView
)

urlpatterns = [
    # Reservas
    path("reservar/", views.disponibilidad_y_reserva, name="crear_reserva"),
    path("confirmar_reserva/", views.confirmar_reserva, name="confirmar_reserva"),
    path("editar/<int:reserva_id>/", views.editar_reserva, name="editar_reserva"),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path("", views.disponibilidad_y_reserva, name="disponibilidad_y_reserva"),

    # Dashboard admin
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),

    # CRUD mesas
    path("mesas/", MesaListView.as_view(), name="mesa_list"),
    path("mesas/create/", MesaCreateView.as_view(), name="mesa_create"),
    path("mesas/<int:pk>/edit/", MesaUpdateView.as_view(), name="mesa_edit"),
    path("mesas/<int:pk>/delete/", MesaDeleteView.as_view(), name="mesa_delete"),
]
