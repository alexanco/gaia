# syntax=docker/dockerfile:1
FROM node:23-alpine AS base

# Instalar dependências apenas quando necessário
FROM base AS deps
WORKDIR /app

# Copiar arquivos de dependências
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Build da aplicação
FROM base AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Imagem de produção com nginx
FROM nginx:1.27-alpine AS runner

# Criar usuário não-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 reactuser

# Copiar arquivos buildados
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração nginx customizada (opcional)
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]