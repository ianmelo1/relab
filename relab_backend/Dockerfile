# Imagem base Python
FROM python:3.11-slim

# Evita arquivos .pyc e buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (PostgreSQL client)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . /app/

# Cria diretórios para static e media
RUN mkdir -p /app/staticfiles /app/media

# Expõe a porta 8000
EXPOSE 8000

# Comando padrão (será sobrescrito pelo docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]