import django_filters
from django.db import models
from .models import Produto


class ProdutoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')
    categoria = django_filters.NumberFilter(field_name='categoria__id')
    categoria_slug = django_filters.CharFilter(field_name='categoria__slug')
    preco_min = django_filters.NumberFilter(field_name='preco', lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name='preco', lookup_expr='lte')
    em_promocao = django_filters.BooleanFilter(method='filter_em_promocao')
    em_destaque = django_filters.BooleanFilter()
    disponivel = django_filters.BooleanFilter()
    em_estoque = django_filters.BooleanFilter(method='filter_em_estoque')

    class Meta:
        model = Produto
        fields = ['categoria', 'categoria_slug', 'em_destaque', 'disponivel']

    def filter_em_promocao(self, queryset, name, value):
        if value:
            return queryset.filter(
                preco_promocional__isnull=False,
                preco_promocional__lt=models.F('preco')
            )
        return queryset

    def filter_em_estoque(self, queryset, name, value):
        if value:
            return queryset.filter(estoque__gt=0)
        return queryset.filter(estoque=0)