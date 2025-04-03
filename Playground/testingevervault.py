import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API endpoint from environment variable
url = os.getenv('API_ENDPOINT')
if not url:
    raise ValueError("API_ENDPOINT environment variable is not set")

# Request body
payload = {
    "number_of_enclaves": 1
}

# Send POST request
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())
except Exception as e:
    print(f"Error: {e}")