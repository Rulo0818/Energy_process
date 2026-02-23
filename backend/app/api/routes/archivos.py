import asyncio
import hashlib
import threading
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


def _procesar_en_background(archivo_id: int, ruta_archivo: str) -> None:
    """Ejecuta el procesamiento en un hilo para no bloquear la respuesta del upload."""
    from app.database import SessionLocal
    from app.services.procesador_service import procesar_archivo
    db = SessionLocal()
    try:
        procesar_archivo(db, archivo_id, ruta_archivo)
    finally:
        db.close()


def _encolar_o_procesar_sync(archivo_id: int, ruta_archivo: str) -> None:
    """Encola tarea Celery o procesa en un hilo en segundo plano si no hay Redis."""
    try:
        from app.tasks import procesar_archivo_task
        procesar_archivo_task.delay(archivo_id, ruta_archivo)
    except Exception:
        thread = threading.Thread(target=_procesar_en_background, args=(archivo_id, ruta_archivo))
        thread.daemon = True
        thread.start()


def _subida_pesada_sync(
    contenido: bytes,
    nombre_archivo: str,
    usuario_id: int,
) -> dict:
    """
    Lógica pesada de subida (hash, guardado, BD, encolar).
    Se ejecuta en un hilo para no bloquear el event loop de FastAPI.
    Devuelve {"ok": True, "archivo_id", "nombre_archivo"} o {"ok": False, "detail": str, "status_code": int}.
    """
    from app.database import SessionLocal
    from app.models.usuario import Usuario

    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            usuario = db.query(Usuario).first()
        if not usuario:
            return {"ok": False, "detail": "No hay usuarios en la base de datos. Ejecute init_db.py", "status_code": 400}
        usuario_id = usuario.id

        hash_archivo = hashlib.sha256(contenido).hexdigest()
        archivo_existente = obtener_archivo_por_hash(db, hash_archivo)
        if archivo_existente:
            return {
                "ok": False,
                "detail": f"Archivo duplicado. Ya procesado con ID {archivo_existente.id}",
                "status_code": 400,
            }

        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        nombre = nombre_archivo or "sin_nombre.xml"
        ruta_guardado = upload_dir / nombre
        ruta_guardado.write_bytes(contenido)
        ruta_str = str(ruta_guardado)

        nuevo_archivo = ArchivoProcesado(
            usuario_id=usuario_id,
            nombre_archivo=nombre,
            hash_archivo=hash_archivo,
            estado="pendiente",
            ruta_archivo=ruta_str,
        )
        db.add(nuevo_archivo)
        db.commit()
        db.refresh(nuevo_archivo)
        archivo_id = nuevo_archivo.id

        _encolar_o_procesar_sync(archivo_id, ruta_str)

        return {
            "ok": True,
            "archivo_id": archivo_id,
            "nombre_archivo": nuevo_archivo.nombre_archivo,
        }
    except Exception as e:
        return {
            "ok": False,
            "detail": f"Error al guardar el archivo: {e}",
            "status_code": 500,
        }
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
    Sube un archivo de peajes. El trabajo pesado (hash, guardado, Celery/hilo)
    se hace en segundo plano para no bloquear el servidor; el dashboard sigue respondiendo.
    """
    from app.models.usuario import Usuario

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        usuario = db.query(Usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe el usuario y no hay usuarios en la BD. Ejecute init_db.py",
        )
    usuario_id = usuario.id

    contenido = await file.read()
    nombre_archivo = file.filename or "sin_nombre.xml"

    # Ejecutar hash, guardado y encolado en un hilo para no bloquear el event loop
    resultado = await asyncio.to_thread(
        _subida_pesada_sync,
        contenido,
        nombre_archivo,
        usuario_id,
    )

    if not resultado.get("ok"):
        raise HTTPException(
            status_code=resultado.get("status_code", 500),
            detail=resultado.get("detail", "Error en la subida"),
        )

    return ArchivoUploadResponse(
        archivo_id=resultado["archivo_id"],
        nombre_archivo=resultado["nombre_archivo"],
        estado="pendiente",
        mensaje="Archivo en cola. El procesamiento continúa en segundo plano (Celery o worker). Consulta estado en Archivos.",
    )


@router.get("/{archivo_id}", response_model=ArchivoStatus)
def get_archivo_status(archivo_id: int, db: Session = Depends(get_db)):
    """Consulta estado de procesamiento de un archivo."""
    archivo = db.query(ArchivoProcesado).filter(ArchivoProcesado.id == archivo_id).first()
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return archivo
