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


    try:
        # Forward token to auth service for validation
        # AUTH_SVC_ADDRESS should point to the auth service (e.g., 'auth:5000')
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
            headers={"Authorization": token},
        )

    except Exception as e:
        print(f"Gateway token validation error: {e}")
        return None, ("auth service unreachable", 500)


    # If token is valid, return decoded user info (or response body)
    if response.status_code == 200:
        return response.text, None
    else:
        # Otherwise, return error message and status code
        return None, (response.text, response.status_code)
