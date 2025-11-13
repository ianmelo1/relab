# pedidos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet

app_name = 'pedidos'  # Namespace para reverse URLs

router = DefaultRouter()
router.register(r'', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs geradas:
# GET    /api/v1/pedidos/                     - Lista pedidos do usuário
# POST   /api/v1/pedidos/                     - Criar pedido
# GET    /api/v1/pedidos/{id}/                - Detalhe do pedido
# PUT    /api/v1/pedidos/{id}/                - Atualizar pedido
# PATCH  /api/v1/pedidos/{id}/                - Atualizar pedido (parcial)
# DELETE /api/v1/pedidos/{id}/                - Cancelar pedido
#
# Custom actions
# POST   /api/v1/pedidos/criar_do_carrinho/   - Criar pedido do carrinho
# PATCH  /api/v1/pedidos/{id}/atualizar_status/ - Atualizar status