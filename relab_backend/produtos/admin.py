from django.contrib import admin
from .models import Categoria, Produto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ativo', 'criado_em']
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'estoque', 'ativo', 'em_destaque']
    list_filter = ['categoria', 'ativo', 'em_destaque']
    prepopulated_fields = {'slug': ('nome',)}