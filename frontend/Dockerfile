# Build stage
FROM node:22 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Accept VITE variables as build-time arguments (essential for Docker builds)
ARG VITE_API_BASE_URL
ARG VITE_USE_MOCK_API

# Set them as environment variables inside the build environment
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_USE_MOCK_API=$VITE_USE_MOCK_API

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]