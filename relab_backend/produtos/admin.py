from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Categoria, Produto, ImagemProduto


class ImagemProdutoInline(admin.TabularInline):
    """Inline para adicionar múltiplas imagens ao produto"""
    model = ImagemProduto
    extra = 1
    fields = ['imagem', 'ordem']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'slug',
        'quantidade_produtos',
        'ordem',
        'ativo',
        'criado_em'
    ]
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['ordem', 'ativo']
    readonly_fields = ['criado_em', 'atualizado_em', 'quantidade_produtos']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao', 'imagem')
        }),
        ('Configurações', {
            'fields': ('ordem', 'ativo')
        }),
        ('Estatísticas', {
            'fields': ('quantidade_produtos', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            produtos_count=Count('produtos', filter=Q(produtos__ativo=True))
        )

    @admin.display(description='Produtos', ordering='produtos_count')
    def quantidade_produtos(self, obj):
        count = obj.produtos_count
        return format_html(
            '<span style="color: {};">{} produto{}</span>',
            'green' if count > 0 else 'red',
            count,
            's' if count != 1 else ''
        )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'imagem_thumb',
        'nome',
        'categoria',
        'preco_display',
        'estoque_display',
        'status_display',
        'ativo',
        'em_destaque',
        'vendas',
        'visualizacoes',
        'criado_em'
    ]
    list_filter = [
        'ativo',
        'disponivel',
        'em_destaque',
        'categoria',
        'criado_em'
    ]
    search_fields = ['nome', 'descricao', 'slug']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['ativo', 'em_destaque']
    readonly_fields = [
        'visualizacoes',
        'vendas',
        'criado_em',
        'atualizado_em',
        'imagem_preview'
    ]
    inlines = [ImagemProdutoInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'nome',
                'slug',
                'descricao_curta',
                'descricao',
                'categoria'
            )
        }),
        ('Preços', {
            'fields': (
                'preco',
                'preco_promocional',
                'preco_custo'
            )
        }),
        ('Estoque', {
            'fields': (
                'estoque',
                'estoque_minimo'
            )
        }),
        ('Mídia', {
            'fields': (
                'imagem',
                'imagem_preview'
            )
        }),
        ('Status e Destaque', {
            'fields': (
                'ativo',
                'disponivel',
                'em_destaque'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_description',
                'meta_keywords'
            ),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': (
                'visualizacoes',
                'vendas',
                'criado_em',
                'atualizado_em'
            ),
            'classes': ('collapse',)
        }),
    )

    # Métodos de exibição customizados
    @admin.display(description='Imagem')
    def imagem_thumb(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.imagem.url
            )
        return '-'

    @admin.display(description='Preview')
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 8px;" />',
                obj.imagem.url
            )
        return 'Sem imagem'

    @admin.display(description='Preço', ordering='preco')
    def preco_display(self, obj):
        preco = f"R$ {obj.preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        if obj.preco_promocional:
            promo = f"R$ {obj.preco_promocional:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{}</span><br>'
                '<span style="color: #e74c3c; font-weight: bold;">{}</span>',
                preco, promo
            )
        return preco

    @admin.display(description='Estoque', ordering='estoque')
    def estoque_display(self, obj):
        if obj.estoque <= 0:
            cor = 'red'
            icone = '❌'
        elif obj.estoque <= obj.estoque_minimo:
            cor = 'orange'
            icone = '⚠️'
        else:
            cor = 'green'
            icone = '✅'

        return format_html(
            '{} <span style="color: {}; font-weight: bold;">{}</span>',
            icone, cor, obj.estoque
        )

    @admin.display(description='Status', ordering='disponivel')
    def status_display(self, obj):
        if obj.disponivel and obj.estoque > 0:
            return format_html('<span style="color: green;">✅ Disponível</span>')
        elif obj.estoque <= 0:
            return format_html('<span style="color: red;">❌ Sem estoque</span>')
        else:
            return format_html('<span style="color: orange;">⚠️ Indisponível</span>')

    # Actions
    actions = ['ativar_produtos', 'desativar_produtos', 'marcar_destaque', 'desmarcar_destaque']

    @admin.action(description='✅ Ativar produtos selecionados')
    def ativar_produtos(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} produto(s) ativado(s) com sucesso.')

    @admin.action(description='❌ Desativar produtos selecionados')
    def desativar_produtos(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} produto(s) desativado(s) com sucesso.')

    @admin.action(description='⭐ Marcar como destaque')
    def marcar_destaque(self, request, queryset):
        updated = queryset.update(em_destaque=True)
        self.message_user(request, f'{updated} produto(s) marcado(s) como destaque.')

    @admin.action(description='⚪ Desmarcar como destaque')
    def desmarcar_destaque(self, request, queryset):
        updated = queryset.update(em_destaque=False)
        self.message_user(request, f'{updated} produto(s) desmarcado(s) como destaque.')


@admin.register(ImagemProduto)
class ImagemProdutoAdmin(admin.ModelAdmin):
    list_display = ['imagem_thumb', 'produto', 'ordem', 'criado_em']
    list_filter = ['criado_em']
    search_fields = ['produto__nome']
    list_editable = ['ordem']

    @admin.display(description='Imagem')
    def imagem_thumb(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.imagem.url
            )
        return '-'