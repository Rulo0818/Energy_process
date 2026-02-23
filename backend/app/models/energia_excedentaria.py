from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    ARRAY,
    Numeric,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EnergiaExcedentaria(Base):
    __tablename__ = "energia_excedentaria"

    id = Column(Integer, primary_key=True, index=True)
    archivo_id = Column(
        Integer,
        ForeignKey("archivo_procesado.id", ondelete="CASCADE"),
        nullable=False,
    )
    cliente_id = Column(
        Integer,
        ForeignKey("cliente.id", ondelete="RESTRICT"),
        nullable=False,
    )
    linea_archivo = Column(Integer, nullable=False)
    instalacion_gen = Column(String(50), nullable=False, index=True)
    fecha_desde = Column(Date, nullable=False, index=True)
    fecha_hasta = Column(Date, nullable=False, index=True)
    tipo_autoconsumo = Column(
        Integer, ForeignKey("tipo_autoconsumo.codigo"), nullable=False
    )
    cups_cliente = Column(String(255), nullable=False, index=True)

    energia_neta_gen = Column(ARRAY(Numeric(12, 3)), nullable=False)
    energia_autoconsumida = Column(ARRAY(Numeric(12, 3)), nullable=False)
    pago_tda = Column(ARRAY(Numeric(12, 2)), nullable=False)

    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())

    archivo = relationship("ArchivoProcesado", back_populates="registros_energia")
    cliente = relationship("Cliente", back_populates="registros_energia")
    tipo = relationship("TipoAutoconsumo", back_populates="registros_energia")

    __table_args__ = (
        CheckConstraint("fecha_hasta >= fecha_desde", name="ck_fechas_validas"),
    )
