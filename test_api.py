import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
api_key = os.getenv("EVERVAULT_API_KEY")
app_uuid = os.getenv("EVERVAULT_APP_UUID")
url = os.getenv("ENCLAVE_DEPLOYMENT_URL")

# Request headers
headers = {
    "Content-Type": "application/json",
    "X-Evervault-API-Key": api_key,
    "X-App-UUID": app_uuid
}

# Request body
payload = {
    "number_of_enclaves": 1
}

# Send POST request
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())
except Exception as e:
    print(f"Error: {e}") 