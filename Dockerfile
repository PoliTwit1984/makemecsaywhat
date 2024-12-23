FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn watchdog[watchmedo]

# Copy application files
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs static/audio static/generated_videos instance && \
    chown -R appuser:appuser /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore"

# Expose port
EXPOSE 8000

# Make startup script executable
COPY start.sh .
RUN chmod +x start.sh && \
    chown appuser:appuser start.sh

# Switch to non-root user
USER appuser

# Run all services
CMD ["./start.sh"]
