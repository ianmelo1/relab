# pedidos/serializers.py
from rest_framework import serializers
from .models import Pedido, ItemPedido, StatusPedido
from produtos.models import Produto


class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_imagem = serializers.ImageField(source='produto.imagem', read_only=True)

    class Meta:
        model = ItemPedido
        fields = [
            'id',
            'produto',
            'produto_nome',
            'produto_imagem',
            'nome_produto',
            'preco_unitario',
            'quantidade',
            'subtotal',
            'criado_em'
        ]
        read_only_fields = ['subtotal', 'nome_produto', 'preco_unitario']


class ItemPedidoCreateSerializer(serializers.Serializer):
    """Serializer para criar itens do pedido"""
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)

    def validate_produto_id(self, value):
        try:
            produto = Produto.objects.get(id=value)
            if not produto.disponivel_venda:
                raise serializers.ValidationError(
                    "Produto indisponível para venda."
                )
            return value
        except Produto.DoesNotExist:
            raise serializers.ValidationError("Produto não encontrado.")

    def validate(self, data):
        produto = Produto.objects.get(id=data['produto_id'])
        if produto.estoque < data['quantidade']:
            raise serializers.ValidationError(
                f"Estoque insuficiente. Disponível: {produto.estoque}"
            )
        return data


class StatusPedidoSerializer(serializers.ModelSerializer):
    criado_por_nome = serializers.CharField(
        source='criado_por.get_full_name',
        read_only=True
    )

    class Meta:
        model = StatusPedido
        fields = [
            'id',
            'status',
            'observacao',
            'criado_por',
            'criado_por_nome',
            'criado_em'
        ]


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    historico_status = StatusPedidoSerializer(many=True, read_only=True)
    cliente_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    endereco_completo = serializers.CharField(source='endereco.endereco_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    forma_pagamento_display = serializers.CharField(
        source='get_forma_pagamento_display',
        read_only=True
    )
    quantidade_itens = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id',
            'numero',
            'usuario',
            'cliente_nome',
            'endereco',
            'endereco_completo',
            'status',
            'status_display',
            'forma_pagamento',
            'forma_pagamento_display',
            'subtotal',
            'desconto',
            'frete',
            'total',
            'observacao',
            'observacao_interna',
            'codigo_rastreio',
            'quantidade_itens',
            'itens',
            'historico_status',
            'criado_em',
            'atualizado_em',
            'pago_em',
            'enviado_em',
            'entregue_em',
            'cancelado_em',
        ]
        read_only_fields = [
            'numero',
            'subtotal',
            'total',
            'criado_em',
            'atualizado_em',
            'pago_em',
            'enviado_em',
            'entregue_em',
            'cancelado_em',
        ]


class PedidoCreateSerializer(serializers.Serializer):
    """Serializer para criar pedido MANUALMENTE (com itens)"""
    endereco_id = serializers.IntegerField()
    forma_pagamento = serializers.ChoiceField(choices=Pedido.FORMA_PAGAMENTO_CHOICES)
    itens = ItemPedidoCreateSerializer(many=True)
    observacao = serializers.CharField(required=False, allow_blank=True)

    def validate_endereco_id(self, value):
        usuario = self.context['request'].user
        try:
            endereco = usuario.enderecos.get(id=value, ativo=True)
            return value
        except:
            raise serializers.ValidationError("Endereço inválido ou não pertence ao usuário.")

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError("O pedido deve ter pelo menos um item.")
        return value

    def create(self, validated_data):
        from decimal import Decimal
        from django.utils import timezone

        usuario = self.context['request'].user
        itens_data = validated_data.pop('itens')

        # Calcula subtotal
        subtotal = Decimal('0.00')
        for item_data in itens_data:
            produto = Produto.objects.get(id=item_data['produto_id'])
            subtotal += produto.preco_final * item_data['quantidade']

        # Cria o pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            endereco_id=validated_data['endereco_id'],
            forma_pagamento=validated_data['forma_pagamento'],
            subtotal=subtotal,
            observacao=validated_data.get('observacao', ''),
            frete=Decimal('0.00'),
            desconto=Decimal('0.00'),
        )

        # Cria os itens do pedido
        for item_data in itens_data:
            produto = Produto.objects.get(id=item_data['produto_id'])
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=item_data['quantidade']
            )

            # Atualiza estoque
            produto.estoque -= item_data['quantidade']
            produto.save()

        # Cria registro no histórico
        StatusPedido.objects.create(
            pedido=pedido,
            status='aguardando_pagamento',
            criado_por=usuario
        )

        return pedido


class PedidoFromCarrinhoSerializer(serializers.Serializer):
    """Serializer para criar pedido a partir do carrinho"""
    endereco_id = serializers.IntegerField()
    forma_pagamento = serializers.ChoiceField(choices=Pedido.FORMA_PAGAMENTO_CHOICES)
    observacao = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_endereco_id(self, value):
        usuario = self.context['request'].user
        try:
            endereco = usuario.enderecos.get(id=value, ativo=True)
            return value
        except:
            raise serializers.ValidationError("Endereço inválido ou não pertence ao usuário.")

    def create(self, validated_data):
        from decimal import Decimal
        from django.utils import timezone
        from carrinho.models import Carrinho

        usuario = self.context['request'].user

        # Busca o carrinho do usuário
        try:
            carrinho = Carrinho.objects.get(usuario=usuario)
        except Carrinho.DoesNotExist:
            raise serializers.ValidationError("Carrinho vazio ou não encontrado.")

        # Verifica se tem itens
        if not carrinho.itens.exists():
            raise serializers.ValidationError("Carrinho está vazio.")

        # Valida estoque de todos os itens
        for item in carrinho.itens.all():
            if not item.produto.disponivel_venda:
                raise serializers.ValidationError(
                    f"Produto '{item.produto.nome}' não está disponível."
                )
            if item.produto.estoque < item.quantidade:
                raise serializers.ValidationError(
                    f"Estoque insuficiente para '{item.produto.nome}'. "
                    f"Disponível: {item.produto.estoque}"
                )

        # Calcula subtotal do carrinho
        subtotal = carrinho.subtotal

        # Cria o pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            endereco_id=validated_data['endereco_id'],
            forma_pagamento=validated_data['forma_pagamento'],
            subtotal=subtotal,
            observacao=validated_data.get('observacao', ''),
            frete=Decimal('0.00'),
            desconto=Decimal('0.00'),
        )

        # Cria os itens do pedido a partir do carrinho
        for item_carrinho in carrinho.itens.all():
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item_carrinho.produto,
                quantidade=item_carrinho.quantidade,
                preco_unitario=item_carrinho.preco_unitario
            )

            # Atualiza estoque e vendas
            produto = item_carrinho.produto
            produto.estoque -= item_carrinho.quantidade
            produto.vendas += item_carrinho.quantidade
            produto.save()

        # Cria registro no histórico
        StatusPedido.objects.create(
            pedido=pedido,
            status='aguardando_pagamento',
            criado_por=usuario
        )

        # LIMPA O CARRINHO
        carrinho.limpar()

        return pedido