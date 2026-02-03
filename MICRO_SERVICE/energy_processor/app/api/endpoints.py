from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db import get_session
from app.services.parser import ParserService
from app.models.domain import EnergyRecord
import traceback

router = APIRouter()

@router.post("/process-file/")
async def upload_file(file: UploadFile = File(...), session: Session = Depends(get_session)):
    parser = ParserService(session)
    try:
        content = await file.read()
        record = parser.process_file(content, file.filename)
        return {"message": "File processed successfully", "id": record.id, "type": record.tipo_autoconsumo}
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/energy-records/", response_model=List[EnergyRecord])
def read_records(session: Session = Depends(get_session)):
    records = session.exec(select(EnergyRecord)).all()
    # "Validar que se muestre una lista vacía, cuando: En la base de datos no existan registros."
    # List[EnergyRecord] defaults to [] in JSON if empty.
    return records
