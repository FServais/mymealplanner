# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Accept build arguments
ARG VITE_API_URL
ARG BUILD_VERSION

# Set them as environment variables for the build
ENV VITE_API_URL=$VITE_API_URL
ENV BUILD_VERSION=$BUILD_VERSION

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Add nginx config to handle client-side routing
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
