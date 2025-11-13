from rest_framework import serializers
from .models import Pagamento


class PagamentoSerializer(serializers.ModelSerializer):
    pedido_id = serializers.IntegerField(source='pedido.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Pagamento
        fields = [
            'id',
            'pedido_id',
            'preference_id',
            'payment_id',
            'tipo',
            'status',
            'status_display',
            'valor',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']


class CriarPagamentoSerializer(serializers.Serializer):
    pedido_id = serializers.IntegerField()

    def validate_pedido_id(self, value):
        from pedidos.models import Pedido

        # Verificar se pedido existe
        try:
            pedido = Pedido.objects.get(id=value)
        except Pedido.DoesNotExist:
            raise serializers.ValidationError("Pedido não encontrado")

        # Verificar se já tem pagamento
        if hasattr(pedido, 'pagamento'):
            raise serializers.ValidationError("Este pedido já possui um pagamento")

        return value