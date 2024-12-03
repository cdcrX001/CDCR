import requests

# API endpoint
url = "http://localhost:8000/deploy-enclaves"

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