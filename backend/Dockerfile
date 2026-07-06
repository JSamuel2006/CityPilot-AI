###############################################################################
# CityPilot AI — Production Dockerfile
# Base: python:3.12-slim  |  Target: Render Web Service
###############################################################################

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies required by psycopg (PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer cache optimisation)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure the start script is executable
RUN chmod +x start.sh

# Expose port (Render injects $PORT automatically)
EXPOSE 8000

# Default entrypoint: run migrations then start the API server
CMD ["./start.sh"]
