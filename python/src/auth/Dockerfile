# file: python/src/auth/Dockerfile

FROM python:3.12-slim-bullseye

# Install system dependencies required by flask_mysqldb
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev \
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

EXPOSE 5000

CMD ["python3", "server.py"]

# Entrypoint script handles SQL generation
ENTRYPOINT ["bash", "entrypoint.sh"]
