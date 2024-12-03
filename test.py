from fastapi import FastAPI, Query, HTTPException
import requests

# Initialize FastAPI app
app = FastAPI()

@app.get("/api/test")
async def get_test_data(publicKey: str = Query(...)):
    """
    Handles the GET request to deploy enclaves.
    
    Args:
        publicKey (str): Public key for authentication
    
    Returns:
        dict: Response from the enclave deployment
    """
    print("received public key: ", publicKey)
    
    url = "https://df54-49-207-244-10.ngrok-free.ap/deploy-enclaves"
    payload = {"number_of_enclaves": 1}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with enclave service: {str(e)}"
        )

# Add a health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
