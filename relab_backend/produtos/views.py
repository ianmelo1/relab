# produtos/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from .models import Categoria, Produto, ImagemProduto
from .serializers import (
    CategoriaListSerializer,
    CategoriaDetailSerializer,
    ProdutoListSerializer,
    ProdutoDetailSerializer,
    ProdutoCreateUpdateSerializer,
    ImagemProdutoSerializer
)
from .filters import ProdutoFilter


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Categorias com endpoints customizados

    list: Lista todas categorias ativas
    retrieve: Detalhe de uma categoria
    create: Criar nova categoria (admin)
    update: Atualizar categoria (admin)
    delete: Deletar categoria (admin)
    produtos: Lista produtos de uma categoria específica
    """
    queryset = Categoria.objects.filter(ativo=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'ordem', 'criado_em']
    ordering = ['ordem', 'nome']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoriaDetailSerializer
        return CategoriaListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Adiciona contagem de produtos
        queryset = queryset.annotate(
            produtos_count=Count('produtos', filter=Q(produtos__ativo=True))
        )

        # Filtro: apenas categorias com produtos
        if self.request.query_params.get('com_produtos') == 'true':
            queryset = queryset.filter(produtos_count__gt=0)

        return queryset

    @action(detail=True, methods=['get'])
    def produtos(self, request, pk=None):
        """
        Endpoint: /api/categorias/{id}/produtos/
        Retorna todos os produtos de uma categoria
        """
        categoria = self.get_object()
        produtos = categoria.produtos.filter(ativo=True, disponivel=True)

        # Aplica filtros
        ordenar = request.query_params.get('ordenar', '-criado_em')
        produtos = produtos.order_by(ordenar)

        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)


class ProdutoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Produtos com filtros avançados

    Filtros disponíveis:
    - ?categoria=1
    - ?preco_min=10&preco_max=100
    - ?em_promocao=true
    - ?em_destaque=true
    - ?search=notebook
    - ?ordenar=preco (preco, -preco, nome, -criado_em)
    """
    queryset = Produto.objects.select_related('categoria').prefetch_related('imagens')
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProdutoFilter
    search_fields = ['nome', 'descricao', 'descricao_curta', 'meta_keywords']
    ordering_fields = ['preco', 'nome', 'criado_em', 'visualizacoes', 'vendas']
    ordering = ['-criado_em']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProdutoDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProdutoCreateUpdateSerializer
        return ProdutoListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apenas produtos ativos e disponíveis para listagem pública
        if self.action == 'list':
            queryset = queryset.filter(ativo=True, disponivel=True)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Override para incrementar visualizações"""
        instance = self.get_object()
        instance.incrementar_visualizacoes()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def destaques(self, request):
        """
        Endpoint: /api/produtos/destaques/
        Retorna produtos em destaque
        """
        produtos = self.get_queryset().filter(
            em_destaque=True,
            ativo=True,
            disponivel=True
        )[:8]

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def promocoes(self, request):
        """
        Endpoint: /api/produtos/promocoes/
        Retorna produtos em promoção
        """
        produtos = self.get_queryset().filter(
            preco_promocional__isnull=False,
            ativo=True,
            disponivel=True
        ).exclude(
            preco_promocional__gte=models.F('preco')
        )

        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        """
        Endpoint: /api/produtos/mais_vendidos/
        Retorna produtos mais vendidos
        """
        produtos = self.get_queryset().filter(
            ativo=True,
            disponivel=True
        ).order_by('-vendas')[:10]

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def novidades(self, request):
        """
        Endpoint: /api/produtos/novidades/
        Retorna produtos mais recentes
        """
        produtos = self.get_queryset().filter(
            ativo=True,
            disponivel=True
        ).order_by('-criado_em')[:12]

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adicionar_imagem(self, request, pk=None):
        """
        Endpoint: /api/produtos/{id}/adicionar_imagem/
        Adiciona imagem adicional ao produto
        """
        produto = self.get_object()
        serializer = ImagemProdutoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(produto=produto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def busca_avancada(self, request):
        """
        Endpoint: /api/produtos/busca_avancada/
        Busca avançada com múltiplos filtros
        """
        queryset = self.get_queryset()

        # Filtro por nome ou descrição
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(descricao__icontains=q) |
                Q(descricao_curta__icontains=q)
            )

        # Filtro por faixa de preço
        preco_min = request.query_params.get('preco_min')
        preco_max = request.query_params.get('preco_max')
        if preco_min:
            queryset = queryset.filter(preco__gte=preco_min)
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)

        # Filtro por categoria (múltiplas)
        categorias = request.query_params.getlist('categorias[]')
        if categorias:
            queryset = queryset.filter(categoria_id__in=categorias)

        # Ordenação
        ordenar = request.query_params.get('ordenar', '-criado_em')
        queryset = queryset.order_by(ordenar)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProdutoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoListSerializer(queryset, many=True)
        return Response(serializer.data)