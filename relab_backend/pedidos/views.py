# pedidos/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .models import Pedido, StatusPedido
from .serializers import (
    PedidoSerializer,
    PedidoCreateSerializer,
    PedidoFromCarrinhoSerializer,  # 🔥 ADICIONE ESTE IMPORT
    StatusPedidoSerializer
)


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar pedidos
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'forma_pagamento']
    search_fields = ['numero', 'usuario__email', 'usuario__first_name']
    ordering_fields = ['criado_em', 'total']
    ordering = ['-criado_em']
    queryset = Pedido.objects.all()

    def get_queryset(self):
        """
        Clientes veem apenas seus pedidos
        Admins veem todos
        """
        user = self.request.user

        if user.is_staff or user.tipo_usuario == 'admin':
            return Pedido.objects.all().select_related(
                'usuario', 'endereco'
            ).prefetch_related('itens', 'historico_status')

        return Pedido.objects.filter(usuario=user).select_related(
            'usuario', 'endereco'
        ).prefetch_related('itens', 'historico_status')

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action == 'criar_do_carrinho':
            return PedidoFromCarrinhoSerializer
        return PedidoSerializer

    def perform_create(self, serializer):
        """Define o comportamento ao criar"""
        pedido = serializer.save()
        return pedido

    def create(self, request, *args, **kwargs):
        """Cria um novo pedido MANUALMENTE"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = self.perform_create(serializer)

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def criar_do_carrinho(self, request):
        """
        POST /api/pedidos/criar_do_carrinho/

        Cria um pedido automaticamente a partir dos itens do carrinho

        Body:
        {
            "endereco_id": 1,
            "forma_pagamento": "pix",
            "observacao": "Entregar no período da tarde"
        }
        """
        serializer = PedidoFromCarrinhoSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def atualizar_status(self, request, pk=None):
        """
        Atualiza o status do pedido

        Body:
        {
            "status": "pago",
            "observacao": "Pagamento confirmado"
        }
        """
        pedido = self.get_object()
        novo_status = request.data.get('status')
        observacao = request.data.get('observacao', '')

        if novo_status not in dict(Pedido.STATUS_CHOICES):
            return Response(
                {'error': 'Status inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.status = novo_status

        if novo_status == 'pago' and not pedido.pago_em:
            pedido.pago_em = timezone.now()
        elif novo_status == 'enviado' and not pedido.enviado_em:
            pedido.enviado_em = timezone.now()
        elif novo_status == 'entregue' and not pedido.entregue_em:
            pedido.entregue_em = timezone.now()
        elif novo_status == 'cancelado' and not pedido.cancelado_em:
            pedido.cancelado_em = timezone.now()

        pedido.save()

        StatusPedido.objects.create(
            pedido=pedido,
            status=novo_status,
            observacao=observacao,
            criado_por=request.user
        )

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def adicionar_rastreio(self, request, pk=None):
        """
        Adiciona código de rastreio ao pedido

        Body:
        {
            "codigo_rastreio": "BR123456789BR"
        }
        """
        pedido = self.get_object()
        codigo = request.data.get('codigo_rastreio')

        if not codigo:
            return Response(
                {'error': 'Código de rastreio é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.codigo_rastreio = codigo
        pedido.save()

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela um pedido (apenas se aguardando pagamento)
        """
        pedido = self.get_object()

        if pedido.usuario != request.user and not (
                request.user.is_staff or request.user.tipo_usuario == 'admin'
        ):
            return Response(
                {'error': 'Você não tem permissão para cancelar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )

        if pedido.status != 'aguardando_pagamento':
            return Response(
                {'error': 'Só é possível cancelar pedidos aguardando pagamento'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Devolve estoque
        for item in pedido.itens.all():
            produto = item.produto
            produto.estoque += item.quantidade
            produto.save()

        pedido.status = 'cancelado'
        pedido.cancelado_em = timezone.now()
        pedido.save()

        StatusPedido.objects.create(
            pedido=pedido,
            status='cancelado',
            observacao=request.data.get('observacao', 'Cancelado pelo cliente'),
            criado_por=request.user
        )

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def meus_pedidos(self, request):
        """Lista os pedidos do usuário autenticado"""
        pedidos = self.get_queryset()
        page = self.paginate_queryset(pedidos)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pedidos, many=True)
        return Response(serializer.data)