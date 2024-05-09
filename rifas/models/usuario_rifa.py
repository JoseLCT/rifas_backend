from django.db import models
from rifas.models import Rifa, Usuario


class UsuarioRifa(models.Model):
    numero_ticket = models.CharField(max_length=10)
    es_ganador = models.BooleanField(default=False)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='rifas')
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='usuarios')

    def __str__(self):
        return f"{self.numero_ticket} - {self.es_ganador}"
