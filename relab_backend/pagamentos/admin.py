# pagamentos/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Pagamento


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    """
    Admin profissional para gerenciar pagamentos
    """

    # Campos exibidos na lista
    list_display = [
        'id',
        'pedido_link',
        'usuario_info',
        'valor_formatado',
        'tipo_badge',
        'status_badge',
        'preference_id',
        'payment_id',
        'criado_em_formatado',
    ]

    # Filtros laterais
    list_filter = [
        'status',
        'tipo',
        'criado_em',
        'atualizado_em',
    ]

    # Campos de busca
    search_fields = [
        'id',
        'pedido__id',
        'pedido__usuario__username',
        'pedido__usuario__email',
        'preference_id',
        'payment_id',
    ]

    # Campos readonly (não podem ser editados)
    readonly_fields = [
        'pedido',
        'preference_id',
        'payment_id',
        'valor',
        'dados_mercadopago_formatado',
        'criado_em',
        'atualizado_em',
    ]

    # Campos editáveis
    fields = [
        'pedido',
        'status',
        'tipo',
        'valor',
        'preference_id',
        'payment_id',
        'dados_mercadopago_formatado',
        'criado_em',
        'atualizado_em',
    ]

    # Ordem padrão (mais recentes primeiro)
    ordering = ['-criado_em']

    # Quantidade de itens por página
    list_per_page = 50

    # Ações em massa
    actions = ['marcar_como_aprovado', 'marcar_como_rejeitado']

    # ========== Métodos Customizados ==========

    @admin.display(description='Pedido', ordering='pedido__id')
    def pedido_link(self, obj):
        """Link clicável para o pedido"""
        url = reverse('admin:pedidos_pedido_change', args=[obj.pedido.id])
        return format_html(
            '<a href="{}" style="font-weight: bold;">Pedido #{}</a>',
            url,
            obj.pedido.id
        )

    @admin.display(description='Usuário')
    def usuario_info(self, obj):
        """Informações do usuário"""
        usuario = obj.pedido.usuario
        nome = getattr(usuario, 'nome', usuario.username)
        return format_html(
            '<div><strong>{}</strong><br><small>{}</small></div>',
            nome,
            usuario.email
        )

    @admin.display(description='Valor', ordering='valor')
    def valor_formatado(self, obj):
        """Valor formatado com R$"""
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">R$ {}</span>',
            f'{obj.valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        )

    @admin.display(description='Tipo')
    def tipo_badge(self, obj):
        """Badge colorido para tipo de pagamento"""
        cores = {
            'credit_card': '#007bff',
            'debit_card': '#17a2b8',
            'pix': '#00c896',
            'boleto': '#ffc107',
        }

        icones = {
            'credit_card': '💳',
            'debit_card': '💳',
            'pix': '📱',
            'boleto': '🧾',
        }

        cor = cores.get(obj.tipo, '#6c757d')
        icone = icones.get(obj.tipo, '💰')

        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            cor,
            icone,
            obj.get_tipo_display() if obj.tipo else 'Pendente'
        )

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        """Badge colorido para status"""
        status_config = {
            'pending': {'cor': '#ffc107', 'emoji': '⏳', 'label': 'Pendente'},
            'approved': {'cor': '#28a745', 'emoji': '✅', 'label': 'Aprovado'},
            'rejected': {'cor': '#dc3545', 'emoji': '❌', 'label': 'Rejeitado'},
            'in_process': {'cor': '#17a2b8', 'emoji': '🔄', 'label': 'Processando'},
            'cancelled': {'cor': '#6c757d', 'emoji': '🚫', 'label': 'Cancelado'},
            'refunded': {'cor': '#fd7e14', 'emoji': '↩️', 'label': 'Reembolsado'},
        }

        config = status_config.get(obj.status, {'cor': '#6c757d', 'emoji': '❓', 'label': 'Desconhecido'})

        return format_html(
            '<span style="background: {}; color: white; padding: 5px 12px; '
            'border-radius: 15px; font-size: 12px; font-weight: bold; '
            'display: inline-block;">{} {}</span>',
            config['cor'],
            config['emoji'],
            config['label']
        )

    @admin.display(description='Criado em', ordering='criado_em')
    def criado_em_formatado(self, obj):
        """Data formatada"""
        return obj.criado_em.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Dados Mercado Pago')
    def dados_mercadopago_formatado(self, obj):
        """JSON formatado dos dados do MP"""
        import json
        if obj.dados_mercadopago:
            json_str = json.dumps(obj.dados_mercadopago, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background: #f8f9fa; padding: 10px; '
                'border-radius: 5px; max-height: 400px; overflow: auto;">{}</pre>',
                json_str
            )
        return '-'

    # ========== Ações em Massa ==========

    @admin.action(description='✅ Marcar como Aprovado')
    def marcar_como_aprovado(self, request, queryset):
        """Marca pagamentos selecionados como aprovados"""
        count = queryset.update(status='approved')
        self.message_user(
            request,
            f'{count} pagamento(s) marcado(s) como aprovado(s).',
            level='success'
        )

    @admin.action(description='❌ Marcar como Rejeitado')
    def marcar_como_rejeitado(self, request, queryset):
        """Marca pagamentos selecionados como rejeitados"""
        count = queryset.update(status='rejected')
        self.message_user(
            request,
            f'{count} pagamento(s) marcado(s) como rejeitado(s).',
            level='warning'
        )

    # ========== Permissões ==========

    def has_add_permission(self, request):
        """Não permite criar pagamentos manualmente"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Não permite deletar pagamentos (auditoria)"""
        return False

    # ========== Estatísticas no Topo ==========

    def changelist_view(self, request, extra_context=None):
        """Adiciona estatísticas no topo da lista"""
        from django.db.models import Sum, Count, Q
        from datetime import date, timedelta

        # Estatísticas gerais
        stats = Pagamento.objects.aggregate(
            total_pagamentos=Count('id'),
            total_aprovados=Count('id', filter=Q(status='approved')),
            total_rejeitados=Count('id', filter=Q(status='rejected')),
            total_pendentes=Count('id', filter=Q(status='pending')),
            valor_total=Sum('valor', filter=Q(status='approved')),
        )

        # Estatísticas do mês
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        stats_mes = Pagamento.objects.filter(
            criado_em__gte=inicio_mes
        ).aggregate(
            pagamentos_mes=Count('id'),
            valor_mes=Sum('valor', filter=Q(status='approved')),
        )

        extra_context = extra_context or {}
        extra_context['stats'] = stats
        extra_context['stats_mes'] = stats_mes

        return super().changelist_view(request, extra_context=extra_context)


# Customização do título no admin
admin.site.site_header = "Relab E-commerce - Administração"
admin.site.site_title = "Relab Admin"
admin.site.index_title = "Painel de Controle"