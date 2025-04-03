# Playground Project

This project contains various utilities for encryption, decryption, and API testing.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following variables:
```
# RSA Keys
PRIVATE_KEY=your_private_key_here
PUBLIC_KEY=your_public_key_here

# API Endpoints
API_ENDPOINT=your_api_endpoint_here
```

## Files Description

- `tester.py`: Handles RSA decryption using private key from environment
- `allin.py`: Complete RSA encryption/decryption utilities using keys from environment
- `testingevervault.py`: API testing utility using endpoint from environment
- `test.py`: Simple FastAPI test server
- `beta.py`: FastAPI server with enclave creation endpoints
- `keycreation.py`: Utility for generating RSA key pairs

## Security Notes

- Never commit the `.env` file to version control
- Keep your private keys secure and never share them
- Use environment variables for all sensitive information 