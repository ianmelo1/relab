from django.urls import path
from .views import CarrinhoViewSet

# Como estamos usando ViewSet, precisamos mapear manualmente as actions
carrinho_list = CarrinhoViewSet.as_view({
    'get': 'list',
})

carrinho_adicionar = CarrinhoViewSet.as_view({
    'post': 'adicionar',
})

carrinho_atualizar = CarrinhoViewSet.as_view({
    'patch': 'atualizar',
})

carrinho_remover = CarrinhoViewSet.as_view({
    'delete': 'remover',
})

carrinho_limpar = CarrinhoViewSet.as_view({
    'delete': 'limpar',
})

urlpatterns = [
    path('', carrinho_list, name='carrinho'),
    path('adicionar/', carrinho_adicionar, name='carrinho-adicionar'),
    path('atualizar/<int:pk>/', carrinho_atualizar, name='carrinho-atualizar'),
    path('remover/<int:pk>/', carrinho_remover, name='carrinho-remover'),
    path('limpar/', carrinho_limpar, name='carrinho-limpar'),
]