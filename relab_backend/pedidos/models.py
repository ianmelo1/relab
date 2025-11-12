# pedidos/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from usuarios.models import Usuario, Endereco
from produtos.models import Produto


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aguardando_pagamento', 'Aguardando Pagamento'),
        ('pago', 'Pago'),
        ('em_separacao', 'Em Separação'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('boleto', 'Boleto'),
    ]

    # Relacionamentos
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Endereço de Entrega'
    )

    # Informações do pedido
    numero = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name='Número do Pedido'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='aguardando_pagamento',
        verbose_name='Status'
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name='Forma de Pagamento'
    )

    # Valores
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )
    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto'
    )
    frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Frete'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total'
    )

    # Observações
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação do Cliente'
    )
    observacao_interna = models.TextField(
        blank=True,
        verbose_name='Observação Interna',
        help_text='Visível apenas para administradores'
    )

    # Rastreamento
    codigo_rastreio = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Código de Rastreio'
    )

    # Timestamps
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    pago_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Pago em'
    )
    enviado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado em'
    )
    entregue_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregue em'
    )
    cancelado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelado em'
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['usuario', '-criado_em']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Pedido #{self.numero} - {self.usuario.get_full_name()}"

    def save(self, *args, **kwargs):
        # Gera número único do pedido
        if not self.numero:
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique = str(uuid.uuid4())[:8].upper()
            self.numero = f"PED{timestamp}{unique}"

        # Calcula o total automaticamente
        self.total = self.subtotal - self.desconto + self.frete

        super().save(*args, **kwargs)

    @property
    def quantidade_itens(self):
        """Retorna a quantidade total de itens do pedido"""
        return sum(item.quantidade for item in self.itens.all())


class ItemPedido(models.Model):
    """Itens do pedido"""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedido',
        verbose_name='Produto'
    )

    # Informações do produto no momento da compra
    nome_produto = models.CharField(
        max_length=255,
        verbose_name='Nome do Produto',
        help_text='Nome do produto no momento da compra'
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Unitário'
    )
    quantidade = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantidade'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Subtotal'
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens dos Pedidos'
        ordering = ['id']

    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto}"

    def save(self, *args, **kwargs):
        # Salva informações do produto no momento da compra
        if not self.nome_produto:
            self.nome_produto = self.produto.nome
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco_final

        # Calcula subtotal
        self.subtotal = self.preco_unitario * self.quantidade

        super().save(*args, **kwargs)


class StatusPedido(models.Model):
    """Histórico de status do pedido"""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historico_status',
        verbose_name='Pedido'
    )
    status = models.CharField(
        max_length=30,
        choices=Pedido.STATUS_CHOICES,
        verbose_name='Status'
    )
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação'
    )
    criado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_pedidos_criados',
        verbose_name='Criado por'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Status do Pedido'
        verbose_name_plural = 'Histórico de Status'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.get_status_display()} - {self.criado_em.strftime('%d/%m/%Y %H:%M')}"