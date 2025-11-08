# produtos/serializers.py
from rest_framework import serializers
from .models import Categoria, Produto, ImagemProduto


class ImagemProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemProduto
        fields = ['id', 'imagem', 'ordem']


class CategoriaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    total_produtos = serializers.ReadOnlyField()

    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'imagem', 'total_produtos']


class CategoriaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes"""
    total_produtos = serializers.ReadOnlyField()

    class Meta:
        model = Categoria
        fields = '__all__'


class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializer otimizado para listagens"""
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    preco_final = serializers.ReadOnlyField()
    em_promocao = serializers.ReadOnlyField()
    desconto_percentual = serializers.ReadOnlyField()
    disponivel_venda = serializers.ReadOnlyField()

    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'slug', 'descricao_curta',
            'categoria', 'categoria_nome',
            'preco', 'preco_promocional', 'preco_final',
            'em_promocao', 'desconto_percentual',
            'estoque', 'disponivel_venda',
            'imagem', 'em_destaque'
        ]


class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do produto"""
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_slug = serializers.CharField(source='categoria.slug', read_only=True)
    imagens = ImagemProdutoSerializer(many=True, read_only=True)

    # Campos calculados
    preco_final = serializers.ReadOnlyField()
    em_promocao = serializers.ReadOnlyField()
    desconto_percentual = serializers.ReadOnlyField()
    estoque_baixo = serializers.ReadOnlyField()
    disponivel_venda = serializers.ReadOnlyField()

    class Meta:
        model = Produto
        fields = '__all__'


class ProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e edição"""

    class Meta:
        model = Produto
        exclude = ['visualizacoes', 'vendas']

    def validate(self, data):
        # Validação: preço promocional deve ser menor que preço normal
        preco = data.get('preco')
        preco_promocional = data.get('preco_promocional')

        if preco_promocional and preco_promocional >= preco:
            raise serializers.ValidationError({
                'preco_promocional': 'O preço promocional deve ser menor que o preço normal.'
            })

        return data