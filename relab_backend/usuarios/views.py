from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Usuario, Endereco
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UsuarioListSerializer,
    UsuarioDetailSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    AlterarSenhaSerializer,
    EnderecoSerializer,
    CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = Usuario.objects.get(email=request.data.get('email'))
            response.data['user'] = {
                'id': user.id,
                'email': user.email,
                'nome': user.get_full_name(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tipo_usuario': user.tipo_usuario,
                'foto_perfil': user.foto_perfil.url if user.foto_perfil else None,
            }

        return response


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.tipo_usuario == 'admin':
            return True
        return obj == request.user


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(ativo=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        elif self.action == 'list':
            return UsuarioListSerializer
        return UsuarioDetailSerializer

    def get_permissions(self):
        # CADASTRO É PÚBLICO - qualquer um pode criar conta
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Usuario.objects.none()
        if user.is_staff or user.tipo_usuario == 'admin':
            return Usuario.objects.all()
        return Usuario.objects.filter(pk=user.pk)

    def create(self, request, *args, **kwargs):
        """Criação de novo usuário (registro público)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        return Response(
            UsuarioDetailSerializer(usuario).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        usuario = request.user

        if request.method == 'GET':
            usuario.ultimo_acesso = timezone.now()
            usuario.save(update_fields=['ultimo_acesso'])
            serializer = UsuarioDetailSerializer(usuario)
            return Response(serializer.data)

        serializer = UsuarioUpdateSerializer(
            usuario,
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(UsuarioDetailSerializer(usuario).data)

    @action(detail=False, methods=['post'])
    def alterar_senha(self, request):
        serializer = AlterarSenhaSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Senha alterada com sucesso.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['delete'])
    def desativar_conta(self, request):
        usuario = request.user
        usuario.ativo = False
        usuario.is_active = False
        usuario.save()

        return Response(
            {'detail': 'Conta desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Endereco.objects.filter(
            usuario=self.request.user,
            ativo=True
        )

    def perform_create(self, serializer):
        tem_enderecos = Endereco.objects.filter(
            usuario=self.request.user,
            ativo=True
        ).exists()

        padrao = serializer.validated_data.get('padrao', False)
        if not tem_enderecos:
            padrao = True

        serializer.save(usuario=self.request.user, padrao=padrao)

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()

        if instance.padrao:
            outro_endereco = Endereco.objects.filter(
                usuario=self.request.user,
                ativo=True
            ).exclude(pk=instance.pk).first()

            if outro_endereco:
                outro_endereco.padrao = True
                outro_endereco.save()

    @action(detail=True, methods=['post'])
    def tornar_padrao(self, request, pk=None):
        endereco = self.get_object()

        Endereco.objects.filter(
            usuario=request.user,
            padrao=True
        ).update(padrao=False)

        endereco.padrao = True
        endereco.save()

        return Response(
            {'detail': 'Endereço marcado como padrão.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def padrao(self, request):
        try:
            endereco = Endereco.objects.get(
                usuario=request.user,
                padrao=True,
                ativo=True
            )
            serializer = self.get_serializer(endereco)
            return Response(serializer.data)
        except Endereco.DoesNotExist:
            return Response(
                {'detail': 'Nenhum endereço padrão encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )