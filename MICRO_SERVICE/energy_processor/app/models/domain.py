from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from sqlalchemy import Column, JSON

class Client(SQLModel, table=True):
    __tablename__ = "clients"
    cups: str = Field(primary_key=True, index=True)
    name: str

    energy_records: List["EnergyRecord"] = Relationship(back_populates="client")

class ProcessedFile(SQLModel, table=True):
    __tablename__ = "processed_files"
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(unique=True, index=True)
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    energy_records: List["EnergyRecord"] = Relationship(back_populates="file")

class EnergyRecord(SQLModel, table=True):
    __tablename__ = "energy_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    file_id: int = Field(foreign_key="processed_files.id")
    cups: str = Field(foreign_key="clients.cups")
    
    fecha_desde: datetime
    fecha_hasta: datetime
    
    instalacion_gen_autoconsumo: str
    
    # Storing 6 values as JSON array
    valor_energia_neta_gen: List[float] = Field(sa_column=Column(JSON))
    
    # Storing 6 values as JSON array
    valor_energia_autoconsumida: List[float] = Field(sa_column=Column(JSON))
    
    pago_tda: List[float] = Field(sa_column=Column(JSON))
    
    # Requisito: Añadir un campo llamado tipo_autoconsumo
    tipo_autoconsumo: str 

    file: ProcessedFile = Relationship(back_populates="energy_records")
    client: Client = Relationship(back_populates="energy_records")
