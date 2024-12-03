from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64


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
    # Generate public-private key pair
    # private_key, public_key = generate_rsa_keys()

    # # Step 2: Encode the public key as Base64
    # base64_public_key = encode_public_key_to_base64(public_key)
    # print(f"Base64 Encoded Public Key: {base64_public_key}")

    # # Step 3: Decode the public key from Base64
    # decoded_public_key = decode_base64_to_public_key(base64_public_key)

    # # Step 4: Encrypt a message using the decoded public key
    # message = "This is a secret message."
    # encrypted_message = encrypt_message_with_public_key(decoded_public_key, message)
    # print(f"Encrypted Message (Base64): {encrypted_message}")

    # # Step 5: Decode the encrypted message from Base64
    # encrypted_data = decode_base64_to_encrypted_message(encrypted_message)
    # print("encryptedbase64: ",encrypted_data)

    # # Step 6: Decrypt the message using the private key
    # decrypted_message = decrypt_message_with_private_key(private_key, encrypted_data)
    # print(f"Decrypted Message: {decrypted_message}")
    # publickey = decode_base64_to_public_key(base64_public_key="LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF2M0RrY3cyU01OZjQyci9pM2Q1RQpvS0NFUVRMZkZPcGZ1Q3NYMHh0L0xlNnFwdlBodEVCeE5oYUdQWHAyUkFlcGF6YXNyRENyeUxCK0pZR3hBRUIrCmx3ZUloTjErRnJvMEg5dnlnM1VidWVZdkpvOHlTZ0JEUVFkMTU3U2pBRkMxM1BIM0hKQ1hIM3BKeS9leU44dTUKbkE5QTRnU2JVaDc3SDZraUZnSzRWTUkyY2dXK1hJU3pEMXRQRDdiL1Y3K3FzZTlGaGdHSCtqM2xPd2FHQzlVSQpyTGdoVWZYTGZyeDJ3QmNsNXVDdlFRMUlYTTZ5WlNCaC8xWEU1U0ZsbERrMGQzL3BwR29Kd3N6Z0tnS2VvcHAvClFZWk5jWjI5cXM4bzh3WnFQOXZrSTFxcmp6SlNhRXkzS2hNV2p2VENHS0g3UjlPNXFmMDZVaWxySjh2ZGl5TlIKTVFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t")
    # print(encrypt_message_with_public_key(public_key=publickey,message="hello"))
    # a = encrypt_message_with_public_key(public_key=publickey,message="hello")
    # print(decode_base64_to_encrypted_message(base64_encrypted_message=a))

if __name__ == "__main__":
    main()
