# Energy Process - Sistema de Procesamiento de Energía

### Configuración inicial

1. **Clonar el repositorio** 
```bash
git clone 
cd Energy_Process
```

2. **Configurar variables de entorno**:


3. **Levantar todo con Docker (RECOMENDADO)**  
   Con un solo comando se inician **Backend (Uvicorn)**, **Worker (Celery)** y **Frontend**, además de PostgreSQL y Redis. El backend espera a la base de datos, la inicializa con datos de prueba y arranca la API; el worker procesa los archivos en segundo plano.

```bash
docker-compose up -d --build
```

   **Servicios que se inician:**
   | Servicio   | Contenedor       | Qué hace                          |
   |-----------|------------------|-----------------------------------|
   | Backend   | peajes_backend   | Uvicorn (API FastAPI en :8000)   |
   | Worker    | peajes_worker    | Celery (procesamiento de archivos)|
   | Frontend  | peajes_frontend  | React (app en :3000)             |
   | PostgreSQL| peajes_postgres  | Base de datos (:5432)             |
   | Redis     | peajes_redis     | Cola para Celery (:6379)         |

   Para que la subida y el procesamiento de archivos funcionen, deben estar en marcha tanto el **backend** (Uvicorn) como el **worker** (Celery); con `docker-compose up -d --build` ambos se levantan automáticamente.

### Ejecución Local (Front, Backend, Celery por separado)

Si quieres levantar **frontend**, **backend (Uvicorn)** y **Celery** cada uno en su propia terminal (sin meterlos en Docker), haz lo siguiente.

**Paso 0 — Obligatorio:** Base de datos y Redis tienen que estar corriendo. Si hiciste `docker-compose down`, Redis y Postgres se apagaron; sin Redis, Celery dará *"Error 10061"* o *"connection refused"*. Levanta solo estos dos servicios:

```powershell
# Desde la raíz del proyecto (Energy_process)
docker-compose up -d postgres redis
```

**Importante:** En `.env` debe estar `REDIS_URL=redis://localhost:6379/0` (no `redis://redis:6379/0`). El host `redis` solo existe dentro de Docker.

Luego abre **3 terminales** y ejecuta:

| Terminal | Ubicación   | Comando |
|----------|-------------|--------|
| **1. Backend (Uvicorn)** | `./backend` | `.\venv\Scripts\Activate.ps1` luego `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| **2. Celery**            | `./backend` | `.\venv\Scripts\Activate.ps1` luego `celery -A app.celery_app worker --loglevel=info -P solo` |
| **3. Frontend**          | `./frontend`| `npm run dev` |

**Ejemplo en PowerShell (orden recomendado):**

```powershell
# Terminal 1 — Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Celery (nueva ventana, misma carpeta backend)
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info -P solo

# Terminal 3 — Frontend
cd frontend
npm run dev
```

Si Celery no conecta a Redis, comprueba que Postgres y Redis estén en marcha: `docker ps` y que aparezcan `peajes_postgres` y `peajes_redis`.

#### Solución de problemas: "Error 10061" o "Timeout connecting to Redis"

- **Causa habitual:** Docker Desktop no está iniciado o no has levantado Redis.
- **Pasos:**
  1. Abre **Docker Desktop** y espera a que esté listo (icono en bandeja del sistema).
  2. En la raíz del proyecto: `docker-compose up -d postgres redis`.
  3. Comprueba con `docker ps` que existan los contenedores `peajes_redis` y `peajes_postgres` en estado "Up".
  4. Desde `backend`: `python check_redis.py`. Si responde "OK", inicia Celery.
- **Si no quieres usar Docker:** necesitas Redis instalado en Windows (por ejemplo [Memurai](https://www.memurai.com/), compatible con Redis). Instálalo, inicia el servicio y deja `REDIS_URL=redis://localhost:6379/0` en `.env`.

#### Detalle por servicio

**Backend (Python)** — desde `./backend`:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Worker Celery** — desde `./backend` en otra terminal:
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info -P solo
```

**Frontend (React)** — desde `./frontend`:
```powershell
npm install
npm run dev
```

### Inicialización de la Base de Datos
Para crear las tablas y datos de prueba:
```powershell
# Vía Docker
docker-compose exec backend python init_db.py

# Vía Local
python init_db.py
```

### Acceso a los servicios

- **Frontend** (con Docker en puerto 3000, local en 5173): http://localhost:3000 o http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379



PS C:\Users\Raul\Music\X\Energy_process> cd .\frontend\
PS C:\Users\Raul\Music\X\Energy_process\frontend> npm run dev

(venv) PS C:\Users\Raul\Music\X\Energy_process\backend> .\venv\Scripts\Activate.ps1   
(venv) PS C:\Users\Raul\Music\X\Energy_process\backend> uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 


(venv) PS C:\Users\Raul\Music\X\Energy_process\backend> .\venv\Scripts\Activate.ps1   
(venv) PS C:\Users\Raul\Music\X\Energy_pr   celery -A app.celery_app worker --loglevel=info -P solo