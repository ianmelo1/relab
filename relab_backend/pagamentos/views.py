from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import mercadopago

from .models import Pagamento
from .serializers import PagamentoSerializer, CriarPagamentoSerializer
from pedidos.models import Pedido


class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Usuário só vê seus próprios pagamentos
        return Pagamento.objects.filter(pedido__usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def criar_preferencia(self, request):
        """
        Cria uma preferência de pagamento no Mercado Pago
        """
        serializer = CriarPagamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedido_id = serializer.validated_data['pedido_id']

        try:
            # Buscar pedido
            pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)

            # Configurar SDK do Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

            # Montar items do pedido
            items = []
            for item in pedido.itens.all():
                items.append({
                    "title": item.produto.nome,
                    "description": item.produto.descricao[:250] if item.produto.descricao else "",
                    "quantity": item.quantidade,
                    "unit_price": float(item.preco_unitario),
                    "currency_id": "BRL"
                })

            # Criar preferência
            preference_data = {
                "items": items,
                "payer": {
                    "name": request.user.nome if hasattr(request.user, 'nome') else request.user.username,
                    "email": request.user.email,
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/pagamento/sucesso",
                    "failure": f"{settings.SITE_URL}/pagamento/falha",
                    "pending": f"{settings.SITE_URL}/pagamento/pendente"
                },
                "auto_return": "approved",
                "statement_descriptor": "MEU ECOMMERCE",
                "external_reference": str(pedido.id),
                "notification_url": f"{settings.SITE_URL}/api/pagamentos/webhook/",
            }

            # Criar preferência no Mercado Pago
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            # Criar registro de pagamento
            pagamento = Pagamento.objects.create(
                pedido=pedido,
                preference_id=preference['id'],
                valor=pedido.total,
                dados_mercadopago=preference
            )

            # Atualizar status do pedido
            pedido.status = 'aguardando_pagamento'
            pedido.save()

            return Response({
                'pagamento_id': pagamento.id,
                'preference_id': preference['id'],
                'init_point': preference['init_point'],  # URL para redirecionar (desktop)
                'sandbox_init_point': preference['sandbox_init_point'],  # URL de teste
            }, status=status.HTTP_201_CREATED)

        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[])
    def webhook(self, request):
        """
        Webhook para receber notificações do Mercado Pago
        """
        # Mercado Pago envia o payment_id
        payment_id = request.query_params.get('data.id') or request.data.get('data', {}).get('id')

        if not payment_id:
            return Response({'error': 'Payment ID não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar informações do pagamento no Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info["response"]

            # Buscar pedido pela external_reference
            pedido_id = payment_data.get('external_reference')
            if not pedido_id:
                return Response({'error': 'External reference não encontrada'}, status=status.HTTP_400_BAD_REQUEST)

            pedido = Pedido.objects.get(id=pedido_id)
            pagamento = pedido.pagamento

            # Atualizar dados do pagamento
            pagamento.payment_id = payment_id
            pagamento.status = payment_data['status']
            pagamento.tipo = payment_data.get('payment_type_id', '')
            pagamento.dados_mercadopago = payment_data
            pagamento.save()

            # Atualizar status do pedido baseado no pagamento
            if payment_data['status'] == 'approved':
                pedido.status = 'confirmado'
                pedido.save()

                # Aqui você pode enviar email de confirmação
                # enviar_email_confirmacao(pedido)

            elif payment_data['status'] == 'rejected':
                pedido.status = 'pagamento_rejeitado'
                pedido.save()

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)

        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def status_pagamento(self, request, pk=None):
        """
        Consulta o status atual de um pagamento
        """
        try:
            pagamento = self.get_object()

            if pagamento.payment_id:
                # Consultar no Mercado Pago
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                payment_info = sdk.payment().get(pagamento.payment_id)
                payment_data = payment_info["response"]

                # Atualizar status
                pagamento.status = payment_data['status']
                pagamento.dados_mercadopago = payment_data
                pagamento.save()

            serializer = self.get_serializer(pagamento)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )