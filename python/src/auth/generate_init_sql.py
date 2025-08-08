# file: python/src/auth/generate_init_sql.py

"""
This script generates a MySQL initialization file (`init-final.sql`) by injecting
environment variables into a template SQL file (`init.sql`).

Why this matters:
- Raw SQL doesn't support environment variables natively.
- Hardcoding credentials in SQL is insecure and not recommended for production.
- This approach keeps sensitive values in `.env`, which is excluded from GitHub.

 Use this for demo setups, local development, or CI/CD bootstrapping.
 Do NOT use this pattern for production secrets—use secret managers instead.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="python/src/auth/env")

# Read the template SQL file
with open("python/src/auth/init.sql", "r") as f:
    sql_template = f.read()

# Replace placeholders with actual env values
for key in ["MYSQL_USER", "MYSQL_HOST", "MYSQL_PASSWORD", "MYSQL_DB"]:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing environment variable: {key}")
    sql_template = sql_template.replace(f"${{{key}}}", value)

# Write the final SQL file
with open("python/src/auth/init-final.sql", "w") as f:
    f.write(sql_template)

print("init-final.sql generated successfully with environment values.")
