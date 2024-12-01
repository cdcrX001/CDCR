from typing import List
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import subprocess
import os
import json
import tempfile
import shutil

app = FastAPI()

class EnclaveRequest(BaseModel):
    number_of_enclaves: int = Field(..., gt=0, description="Number of enclaves to deploy")
    # Removed dockerfile_url since we'll use a local dockerfile

class EnclaveResponse(BaseModel):
    domain: str
    pcrs: dict
    uuid: str

class EnclaveDeploymentResponse(BaseModel):
    enclaves: List[EnclaveResponse]
    message: str

@app.post("/deploy-enclaves", response_model=EnclaveDeploymentResponse)
async def deploy_enclaves(
    request: EnclaveRequest,
    api_key: str = Header(..., alias="X-Evervault-API-Key"),
    app_uuid: str = Header(..., alias="X-App-UUID")
):
    try:
        # First, verify ev CLI is installed
        try:
            version_result = subprocess.run(
                ["ev", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Evervault CLI version: {version_result.stdout}")
        except subprocess.CalledProcessError:
            raise HTTPException(
                status_code=500,
                detail="Evervault CLI not found. Please install it using: curl https://cli.evervault.com/v4/install -sL | sh"
            )
        
        deployed_enclaves = []
        
        # Set environment variables for the CLI
        env = os.environ.copy()
        env["EV_API_KEY"] = api_key
        env["EV_APP_UUID"] = app_uuid

        # Create a temporary directory for our work
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the hello-enclave repository
            repo_name = "hello-enclave"
            clone_path = os.path.join(temp_dir, repo_name)
            
            print(f"Cloning repository to: {clone_path}")
            clone_result = subprocess.run(
                ["git", "clone", "https://github.com/evervault/hello-enclave", clone_path],
                check=True,
                env=env,
                capture_output=True,
                text=True
            )
            print(f"Cloned repository to: {clone_path}")
            
            # List files in clone_path to verify
            print("Files in cloned repository:")
            for file in os.listdir(clone_path):
                print(f"- {file}")

            # Verify the Dockerfile exists
            dockerfile_path = os.path.join(clone_path, "Dockerfile")
            print(f"Dockerfile path: {dockerfile_path}")
            if not os.path.exists(dockerfile_path):
                raise HTTPException(
                    status_code=500,
                    detail=f"Dockerfile not found at {dockerfile_path}"
                )
            
            print(f"Found Dockerfile at: {dockerfile_path}")
            
            # Verify other required files
            required_files = ["index.js", "package.json", "package-lock.json"]
            for file in required_files:
                file_path = os.path.join(clone_path, file)
                if not os.path.exists(file_path):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Required file {file} not found at {file_path}"
                    )
                print(f"Found required file: {file}")

            for i in range(request.number_of_enclaves):
                enclave_name = f"enclave-{i}"
                
                print(f"Initializing enclave: {enclave_name}")
                try:
                    init_result = subprocess.run(
                        ["ev", "enclave", "init",
                         "-f", dockerfile_path,
                         "--name", enclave_name,
                         "--egress"],
                        cwd=clone_path,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Initialization command output: {init_result.stdout}")
                    if init_result.stderr:
                        print(f"Initialization stderr: {init_result.stderr}")
                except subprocess.CalledProcessError as e:
                    print(f"Initialization failed: {e.stdout}\n{e.stderr}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to initialize enclave: {e.stdout}\n{e.stderr}"
                    )

                print(f"Deploying enclave: {enclave_name}")
                try:
                    deploy_result = subprocess.run(
                        ["ev", "enclave", "deploy", "-v"],
                        cwd=clone_path,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Deployment command output: {deploy_result.stdout}")
                    if deploy_result.stderr:
                        print(f"Deployment stderr: {deploy_result.stderr}")
                except subprocess.CalledProcessError as e:
                    print(f"Deployment failed: {e.stdout}\n{e.stderr}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to deploy enclave: {e.stdout}\n{e.stderr}"
                    )

                # Parse the enclave.toml file to get PCRs and other info
                enclave_toml = os.path.join(clone_path, "enclave.toml")
                if not os.path.exists(enclave_toml):
                    raise HTTPException(
                        status_code=500,
                        detail=f"enclave.toml not found at {enclave_toml}"
                    )

                with open(enclave_toml, "r") as f:
                    config_content = f.read()
                    # Extract UUID and other details from config
                    uuid = None
                    pcrs = {}
                    for line in config_content.split("\n"):
                        if line.startswith("uuid"):
                            uuid = line.split("=")[1].strip().strip('"')
                        elif line.startswith("PCR"):
                            pcr_num = line[3]
                            pcr_value = line.split("=")[1].strip().strip('"')
                            pcrs[f"pcr{pcr_num}"] = pcr_value

                deployed_enclaves.append(EnclaveResponse(
                    domain=f"{enclave_name}.{app_uuid}.enclave.evervault.com",
                    pcrs=pcrs,
                    uuid=uuid
                ))

        return EnclaveDeploymentResponse(
            enclaves=deployed_enclaves,
            message=f"Successfully deployed {request.number_of_enclaves} enclaves"
        )

    except subprocess.CalledProcessError as e:
        print(f"Command failed with output: {e.stdout}\nError: {e.stderr}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy enclave: {e.stdout}\n{e.stderr}"
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deploying enclaves: {str(e)}"
        )


