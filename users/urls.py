from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

urlpatterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
    path('register/', views.registro_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('inicio', views.base_view, name='home'),
]


def test_view(request):
    return HttpResponse("Sistema activo")

urlpatterns += [
    path('test/', test_view),
]