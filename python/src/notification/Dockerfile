# Base image: lightweight Python 3.12 on Debian Bullseye
# Ideal for production-grade containers with minimal footprint
FROM python:3.12-slim-bullseye

# Install system-level dependencies required by some Python packages
# - build-essential: compilers and linkers
# - python3-dev: headers for building Python extensions
# - pkg-config: helps locate libraries during builds
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set working directory inside the container
# All subsequent paths are relative to /app
WORKDIR /app

# Copy Python dependency list and install packages
# - Upgrade pip to latest version
# - Install all packages listed in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all application files into the container
# Includes consumer.py and send.py
COPY . .

# Optional: specify path to .env file for dotenv loading
# This allows environment variables to be loaded from /app/env
ENV DOTENV_PATH=/app/env

# Define the default command to run when the container starts
# Launches the RabbitMQ consumer script
CMD ["python3", "consumer.py"]
