from django.contrib.auth.models import User
from django.db import models


class Usuario(models.Model):
    telefono = models.CharField(max_length=10)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username}"
