# pagamentos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PagamentoViewSet

app_name = 'pagamentos'  # Namespace para reverse URLs

router = DefaultRouter()
router.register(r'', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs geradas:
# GET    /api/v1/pagamentos/                       - Lista pagamentos do usuário
# GET    /api/v1/pagamentos/{id}/                  - Detalhe do pagamento
# 
# Custom actions:
# POST   /api/v1/pagamentos/criar_preferencia/    - Criar preferência MP
# POST   /api/v1/pagamentos/webhook/              - Webhook do Mercado Pago
# GET    /api/v1/pagamentos/{id}/status_pagamento/ - Consultar status