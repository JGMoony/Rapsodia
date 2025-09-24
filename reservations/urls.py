from django.urls import path
from . import views

urlpatterns = [
    path('availability/', views.check_availability, name='check_availability'),
    path('mesas/', views.lista_mesas, name='lista_mesas'),
]