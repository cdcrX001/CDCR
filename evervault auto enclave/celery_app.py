from celery import Celery
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'enclave_tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Optional configurations
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Auto-discover tasks in all modules
celery_app.autodiscover_tasks(['tasks'])

# After creating the celery_app, add:
try:
    celery_app.connection().ensure_connection(timeout=3)
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Error connecting to Redis: {e}") 