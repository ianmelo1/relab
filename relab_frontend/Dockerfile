# Imagem base Node
FROM node:20-alpine

# Diretório de trabalho
WORKDIR /app

# Copia package.json e package-lock.json
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia todo o código
COPY . .

# Expõe a porta 3000
EXPOSE 3000

# Inicia o app em modo desenvolvimento
CMD ["npm", "run", "dev"]