from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from rifas.api import UsuarioSerializer
from rifas.models import UsuarioRifa, Usuario


class UsuarioRifaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source='usuario', write_only=True
    )
    class Meta:
        model = UsuarioRifa
        fields = '__all__'


class UsuarioRifaViewSet(viewsets.GenericViewSet):
    queryset = UsuarioRifa.objects.all()
    serializer_class = UsuarioRifaSerializer
    permission_classes = [IsAuthenticated]
