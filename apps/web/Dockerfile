# Imagem do frontend: o Vue é compilado e servido pelo Nginx, que também repassa /api para a API.
#   docker build -t talentix-web apps/web
FROM node:24-alpine AS build

WORKDIR /app
# Usa a versão do pnpm definida em package.json (packageManager).
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Nginx sem privilégios de root, escutando na porta 8080.
FROM nginxinc/nginx-unprivileged:1.30-alpine

# O Nginx substitui ${API_URL} no template ao iniciar o contêiner (endereço interno da API na Azure).
ENV API_URL=http://localhost:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
