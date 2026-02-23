"""
Comprueba que Redis esté accesible antes de arrancar Celery.
Uso: python check_redis.py
"""
import sys
import os

# Cargar .env desde la raíz del proyecto
from pathlib import Path
root = Path(__file__).resolve().parent.parent
env_file = root / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

try:
    import redis
except ImportError:
    print("Instala redis: pip install redis")
    sys.exit(1)

url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
print(f"Comprobando Redis en {url} ...")

try:
    r = redis.from_url(url, socket_connect_timeout=2)
    r.ping()
    print("OK: Redis está corriendo. Puedes iniciar Celery.")
    sys.exit(0)
except Exception as e:
    print("ERROR: No se pudo conectar a Redis.")
    print(f"  Detalle: {e}")
    print()
    print("Para ejecución local, levanta Redis (y Postgres) con Docker:")
    print("  docker-compose up -d postgres redis")
    print()
    print("Asegúrate de que en .env tengas: REDIS_URL=redis://localhost:6379/0")
    sys.exit(1)
