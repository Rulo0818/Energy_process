import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select
from app.models.domain import Client, ProcessedFile, EnergyRecord
from fastapi import HTTPException

class ParserService:
    def __init__(self, session: Session):
        self.session = session

    def process_file(self, file_content: bytes, filename: str):
        # 1. Validation: File uniqueness
        existing_file = self.session.exec(select(ProcessedFile).where(ProcessedFile.filename == filename)).first()
        if existing_file:
            raise HTTPException(status_code=400, detail=f"El archivo '{filename}' ya ha sido procesado")

        try:
            root = ET.fromstring(file_content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Error de formato XML: No se pudo procesar el archivo")

        # Extract basic info
        cups_element = root.find(".//CUPS")
        if cups_element is None:
             raise HTTPException(status_code=400, detail="Error: CUPS no encontrado en el archivo XML")
        cups = cups_element.text

        # 2. Validation: Customer exists
        client = self.session.get(Client, cups)
        if not client:
             raise HTTPException(status_code=400, detail=f"Error: No existe el cliente con CUPS '{cups}' en la base de datos")

        # Parsing specific fields
        instalacion_node = root.find(".//InstalacionGenAutoconsumo")
        instalacion_val = instalacion_node.text if instalacion_node is not None else ""
        
        # Determine 'tipo_autoconsumo'.
        supported_types = ["12", "41", "42", "43", "51"]
        tipo_autoconsumo = instalacion_val.strip() if instalacion_val else "Desconocido"
        
        if tipo_autoconsumo not in supported_types:
             raise HTTPException(status_code=400, detail=f"Error: Tipo de autoconsumo '{tipo_autoconsumo}' no soportado (Soportados: {', '.join(supported_types)})")

        periodos = root.findall(".//Periodo")
        if not periodos:
            fecha_desde = datetime.now(timezone.utc)
            fecha_hasta = datetime.now(timezone.utc)
        else:
            try:
                p1 = periodos[0]
                fd_str = p1.find("FechaDesde").text
                fh_str = p1.find("FechaHasta").text
                fecha_desde = datetime.strptime(fd_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                fecha_hasta = datetime.strptime(fh_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except Exception as e:
                print(f"Error parsing dates: {e}")
                fecha_desde = datetime.now(timezone.utc)
                fecha_hasta = datetime.now(timezone.utc)

        val_energia_neta = [0.0] * 6
        val_energia_auto = [0.0] * 6
        pago_tda_vals = [0.0] * 6

        for i, p in enumerate(periodos[:6]):
             try:
                 net_el = p.find("ValorEnergiaNetaGen")
                 if net_el is not None:
                    val_energia_neta[i] = float(net_el.text)
             except: pass
             
             try:
                 auto_el = p.find("ValorEnergiaAutoconsumida")
                 if auto_el is not None:
                    val_energia_auto[i] = float(auto_el.text)
             except: pass

             try:
                 tda_el = p.find("PagoTDA")
                 if tda_el is not None:
                    pago_tda_vals[i] = float(tda_el.text)
             except: pass

        # Save to DB
        new_file_record = ProcessedFile(filename=filename)
        self.session.add(new_file_record)
        self.session.commit()
        self.session.refresh(new_file_record)

        energy_record = EnergyRecord(
            file_id=new_file_record.id,
            cups=cups,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            instalacion_gen_autoconsumo=instalacion_val,
            valor_energia_neta_gen=val_energia_neta,
            valor_energia_autoconsumida=val_energia_auto,
            pago_tda=pago_tda_vals,
            tipo_autoconsumo=tipo_autoconsumo
        )
        self.session.add(energy_record)
        self.session.commit()
        self.session.refresh(energy_record)
        
        return energy_record
