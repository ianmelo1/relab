from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Usuario, Endereco


class EnderecoInline(admin.TabularInline):
    """Inline para gerenciar endereços do usuário"""
    model = Endereco
    extra = 0
    fields = ['titulo', 'tipo', 'logradouro', 'numero', 'cidade', 'estado', 'padrao', 'ativo']
    readonly_fields = []


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin personalizado para o modelo Usuario"""

    list_display = [
        'foto_thumb',
        'email',
        'get_full_name',
        'cpf_formatado',
        'telefone_formatado',
        'tipo_usuario',
        'status_display',
        'total_enderecos',
        'criado_em'
    ]

    list_filter = [
        'tipo_usuario',
        'ativo',
        'is_active',
        'is_staff',
        'aceita_newsletter',
        'criado_em'
    ]

    search_fields = [
        'email',
        'username',
        'first_name',
        'last_name',
        'cpf',
        'telefone'
    ]

    ordering = ['-criado_em']

    readonly_fields = [
        'criado_em',
        'atualizado_em',
        'ultimo_acesso',
        'foto_preview',
        'total_enderecos',
        'cpf_formatado',
        'telefone_formatado'
    ]

    inlines = [EnderecoInline]

    fieldsets = (
        ('Credenciais', {
            'fields': ('username', 'email', 'password')
        }),
        ('Informações Pessoais', {
            'fields': (
                'first_name',
                'last_name',
                ('cpf', 'cpf_formatado'),
                ('telefone', 'telefone_formatado'),
                'data_nascimento',
                'foto_perfil',
                'foto_preview'
            )
        }),
        ('Tipo e Permissões', {
            'fields': (
                'tipo_usuario',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Configurações', {
            'fields': ('aceita_newsletter', 'ativo')
        }),
        ('Estatísticas', {
            'fields': (
                'total_enderecos',
                'criado_em',
                'atualizado_em',
                'ultimo_acesso',
                'last_login'
            ),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Criar Novo Usuário', {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'cpf',
                'telefone',
                'tipo_usuario'
            ),
        }),
    )

    @admin.display(description='Foto')
    def foto_thumb(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />',
                obj.foto_perfil.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: #ccc; border-radius: 50%; '
            'display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">'
            '{}</div>',
            obj.first_name[0].upper() if obj.first_name else 'U'
        )

    @admin.display(description='Preview da Foto')
    def foto_preview(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" style="max-width: 200px; border-radius: 8px;" />',
                obj.foto_perfil.url
            )
        return 'Sem foto'

    @admin.display(description='Status', ordering='ativo')
    def status_display(self, obj):
        if obj.ativo and obj.is_active:
            return format_html('<span style="color: green;">✅ Ativo</span>')
        return format_html('<span style="color: red;">❌ Inativo</span>')

    @admin.display(description='Endereços')
    def total_enderecos(self, obj):
        count = obj.enderecos.filter(ativo=True).count()
        if count == 0:
            return format_html('<span style="color: orange;">⚠️ Nenhum</span>')
        return format_html(
            '<span style="color: green;">📍 {}</span>',
            count
        )

    # Actions
    actions = ['ativar_usuarios', 'desativar_usuarios', 'tornar_admin', 'tornar_cliente']

    @admin.action(description='✅ Ativar usuários selecionados')
    def ativar_usuarios(self, request, queryset):
        updated = queryset.update(ativo=True, is_active=True)
        self.message_user(request, f'{updated} usuário(s) ativado(s).')

    @admin.action(description='❌ Desativar usuários selecionados')
    def desativar_usuarios(self, request, queryset):
        updated = queryset.update(ativo=False, is_active=False)
        self.message_user(request, f'{updated} usuário(s) desativado(s).')

    @admin.action(description='👑 Tornar administrador')
    def tornar_admin(self, request, queryset):
        updated = queryset.update(tipo_usuario='admin', is_staff=True)
        self.message_user(request, f'{updated} usuário(s) promovido(s) a administrador.')

    @admin.action(description='👤 Tornar cliente')
    def tornar_cliente(self, request, queryset):
        updated = queryset.update(tipo_usuario='cliente')
        self.message_user(request, f'{updated} usuário(s) alterado(s) para cliente.')


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    """Admin para o modelo Endereco"""

    list_display = [
        'titulo',
        'usuario',
        'tipo',
        'cep_formatado',
        'cidade',
        'estado',
        'padrao_display',
        'ativo',
        'criado_em'
    ]

    list_filter = [
        'tipo',
        'padrao',
        'ativo',
        'estado',
        'criado_em'
    ]

    search_fields = [
        'titulo',
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name',
        'logradouro',
        'bairro',
        'cidade',
        'cep'
    ]

    readonly_fields = ['criado_em', 'atualizado_em', 'endereco_completo', 'cep_formatado', 'telefone_contato_formatado']

    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Informações Básicas', {
            'fields': (
                'titulo',
                'tipo',
                'destinatario',
                ('telefone_contato', 'telefone_contato_formatado')
            )
        }),
        ('Endereço', {
            'fields': (
                ('cep', 'cep_formatado'),
                'logradouro',
                'numero',
                'complemento',
                'bairro',
                'cidade',
                'estado',
                'referencia',
                'endereco_completo'
            )
        }),
        ('Configurações', {
            'fields': ('padrao', 'ativo')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Padrão', boolean=True, ordering='padrao')
    def padrao_display(self, obj):
        return obj.padrao

    # Actions
    actions = ['marcar_padrao', 'ativar_enderecos', 'desativar_enderecos']

    @admin.action(description='⭐ Marcar como padrão')
    def marcar_padrao(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                'Selecione apenas um endereço por vez para marcar como padrão.',
                level='error'
            )
            return

        endereco = queryset.first()
        Endereco.objects.filter(usuario=endereco.usuario, padrao=True).update(padrao=False)
        endereco.padrao = True
        endereco.save()

        self.message_user(request, f'Endereço "{endereco.titulo}" marcado como padrão.')

    @admin.action(description='✅ Ativar endereços')
    def ativar_enderecos(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} endereço(s) ativado(s).')

    @admin.action(description='❌ Desativar endereços')
    def desativar_enderecos(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} endereço(s) desativado(s).')