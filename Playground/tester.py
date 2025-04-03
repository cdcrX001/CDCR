from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def decrypt_with_private_key(private_key_pem: str, encrypted_message: str) -> str:
    """
    Decrypt the message using the provided private key in PEM format.
    """
    try:
        encrypted_data = base64.b64decode(encrypted_message)
        print("encryptdmsg: ",encrypted_data)
        # Load the private key
        private_key_obj = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=None
        )

        # Decode the encrypted message from base64
        encrypted_data = base64.b64decode(encrypted_message)
        print("encryptdmsg: ",encrypted_data)

        # Decrypt the data using the private key
        decrypted_data = private_key_obj.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
        return decrypted_data.decode('utf-8')
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Get private key from environment variable
    private_key_pem = os.getenv('PRIVATE_KEY')
    if not private_key_pem:
        raise ValueError("PRIVATE_KEY environment variable is not set")

    # Encrypted message (Base64 encoded string from the encryption step)
    encrypted_message = "mfqlqDJpypnpywjNiTMbQfcGH/8xCNkpEWeYn1FSTqUm2Ye5Ckn9rsDFEUggK7UoRw0TDOGmAYOHiwunjx5a1seNJyFyNBdVitZEdOfAmZL8BD/Gi3F9FPiT/oXzYcmYcPDtTNJ9Ki9jLAeiXruFqVlQ99J6DZkVJjnc/juK49yuXCE89Xw++3ucUugsXDqF/6Z5Qs7UfzXiOSQQ6sBJTM3oVg+dNqr2iJbyXyEW0V+lljyMN1gdsZKLlly11i9HxkbFqlHd+XPl9SlOe5WefmgOSbfORwXQWbTgXjDzoOiNjuJhIVxNaxgO9FknRO7aoDjKS3OMBLYumMz6fazBTQ=="  # Replace with actual encrypted data

    # Decrypt the message
    decrypted_message = decrypt_with_private_key(private_key_pem, encrypted_message)

    print("Decrypted message:", decrypted_message)
