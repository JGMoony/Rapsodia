from django.contrib import admin
from django.urls import path, include
from users.views import home, login_view, logout_view, registro_view

urlpatterns = [
    path('', login_view, name='login'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('reservations/', include('reservations.urls')),
    path('administration/', include('administration.urls')),
    
]