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

# Initialize MySQL. this must done after setting the config as it reads from it
mysql = MySQL(server)


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for user and password
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email,password FROM user WHERE email = %s", (auth.username))
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.getenv("JWT_SECRET"), True )

    else:
        return "invalid credentials", 401
    


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(encoded_jwt, os.getenv("JWT_SECRET"), algorithms=["HS256"])

    except:
        return "not authorized", 403
    
    return decoded, 200




def createJWT(username, secret, authz):
    return jwt.encode(
                {
                    "username":username,
                    "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
                    "iat":datetime.datetime.utcnow(),
                    "admin": authz

                },
                secret,
                algorithm="HS256",
            )
        



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
