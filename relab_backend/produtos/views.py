# produtos/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
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
    ViewSet para Categorias
    - GET: Público (qualquer um pode ver)
    - POST/PUT/DELETE: Apenas admin
    """
    queryset = Categoria.objects.filter(ativo=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'ordem', 'criado_em']
    ordering = ['ordem', 'nome']

    # ✅ ADICIONAR ISSO
    permission_classes = [IsAuthenticatedOrReadOnly]  # Leitura pública, escrita autenticada

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoriaDetailSerializer
        return CategoriaListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            produtos_count=Count('produtos', filter=Q(produtos__ativo=True))
        )

        if self.request.query_params.get('com_produtos') == 'true':
            queryset = queryset.filter(produtos_count__gt=0)

        return queryset

    @action(detail=True, methods=['get'])
    def produtos(self, request, pk=None):
        """Retorna todos os produtos de uma categoria"""
        categoria = self.get_object()
        produtos = categoria.produtos.filter(ativo=True, disponivel=True)

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
    ViewSet para Produtos
    - GET: Público
    - POST/PUT/DELETE: Apenas admin
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

    # ✅ ADICIONAR ISSO
    permission_classes = [IsAuthenticatedOrReadOnly]  # Leitura pública, escrita autenticada

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProdutoDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProdutoCreateUpdateSerializer
        return ProdutoListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.filter(ativo=True, disponivel=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Override para incrementar visualizações"""
        instance = self.get_object()
        instance.incrementar_visualizacoes()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def destaques(self, request):
        """Endpoint público: produtos em destaque"""
        produtos = self.get_queryset().filter(
            em_destaque=True,
            ativo=True,
            disponivel=True
        )[:8]
        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def promocoes(self, request):
        """Endpoint público: produtos em promoção"""
        produtos = self.get_queryset().filter(
            preco_promocional__isnull=False,
            ativo=True,
            disponivel=True
        )

        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def mais_vendidos(self, request):
        """Endpoint público: produtos mais vendidos"""
        produtos = self.get_queryset().filter(
            ativo=True,
            disponivel=True
        ).order_by('-vendas')[:10]
        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def novidades(self, request):
        """Endpoint público: produtos mais recentes"""
        produtos = self.get_queryset().filter(
            ativo=True,
            disponivel=True
        ).order_by('-criado_em')[:12]
        serializer = ProdutoListSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def adicionar_imagem(self, request, pk=None):
        """Endpoint admin: adicionar imagem ao produto"""
        produto = self.get_object()
        serializer = ImagemProdutoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(produto=produto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def busca_avancada(self, request):
        """Endpoint público: busca avançada"""
        queryset = self.get_queryset()

        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(descricao__icontains=q) |
                Q(descricao_curta__icontains=q)
            )

        preco_min = request.query_params.get('preco_min')
        preco_max = request.query_params.get('preco_max')
        if preco_min:
            queryset = queryset.filter(preco__gte=preco_min)
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)

        categorias = request.query_params.getlist('categorias[]')
        if categorias:
            queryset = queryset.filter(categoria_id__in=categorias)

        ordenar = request.query_params.get('ordenar', '-criado_em')
        queryset = queryset.order_by(ordenar)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProdutoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoListSerializer(queryset, many=True)
        return Response(serializer.data)