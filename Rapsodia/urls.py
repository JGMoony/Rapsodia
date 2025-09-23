from django.contrib import admin
from django.urls import path, include
from users.views import login_view, registro_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('reservations', include('reservations.urls')),
    path('account/login/', login_view, name='account_login'),
    path('account/register/', registro_view, name='account_register'),
    path('account/', include('allauth.urls')),
]

from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Sistema activo")

urlpatterns += [
    path('test/', test_view),
]