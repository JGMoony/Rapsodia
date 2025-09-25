from django.contrib import admin
from django.urls import path, include
from users.views import base_view, login_view, logout_view, registro_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('reservations', include('reservations.urls')),
    path('users/registro/', registro_view, name='registro'),
    path('users/login/', login_view, name='login'),
    path('users/logout/', logout_view, name='logout'),
    path('users/inicio/', base_view, name='home'),

]