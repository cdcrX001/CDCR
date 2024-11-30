from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

class EnclaveCreationRequest(BaseModel):
    publicKey: str

class EnclaveCreationResponse(BaseModel):
    requestId: str
    encryptedDetails: str

enclave_requests = {}

@app.post("/api/createEnclave")
def create_enclave(request: EnclaveCreationRequest):
 
    if not request.publicKey:
        raise HTTPException(status_code=400, detail="Public key is required")
    
    request_id = str(uuid.uuid4()).replace('-', '')[:32]
    
    encrypted_details = f"ENCRYPTED_DETAILS_FOR_{request.publicKey}"
    
    enclave_requests[request_id] = {
        "publicKey": request.publicKey,
        "encryptedDetails": encrypted_details
    }
    
    return """{
        "requestId": request_id,
        "encryptedDetails": encrypted_details
    }"""

@app.get("/api/enclaveDetails/{request_id}")
def get_enclave_details(request_id: str):
    # Retrieve enclave details
    enclave_data = enclave_requests.get(request_id)
    
    if not enclave_data:
        raise HTTPException(status_code=404, detail="Enclave request not found")
    
    return {
        "encryptedDetails": enclave_data["encryptedDetails"]
    }