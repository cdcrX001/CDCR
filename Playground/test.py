from fastapi import FastAPI

app = FastAPI()

@app.get("/api/test")
async def get_test_data():
    # Flatten the data into a single string format
    return {
        "data": "enclave1:https://example.com:value0:value1:value2:value8"
    }

@app.get("/")
async def root():
    return {"message": "FastAPI server is running"}
