from django.db import models

from rifas.models import Usuario

PENDIENTE = 0
EN_CURSO = 1
FINALIZADO = 2

ESTADO_CHOICES = (
    (PENDIENTE, 'Pendiente'),
    (EN_CURSO, 'En curso'),
    (FINALIZADO, 'Finalizado'),
)


class Rifa(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad_tickets = models.IntegerField()
    codigo = models.CharField(max_length=3, unique=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=0)

    usuario_creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='rifas_creadas')
    usuarios_participantes = models.ManyToManyField(Usuario, through='UsuarioRifa', related_name='rifas_participadas')

    def __str__(self):
        return f"{self.titulo} - {self.codigo}"
