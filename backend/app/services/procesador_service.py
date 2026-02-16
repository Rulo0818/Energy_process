"""Procesamiento de archivos de peajes: parsing, validaciones y persistencia."""

import json
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy.orm import Session

from app.models import ArchivoProcesado, EnergiaExcedentaria, RegistroErrores
from app.utils.validators import TIPOS_AUTOCONSUMO_VALIDOS


def validar_cups_existe(cups: str, db: Session) -> bool:
    """
    Verifica si CUPS existe en la tabla de clientes.
    """
    from app.models import Cliente
    return db.query(Cliente).filter(Cliente.cups == cups).first() is not None


def validar_linea(
    row: dict[str, Any], num_linea: int, db: Session
) -> list[tuple[str, str]]:
    """
    Valida una línea del archivo siguiendo las 7 reglas:
    1. CUPS formato "ES" + longitud >= 10
    2. Tipo autoconsumo {12, 41, 42, 43, 51}
    3. Fechas válidas (hasta >= desde)
    4. Arrays con 6 períodos exactos
    5. Conversión numérica correcta
    6. CUPS existe en sistema
    7. Registro único (simulado por ahora si no hay hash por registro)
    """
    errores: list[tuple[str, str]] = []

    # 1. CUPS formato
    cups = (row.get("cups_cliente") or "").strip()
    if not cups or not cups.startswith("ES") or len(cups) < 10:
        errores.append(
            ("formato_cups_invalido", f"CUPS {cups or '(vacío)'} debe empezar por ES y tener longitud >= 10")
        )
    
    # 6. CUPS existe en sistema
    elif not validar_cups_existe(cups, db):
        errores.append(
            ("cliente_inexistente", f"CUPS {cups} no encontrado en la base de datos de clientes")
        )

    # 2. Tipo autoconsumo
    try:
        tipo_str = row.get("tipo_autoconsumo")
        if tipo_str is None or tipo_str == "":
            errores.append(("tipo_vacio", "Tipo autoconsumo es obligatorio"))
        else:
            tipo = int(tipo_str)
            if tipo not in TIPOS_AUTOCONSUMO_VALIDOS:
                errores.append(
                    (
                        "tipo_no_soportado",
                        f"Tipo autoconsumo {tipo} no válido. Permitidos: {sorted(TIPOS_AUTOCONSUMO_VALIDOS)}",
                    )
                )
    except (ValueError, TypeError):
        errores.append(("formato_invalido", f"Tipo autoconsumo no es un número entero: {row.get('tipo_autoconsumo')}"))

    # 3. Fechas válidas y 5. Conversión numérica (fechas)
    fecha_desde = None
    fecha_hasta = None
    try:
        fecha_desde_str = (row.get("fecha_desde_1") or "").strip()
        fecha_hasta_str = (row.get("fecha_hasta_1") or "").strip()
        if not fecha_desde_str or not fecha_hasta_str:
            errores.append(("fecha_vacia", "Las fechas desde/hasta son obligatorias"))
        else:
            fecha_desde = datetime.strptime(fecha_desde_str, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(fecha_hasta_str, "%Y-%m-%d").date()
            if fecha_hasta < fecha_desde:
                errores.append(("rango_fechas_invalido", "La fecha hasta no puede ser menor a la fecha desde"))
    except ValueError:
        errores.append(
            ("fecha_formato_invalido", f"Formato de fecha incorrecto (esperado YYYY-MM-DD): {row.get('fecha_desde_1')} / {row.get('fecha_hasta_1')}")
        )

    # 4. Arrays con 6 períodos exactos y 5. Conversión numérica (valores)
    for campo in ["energia_neta_gen", "energia_autoconsumida", "pago_tda"]:
        valores_validos = 0
        for i in range(1, 7):
            key = f"{campo}_{i}"
            val = row.get(key)
            if val is not None and str(val).strip() != "":
                try:
                    Decimal(str(val).strip())
                    valores_validos += 1
                except (InvalidOperation, TypeError):
                    errores.append(
                        ("formato_numerico_invalido", f"Valor numérico inválido en {key}: {val}")
                    )
                    break
        
        if valores_validos != 6:
            errores.append(
                (
                    "periodos_insuficientes",
                    f"El campo {campo} debe tener exactamente 6 periodos (P1-P6). Encontrados: {valores_validos}",
                )
            )

    return errores


def insertar_energia(
    db: Session, archivo_id: int, linea: int, row: dict[str, Any]
) -> None:
    """Inserta un registro de energía validado."""
    from app.models import Cliente
    
    # Obtener el ID del cliente basado en el CUPS
    cliente = db.query(Cliente).filter(Cliente.cups == row["cups_cliente"].strip()).first()
    
    energia_neta = [
        Decimal(str(row.get(f"energia_neta_gen_{i}", 0)).strip())
        for i in range(1, 7)
    ]
    energia_auto = [
        Decimal(str(row.get(f"energia_autoconsumida_{i}", 0)).strip())
        for i in range(1, 7)
    ]
    pago = [
        Decimal(str(row.get(f"pago_tda_{i}", 0)).strip()) for i in range(1, 7)
    ]

    registro = EnergiaExcedentaria(
        archivo_id=archivo_id,
        cliente_id=cliente.id,
        cups_cliente=cliente.cups,
        linea_archivo=linea,
        instalacion_gen=(row.get("instalacion_gen") or "").strip(),
        fecha_desde=datetime.strptime(
            (row.get("fecha_desde_1") or "").strip(), "%Y-%m-%d"
        ).date(),
        fecha_hasta=datetime.strptime(
            (row.get("fecha_hasta_1") or "").strip(), "%Y-%m-%d"
        ).date(),
        tipo_autoconsumo=int(row["tipo_autoconsumo"]),
        energia_neta_gen=energia_neta,
        energia_autoconsumida=energia_auto,
        pago_tda=pago,
    )
    db.add(registro)
    db.commit()


def registrar_error(
    db: Session,
    archivo_id: int,
    linea: int,
    tipo: str,
    desc: str,
    datos: str | None = None,
) -> None:
    """Registra un error en la BD."""
    error = RegistroErrores(
        archivo_id=archivo_id,
        linea_archivo=linea,
        tipo_error=tipo,
        descripcion=desc,
        datos_linea=datos,
    )
    db.add(error)
    db.commit()


def procesar_archivo(db: Session, archivo_id: int, ruta_archivo: str) -> None:
    """
    Procesa archivo de peajes (CSV o XML) línea por línea.
    Usa primer valor de fechas, valida arrays de 6, tipos {12,41,42,43,51}, CUPS.
    """
    archivo = db.query(ArchivoProcesado).filter(ArchivoProcesado.id == archivo_id).first()
    if not archivo:
        return

    archivo.estado = "procesando"
    archivo.fecha_procesamiento = datetime.utcnow()
    db.commit()

    exitosos = 0
    con_error = 0
    total = 0

    try:
        # CORRECCIÓN PARA WINDOWS: Si la ruta viene de Docker (/app/uploads), 
        # la traducimos a la carpeta local de uploads.
        if ruta_archivo.startswith("/app/uploads/"):
            filename = os.path.basename(ruta_archivo)
            ruta_archivo = os.path.join(os.getcwd(), "uploads", filename)
        
        ruta_archivo_abs = os.path.abspath(ruta_archivo)
        
        if not os.path.exists(ruta_archivo_abs):
            error_msg = f"Archivo no encontrado físicamente en: {ruta_archivo_abs}"
            registrar_error(db, archivo_id, 0, "archivo_no_encontrado", error_msg)
            archivo.estado = "error"
            db.commit()
            return

        ext = os.path.splitext(ruta_archivo_abs)[1].lower()
        
        if ext == ".xml":
            import xml.etree.ElementTree as ET
            try:
                with open(ruta_archivo_abs, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                    if "</energiaExcedentaria>" in xml_content:
                        xml_content = xml_content.split("</energiaExcedentaria>")[0] + "</energiaExcedentaria>"
                root = ET.fromstring(xml_content)
            except Exception as e:
                registrar_error(db, archivo_id, 0, "error_xml", f"Error al leer XML: {str(e)}")
                archivo.estado = "error"
                db.commit()
                return

            for num_linea, reg in enumerate(root.findall("registro"), start=2):
                total += 1
                row = {
                    "cups_cliente": reg.findtext("cupsCliente"),
                    "instalacion_gen": reg.findtext("instalacionGen"),
                    "fecha_desde_1": reg.findtext("fechaDesde"),
                    "fecha_hasta_1": reg.findtext("fechaHasta"),
                    "tipo_autoconsumo": reg.findtext("tipoAutoconsumo"),
                }
                for campo_xml, campo_csv in [("energiaNetaGen", "energia_neta_gen"), ("energiaAutoconsumida", "energia_autoconsumida"), ("pagoTDA", "pago_tda")]:
                    elem = reg.find(campo_xml)
                    if elem is not None:
                        valores = [e.text.strip() for e in elem if e.text and e.text.strip()]
                        for i, v in enumerate(valores, start=1):
                            if i <= 6: row[f"{campo_csv}_{i}"] = v
                
                errores = validar_linea(row, num_linea, db)
                if not errores:
                    # Validación de duplicado
                    try:
                        f_d = datetime.strptime(row['fecha_desde_1'], "%Y-%m-%d").date()
                        f_h = datetime.strptime(row['fecha_hasta_1'], "%Y-%m-%d").date()
                        if db.query(EnergiaExcedentaria).filter(EnergiaExcedentaria.cups_cliente == row['cups_cliente'], EnergiaExcedentaria.fecha_desde == f_d, EnergiaExcedentaria.fecha_hasta == f_h, EnergiaExcedentaria.instalacion_gen == row.get('instalacion_gen', '')).first():
                            errores.append(("registro_duplicado", "Ya existe este periodo para este CUPS"))
                    except: pass

                if errores:
                    for t, d in errores: registrar_error(db, archivo_id, num_linea, t, d, json.dumps(row))
                    con_error += 1
                else:
                    try:
                        insertar_energia(db, archivo_id, num_linea, row)
                        exitosos += 1
                    except Exception as e:
                        registrar_error(db, archivo_id, num_linea, "inconsistencia", str(e), json.dumps(row))
                        con_error += 1
        else:
            import csv
            try:
                with open(ruta_archivo_abs, "r", encoding="utf-8-sig", newline="") as f:
                    sample = f.read(2048)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;|') if sample else 'excel'
                    reader = csv.DictReader(f, dialect=dialect)
                    for num_linea, row in enumerate(reader, start=2):
                        total += 1
                        row = {k.strip(): v for k, v in row.items() if k}
                        mapping = {'cups': 'cups_cliente', 'CUPS': 'cups_cliente', 'tipo': 'tipo_autoconsumo', 'fecha_desde': 'fecha_desde_1', 'fecha_hasta': 'fecha_hasta_1'}
                        for ok, nk in mapping.items():
                            if ok in row and nk not in row: row[nk] = row[ok]
                        
                        errores = validar_linea(row, num_linea, db)
                        if not errores:
                            try:
                                f_d = datetime.strptime(row['fecha_desde_1'], "%Y-%m-%d").date()
                                f_h = datetime.strptime(row['fecha_hasta_1'], "%Y-%m-%d").date()
                                if db.query(EnergiaExcedentaria).filter(EnergiaExcedentaria.cups_cliente == row['cups_cliente'], EnergiaExcedentaria.fecha_desde == f_d, EnergiaExcedentaria.fecha_hasta == f_h).first():
                                    errores.append(("registro_duplicado", "Ya existe"))
                            except: pass
                        
                        if errores:
                            for t, d in errores: registrar_error(db, archivo_id, num_linea, t, d, json.dumps(row))
                            con_error += 1
                        else:
                            try:
                                insertar_energia(db, archivo_id, num_linea, row)
                                exitosos += 1
                            except Exception as e:
                                registrar_error(db, archivo_id, num_linea, "inconsistencia", str(e), json.dumps(row))
                                con_error += 1
            except Exception as e:
                registrar_error(db, archivo_id, 0, "error_lectura", str(e))
                archivo.estado = "error"
                db.commit()
                return

        archivo.estado = "completado"
        archivo.total_registros = total
        archivo.registros_exitosos = exitosos
        archivo.registros_con_error = con_error
        db.commit()
    except Exception as e:
        archivo.estado = "error"
        registrar_error(db, archivo_id, 0, "error_global", str(e))
        db.commit()
