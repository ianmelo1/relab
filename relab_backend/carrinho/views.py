from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.apps import apps

from .models import Carrinho, ItemCarrinho
from .serializers import (
    CarrinhoSerializer,
    ItemCarrinhoSerializer,
    AdicionarItemSerializer,
    AtualizarQuantidadeSerializer
)

# Lazy import para evitar circular import
Produto = apps.get_model('produtos', 'Produto')


class CarrinhoViewSet(viewsets.ViewSet):
    """
    ViewSet para gerenciar o carrinho de compras

    - GET /api/carrinho/ - Ver carrinho
    - POST /api/carrinho/adicionar/ - Adicionar item
    - PATCH /api/carrinho/atualizar/{item_id}/ - Atualizar quantidade
    - DELETE /api/carrinho/remover/{item_id}/ - Remover item
    - DELETE /api/carrinho/limpar/ - Limpar carrinho
    """
    permission_classes = [IsAuthenticated]

    def get_or_create_carrinho(self, usuario):
        """Obtém ou cria o carrinho do usuário"""
        carrinho, created = Carrinho.objects.get_or_create(usuario=usuario)
        return carrinho

    def list(self, request):
        """
        GET /api/carrinho/
        Retorna o carrinho do usuário
        """
        carrinho = self.get_or_create_carrinho(request.user)
        serializer = CarrinhoSerializer(carrinho)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def adicionar(self, request):
        """
        POST /api/carrinho/adicionar/
        Body: {"produto_id": 1, "quantidade": 2}

        Adiciona um produto ao carrinho ou incrementa a quantidade se já existir
        """
        serializer = AdicionarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        produto_id = serializer.validated_data['produto_id']
        quantidade = serializer.validated_data['quantidade']

        # Verifica se o produto existe
        produto = get_object_or_404(Produto, id=produto_id, ativo=True)

        # Verifica estoque
        if produto.estoque < quantidade:
            return Response(
                {'erro': f'Estoque insuficiente. Disponível: {produto.estoque}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtém ou cria o carrinho
        carrinho = self.get_or_create_carrinho(request.user)

        # Verifica se o produto já está no carrinho
        item, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': quantidade, 'preco_unitario': produto.preco}
        )

        if not created:
            # Se já existe, incrementa a quantidade
            nova_quantidade = item.quantidade + quantidade

            if nova_quantidade > produto.estoque:
                return Response(
                    {'erro': f'Estoque insuficiente. Disponível: {produto.estoque}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if nova_quantidade > 99:
                return Response(
                    {'erro': 'Quantidade máxima por produto é 99'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantidade = nova_quantidade
            item.save()

        # Retorna o carrinho atualizado
        carrinho_serializer = CarrinhoSerializer(carrinho)
        return Response(
            carrinho_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def atualizar(self, request, pk=None):
        """
        PATCH /api/carrinho/atualizar/{item_id}/
        Body: {"quantidade": 3}

        Atualiza a quantidade de um item específico
        """
        serializer = AtualizarQuantidadeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        carrinho = self.get_or_create_carrinho(request.user)

        # Busca o item no carrinho do usuário
        item = get_object_or_404(ItemCarrinho, id=pk, carrinho=carrinho)

        nova_quantidade = serializer.validated_data['quantidade']

        # Verifica estoque
        if item.produto.estoque < nova_quantidade:
            return Response(
                {'erro': f'Estoque insuficiente. Disponível: {item.produto.estoque}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantidade = nova_quantidade
        item.save()

        # Retorna o carrinho atualizado
        carrinho_serializer = CarrinhoSerializer(carrinho)
        return Response(carrinho_serializer.data)

    @action(detail=True, methods=['delete'])
    def remover(self, request, pk=None):
        """
        DELETE /api/carrinho/remover/{item_id}/

        Remove um item específico do carrinho
        """
        carrinho = self.get_or_create_carrinho(request.user)
        item = get_object_or_404(ItemCarrinho, id=pk, carrinho=carrinho)
        item.delete()

        # Retorna o carrinho atualizado
        carrinho_serializer = CarrinhoSerializer(carrinho)
        return Response(carrinho_serializer.data)

    @action(detail=False, methods=['delete'])
    def limpar(self, request):
        """
        DELETE /api/carrinho/limpar/

        Remove todos os itens do carrinho
        """
        carrinho = self.get_or_create_carrinho(request.user)
        carrinho.limpar()

        carrinho_serializer = CarrinhoSerializer(carrinho)
        return Response(carrinho_serializer.data)