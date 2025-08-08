#!/bin/bash

# Enable strict error handling:
# -e: Exit immediately if any command fails
# -u: Treat unset variables as an error and exit
# -o pipefail: If any command in a pipeline fails, the entire pipeline fails
set -euo pipefail

echo "Entrypoint script started..."

# Load environment variables from .env file if it exists
# This allows secrets and config to be injected at runtime
if [ -f "$DOTENV_PATH" ]; then
    echo "Loading environment variables from $DOTENV_PATH"
    
    # Export all key=value pairs from the .env file, ignoring comments
    export $(grep -v '^#' "$DOTENV_PATH" | xargs)
else
    echo "No .env file found at $DOTENV_PATH. Skipping env loading."
fi

# Define the name of the SQL file to be generated
SQL_FILE="init-final.sql"

# Generate the SQL file only if it doesn't already exist
# This avoids regenerating it every time the container starts
if [ ! -f "$SQL_FILE" ]; then
    echo "Generating $SQL_FILE using generate_init_sql.py..."
    python /app/generate_init_sql.py
    echo "$SQL_FILE generated successfully."
else
    echo "$SQL_FILE already exists. Skipping generation."
fi

# Optional: Apply the SQL file to a MySQL database if credentials are available
# This step is skipped if MYSQL_ROOT_PASSWORD or MYSQL_HOST are not set
if [ -n "${MYSQL_ROOT_PASSWORD:-}" ] && [ -n "${MYSQL_HOST:-}" ]; then
    echo "Applying $SQL_FILE to MySQL at $MYSQL_HOST..."
    
    # Run the SQL file against the MySQL server
    mysql -h "$MYSQL_HOST" -u root -p"$MYSQL_ROOT_PASSWORD" < "$SQL_FILE"
else
    echo "Skipping MySQL setup. MYSQL_ROOT_PASSWORD or MYSQL_HOST not set."
fi

# Start the Flask application
# 'exec' replaces the shell with the Python process, allowing proper signal handling
echo "Starting Flask app..."
exec python server.py
