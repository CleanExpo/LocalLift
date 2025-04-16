# Use official Python image as base with optimized slim variant
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV NODE_ENV=production
ENV RAILWAY_DEPLOYMENT=true
ENV PATH="/app/.local/bin:${PATH}"

# Install system dependencies with cleanup in same layer (reduces image size)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r locallift && useradd -r -g locallift locallift

# Copy requirements and package files first (for better layer caching)
COPY requirements.txt ./
COPY package*.json ./

# Install Python dependencies with specific version pins
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Node dependencies if needed
RUN if [ -f package.json ]; then npm ci --production --no-audit; else echo "No package.json"; fi

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/static && \
    chown -R locallift:locallift /app

# Copy application code
COPY --chown=locallift:locallift . .

# Copy Railway environment file to .env for production
COPY --chown=locallift:locallift .env.railway .env

# Create Docker healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose the PORT variable for Railway
EXPOSE ${PORT}

# Switch to non-root user
USER locallift

# Start the application with the Railway-specific entry point and proper logging
CMD ["sh", "-c", "uvicorn railway_entry:app --host 0.0.0.0 --port ${PORT} --log-level info"]
