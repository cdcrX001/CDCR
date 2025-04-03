from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Step 1: Generate public-private key pair
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


# Step 2: Encode public key as Base64
def encode_public_key_to_base64(public_key):
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(public_key_pem).decode('utf-8')


# Step 3: Decode Base64 encoded public key
def decode_base64_to_public_key(base64_public_key):
    public_key_pem = base64.b64decode(base64_public_key)
    return serialization.load_pem_public_key(public_key_pem)


# Step 4: Encrypt a message using the public key
def encrypt_message_with_public_key(public_key, message):
    encrypted_data = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(encrypted_data)
    return base64.b64encode(encrypted_data).decode('utf-8')


# Step 5: Decode Base64 encrypted message
def decode_base64_to_encrypted_message(base64_encrypted_message):
    return base64.b64decode(base64_encrypted_message)


# Step 6: Decrypt the encrypted message using the private key
def decrypt_message_with_private_key(private_key, encrypted_data):
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode('utf-8')


# Main function to test the whole process
def main():
    # Get public key from environment variable
    base64_public_key = os.getenv('PUBLIC_KEY')
    if not base64_public_key:
        raise ValueError("PUBLIC_KEY environment variable is not set")

    publickey = decode_base64_to_public_key(base64_public_key)
    message = """{
    "job_id": "d4a186fe-4c95-412d-b21e-dd3b9781ba48",
    "socket_room": "d033be16-9c95-4212-baa2-1fe65ca4d48c",
    "socket_url": "https://df54-49-207-244-10.ngrok-free.app/deployment"
    "message": "Enclave deployment started. Connect to WebSocket for real-time updates."
}"""
    a = encrypt_message_with_public_key(public_key=publickey, message=message)
    print(decode_base64_to_encrypted_message(base64_encrypted_message=a))

if __name__ == "__main__":
    main()
