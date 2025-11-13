# config/urls.py (PROFISSIONAL AVANÇADO)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# URLs da API
api_v1_patterns = [
    path('produtos/', include('produtos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('carrinho/', include('carrinho.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('pagamentos/', include('pagamentos.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include(api_v1_patterns)),

    # Futura API v2 (quando precisar)
    # path('api/v2/', include(api_v2_patterns)),
]

# Arquivos estáticos (apenas em desenvolvimento)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customização do Admin
admin.site.site_header = "Relab - Administração"
admin.site.site_title = "Relab Admin"
admin.site.index_title = "Painel de Controle"