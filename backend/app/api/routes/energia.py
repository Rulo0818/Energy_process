from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import EnergiaExcedentaria
from app.schemas.energia import EnergiaExcedenteResponse, EnergiaListResponse

router = APIRouter(prefix="/api/v1/energia", tags=["energia"])


@router.get("", response_model=EnergiaListResponse)
def get_energia_registros(
    cups: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    tipo_autoconsumo: Optional[int] = Query(None),
    archivo_id: Optional[int] = Query(None, description="Filtrar por ID de archivo (registros OK de ese archivo)"),
    db: Session = Depends(get_db),
):
    """
    Consulta registros de energía con filtros opcionales.
    Use archivo_id para ver los registros OK de un archivo concreto.
    """
    query = db.query(EnergiaExcedentaria)
    if archivo_id is not None:
        query = query.filter(EnergiaExcedentaria.archivo_id == archivo_id)
    if cups:
        query = query.filter(EnergiaExcedentaria.cups_cliente == cups)
    if fecha_desde is not None:
        query = query.filter(EnergiaExcedentaria.fecha_desde >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(EnergiaExcedentaria.fecha_hasta <= fecha_hasta)
    if tipo_autoconsumo is not None:
        query = query.filter(EnergiaExcedentaria.tipo_autoconsumo == tipo_autoconsumo)

    registros = query.order_by(EnergiaExcedentaria.linea_archivo).all()
    return EnergiaListResponse(
        total=len(registros),
        registros=[EnergiaExcedenteResponse.model_validate(r) for r in registros],
    )
