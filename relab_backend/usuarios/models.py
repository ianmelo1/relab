from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def formatar_cpf(cpf):
    """Formata CPF: 12345678900 -> 123.456.789-00"""
    cpf = ''.join(filter(str.isdigit, cpf))  # Remove tudo que não é número
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf

def formatar_telefone(telefone):
    """Formata telefone: 11987654321 -> (11) 98765-4321"""
    telefone = ''.join(filter(str.isdigit, telefone))
    if len(telefone) == 11:  # Celular
        return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'
    elif len(telefone) == 10:  # Fixo
        return f'({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}'
    return telefone

def formatar_cep(cep):
    """Formata CEP: 12345678 -> 12345-678"""
    cep = ''.join(filter(str.isdigit, cep))
    if len(cep) == 8:
        return f'{cep[:5]}-{cep[5:]}'
    return cep


class Usuario(AbstractUser):

    """
    Modelo de usuário personalizado estendendo AbstractUser
    """
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ]

    email = models.EmailField(_('email'), unique=True)
    cpf = models.CharField(
        max_length=14,  # Só os números
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='CPF deve conter 11 dígitos'
            )
        ],
        verbose_name='CPF'
    )
    telefone = models.CharField(
        max_length=16,  # Só os números (DDD + número)
        validators=[
            RegexValidator(
                regex=r'^\d{10,11,16}$',
                message='Telefone deve conter 10 ou 11 dígitos'
            )
        ],
        verbose_name='Telefone'
    )
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente',
        verbose_name='Tipo de Usuário'
    )

    # Campos adicionais
    foto_perfil = models.ImageField(
        upload_to='usuarios/perfil/',
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )
    aceita_newsletter = models.BooleanField(default=False, verbose_name='Aceita Newsletter')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    ultimo_acesso = models.DateTimeField(null=True, blank=True, verbose_name='Último Acesso')

    # Usar email como username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'cpf', 'telefone', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Retorna o nome completo do usuário"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    @property
    def eh_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'admin' or self.is_staff or self.is_superuser

    def cpf_formatado(self):
        """Retorna o CPF formatado: 123.456.789-00"""
        return formatar_cpf(self.cpf)
    cpf_formatado.short_description = 'CPF'

    def telefone_formatado(self):
        """Retorna o telefone formatado: (11) 98765-4321"""
        return formatar_telefone(self.telefone)
    telefone_formatado.short_description = 'Telefone'


class Endereco(models.Model):
    """
    Modelo para endereços dos usuários
    """
    TIPO_ENDERECO_CHOICES = [
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='enderecos',
        verbose_name='Usuário'
    )

    # Informações do endereço
    titulo = models.CharField(
        max_length=50,
        help_text='Ex: Casa, Trabalho, Casa dos Pais',
        verbose_name='Título'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_ENDERECO_CHOICES,
        default='residencial',
        verbose_name='Tipo'
    )

    # CEP e localização
    cep = models.CharField(
        max_length=15,  # Só os números
        validators=[
            RegexValidator(
                regex=r'^\d{15}$',
                message='CEP deve conter 8 dígitos'
            )
        ],
        verbose_name='CEP'
    )
    logradouro = models.CharField(max_length=255, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(
        max_length=2,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}$',
                message='Estado deve conter 2 letras maiúsculas. Ex: SP, RJ'
            )
        ],
        verbose_name='Estado (UF)'
    )

    # Informações adicionais
    destinatario = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nome de quem receberá a entrega (opcional)',
        verbose_name='Destinatário'
    )
    telefone_contato = models.CharField(
        max_length=20,  # Só os números
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10,20}$',
                message='Telefone deve conter 10 ou 11 dígitos'
            )
        ],
        help_text='Telefone para contato na entrega (opcional)',
        verbose_name='Telefone de Contato'
    )
    referencia = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ponto de referência para entrega',
        verbose_name='Ponto de Referência'
    )

    # Configurações
    padrao = models.BooleanField(
        default=False,
        verbose_name='Endereço Padrão',
        help_text='Marque como endereço padrão de entrega'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        ordering = ['-padrao', '-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'padrao']),
            models.Index(fields=['cep']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"

    def save(self, *args, **kwargs):
        """
        Se este endereço for marcado como padrão,
        desmarca todos os outros endereços do usuário como não-padrão
        """
        if self.padrao:
            Endereco.objects.filter(
                usuario=self.usuario,
                padrao=True
            ).exclude(pk=self.pk).update(padrao=False)

        super().save(*args, **kwargs)

    @property
    def endereco_completo(self):
        """Retorna o endereço formatado em uma linha"""
        complemento = f", {self.complemento}" if self.complemento else ""
        return f"{self.logradouro}, {self.numero}{complemento} - {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep_formatado()}"

    def cep_formatado(self):
        """Retorna o CEP formatado: 12345-678"""
        return formatar_cep(self.cep)
    cep_formatado.short_description = 'CEP'

    def telefone_contato_formatado(self):
        """Retorna o telefone de contato formatado"""
        if self.telefone_contato:
            return formatar_telefone(self.telefone_contato)
        return ''
    telefone_contato_formatado.short_description = 'Telefone de Contato'