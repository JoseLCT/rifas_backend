from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rifas.models import Rifa


class RifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rifa
        fields = '__all__'


class RifaViewSet(viewsets.ModelViewSet):
    queryset = Rifa.objects.all()
    serializer_class = RifaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='sortear', url_name='sortear')
    def sortear(self, request):
        rifa_id = request.query_params.get('rifa_id')
        cantidad_ganadores = request.query_params.get('cantidad_ganadores', 1)

        rifa = Rifa.objects.get(pk=rifa_id)
        participantes = rifa.usuarios_participantes.all()

        ganadores_anteriores = participantes.filter(es_ganador=True)

        if cantidad_ganadores > (participantes.count() - ganadores_anteriores.count()):
            return Response({'error': 'No hay suficientes participantes para sortear esa cantidad de ganadores'},
                            status=400)

        if ganadores_anteriores.count() > 0:
            participantes = participantes.exclude(pk__in=ganadores_anteriores.values_list('pk', flat=True))

        ganadores = participantes.order_by('?')[:cantidad_ganadores]
        for ganador in ganadores:
            ganador.es_ganador = True
            ganador.save()

        return Response({'ganadores': [ganador.username for ganador in ganadores]})
