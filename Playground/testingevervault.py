import requests

# API endpoint
url = "https://14df-103-214-61-70.ngrok-free.app/deploy-enclaves"

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