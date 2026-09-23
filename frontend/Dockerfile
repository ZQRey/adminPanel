# Stage 1: Build the Vue 3 SPA
FROM node:20-alpine AS build-stage

WORKDIR /app

# Install dependencies first for efficient layer caching
COPY package*.json ./
RUN npm ci || npm install

# Copy source code and build production assets
COPY . .
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine AS production-stage

# Copy compiled static files
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with API & WebSocket reverse proxies
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
