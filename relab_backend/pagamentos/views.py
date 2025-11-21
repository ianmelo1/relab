from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import mercadopago
import hmac
import hashlib

from .models import Pagamento
from .serializers import PagamentoSerializer, CriarPagamentoSerializer
from pedidos.models import Pedido


class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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
            pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)

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
                "notification_url": f"{settings.SITE_URL}/api/v1/pagamentos/webhook/",
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            # Criar registro de pagamento
            pagamento = Pagamento.objects.create(
                pedido=pedido,
                preference_id=preference['id'],
                valor=pedido.total,
                dados_mercadopago=preference
            )

            pedido.status = 'aguardando_pagamento'
            pedido.save()

            return Response({
                'pagamento_id': pagamento.id,
                'preference_id': preference['id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference['sandbox_init_point'],
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

        IMPORTANTE: Configure no painel do MP:
        - URL: https://seusite.com/api/v1/pagamentos/webhook/
        - Eventos: payment, merchant_order
        """

        # ===== VALIDAÇÃO DE SEGURANÇA =====
        # Validar assinatura do Mercado Pago (OBRIGATÓRIO em produção)
        x_signature = request.headers.get('x-signature')
        x_request_id = request.headers.get('x-request-id')

        if settings.MERCADO_PAGO_WEBHOOK_SECRET and x_signature:
            # Validar assinatura HMAC
            data_id = request.query_params.get('data.id', '')
            expected_signature = hmac.new(
                settings.MERCADO_PAGO_WEBHOOK_SECRET.encode(),
                f"{x_request_id}{data_id}".encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(x_signature, expected_signature):
                return Response(
                    {'error': 'Assinatura inválida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # ===== OBTER PAYMENT ID =====
        # Mercado Pago envia de várias formas
        payment_id = None

        # Formato 1: Query param
        payment_id = request.query_params.get('data.id')

        # Formato 2: Body JSON
        if not payment_id and request.data:
            payment_id = request.data.get('data', {}).get('id')

        # Formato 3: ID direto
        if not payment_id and request.data:
            payment_id = request.data.get('id')

        if not payment_id:
            return Response(
                {'error': 'Payment ID não fornecido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar informações do pagamento no Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info["response"]

            # Buscar pedido pela external_reference
            pedido_id = payment_data.get('external_reference')
            if not pedido_id:
                return Response(
                    {'error': 'External reference não encontrada'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pedido = Pedido.objects.get(id=pedido_id)

            # CORREÇÃO: Buscar pagamento corretamente
            try:
                pagamento = Pagamento.objects.get(pedido=pedido)
            except Pagamento.DoesNotExist:
                return Response(
                    {'error': 'Pagamento não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

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

                # TODO: Enviar email de confirmação
                # from .tasks import enviar_email_confirmacao
                # enviar_email_confirmacao.delay(pedido.id)

            elif payment_data['status'] == 'rejected':
                pedido.status = 'pagamento_rejeitado'
                pedido.save()

            elif payment_data['status'] in ['pending', 'in_process']:
                pedido.status = 'aguardando_pagamento'
                pedido.save()

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)

        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log do erro (adicione logging em produção)
            print(f"Erro no webhook: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def status_pagamento(self, request, pk=None):
        """
        Consulta o status atual de um pagamento
        """
        try:
            pagamento = self.get_object()

            if pagamento.payment_id:
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