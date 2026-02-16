# Energy Process - Sistema de Procesamiento de Energía

### Configuración inicial

1. **Clonar el repositorio** 
```bash
git clone 
cd Energy_Process
```

2. **Configurar variables de entorno**:


3. **Levantar los servicios con Docker**:



### Ejecución Local (Sin Docker completo)

Si deseas ejecutar los servicios de manera individual en Windows o Linux, sigue estos pasos. Recuerda que siempre necesitarás la base de datos y Redis activos:

```powershell
# Solo levantar bases de datos
docker-compose up -d postgres redis
```

#### 1. Backend (Python)
Desde la carpeta `./backend`:
```powershell
# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Arch

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Worker Celery (Procesamiento)
Desde la carpeta `./backend` en una nueva terminal:
```powershell
# Iniciar worker (Windows requiere -P solo)
celery -A app.celery_app worker --loglevel=info -P solo
```

#### 3. Frontend (React)
Desde la carpeta `./frontend` en una nueva terminal:
```powershell
# Instalar dependencias
npm install

# Iniciar desarrollo
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

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379


