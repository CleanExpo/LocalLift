# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed (optional, add if specific libraries require them)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Add a non-root user for security
RUN useradd -m appuser
USER appuser

# Make port $PORT available to the world outside this container (Railway injects the PORT variable)
# EXPOSE $PORT # Note: EXPOSE is documentation; Railway handles port exposure based on Procfile/start command

# Define the command to run the application using the wrapper script
# This ensures consistent startup behavior whether Procfile or CMD is used.
CMD ["python", "run_server.py"]
