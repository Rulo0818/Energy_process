# Energy Processor System

Sistema de procesamiento de archivos de peajes y gestión de energía.

## Requisitos
- Docker & Docker Compose

## Ejecución

1. Construir y levantar servicios:
   cd energy_processor
   docker-compose up --build
   
2. La API estará disponible en `http://localhost:8000`.
   - Documentación interactiva: `http://localhost:8000/docs`

3. **Probar Login (Prueba de Sistema)**:
   - Endpoint: `POST /api/login`
   - Cuerpo (JSON): `{"username": "admin", "password": "0823"}`
   - Puedes usar la documentación interactiva o `curl`:
     ```powershell
     Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/login" -ContentType "application/json" -Body '{"username":"admin", "password":"0823"}'
     

## Estructura del Proyecto

A continuación, se detalla la organización de carpetas y archivos para facilitar el desarrollo y mantenimiento:

### Backend (API & Lógica)
- **`app/`**: Directorio principal del código fuente de Python.
  - **`main.py`**: Punto de entrada de la aplicación. Configura FastAPI, monta los archivos estáticos y registra los routers.
  - **`db.py`**: Configuración de la conexión a base de datos (PostgreSQL) y sesión.
  - **`api/`**: Contiene los **Endpoints (Vistas)** de la API.
    - `endpoints.py`: Rutas principales (ej. procesamiento de archivos).
    - `auth.py`: Rutas de autenticación (ej. login).
    - *Para agregar una nueva vista:* Crea un archivo aquí y regístralo en `main.py`.
  - **`models/`**: Definiciones de datos (SQLModel/Pydantic).
    - `domain.py`: Tablas de base de datos (`Client`, `EnergyRecord`, etc.).
  - **`services/`**: Lógica de negocio compleja separada de las vistas.
    - `parser.py`: Lógica para procesar y validar el contenido XML.

### Frontend (Panel Administrativo)
- **`static/`**: Archivos del dashboard web (HTML, CSS, JS).
  - `index.html`: Estructura principal del panel.
  - `style.css`: Estilos visuales (Tema oscuro, Glassmorphism).
  - `dashboard.js`: Lógica del frontend (Llamadas a API, gráficos, carga de archivos).

### Configuración y Despliegue
- **`docker-compose.yml`**: Orquestación de contenedores (Web + Base de datos).
- **`Dockerfile`**: Definición de la imagen de Python para el backend.
- **`requirements.txt`**: Lista de dependencias de Python.

## Tests
Para ejecutar los tests unitarios:
```powershell
docker-compose run web pytest
```
