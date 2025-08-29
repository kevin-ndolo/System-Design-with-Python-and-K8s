import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL



# Initialize Flask app 
server = Flask(__name__)

# configure MySQL connection parameters
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


# Initialize MySQL. this must done after setting the config as it reads from it
mysql = MySQL(server)


@server.route("/login", methods=["POST"])
def login():
    try:
        auth = request.authorization
        if not auth:
            print("Missing credentials in request")
            return "missing credentials", 401

        print(f"Login attempt: {auth.username}")

        # check db for user and password
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT email,password FROM user WHERE email = %s", (auth.username,))
        if res > 0:
            user_row = cur.fetchone()
            email = user_row[0]
            password = user_row[1]

            print(f"User found: {email}")

            if auth.username != email or auth.password != password:
                print("Invalid credentials")
                return "invalid credentials", 401
            else:
                print("Credentials valid, generating JWT")
                return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)

        else:
            print("User not found")
            return "invalid credentials", 401

    except Exception as e:
        print(f"Login route error: {e}")
        return "internal server error", 500



@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])

    except:
        return "not authorized", 403
    
    return decoded, 200




def createJWT(username, secret, authz):
    return jwt.encode(
                {
                    "username":username,
                    "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
                    "iat":datetime.datetime.utcnow(),
                    "admin": authz,

                },
                secret,
                algorithm="HS256",
            )
        



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
