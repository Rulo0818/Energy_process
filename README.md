# Energy Process - Sistema de Procesamiento de Energía

### Configuración inicial

1. **Clonar el repositorio** (una vez subido a GitHub):
```bash
git clone <URL_DEL_REPOSITORIO>
cd Energy_Process
```

2. **Configurar variables de entorno**:


3. **Levantar los servicios con Docker**:



### Acceso a los servicios

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Desarrollo local

#### Backend
```bash
cd backend
python -m virtualenv venv  # or: python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 1: Use the startup script (recommended)
./start_dev.sh

# Option 2: Run directly with python -m
python -m uvicorn app.main:app --reload

# Option 3: Clear shell cache first
hash -r && uvicorn app.main:app --reload
```

**Important**: If you get `ModuleNotFoundError: No module named 'fastapi'`, see [`backend/README_VENV.md`](backend/README_VENV.md) for troubleshooting.

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Ejecutar tests

```bash
docker-compose exec backend pytest
```

---

## Arquitectura del Proyecto

```
Energy_Process/
├── backend/          # API FastAPI + Celery worker
│   ├── app/
│   │   ├── api/      # Rutas y endpoints
│   │   ├── models/   # Modelos de base de datos
│   │   ├── schemas/  # Esquemas Pydantic
│   │   ├── services/ # Lógica de negocio


