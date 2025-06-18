# Use Python 3.10 slim image (matches your requirements.txt)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for psycopg2 and curl for health checks)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY fao/ ./fao/
COPY static/ ./static/

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Health check for App Runner
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the FastAPI application
# App Runner sets PORT environment variable, but FastAPI defaults to 8000
CMD uvicorn fao.src.api.__main__:app --host 0.0.0.0 --port ${PORT:-8000}

