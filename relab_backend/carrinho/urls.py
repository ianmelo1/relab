# carrinho/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarrinhoViewSet

app_name = 'carrinho'  # Namespace para reverse URLs

router = DefaultRouter()
router.register(r'', CarrinhoViewSet, basename='carrinho')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs geradas com @action decorators no ViewSet:
# GET    /api/v1/carrinho/                    - Ver carrinho
# POST   /api/v1/carrinho/adicionar/          - Adicionar item
# PATCH  /api/v1/carrinho/{id}/atualizar/     - Atualizar quantidade
# DELETE /api/v1/carrinho/{id}/remover/       - Remover item
# DELETE /api/v1/carrinho/limpar/             - Limpar carrinho
