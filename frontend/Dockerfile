# Multi-sep build dockerfile
# Phase 1 - Build
FROM node:lts-alpine AS build-stage

WORKDIR /app

RUN apk add --no-cache git

COPY . .
RUN npm install
RUN npm run build

# Phase 2 - Serve
FROM nginx:stable-alpine AS production-stage

LABEL org.opencontainers.image.source=https://github.com/Mosquito-Alert/anomaly_detection/

HEALTHCHECK --interval=30s --retries=3 --timeout=5s CMD curl --fail http://localhost || exit 1
EXPOSE 80

WORKDIR /app
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist/spa /app
# /usr/share/nginx/html
