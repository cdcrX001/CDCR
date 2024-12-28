from celery_app import celery_app
import subprocess
import os
import tempfile
from typing import Dict, Any
import socketio
import json
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# initial export of env variables
print(f"API Key: {os.getenv('EVERVAULT_API_KEY')}")
print(f"App UUID: {os.getenv('EVERVAULT_APP_UUID')}")


# If you need to set environment variables, use os.environ instead:
os.environ["EV_API_KEY"] = os.getenv('EVERVAULT_API_KEY')
os.environ["EV_APP_UUID"] = os.getenv('EVERVAULT_APP_UUID')


# Initialize Socket.IO client
sio = socketio.Client(logger=True, engineio_logger=True)

# Add connection event handlers
@sio.on('connect', namespace='/deployment')
def on_connect():
    logger.info("Connected to Socket.IO server")

@sio.on('connect_error', namespace='/deployment')
def on_connect_error(data):
    logger.error(f"Connection error: {data}")

@sio.on('disconnect', namespace='/deployment')
def on_disconnect():
    logger.info("Disconnected from Socket.IO server")

def get_existing_enclaves(env: Dict[str, str]) -> list:
    """Get list of existing enclaves"""
    try:
        result = subprocess.run(
            ["ev", "enclave", "ls", "--json"],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return json.loads(result.stdout)
    except Exception:
        return []

def generate_unique_enclave_name(base_name: str, existing_enclaves: list) -> str:
    """Generate a unique enclave name"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    existing_names = {enclave.get('name', '') for enclave in existing_enclaves}
    
    counter = 0
    while True:
        name = f"{base_name}-{timestamp}-{counter}"
        if name not in existing_names:
            return name
        counter += 1

def safe_emit(event, data, namespace):
    try:
        if sio.connected:
            logger.info(f"Emitting {event} with data: {data}")
            sio.emit(event, data, namespace=namespace)
            logger.info(f"Emitted {event} successfully")
        else:
            logger.error("Socket not connected when trying to emit")
    except Exception as e:
        logger.error(f"Error emitting {event}: {e}")

@celery_app.task(bind=True)
def deploy_enclaves_task(self, room_id: str, number_of_enclaves: int, api_key: str, app_uuid: str) -> Dict[str, Any]:
    try:
        logger.info(f"Connecting to Socket.IO server for room {room_id}")
        sio.connect('http://localhost:8000', namespaces=['/deployment'], socketio_path='socket.io')
        logger.info("Connected to Socket.IO server")

        deployed_enclaves = []
        env = os.environ.copy()
        env["EV_API_KEY"] = api_key
        env["EV_APP_UUID"] = app_uuid
        # put an update in the log
        print(f"Deploying {number_of_enclaves} enclaves")
        # Send initial status
        safe_emit('deployment_update', {
            'room': room_id,
            'status': 'started',
            'message': f'Starting deployment for room {room_id}'
        }, '/deployment')

        # First, verify ev CLI is installed
        try:
            version_result = subprocess.run(
                ["ev", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Evervault CLI version: {version_result.stdout}")
            safe_emit('deployment_update', {
                'room': room_id,
                'status': 'setup',
                'message': f'Evervault CLI version: {version_result.stdout}'
            }, '/deployment')
        except subprocess.CalledProcessError as e:
            raise Exception("Evervault CLI not found. Please install it using: curl https://cli.evervault.com/v4/install -sL | sh")

        # Get existing enclaves
        existing_enclaves = get_existing_enclaves(env)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone repository
            repo_name = "hello-enclave"
            clone_path = os.path.join(temp_dir, repo_name)
            print(f"Cloning repository to {clone_path}")
            safe_emit('deployment_update', {
                'room': room_id,
                'status': 'cloning',
                'message': 'Cloning hello-enclave repository'
            }, '/deployment')

            clone_result = subprocess.run(
                ["git", "clone", "https://github.com/evervault/hello-enclave", clone_path],
                check=True,
                env=env,
                capture_output=True,
                text=True
            )

            # Verify the Dockerfile exists
            dockerfile_path = os.path.join(clone_path, "Dockerfile")
            if not os.path.exists(dockerfile_path):
                raise Exception(f"Dockerfile not found at {dockerfile_path}")

            # Verify other required files
            required_files = ["index.js", "package.json", "package-lock.json"]
            for file in required_files:
                file_path = os.path.join(clone_path, file)
                if not os.path.exists(file_path):
                    raise Exception(f"Required file {file} not found at {file_path}")

            for i in range(number_of_enclaves):
                enclave_name = generate_unique_enclave_name(f"enclave", existing_enclaves)
                print(f"Initializing enclave {i+1} of {number_of_enclaves}: {enclave_name}")
                safe_emit('deployment_update', {
                    'room': room_id,
                    'status': 'initializing',
                    'message': f'Initializing enclave {i+1} of {number_of_enclaves}: {enclave_name}'
                }, '/deployment')

                # Initialize enclave
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
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Failed to initialize enclave: {e.stdout}\n{e.stderr}")

                print(f"Deploying enclave {i+1} of {number_of_enclaves}: {enclave_name}")
                safe_emit('deployment_update', {
                    'room': room_id,
                    'status': 'deploying',
                    'message': f'Deploying enclave {i+1} of {number_of_enclaves}: {enclave_name}'
                }, '/deployment')

                # Deploy enclave
                try:
                    deploy_result = subprocess.run(
                        ["ev", "enclave", "deploy", "-v"],
                        cwd=clone_path,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Failed to deploy enclave: {e.stdout}\n{e.stderr}")

                # Parse the enclave.toml file to get PCRs and other info
                enclave_toml = os.path.join(clone_path, "enclave.toml")
                if not os.path.exists(enclave_toml):
                    raise Exception(f"enclave.toml not found at {enclave_toml}")

                # Extract UUID and PCRs from enclave.toml
                uuid = None
                pcrs = {}
                with open(enclave_toml, "r") as f:
                    config_content = f.read()
                    for line in config_content.split("\n"):
                        if line.startswith("uuid"):
                            uuid = line.split("=")[1].strip().strip('"')
                        elif line.startswith("PCR"):
                            pcr_num = line[3]
                            pcr_value = line.split("=")[1].strip().strip('"')
                            pcrs[f"pcr{pcr_num}"] = pcr_value

                deployed_enclaves.append({
                    'name': enclave_name,
                    'domain': f"{enclave_name}.{app_uuid}.enclave.evervault.com",
                    'pcrs': pcrs,
                    'uuid': uuid
                })

                # Add the newly created enclave to our list of existing enclaves
                existing_enclaves.append({'name': enclave_name})

                print(f"Successfully deployed enclave {i+1} of {number_of_enclaves}: {enclave_name}")
                safe_emit('deployment_update', {
                    'room': room_id,
                    'status': 'enclave_completed',
                    'message': f'Successfully deployed enclave {i+1} of {number_of_enclaves}',
                    'enclave': deployed_enclaves[-1]
                }, '/deployment')

                # Add a small delay between deployments
                if i < number_of_enclaves - 1:
                    time.sleep(2)

        # Send final success response
        final_response = {
            'status': 'completed',
            'enclaves': deployed_enclaves,
            'message': f"Successfully deployed {number_of_enclaves} enclaves"
        }
        print(f"Final response: {final_response}")
        safe_emit('deployment_complete', {
            'room': room_id,
            'data': final_response
        }, '/deployment')
        
        sio.disconnect()
        return final_response

    except Exception as e:
        error_message = str(e)
        try:
            if sio.connected:
                safe_emit('deployment_error', {
                    'room': room_id,
                    'error': error_message
                }, '/deployment')
        except:
            pass
        finally:
            if sio.connected:
                sio.disconnect()
        raise

@celery_app.task
def test_task():
    return "Hello from Celery!"