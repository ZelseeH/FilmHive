# Stage 1: Build
FROM node:18-alpine AS build

WORKDIR /app

# Kopiowanie package.json i instalacja zależności
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Kopiowanie źródeł i budowanie
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Kopiowanie build z poprzedniego stage
COPY --from=build /app/build /usr/share/nginx/html

# Kopiowanie konfiguracji Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]