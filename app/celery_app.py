# In app/core/celery_app.py
from celery import Celery
from app.core.config import settings

# 1. Define the Celery application instance.
#    We point the broker and backend to the same REDIS_URL from our settings.
celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    # This is a good production setting for reliability.
    broker_connection_retry_on_startup=True
)

# 2. Optional: Add some robust, professional configurations.
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# 3. Auto-discover tasks.
#    This line tells Celery to look for task definitions in a file
#    named `celery_tasks.py` inside our `app` directory.
celery_app.autodiscover_tasks(["app"])
