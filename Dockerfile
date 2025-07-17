# Multi-stage build for webapp
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY webapp/package*.json ./
RUN npm install

# Copy source and build
COPY webapp/ ./
RUN npm run build

# Production stage
FROM node:18-alpine as production

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built app from builder stage
COPY --from=builder /app/dist ./dist

# Expose port (Railway will set PORT env var)
EXPOSE 3000

# Start the application with dynamic port
CMD sh -c "serve -s dist -l ${PORT:-3000}" 