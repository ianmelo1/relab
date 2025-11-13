# produtos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProdutoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'', ProdutoViewSet, basename='produto')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs geradas:
# GET    /api/v1/produtos/                    - Lista produtos
# POST   /api/v1/produtos/                    - Cria produto
# GET    /api/v1/produtos/{id}/               - Detalhe do produto
# PUT    /api/v1/produtos/{id}/               - Atualiza produto (completo)
# PATCH  /api/v1/produtos/{id}/               - Atualiza produto (parcial)
# DELETE /api/v1/produtos/{id}/               - Deleta produto
# GET    /api/v1/produtos/categorias/         - Lista categorias
# POST   /api/v1/produtos/categorias/         - Cria categoria
# GET    /api/v1/produtos/categorias/{id}/    - Detalhe da categoria