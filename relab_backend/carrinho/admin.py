from django.contrib import admin
from .models import Carrinho, ItemCarrinho


class ItemCarrinhoInline(admin.TabularInline):
    """Inline para exibir itens do carrinho"""
    model = ItemCarrinho
    extra = 0
    readonly_fields = ['subtotal', 'criado_em', 'atualizado_em']
    fields = ['produto', 'quantidade', 'preco_unitario', 'subtotal']

    def subtotal(self, obj):
        return f"R$ {obj.subtotal:.2f}"

    subtotal.short_description = 'Subtotal'


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    """Admin para Carrinho"""
    list_display = ['usuario', 'total_itens', 'subtotal_display', 'atualizado_em']
    list_filter = ['criado_em', 'atualizado_em']
    search_fields = ['usuario__email', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['total_itens', 'subtotal_display', 'total_display', 'criado_em', 'atualizado_em']
    inlines = [ItemCarrinhoInline]

    def subtotal_display(self, obj):
        return f"R$ {obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'

    def total_display(self, obj):
        return f"R$ {obj.total:.2f}"

    total_display.short_description = 'Total'


@admin.register(ItemCarrinho)
class ItemCarrinhoAdmin(admin.ModelAdmin):
    """Admin para ItemCarrinho"""
    list_display = ['carrinho', 'produto', 'quantidade', 'preco_unitario', 'subtotal_display', 'criado_em']
    list_filter = ['criado_em', 'atualizado_em']
    search_fields = ['carrinho__usuario__email', 'produto__nome']
    readonly_fields = ['subtotal_display', 'criado_em', 'atualizado_em']

    def subtotal_display(self, obj):
        return f"R$ {obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'