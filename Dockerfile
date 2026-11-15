FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY . .

# Expose Web Dashboard port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run web dashboard and service
CMD ["python", "app.py"]
