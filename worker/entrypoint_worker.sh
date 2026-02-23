#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
python << 'END'
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:0823@postgres:5432/energy_process")
url = urlparse(db_url)
host = url.hostname
port = url.port or 5432

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            print("Base de datos conectada!")
            break
    except (socket.timeout, ConnectionRefusedError):
        print("Esperando a la base de datos...")
        time.sleep(1)
END

echo "Esperando a Redis..."
python << 'END'
import socket
import time
import os
from urllib.parse import urlparse

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
url = urlparse(redis_url)
host = url.hostname
port = url.port or 6379

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            print("Redis conectado!")
            break
    except (socket.timeout, ConnectionRefusedError):
        print("Esperando a Redis...")
        time.sleep(1)
END

echo "Iniciando worker (Celery)..."
exec celery -A app.celery_app worker -l info
