from dotenv import load_dotenv
import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL


# Load environment variables from .env file
load_dotenv()

# Initialize Flask app 
server = Flask(__name__)

# configure MySQL connection parameters
server.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
server.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT"))

# Initialize MySQL. this must done after setting the config
mysql = MySQL(server)


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
