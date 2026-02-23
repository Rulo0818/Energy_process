from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

# Raíz del proyecto (Energy_process), para cargar .env aunque uvicorn se ejecute desde backend/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""

    # Environment
    ENVIRONMENT: str = "development"

    # Database: usa las MISMAS credenciales que en pgAdmin
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "energy_process"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    # Si defines DATABASE_URL en el .env, se usa; si no, se construye con las variables de arriba
    DATABASE_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Upload
    UPLOAD_DIR: str = "./uploads"

    model_config = {
        "env_file": _PROJECT_ROOT / ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()
