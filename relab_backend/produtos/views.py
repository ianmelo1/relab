from rest_framework import viewsets
from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = Produto.objects.filter(ativo=True)
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__slug=categoria)
        return queryset