# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for Railway
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create a non-root user (Railway prefers this)
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Expose port for health checks and webhooks
EXPOSE 8000

# Health check - Railway handles this externally, but keeping for local testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the enhanced Railway bot (matches railway.json)
CMD ["python", "deployment/simple_railway_bot.py"] 