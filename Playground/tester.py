from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

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
    # Example private key in PEM format (you can use your private key here)
    private_key_pem = """
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCpOCl/aHHtSpk8
ez3K6LT6JiQgqVsJfuzC9AcYIvdyJzA90KQVeQYzlS3wFEPGgP2fj62YfidPx/zz
W+QvUeqtWNZNbCu0SPQ0uvk6PxQgEJelWjRqlYni+xnmEmrMWEOrpzAVWeomIDud
2/Qa429rlFOkXiBsT7/+SLq3+uruogFH2f3PWacU44M2Z8ZGP1xxHMOZ4Vi50Yva
9NGvKooW8pKNlOh1BVz0UNzhFqAcnBGbvpz4muEkOqqle4s/NM2iwnEfpZgfbOGL
eKHC40fX/VM3jYqINiPyaF/SOZ3jpdgvEg09KNJv5jyx0Gfia8HyGwZRBS1kLKGX
Sq0KYIRbAgMBAAECggEAR2DFQFTSGYGp+XUSr5BRJmMIQi6tk+fR/rnodCnrrl8R
XkGvtM8D6qY2Zlpl7ElksfVtCDHOazy0WgKc0cj/8HbUjnveQ4GyYLutfQA2gP/+
t2TBT2QccX3xgraqDd/9S16OTbNLrSFThFbPNLhSu1Ippd9+VbGeDqim+gwBJP7J
YE8a6StE/7GXjkGqPhn3qFV98WkI4aDlAV9VEsHMXLVDqkp03e+XiK/lSn1reVck
3mxWCjGBXKYlW32FcXhY8yCiv0zTiLGOIj6ap35qdt1d7JGojtpaD9Yri4MB5pFt
hE9yBB0ifzfUlntBGWT9HRco0YjMO1KVrfcXlEHeQQKBgQDVHI9tTx7pyhxHzRtM
l2HguKnYApfJdQWuc6z+Q3oWfdrzn9FcoEnM9sbLBCm05kPbKpupT9XO3tnoRM3H
V7c3svB3oWavKCOTFqCyheQswsbglQqy7EeiOei2TzMnyt6RkWhQ/pwGCh7QDO4G
9TqUepZVJbHW4EqEy1IWnJrr+QKBgQDLRkpsa0fCHgHNlP9ZMvTXOx+ztEOTGLMP
IWDhg7QECkddcSIyhKSLp2JOEmO7jNnzo9YfH6SgWH8UE/lvKRz06xnkv//8XLLG
6466/TMYXe2wcM3Xtyr9DTZl5NSgT38K2bMo21I/TMD7FnUueAH2XZYMGhX6uRZL
wuzxJtJ/8wKBgBEcX++44JSI48hoEX8O0I8IhKqRWrqUKMafBw7LQCw6IrBY7qhv
Pj20urVmOisKKfyY6TKo9FPN1NUvYQ5WXqGcPm58iRAbOu/+axyqX22wneM+VEOV
cRL3b1Xj+gmB4mjxsdx+9OwPN/Ygc6QfYHq3dQaVJjhIffM3l/m0zUORAoGAG/PK
gCYwc+0UamS2yFlNedtTfK6pLC0VUltQqzIlKvkO3zaTcUb0KZAW4I1+0WeJAQvi
gd0kEjiZIPWuMy8AIF3D7cTJOra0js4NjoEK6arg6IZah/NUIgATHufcpT7JRYCy
NkgSg0nWr7Bi5MTz4CD2ZSuhIh0Zh8mCM5cXEykCgYBA1WaW+LjX/dmti6gt7X8Y
rRL/r1TpXxtPSE+LXI01LFVlPtcqvD28v39iPA2+yfvCD7OE6wcwpvOY1hd/SOze
kJBIGkRDNBXCYj6KULn4QKQCsby89UKHQNZs32f24IWGg0dTkkQooRMW53yHvrPi
3ACAtKLm4o4NJD9uiv7AWw==
-----END PRIVATE KEY-----
    """

    # Encrypted message (Base64 encoded string from the encryption step)
    encrypted_message = "mfqlqDJpypnpywjNiTMbQfcGH/8xCNkpEWeYn1FSTqUm2Ye5Ckn9rsDFEUggK7UoRw0TDOGmAYOHiwunjx5a1seNJyFyNBdVitZEdOfAmZL8BD/Gi3F9FPiT/oXzYcmYcPDtTNJ9Ki9jLAeiXruFqVlQ99J6DZkVJjnc/juK49yuXCE89Xw++3ucUugsXDqF/6Z5Qs7UfzXiOSQQ6sBJTM3oVg+dNqr2iJbyXyEW0V+lljyMN1gdsZKLlly11i9HxkbFqlHd+XPl9SlOe5WefmgOSbfORwXQWbTgXjDzoOiNjuJhIVxNaxgO9FknRO7aoDjKS3OMBLYumMz6fazBTQ=="  # Replace with actual encrypted data

    # Decrypt the message
    decrypted_message = decrypt_with_private_key(private_key_pem, encrypted_message)

    print("Decrypted message:", decrypted_message)
