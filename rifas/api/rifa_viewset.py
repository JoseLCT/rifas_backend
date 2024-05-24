import random

from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rifas.api import UsuarioRifaSerializer
from rifas.models import EN_CURSO, FINALIZADO, PENDIENTE, Usuario, UsuarioRifa

from rifas.models import Rifa


class RifaSerializer(serializers.ModelSerializer):
    usuarios_participantes_ids = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source='usuarios_participantes', write_only=True, many=True
    )
    usuarios_rifa = UsuarioRifaSerializer(many=True, read_only=True, source='usuarios')

    class Meta:
        model = Rifa
        fields = '__all__'


class RifaViewSet(viewsets.ModelViewSet):
    queryset = Rifa.objects.all()
    serializer_class = RifaSerializer
    permission_classes = [IsAuthenticated]

    def add_ticket(self, usuarios_rifa, rifa):
        ultimo_numero_ticket = 0
        # mayor a 1 ya que el usuario ya está en la rifa pero no tiene número de ticket
        if usuarios_rifa.count() > 1:
            # se resta 2 porque el último usuario es el usuario actual
            last_ticket = usuarios_rifa[usuarios_rifa.count() - 2].numero_ticket
            if last_ticket:
                ultimo_numero_ticket = int(last_ticket.split('-')[1])
        contador = ultimo_numero_ticket + 1
        for usuario in usuarios_rifa:
            if not usuario.numero_ticket:
                usuario.numero_ticket = f'{rifa.codigo}-{contador}'
                usuario.save()
                contador += 1

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if 'usuario_creador' not in request.data:
            usuario_creador = Usuario.objects.get(usuario=request.user)
            request.data['usuario_creador'] = usuario_creador.id
        serializer.is_valid(raise_exception=True)

        if 'codigo' not in request.data:
            codigo = request.data['titulo'][:3]
            request.data['codigo'] = codigo

        self.perform_create(serializer)

        rifa = Rifa.objects.get(pk=serializer.data['id'])
        usuarios_rifa = UsuarioRifa.objects.filter(rifa=rifa)
        contador = 1
        for usuario in usuarios_rifa:
            usuario.numero_ticket = f'{rifa.codigo}-{contador}'
            usuario.save()
            contador += 1

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if 'usuario_creador' not in request.data:
            usuario_creador = Usuario.objects.get(usuario=request.user)
            request.data['usuario_creador'] = usuario_creador.id
        serializer.is_valid(raise_exception=True)

        if request.user != instance.usuario_creador.usuario:
            return Response({'error': 'No tienes permisos para editar esta rifa'}, status=403)

        print(request.data)

        self.perform_update(serializer)

        usuarios_rifa = UsuarioRifa.objects.filter(rifa=instance)
        self.add_ticket(usuarios_rifa, instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mis-rifas-creadas', url_name='mis-rifas-creadas')
    def mis_rifas_creadas(self, request):
        usuario = Usuario.objects.get(usuario=request.user)
        rifas = Rifa.objects.filter(usuario_creador=usuario)
        serializer = self.get_serializer(rifas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mis-rifas', url_name='mis-rifas')
    def mis_rifas(self, request):
        usuario = Usuario.objects.get(usuario=request.user)
        rifas = Rifa.objects.filter(usuarios_participantes=usuario)
        serializer = self.get_serializer(rifas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='disponibles', url_name='disponibles')
    def rifas_disponibles(self, request):
        usuario = Usuario.objects.get(usuario=request.user)
        rifas = Rifa.objects.filter(estado=PENDIENTE).exclude(usuario_creador=usuario)
        serializer = self.get_serializer(rifas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='participar', url_name='participar')
    def participar(self, request):
        rifa_id = request.data.get('rifa_id')
        user = request.user

        rifa = Rifa.objects.get(pk=rifa_id)
        usuario = Usuario.objects.get(usuario=user)

        if rifa.usuario_creador == usuario:
            return Response({'error': 'El usuario creador de la rifa no puede participar en ella'}, status=400)

        if rifa.estado != PENDIENTE:
            return Response({'error': 'Solo se pueden participar en rifas pendientes'}, status=400)

        if usuario in rifa.usuarios_participantes.all():
            return Response({'error': 'El usuario ya está participando en la rifa'}, status=400)

        rifa.usuarios_participantes.add(usuario)

        self.add_ticket(UsuarioRifa.objects.filter(rifa=rifa), rifa)

        return Response({'rifa_id': rifa_id, 'usuario_id': usuario.id})

    @action(detail=False, methods=['delete'], url_path='abandonar', url_name='abandonar')
    def abandonar(self, request):
        rifa_id = request.data.get('rifa_id')
        user = request.user

        rifa = Rifa.objects.get(pk=rifa_id)
        usuario = Usuario.objects.get(usuario=user)

        if usuario in rifa.usuarios_participantes.all():
            rifa.usuarios_participantes.remove(usuario)
            rifa.save()
            return Response({'rifa_id': rifa_id, 'usuario_id': usuario.id})
        return Response({'error': 'El usuario no está participando en la rifa'}, status=400)

    @action(detail=False, methods=['post'], url_path='finalizar-sorteo', url_name='finalizar-sorteo')
    def finalizar_sorteo(self, request):
        rifa_id = request.data.get('rifa_id')

        rifa = Rifa.objects.get(pk=rifa_id)

        rifa.estado = FINALIZADO
        rifa.save()

        return Response({'rifa_id': rifa_id, 'estado': rifa.estado})

    @action(detail=False, methods=['get'], url_path='obtener-ganador', url_name='obtener-ganador')
    def obtener_ganador(self, request):
        rifa_id = request.query_params.get('id')

        rifa = Rifa.objects.get(pk=rifa_id)
        participantes = rifa.usuarios_participantes.all()
        cantidad_participantes = participantes.count()
        participantes = UsuarioRifa.objects.filter(rifa=rifa, usuario__in=participantes, es_ganador=False)

        if rifa.estado == FINALIZADO:
            return Response({'error': 'La rifa ya fue finalizada'}, status=400)

        if participantes.count() < 1:
            return Response({'error': 'No hay suficientes participantes para sortear'},
                            status=400)

        ganadores_anteriores = UsuarioRifa.objects.filter(rifa=rifa, es_ganador=True)

        if ganadores_anteriores.count() == 0:
            # Si no hay ganadores anteriores, se asume que es el primer sorteo y se cambia el estado de la rifa.
            rifa.estado = EN_CURSO
            rifa.save()

        if ganadores_anteriores.count() + 1 == cantidad_participantes:
            # Si todos los participantes han ganado, se finaliza la rifa.
            rifa.estado = FINALIZADO
            rifa.save()

        ganador = participantes.order_by('?').first()
        ganador.es_ganador = True
        ganador.save()

        serializer = UsuarioRifaSerializer(ganador)

        return Response({'rifa_id': rifa_id, 'ganador': serializer.data})

    @action(detail=False, methods=['get'], url_path='generar-codigo', url_name='generar-codigo')
    def get_code(self, request):
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        code = ''
        for i in range(3):
            code += letters[random.randint(0, 25)]
        rifas = Rifa.objects.filter(codigo=code)
        if rifas.count() > 0:
            return self.get_code(request)
        return Response(code)
