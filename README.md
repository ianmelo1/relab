#  Relab E-commerce - Documentação Interna

 **CONFIDENCIAL** - Apenas para desenvolvedores autorizados

---

##  Stack Completa

### Backend
- **Django 5.2.8** - Framework web
- **Django REST Framework** - API RESTful
- **PostgreSQL 15** - Banco de dados
- **JWT (Simple JWT)** - Autenticação via tokens
- **Django Filter** - Filtros avançados
- **Python Decouple** - Gerenciamento de variáveis

### Frontend
- **Next.js** - Framework React
- **TypeScript** - Tipagem estática
- **React** - Interface

### DevOps
- **Docker & Docker Compose** - Containerização
- **PostgreSQL (container)** - Banco em Docker

### Integrações
- **Mercado Pago** - Gateway de pagamento

---

##  Instalação Completa

### Pré-requisitos
```bash
- Docker Desktop instalado
- Docker Compose
- Git
- 4GB RAM mínimo
```

### Passo 1: Clone o Repositório
```bash
git clone [URL-DO-REPO-PRIVADO]
cd relab
```

### Passo 2: Configure as Variáveis de Ambiente

**Copie o arquivo de exemplo:**
```bash
cp .env.example .env
```

**Edite o `.env` com suas credenciais:**
```env
SECRET_KEY=django-insecure-sua-chave-aqui-MUDE-ISSO
DEBUG=True
DATABASE_PASSWORD=sua-senha-forte-aqui

# Mercado Pago - Obter em: https://www.mercadopago.com.br/developers/panel
MERCADO_PAGO_ACCESS_TOKEN=TEST-seu-token-aqui
MERCADO_PAGO_PUBLIC_KEY=TEST-sua-key-aqui
```

### Passo 3: Suba os Containers
```bash
# Build e start dos containers
docker-compose up -d --build

# Aguarde ~30 segundos para os serviços iniciarem
```

### Passo 4: Configuração Inicial do Django
```bash
# Aplicar migrações
docker-compose exec backend python manage.py migrate

# Criar superusuário (admin)
docker-compose exec backend python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput
```

### Passo 5: Acesse a Aplicação
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/v1
- **Django Admin:** http://localhost:8000/admin
- **Banco PostgreSQL:** localhost:5433

---

##  Estrutura do Banco de Dados

### Apps Django

#### `usuarios/`
- Model: `Usuario` (custom user)
- Autenticação JWT
- Perfis de cliente

#### `produtos/`
- Model: `Produto`
- Categorias
- Estoque
- Imagens (media)

#### `carrinho/`
- Model: `Carrinho`, `ItemCarrinho`
- Sessão de compra
- Cálculos automáticos

#### `pedidos/`
- Model: `Pedido`, `ItemPedido`
- Status: pendente, pago, enviado, entregue
- Histórico

#### `pagamentos/`
- Integração Mercado Pago
- Webhook para notificações
- Status de pagamento

---

##  Autenticação JWT

### Tokens
- **Access Token:** 2 horas de validade
- **Refresh Token:** 7 dias de validade
- **Rotação:** Tokens são rotacionados após refresh
- **Blacklist:** Tokens antigos são invalidados

### Endpoints de Auth
```
POST /api/v1/auth/login/          # Login
POST /api/v1/auth/refresh/        # Refresh token
POST /api/v1/auth/logout/         # Logout (blacklist)
POST /api/v1/auth/register/       # Registro
```

### Exemplo de Uso
```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'senha123' })
});

const { access, refresh } = await response.json();

// Usar o token
fetch('http://localhost:8000/api/v1/produtos/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
```

---

##  Comandos Úteis

### Docker
```bash
# Iniciar containers
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Parar containers
docker-compose down

# Parar e remover volumes (⚠️ APAGA O BANCO)
docker-compose down -v

# Rebuild após mudanças no Dockerfile
docker-compose up -d --build

# Acessar shell do container
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec db psql -U postgres -d relab_db
```

### Django (Backend)
```bash
# Criar migrações
docker-compose exec backend python manage.py makemigrations

# Aplicar migrações
docker-compose exec backend python manage.py migrate

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# Shell interativo do Django
docker-compose exec backend python manage.py shell

# Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic

# Criar dados de teste
docker-compose exec backend python manage.py seed_data  # se existir
```

### PostgreSQL (Banco)
```bash
# Acessar o PostgreSQL
docker-compose exec db psql -U postgres -d relab_db

# Backup do banco
docker-compose exec db pg_dump -U postgres relab_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres relab_db < backup.sql

# Ver tabelas
docker-compose exec db psql -U postgres -d relab_db -c "\dt"
```

### Frontend (Next.js)
```bash
# Instalar nova dependência
docker-compose exec frontend npm install [pacote]

# Build de produção
docker-compose exec frontend npm run build

# Limpar cache do Next.js
docker-compose exec frontend rm -rf .next
```

---

## 📡 Estrutura da API

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints Principais

#### Autenticação
```
POST   /auth/login/              # Login
POST   /auth/register/           # Registro
POST   /auth/refresh/            # Refresh token
POST   /auth/logout/             # Logout
```

#### Produtos
```
GET    /produtos/                # Listar produtos
GET    /produtos/{id}/           # Detalhe do produto
POST   /produtos/                # Criar (admin)
PUT    /produtos/{id}/           # Atualizar (admin)
DELETE /produtos/{id}/           # Deletar (admin)
```

#### Carrinho
```
GET    /carrinho/                # Ver carrinho
POST   /carrinho/adicionar/      # Adicionar item
PUT    /carrinho/atualizar/      # Atualizar quantidade
DELETE /carrinho/remover/{id}/   # Remover item
```

#### Pedidos
```
GET    /pedidos/                 # Listar pedidos do usuário
GET    /pedidos/{id}/            # Detalhe do pedido
POST   /pedidos/criar/           # Criar pedido
```

#### Pagamentos
```
POST   /pagamentos/processar/    # Processar pagamento
POST   /pagamentos/webhook/      # Webhook Mercado Pago
GET    /pagamentos/status/{id}/  # Status do pagamento
```

---

##  Integração Mercado Pago

### Configuração
1. Crie uma conta em: https://www.mercadopago.com.br
2. Acesse: https://www.mercadopago.com.br/developers/panel
3. Crie uma aplicação
4. Copie as credenciais de TESTE para o `.env`

### Fluxo de Pagamento
1. Cliente finaliza pedido
2. Backend cria preferência no Mercado Pago
3. Frontend redireciona para checkout
4. Mercado Pago processa pagamento
5. Webhook notifica backend
6. Status do pedido é atualizado

### Webhook URL
```
https://seu-dominio.com/api/v1/pagamentos/webhook/
```
*Configurar no painel do Mercado Pago*

---

##  Segurança

### Checklist de Produção
- [ ] Mudar `DEBUG=False`
- [ ] Gerar novo `SECRET_KEY` forte
- [ ] Configurar `ALLOWED_HOSTS` correto
- [ ] Usar credenciais de PRODUÇÃO do Mercado Pago
- [ ] Configurar HTTPS
- [ ] Habilitar CORS apenas para domínios permitidos
- [ ] Configurar firewall
- [ ] Backups automáticos do banco

### Geração de SECRET_KEY
```python
# No shell Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

##  Deploy (Railway)

### Preparação
1. Criar conta no Railway
2. Conectar repositório GitHub
3. Configurar variáveis de ambiente
4. Deploy automático via Git push

### Variáveis de Ambiente Railway
```
DEBUG=False
SECRET_KEY=[gerar-novo]
DATABASE_URL=[fornecido-pelo-railway]
ALLOWED_HOSTS=.railway.app,relab.co
MERCADO_PAGO_ACCESS_TOKEN=[produção]
MERCADO_PAGO_PUBLIC_KEY=[produção]
```

---

##  Troubleshooting

### Banco não conecta
```bash
# Verificar se o container está rodando
docker-compose ps

# Ver logs do banco
docker-compose logs db

# Recriar o banco
docker-compose down -v
docker-compose up -d
```

### Frontend não conecta no backend
```bash
# Verificar variável NEXT_PUBLIC_API_URL
# Deve ser: http://localhost:8000/api/v1

# Verificar CORS no backend (settings.py)
# Adicionar http://localhost:3000 em CORS_ALLOWED_ORIGINS
```

### Erro de migração
```bash
# Resetar migrações (⚠️ CUIDADO: apaga dados)
docker-compose exec backend python manage.py migrate [app] zero
docker-compose exec backend python manage.py migrate
```

---

##  Suporte

**Administrador:** [Ian Melo Gonçalves]  
**Email:** [ianmelogg@gmail.com]  

---

**Última atualização:** Novembro 2025  
**Versão:** 1.0.0
