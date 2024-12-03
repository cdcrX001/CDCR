import socketio
import eventlet
import logging
from aiohttp import web

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.Server(
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create WSGI app
app = web.Application()
socket_app = socketio.WSGIApp(sio)

# Socket.IO event handlers
@sio.on('connect')
def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.on('join')
def join(sid, room):
    logger.info(f"Client {sid} joining room: {room}")
    sio.enter_room(sid, room)
    sio.emit('joined', {'room': room}, room=sid)

@sio.on('disconnect')
def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

# Function to broadcast updates (called by Celery tasks)
def broadcast_to_room(room, event, data):
    logger.info(f"Broadcasting to room {room}: {event} - {data}")
    sio.emit(event, data, room=room)

if __name__ == '__main__':
    # Start Socket.IO server
    port = 8001  # Different port from FastAPI
    logger.info(f"Starting Socket.IO server on port {port}")
    eventlet.wsgi.server(eventlet.listen(('', port)), socket_app) 