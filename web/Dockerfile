# ---- build stage ----
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- runtime stage ----
FROM nginx:1.27-alpine

# Nginx SPA config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Built web assets
COPY --from=build /app/dist /usr/share/nginx/html

COPY docker-entrypoint.d/99-env.sh /docker-entrypoint.d/99-env.sh
RUN chmod +x /docker-entrypoint.d/99-env.sh

EXPOSE 80
