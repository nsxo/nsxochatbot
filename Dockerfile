# Multi-stage build for webapp with API server
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY webapp/package*.json ./
RUN npm install

# Copy source and build
COPY webapp/ ./
RUN npm run build

# Production stage with Python and Node
FROM python:3.11-alpine as production

WORKDIR /app

# Install Node.js in the Python image
RUN apk add --no-cache nodejs npm

# Install Python dependencies
COPY webapp/api/requirements.txt ./
RUN pip install -r requirements.txt

# Copy API server
COPY webapp/api/ ./api/

# Copy scripts
COPY webapp/test_deployment.py ./
COPY webapp/test_db_connection.py ./
COPY webapp/init_database.py ./

# Copy built React app from builder stage
COPY --from=builder /app/dist ./dist

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Initialize database and start Flask API server
CMD ["sh", "-c", "python init_database.py && python api/dashboard.py"] 