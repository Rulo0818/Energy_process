from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RegistroErrores(Base):
    __tablename__ = "registro_errores"

    id = Column(Integer, primary_key=True, index=True)
    archivo_id = Column(
        Integer,
        ForeignKey("archivo_procesado.id", ondelete="CASCADE"),
        nullable=False,
    )
    linea_archivo = Column(Integer, nullable=False)
    tipo_error = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    datos_linea = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())

    archivo = relationship("ArchivoProcesado", back_populates="errores")
