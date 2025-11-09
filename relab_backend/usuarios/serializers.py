from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Endereco


# ✅ Serializer customizado para JWT (usando email)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'


class EnderecoSerializer(serializers.ModelSerializer):
    """Serializer para endereços"""

    class Meta:
        model = Endereco
        fields = [
            'id', 'titulo', 'tipo', 'cep', 'logradouro', 'numero',
            'complemento', 'bairro', 'cidade', 'estado',
            'destinatario', 'telefone_contato', 'referencia',
            'padrao', 'ativo', 'endereco_completo',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'endereco_completo', 'criado_em', 'atualizado_em']

    def validate(self, data):
        """Validações customizadas"""
        if 'padrao' in data and not data['padrao']:
            usuario = self.context['request'].user
            if self.instance and self.instance.padrao:
                outros_enderecos = Endereco.objects.filter(
                    usuario=usuario,
                    ativo=True
                ).exclude(pk=self.instance.pk).exists()

                if not outros_enderecos:
                    raise serializers.ValidationError({
                        'padrao': 'Você precisa ter pelo menos um endereço padrão ativo.'
                    })

        return data


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    nome_completo = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo',
            'first_name', 'last_name', 'foto_perfil',
            'tipo_usuario', 'ativo', 'criado_em'
        ]


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para visualização de perfil"""
    nome_completo = serializers.CharField(source='get_full_name', read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    eh_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo',
            'first_name', 'last_name', 'cpf', 'telefone',
            'data_nascimento', 'tipo_usuario', 'foto_perfil',
            'aceita_newsletter', 'ativo', 'eh_admin',
            'enderecos', 'criado_em', 'atualizado_em', 'ultimo_acesso'
        ]
        read_only_fields = [
            'id', 'username', 'tipo_usuario', 'eh_admin',
            'criado_em', 'atualizado_em', 'ultimo_acesso'
        ]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de novo usuário (registro)"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'cpf', 'telefone',
            'data_nascimento', 'aceita_newsletter'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        """Validação customizada"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })

        if Usuario.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este email já está cadastrado.'
            })

        if Usuario.objects.filter(cpf=data['cpf']).exists():
            raise serializers.ValidationError({
                'cpf': 'Este CPF já está cadastrado.'
            })

        return data

    def create(self, validated_data):
        """Cria um novo usuário"""
        validated_data.pop('password_confirm')

        usuario = Usuario.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data['email'],
            password=validated_data.pop('password'),
            **validated_data
        )

        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de perfil"""

    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'telefone',
            'data_nascimento', 'foto_perfil', 'aceita_newsletter'
        ]

    def validate_telefone(self, value):
        """Valida se o telefone já não está em uso por outro usuário"""
        usuario = self.context['request'].user
        if Usuario.objects.filter(telefone=value).exclude(pk=usuario.pk).exists():
            raise serializers.ValidationError('Este telefone já está em uso.')
        return value


class AlterarSenhaSerializer(serializers.Serializer):
    """Serializer para alteração de senha"""
    senha_atual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    nova_senha = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirmar_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_senha_atual(self, value):
        """Valida se a senha atual está correta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value

    def validate(self, data):
        """Valida se as novas senhas coincidem"""
        if data['nova_senha'] != data['confirmar_senha']:
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        return data

    def save(self):
        """Salva a nova senha"""
        user = self.context['request'].user
        user.set_password(self.validated_data['nova_senha'])
        user.save()
        return user