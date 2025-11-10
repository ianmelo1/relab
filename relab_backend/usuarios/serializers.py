from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Endereco, formatar_cpf, formatar_telefone, formatar_cep


# ✅ Serializer customizado para JWT (usando email)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'


class EnderecoSerializer(serializers.ModelSerializer):
    """Serializer para endereços"""
    cep_formatado = serializers.SerializerMethodField()
    telefone_contato_formatado = serializers.SerializerMethodField()

    class Meta:
        model = Endereco
        fields = [
            'id', 'titulo', 'tipo', 'cep', 'cep_formatado', 'logradouro', 'numero',
            'complemento', 'bairro', 'cidade', 'estado',
            'destinatario', 'telefone_contato', 'telefone_contato_formatado', 'referencia',
            'padrao', 'ativo', 'endereco_completo',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'cep_formatado', 'telefone_contato_formatado', 'endereco_completo', 'criado_em',
                            'atualizado_em']

    def get_cep_formatado(self, obj):
        """Retorna CEP formatado: 12345-678"""
        return formatar_cep(obj.cep)

    def get_telefone_contato_formatado(self, obj):
        """Retorna telefone formatado: (11) 98765-4321"""
        if obj.telefone_contato:
            return formatar_telefone(obj.telefone_contato)
        return ''

    def validate_cep(self, value):
        """Remove formatação do CEP antes de salvar"""
        return ''.join(filter(str.isdigit, value))

    def validate_telefone_contato(self, value):
        """Remove formatação do telefone antes de salvar"""
        if value:
            return ''.join(filter(str.isdigit, value))
        return value

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
    cpf_formatado = serializers.SerializerMethodField()
    telefone_formatado = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo',
            'first_name', 'last_name', 'cpf', 'cpf_formatado',
            'telefone', 'telefone_formatado', 'foto_perfil',
            'tipo_usuario', 'ativo', 'criado_em'
        ]

    def get_cpf_formatado(self, obj):
        """Retorna CPF formatado: 123.456.789-00"""
        return formatar_cpf(obj.cpf)

    def get_telefone_formatado(self, obj):
        """Retorna telefone formatado: (11) 98765-4321"""
        return formatar_telefone(obj.telefone)


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para visualização de perfil"""
    nome_completo = serializers.CharField(source='get_full_name', read_only=True)
    cpf_formatado = serializers.SerializerMethodField()
    telefone_formatado = serializers.SerializerMethodField()
    enderecos = EnderecoSerializer(many=True, read_only=True)
    eh_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo',
            'first_name', 'last_name', 'cpf', 'cpf_formatado',
            'telefone', 'telefone_formatado', 'data_nascimento',
            'tipo_usuario', 'foto_perfil',
            'aceita_newsletter', 'ativo', 'eh_admin',
            'enderecos', 'criado_em', 'atualizado_em', 'ultimo_acesso'
        ]
        read_only_fields = [
            'id', 'username', 'cpf_formatado', 'telefone_formatado',
            'tipo_usuario', 'eh_admin',
            'criado_em', 'atualizado_em', 'ultimo_acesso'
        ]

    def get_cpf_formatado(self, obj):
        """Retorna CPF formatado: 123.456.789-00"""
        return formatar_cpf(obj.cpf)

    def get_telefone_formatado(self, obj):
        """Retorna telefone formatado: (11) 98765-4321"""
        return formatar_telefone(obj.telefone)


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

    def validate_cpf(self, value):
        """Remove formatação do CPF antes de salvar"""
        cpf_limpo = ''.join(filter(str.isdigit, value))

        if Usuario.objects.filter(cpf=cpf_limpo).exists():
            raise serializers.ValidationError('Este CPF já está cadastrado.')

        return cpf_limpo

    def validate_telefone(self, value):
        """Remove formatação do telefone antes de salvar"""
        return ''.join(filter(str.isdigit, value))

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
        """Remove formatação e valida se o telefone já não está em uso"""
        telefone_limpo = ''.join(filter(str.isdigit, value))
        usuario = self.context['request'].user

        if Usuario.objects.filter(telefone=telefone_limpo).exclude(pk=usuario.pk).exists():
            raise serializers.ValidationError('Este telefone já está em uso.')

        return telefone_limpo


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