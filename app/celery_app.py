from celery import Celery
from app.core.config import settings

celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.embeddings']
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)