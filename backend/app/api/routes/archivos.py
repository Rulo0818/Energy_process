import hashlib
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.models import ArchivoProcesado
from app.schemas.archivo import ArchivoUploadResponse, ArchivoStatus
from app.services.archivo_service import obtener_archivo_por_hash

router = APIRouter(prefix="/api/v1/archivos", tags=["archivos"])


@router.get("", response_model=list[ArchivoStatus])
def list_archivos(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista archivos procesados (más recientes primero)."""
    archivos = (
        db.query(ArchivoProcesado)
        .order_by(ArchivoProcesado.fecha_carga.desc())
        .limit(limit)
        .all()
    )
    return archivos


def _encolar_o_procesar_sync(archivo_id: int, ruta_archivo: str) -> None:
    """Encola tarea Celery o procesa en sincróno si no hay Redis."""
    try:
        from app.tasks import procesar_archivo_task
        procesar_archivo_task.delay(archivo_id, ruta_archivo)
    except Exception:
        from app.database import SessionLocal
        from app.services.procesador_service import procesar_archivo
        db = SessionLocal()
        try:
            procesar_archivo(db, archivo_id, ruta_archivo)
        finally:
            db.close()


@router.post(
    "/upload",
    response_model=ArchivoUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_archivo(
    file: UploadFile = File(...),
    usuario_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Sube un archivo de peajes para procesamiento.
    Detecta duplicados por hash SHA256.
    """
    from app.models.usuario import Usuario
    # Verificar que el usuario existe, si no, usar el primero disponible
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        usuario = db.query(Usuario).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe el usuario especificado y no hay usuarios en la base de datos. Ejecute init_db.py",
            )
        usuario_id = usuario.id

    contenido = await file.read()
    hash_archivo = hashlib.sha256(contenido).hexdigest()

    archivo_existente = obtener_archivo_por_hash(db, hash_archivo)
    if archivo_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo duplicado. Ya procesado con ID {archivo_existente.id}",
        )

    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        ruta_guardado = upload_dir / (file.filename or "sin_nombre.xml")
        ruta_guardado.write_bytes(contenido)
        ruta_str = str(ruta_guardado)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo en el servidor: {e}",
        )

    nuevo_archivo = ArchivoProcesado(
        usuario_id=usuario_id,
        nombre_archivo=file.filename or "sin_nombre.xml",
        hash_archivo=hash_archivo,
        estado="pendiente",
        ruta_archivo=ruta_str,
    )
    db.add(nuevo_archivo)
    db.commit()
    db.refresh(nuevo_archivo)

    _encolar_o_procesar_sync(nuevo_archivo.id, ruta_str)

    return ArchivoUploadResponse(
        archivo_id=nuevo_archivo.id,
        nombre_archivo=nuevo_archivo.nombre_archivo,
        estado="pendiente",
        mensaje="Archivo en cola de procesamiento",
    )


@router.get("/{archivo_id}", response_model=ArchivoStatus)
def get_archivo_status(archivo_id: int, db: Session = Depends(get_db)):
    """Consulta estado de procesamiento de un archivo."""
    archivo = db.query(ArchivoProcesado).filter(ArchivoProcesado.id == archivo_id).first()
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return archivo
