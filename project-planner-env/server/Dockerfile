FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV WORKERS=4
ENV MAX_CONCURRENT_ENVS=100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]