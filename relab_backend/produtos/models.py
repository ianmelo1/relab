from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='produtos'
    )

    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    estoque = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    em_destaque = models.BooleanField(default=False)

    imagem = models.ImageField(
        upload_to='produtos/',
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome

    @property
    def preco_final(self):
        """Retorna preço promocional se existir, senão retorna preço normal"""
        return self.preco_promocional if self.preco_promocional else self.preco

    @property
    def em_promocao(self):
        """Verifica se produto está em promoção"""
        return self.preco_promocional is not None and self.preco_promocional < self.preco