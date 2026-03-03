# Stage 1: build the CSS
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: serve static files with nginx on Alpine
FROM nginx:alpine

COPY --from=builder /app/public /usr/share/nginx/html

EXPOSE 80
