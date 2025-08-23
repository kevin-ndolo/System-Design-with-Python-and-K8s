# file: python/src/auth/Dockerfile

FROM python:3.12-slim-bullseye

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    build-essential ffmpeg \
    python3-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
 
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Optional: set path to .env file
ENV DOTENV_PATH=/app/env

# Command to run the application
CMD ["python3", "consumer.py"]

# Note: Ensure that the consumer.py file is present in the copied files