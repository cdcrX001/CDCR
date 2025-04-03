from fastapi import FastAPI, Query, HTTPException
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import base64
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

def encrypt_with_public_key(base64_public_key: str, message: str) -> str:
    """
    Encrypt the message using the provided RSA public key in PEM format.
    """
    try:
        # First decode the double-encoded public key
        pem_data = base64.b64decode(base64_public_key).decode('utf-8')
        
        # Now load the PEM formatted key
        public_key_obj = serialization.load_pem_public_key(
            pem_data.encode('utf-8')
        )

        # Verify that we have an RSA public key
        if not isinstance(public_key_obj, RSAPublicKey):
            raise ValueError("The provided key is not an RSA public key")

        # Convert message to string if it's not already
        if isinstance(message, (dict, list)):
            message = json.dumps(message)

        # Encrypt the message using RSA-OAEP padding
        encrypted_data = public_key_obj.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Return base64 encoded encrypted data
        return base64.b64encode(encrypted_data).decode('utf-8')

    except Exception as e:
        print(f"Encryption error: {str(e)}")
        raise Exception(f"Encryption failed: {str(e)}")

@app.get("/api/test")
async def get_test_data(publicKey: str = Query(...)):
    print("Received public key:", publicKey)
    
    try:
        # Make request to enclave deployment endpoint
        url = os.getenv("ENCLAVE_DEPLOYMENT_URL")
        if not url:
            raise HTTPException(status_code=500, detail="ENCLAVE_DEPLOYMENT_URL environment variable is not set")
            
        payload = {"number_of_enclaves": 1}
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data_to_encrypt = response.json()
        encrypted_response = encrypt_with_public_key(publicKey, data_to_encrypt)
        
        return {"data": encrypted_response}
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy enclaves: {str(e)}")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "FastAPI server is running"} 