from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

@app.get("/api/test")
async def get_test_data():
    # Simulating some API response data
    # return {
    #     "data": "Hello from FastAPI!"
    # }
  return {
  "data": {
    "enclaveid": "enclave1",
    "enclave_endpoint": "https://example.com",
    "pcr0": "value0",
    "pcr1": "value1",
    "pcr2": "value2",
    "pcr8": "value8"
  }
}

# Optional: An endpoint for testing locally
@app.get("/")
async def root():
    return {"message": "FastAPI server is running"}
