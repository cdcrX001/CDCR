from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uuid
from tasks import deploy_enclaves_task
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
fastapi_app = FastAPI()


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnclaveRequest(BaseModel):
    number_of_enclaves: int = Field(..., gt=0, description="Number of enclaves to deploy")

class JobResponse(BaseModel):
    job_id: str
    socket_room: str
    socket_server_url: str


@fastapi_app.get("/")
async def root():
    return {"message": "Hello World"}


@fastapi_app.post("/deploy-enclaves", response_model=JobResponse)
async def deploy_enclaves(request: EnclaveRequest):
    try:
        # Get credentials from environment variables
        api_key = os.getenv("EVERVAULT_API_KEY")
        app_uuid = os.getenv("EVERVAULT_APP_UUID")

        if not api_key or not app_uuid:
            raise HTTPException(
                status_code=500,
                detail="Missing required environment variables"
            )

        # Generate unique room ID for this deployment
        room_id = str(uuid.uuid4())

        # Start Celery task
        task = deploy_enclaves_task.delay(
            room_id,
            request.number_of_enclaves,
            api_key,
            app_uuid
        )

        return JobResponse(
            job_id=task.id,
            socket_room=room_id,
            socket_server_url="http://localhost:8000/deployment"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting deployment: {str(e)}"
        )

@sio.on('connect', namespace='/deployment')
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.on('join', namespace='/deployment')
async def join(sid, room):
    logger.info(f"Client {sid} joining room: {room}")
    await sio.enter_room(sid, room, namespace='/deployment')
    # Get all rooms for this sid to verify
    rooms = await sio.rooms(sid, namespace='/deployment')
    logger.info(f"Client {sid} is now in rooms: {rooms}")
    await sio.emit('joined', {'room': room, 'sid': sid}, room=sid, namespace='/deployment')
    logger.info(f"Client {sid} joined room {room}")


@sio.on('deployment_update', namespace='/deployment')
async def deployment_update(sid, data):
    logger.info(f"Deployment update received: {data}")
    room = data.get('room')
    if room:
        logger.info(f"Broadcasting update to room {room}")
        # print all the connected clients to this room 
        logger.info(f"Connected clients to room {room}: {sio.rooms(room, namespace='/deployment')}")
        await sio.emit('deployment_update_client', data, room=room, namespace='/deployment')
    else:
        logger.error("No room specified in deployment update")

@sio.on('deployment_complete', namespace='/deployment')
async def deployment_complete(sid, data):
    logger.info(f"Deployment complete received: {data}")
    room = data.get('room')
    if room:
        logger.info(f"Broadcasting completion to room {room}")
        await sio.emit('deployment_complete_client', data, room=room, namespace='/deployment')
    else:
        logger.error("No room specified in deployment complete")

@sio.on('deployment_error', namespace='/deployment')
async def deployment_error(sid, data):
    logger.info(f"Deployment error received: {data}")
    room = data.get('room')
    if room:
        logger.info(f"Broadcasting error to room {room}")
        await sio.emit('deployment_error_client', data, room=room, namespace='/deployment')
    else:
        logger.error("No room specified in deployment error")

@sio.on('disconnect', namespace='/deployment')
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.on('*', namespace='/deployment')
async def catch_all(event, sid, data):
    logger.info(f"Caught event: {event} from {sid} with data: {data}")

# Create the ASGI app by mounting both Socket.IO and FastAPI
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=fastapi_app,
    socketio_path='socket.io'
)


