# pedidos/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Pedido, ItemPedido, StatusPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['produto', 'nome_produto', 'quantidade', 'preco_unitario', 'subtotal']


class StatusPedidoInline(admin.TabularInline):
    model = StatusPedido
    extra = 0
    readonly_fields = ['criado_em', 'criado_por']
    fields = ['status', 'observacao', 'criado_por', 'criado_em']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero',
        'cliente',
        'status_badge',
        'forma_pagamento_display',
        'total_formatado',
        'quantidade_itens',
        'criado_em'
    ]

    list_filter = [
        'status',
        'forma_pagamento',
        'criado_em',
        'pago_em'
    ]

    search_fields = [
        'numero',
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name',
        'codigo_rastreio'
    ]

    readonly_fields = [
        'numero',
        'subtotal',
        'total',
        'quantidade_itens',
        'criado_em',
        'atualizado_em',
        'pago_em',
        'enviado_em',
        'entregue_em',
        'cancelado_em'
    ]

    inlines = [ItemPedidoInline, StatusPedidoInline]

    fieldsets = (
        ('Informações do Pedido', {
            'fields': (
                'numero',
                'usuario',
                'endereco',
                'status',
                'forma_pagamento'
            )
        }),
        ('Valores', {
            'fields': (
                'subtotal',
                'desconto',
                'frete',
                'total',
                'quantidade_itens'
            )
        }),
        ('Observações', {
            'fields': ('observacao', 'observacao_interna'),
            'classes': ('collapse',)
        }),
        ('Rastreamento', {
            'fields': ('codigo_rastreio',)
        }),
        ('Datas', {
            'fields': (
                'criado_em',
                'atualizado_em',
                'pago_em',
                'enviado_em',
                'entregue_em',
                'cancelado_em'
            ),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Cliente')
    def cliente(self, obj):
        return obj.usuario.get_full_name()

    @admin.display(description='Status')
    def status_badge(self, obj):
        cores = {
            'aguardando_pagamento': '#ffc107',
            'pago': '#28a745',
            'em_separacao': '#17a2b8',
            'enviado': '#007bff',
            'entregue': '#28a745',
            'cancelado': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            cores.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )

    @admin.display(description='Forma de Pagamento')
    def forma_pagamento_display(self, obj):
        return obj.get_forma_pagamento_display()

    @admin.display(description='Total')
    def total_formatado(self, obj):
        return format_html(
            '<strong style="color: #28a745;">R$ {:.2f}</strong>',
            obj.total
        )

    actions = ['marcar_como_pago', 'marcar_como_enviado', 'cancelar_pedidos']

    @admin.action(description='✅ Marcar como Pago')
    def marcar_como_pago(self, request, queryset):
        from django.utils import timezone
        for pedido in queryset:
            if pedido.status == 'aguardando_pagamento':
                pedido.status = 'pago'
                pedido.pago_em = timezone.now()
                pedido.save()

                StatusPedido.objects.create(
                    pedido=pedido,
                    status='pago',
                    observacao='Marcado como pago via admin',
                    criado_por=request.user
                )

        self.message_user(request, f'{queryset.count()} pedido(s) marcado(s) como pago.')

    @admin.action(description='📦 Marcar como Enviado')
    def marcar_como_enviado(self, request, queryset):
        from django.utils import timezone
        for pedido in queryset.filter(status='pago'):
            pedido.status = 'enviado'
            pedido.enviado_em = timezone.now()
            pedido.save()

            StatusPedido.objects.create(
                pedido=pedido,
                status='enviado',
                observacao='Marcado como enviado via admin',
                criado_por=request.user
            )

        self.message_user(request, f'{queryset.count()} pedido(s) marcado(s) como enviado.')

    @admin.action(description='❌ Cancelar Pedidos')
    def cancelar_pedidos(self, request, queryset):
        from django.utils import timezone
        count = 0
        for pedido in queryset.filter(status='aguardando_pagamento'):
            # Devolve estoque
            for item in pedido.itens.all():
                produto = item.produto
                produto.estoque += item.quantidade
                produto.save()

            pedido.status = 'cancelado'
            pedido.cancelado_em = timezone.now()
            pedido.save()

            StatusPedido.objects.create(
                pedido=pedido,
                status='cancelado',
                observacao='Cancelado via admin',
                criado_por=request.user
            )
            count += 1

        self.message_user(request, f'{count} pedido(s) cancelado(s).')


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido_numero', 'nome_produto', 'quantidade', 'preco_unitario', 'subtotal']
    list_filter = ['criado_em']
    search_fields = ['pedido__numero', 'nome_produto', 'produto__nome']
    readonly_fields = ['subtotal', 'criado_em']

    @admin.display(description='Pedido')
    def pedido_numero(self, obj):
        return obj.pedido.numero