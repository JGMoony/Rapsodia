from django.contrib import admin
from django.urls import path, include
from users.views import base_view, login_view, logout_view, registro_view

urlpatterns = [
    path('', login_view, name='login'),
    path('home/', base_view, name='base'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('reservations/', include('reservations.urls')),
    
]