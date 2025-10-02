from django.urls import path
from . import views
from .views import (
    admin_dashboard,
    MesaListView, MesaCreateView, MesaUpdateView, MesaDeleteView
)

urlpatterns = [
    path("reservar/", views.disponibilidad_y_reserva, name="crear_reserva"),
    path("confirmar_reserva/", views.confirmar_reserva, name="confirmar_reserva"),
    path('reservations/reserva_confirmada/<int:reserva_id>/', views.reserva_confirmada, name='reserva_confirmada'),
    path('editar_reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path('reservas/eliminar/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path("", views.disponibilidad_y_reserva, name="disponibilidad_y_reserva"),

    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),

    path("mesas/", MesaListView.as_view(), name="mesa_list"),
    path("mesas/create/", MesaCreateView.as_view(), name="mesa_create"),
    path("mesas/<int:pk>/edit/", MesaUpdateView.as_view(), name="mesa_edit"),
    path("mesas/<int:pk>/delete/", MesaDeleteView.as_view(), name="mesa_delete"),
]
