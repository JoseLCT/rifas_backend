from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rifas.api import SimpleUserSerializer
from rifas.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    usuario = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = '__all__'


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        serializer.save(usuario=user)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user = instance.usuario

        if 'username' in request.data:
            username = request.data.get('username')
            user.username = username
        if 'first_name' in request.data:
            first_name = request.data.get('first_name')
            user.first_name = first_name
        if 'last_name' in request.data:
            last_name = request.data.get('last_name')
            user.last_name = last_name

        user.save()

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me', url_name='me')
    def get_user_info(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
