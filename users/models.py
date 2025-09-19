from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre', 'apellido']
    
    def _str_(self):
        return f"{self.nombre} {self.apellido}"