# file: python/src/auth/Dockerfile

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Optional: set path to .env file
ENV DOTENV_PATH=/app/env

# Entrypoint script handles SQL generation + app startup
ENTRYPOINT ["bash", "entrypoint.sh"]
