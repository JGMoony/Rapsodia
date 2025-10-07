from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'nombre', 'apellido', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'role')
    ordering = ('email',)
    search_fields = ('email', 'nombre', 'apellido')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'role')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'password1', 'password2', 'is_staff', 'is_active', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)