# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV NODE_ENV=production

# Install Node.js for potential frontend dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and package files first (for better layer caching)
COPY requirements.txt ./
COPY package*.json ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node dependencies if needed (with specific flags to avoid cache issues)
RUN if [ -f package.json ]; then npm install --production --no-cache; else echo "No package.json"; fi

# Copy application code
COPY . .

# Copy Railway environment file to .env for production
COPY .env.railway .env

# Export the PORT variable for Railway
EXPOSE ${PORT}

# Start the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
