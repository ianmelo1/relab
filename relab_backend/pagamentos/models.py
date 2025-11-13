from django.db import models
from pedidos.models import Pedido


class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('in_process', 'Em Processamento'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    TIPO_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='pagamento'
    )

    # Dados do Mercado Pago
    preference_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    # Informações do pagamento
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    # Dados adicionais
    dados_mercadopago = models.JSONField(default=dict, blank=True)

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f"Pagamento #{self.id} - Pedido #{self.pedido.id} - {self.status}"