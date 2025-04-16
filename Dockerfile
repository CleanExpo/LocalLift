FROM python:3.11-bullseye

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set up a healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Use Uvicorn directly instead of Gunicorn
CMD exec uvicorn railway_entry:app --host 0.0.0.0 --port ${PORT} --workers 2
