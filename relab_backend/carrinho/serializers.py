from rest_framework import serializers
from .models import Carrinho, ItemCarrinho


class ProdutoCarrinhoSerializer(serializers.Serializer):
    """Serializer simples para exibir detalhes do produto no carrinho"""
    id = serializers.IntegerField()
    nome = serializers.CharField()
    slug = serializers.CharField()
    preco = serializers.DecimalField(max_digits=10, decimal_places=2)
    preco_promocional = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    preco_final = serializers.DecimalField(max_digits=10, decimal_places=2)
    imagem = serializers.ImageField(allow_null=True)
    estoque = serializers.IntegerField()
    categoria_nome = serializers.CharField(source='categoria.nome', allow_null=True)


class ItemCarrinhoSerializer(serializers.ModelSerializer):
    """Serializer para itens do carrinho"""
    produto_detalhes = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ItemCarrinho
        fields = [
            'id', 'produto', 'produto_detalhes', 'quantidade',
            'preco_unitario', 'subtotal', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'preco_unitario', 'criado_em', 'atualizado_em']

    def get_produto_detalhes(self, obj):
        """Retorna os detalhes do produto"""
        produto = obj.produto
        return {
            'id': produto.id,
            'nome': produto.nome,
            'slug': produto.slug,
            'preco': produto.preco,
            'preco_promocional': produto.preco_promocional,
            'preco_final': produto.preco_final,
            'imagem': produto.imagem.url if produto.imagem else None,
            'estoque': produto.estoque,
            'categoria_nome': produto.categoria.nome if produto.categoria else None,
        }

    def validate_quantidade(self, value):
        """Valida a quantidade"""
        if value < 1:
            raise serializers.ValidationError("A quantidade deve ser no mínimo 1.")
        if value > 99:
            raise serializers.ValidationError("A quantidade máxima é 99.")
        return value

    def validate(self, data):
        """Valida o estoque do produto"""
        produto = data.get('produto')
        quantidade = data.get('quantidade', 1)

        if not produto.ativo:
            raise serializers.ValidationError({
                'produto': 'Este produto não está mais disponível.'
            })

        if produto.estoque < quantidade:
            raise serializers.ValidationError({
                'quantidade': f'Estoque insuficiente. Disponível: {produto.estoque}'
            })

        return data


class AdicionarItemSerializer(serializers.Serializer):
    """Serializer para adicionar item ao carrinho"""
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(default=1, min_value=1, max_value=99)


class AtualizarQuantidadeSerializer(serializers.Serializer):
    """Serializer para atualizar quantidade de um item"""
    quantidade = serializers.IntegerField(min_value=1, max_value=99)


class CarrinhoSerializer(serializers.ModelSerializer):
    """Serializer completo do carrinho"""
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total_itens = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Carrinho
        fields = [
            'id', 'usuario', 'itens', 'total_itens',
            'subtotal', 'total', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'usuario', 'criado_em', 'atualizado_em']