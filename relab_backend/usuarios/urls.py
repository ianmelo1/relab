# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UsuarioViewSet, EnderecoViewSet, CustomTokenObtainPairView

app_name = 'usuarios'  # Namespace para reverse URLs

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')
router.register(r'enderecos', EnderecoViewSet, basename='endereco')

urlpatterns = [
    # Autenticação JWT (sempre no topo para prioridade de matching)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Rotas do router (usuários e endereços)
    path('', include(router.urls)),
]

# URLs geradas:
# POST   /api/v1/usuarios/auth/login/         - Login (obter tokens)
# POST   /api/v1/usuarios/auth/refresh/       - Refresh token
# POST   /api/v1/usuarios/auth/verify/        - Verificar token
# 
# POST   /api/v1/usuarios/                    - Criar usuário (registro)
# GET    /api/v1/usuarios/                    - Lista usuários (admin)
# GET    /api/v1/usuarios/{id}/               - Detalhe do usuário
# PUT    /api/v1/usuarios/{id}/               - Atualizar usuário
# DELETE /api/v1/usuarios/{id}/               - Deletar usuário
# 
# GET    /api/v1/usuarios/enderecos/          - Lista endereços do usuário
# POST   /api/v1/usuarios/enderecos/          - Criar endereço
# GET    /api/v1/usuarios/enderecos/{id}/     - Detalhe do endereço
# PUT    /api/v1/usuarios/enderecos/{id}/     - Atualizar endereço
# DELETE /api/v1/usuarios/enderecos/{id}/     - Deletar endereço