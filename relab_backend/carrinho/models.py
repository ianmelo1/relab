from django.db import models
from django.conf import settings
from produtos.models import Produto


class Carrinho(models.Model):
    """Carrinho de compras do usuário"""
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrinho'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'
        ordering = ['-atualizado_em']

    def __str__(self):
        return f"Carrinho de {self.usuario.email}"

    @property
    def total_itens(self):
        """Quantidade total de itens no carrinho"""
        return sum(item.quantidade for item in self.itens.all())

    @property
    def subtotal(self):
        """Valor total dos produtos (sem frete)"""
        return sum(item.subtotal for item in self.itens.all())

    @property
    def total(self):
        """Valor total (por enquanto só subtotal, depois adiciona frete)"""
        return self.subtotal

    def limpar(self):
        """Remove todos os itens do carrinho"""
        self.itens.all().delete()


class ItemCarrinho(models.Model):
    """Item individual do carrinho"""
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        'produtos.Produto',  # String reference para evitar circular import
        on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço do produto no momento da adição ao carrinho"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['carrinho', 'produto']
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    @property
    def subtotal(self):
        """Subtotal do item (quantidade x preço)"""
        return self.quantidade * self.preco_unitario

    def save(self, *args, **kwargs):
        """Salva o preço atual do produto se não foi definido"""
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)