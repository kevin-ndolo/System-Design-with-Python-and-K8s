from dotenv import load_dotenv
import os, requests

# Load environment variables from .env file
load_dotenv()

def login(request):
    # Extract Basic Auth credentials from incoming request
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    # Format credentials for HTTP Basic Auth
    basicAuth = (auth.username, auth.password)

    # Forward login request to the auth service
    # AUTH_SVC_ADDRESS is expected to be set in .env (e.g., 'auth:5000')
    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
    )

    # If login is successful, return token (or response body)
    if response.status_code == 200:
        return response.text, None
    else:
        # Otherwise, return error message and status code
        return None, (response.text, response.status_code)
