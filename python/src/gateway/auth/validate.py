from dotenv import load_dotenv
import os, requests

# Load environment variables from .env file
load_dotenv()

def token(request):
    # Check if Authorization header is present
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    # Extract token from Authorization header
    token = request.headers["Authorization"]

    # Check if token is empty
    if not token:
        return None, ("missing credentials", 401)

    # Forward token to auth service for validation
    # AUTH_SVC_ADDRESS should point to the auth service (e.g., 'auth:5000')
    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    # If token is valid, return decoded user info (or response body)
    if response.status_code == 200:
        return response.text, None
    else:
        # Otherwise, return error message and status code
        return None, (response.text, response.status_code)
