import requests
import json
from environs import Env

# Load environment variables
env = Env()
env.read_env()

# Constants
LOGIN_URL = env.str("SD_LOGIN_URL")

def auth_sales_doctor():
    """
    Authenticate with the Sales Doctor API and return the token and userId.

    Returns:
        tuple: A tuple containing the token and userId if successful, otherwise (None, None).
    """
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "method": "login",
        "auth": {
            "login": env.str("SD_LOGIN"),
            "password": env.str("SD_PASSWORD")
        }
    }
    
    try:
        response = requests.post(LOGIN_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

        result = response.json().get('result')
        if result:
            return result['token'], result['userId']
        else:
            return None, None
    
    except requests.exceptions.RequestException as e:
        # Log the exception (print statement for simplicity, use logging in real applications)
        print(f"An error occurred: {e}")
        return None, None

