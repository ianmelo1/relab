# produtos/models.py
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    imagem = models.ImageField(upload_to='categorias/', null=True, blank=True, verbose_name="Imagem")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição", verbose_name="Ordem")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def save(self, *args, **kwargs):
        # Gera slug automaticamente se não existir
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    # Informações básicas
    nome = models.CharField(max_length=255, verbose_name="Nome")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    descricao_curta = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descrição Curta",
        help_text="Descrição breve para listagens"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Relacionamentos
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name="Categoria"
    )

    # Preços
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preço"
    )
    preco_promocional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preço Promocional"
    )
    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço de Custo",
        help_text="Preço de custo (não mostrado ao cliente)"
    )

    # Estoque e disponibilidade
    estoque = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Estoque"
    )
    estoque_minimo = models.IntegerField(
        default=5,
        verbose_name="Estoque Mínimo",
        help_text="Alerta quando estoque atingir este valor"
    )

    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    em_destaque = models.BooleanField(default=False, verbose_name="Em Destaque")
    disponivel = models.BooleanField(
        default=True,
        verbose_name="Disponível",
        help_text="Desmarque para ocultar temporariamente sem desativar"
    )

    # Mídia
    imagem = models.ImageField(
        upload_to='produtos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Imagem"
    )

    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Descrição",
        help_text="Descrição para mecanismos de busca"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Palavras-chave",
        help_text="Palavras-chave separadas por vírgula"
    )

    # Métricas
    visualizacoes = models.IntegerField(default=0, editable=False, verbose_name="Visualizações")
    vendas = models.IntegerField(default=0, editable=False, verbose_name="Vendas")

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def save(self, *args, **kwargs):
        """Gera slug automaticamente baseado no nome se não existir"""
        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1

            # Garante que o slug seja único
            while Produto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def preco_final(self):
        """Retorna o preço promocional se existir, senão o preço normal"""
        return self.preco_promocional if self.preco_promocional else self.preco

    @property
    def tem_estoque(self):
        """Verifica se há estoque disponível"""
        return self.estoque > 0

    @property
    def estoque_baixo(self):
        """Verifica se o estoque está abaixo do mínimo"""
        return self.estoque <= self.estoque_minimo

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['ativo', 'disponivel']),
            models.Index(fields=['-criado_em']),
        ]

    def __str__(self):
        return self.nome


class ImagemProduto(models.Model):
    """Imagens adicionais do produto"""
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='imagens',
        verbose_name="Produto"
    )
    imagem = models.ImageField(upload_to='produtos/%Y/%m/galeria/', verbose_name="Imagem")
    ordem = models.IntegerField(default=0, verbose_name="Ordem")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ['ordem', 'criado_em']
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens dos Produtos"

    def __str__(self):
        return f"Imagem de {self.produto.nome}"