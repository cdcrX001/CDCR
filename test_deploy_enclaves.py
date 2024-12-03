import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_deploy_enclaves():
    # Get API credentials from environment variables
    api_key = os.getenv("EVERVAULT_API_KEY")
    app_uuid = os.getenv("EVERVAULT_APP_UUID")
    
    # API endpoint URL (adjust if running on different port)
    url = "http://localhost:8000/deploy-enclaves"
    
    # Request headers
    headers = {
        "Content-Type": "application/json",
        "X-Evervault-API-Key": api_key,
        "X-App-UUID": app_uuid
    }
    
    # Request body
    payload = {
        "number_of_enclaves": 1  # Start with 1 for testing
    }
    
    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response status and content
        print(f"Status Code: {response.status_code}")
        print("\nResponse Headers:")
        print(response.headers)
        print("\nResponse Body:")
        print(response.json())
        
        # Check if request was successful
        if response.status_code == 200:
            print("\nSuccessfully deployed enclaves!")
            enclaves = response.json().get("enclaves", [])
            for i, enclave in enumerate(enclaves, 1):
                print(f"\nEnclave {i}:")
                print(f"Domain: {enclave.get('domain')}")
                print(f"UUID: {enclave.get('uuid')}")
                print("PCRs:", enclave.get('pcrs'))
        else:
            print(f"\nError: {response.json().get('detail', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_deploy_enclaves() 