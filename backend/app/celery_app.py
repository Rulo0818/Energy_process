"""Configuración Celery para encolar procesamiento de archivos."""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "energy_process",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Reconexión automática si Redis se cae o cierra la conexión (p. ej. Docker, timeouts)
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=50,
    # Comportamiento al perder conexión: reconectar y no dejar tareas colgadas
    worker_cancel_long_running_tasks_on_connection_loss=True,
    # Redis: comprobar conexión periódicamente para evitar cierres por inactividad
    broker_transport_options={
        "visibility_timeout": 3600,
        "health_check_interval": 30,
        "socket_keepalive": True,
        "socket_connect_timeout": 10,
    },
)
