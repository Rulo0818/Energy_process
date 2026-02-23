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


# Tipos que la BD acepta (migración 001). Si no está la 002, solo estos 7 están permitidos.
# Cualquier otro tipo se guarda como "formato_invalido"; la descripción sigue siendo la real.
TIPOS_ERROR_BD_PERMITIDOS = frozenset({
    "cliente_inexistente", "tipo_no_soportado", "formato_invalido", "archivo_duplicado",
    "inconsistencia_numerica", "array_longitud_invalida", "fecha_invalida",
})


def registrar_error(
    db: Session,
    archivo_id: int,
    linea: int,
    tipo: str,
    desc: str,
    datos: str | None = None,
) -> None:
    """Registra un error en la BD (queda listado en Archivos y errores)."""
    tipo_ok = tipo if tipo in TIPOS_ERROR_BD_PERMITIDOS else "formato_invalido"
    error = RegistroErrores(
        archivo_id=archivo_id,
        linea_archivo=linea,
        tipo_error=tipo_ok,
        descripcion=desc[:5000] if desc else "",  # límite razonable
        datos_linea=datos,
    )
    try:
        db.add(error)
        db.commit()
    except Exception:
        db.rollback()
        raise


# Estructura XML esperada (para validación)
XML_ROOT_TAG = "energiaExcedentaria"
XML_REGISTRO_TAG = "registro"
XML_CAMPOS_OBLIGATORIOS = ("cupsCliente", "instalacionGen", "fechaDesde", "fechaHasta", "tipoAutoconsumo")
XML_BLOQUES_6_HORAS = ("energiaNetaGen", "energiaAutoconsumida", "pagoTDA")
NUM_PERIODOS = 6
# Aceptamos 6 <hora> o bien <p1>..<p6> como períodos
XML_TAGS_PERIODO_HORA = "hora"
XML_TAGS_PERIODO_P = ("p1", "p2", "p3", "p4", "p5", "p6")


def _tag_sin_namespace(tag: str) -> str:
    """Devuelve el nombre del tag sin namespace (ej. {uri}energiaExcedentaria -> energiaExcedentaria)."""
    if tag and "}" in tag:
        return tag.split("}", 1)[1]
    return tag or ""


def _find_child(element, local_name: str):
    """Obtiene el primer hijo cuyo tag (sin namespace) sea local_name."""
    for child in element:
        if _tag_sin_namespace(child.tag) == local_name:
            return child
    return element.find(local_name)  # por si no hay namespace


def _obtener_valores_periodo(elem) -> tuple[list, list[tuple[str, str]]]:
    """
    Obtiene 6 valores numéricos de un bloque (energiaNetaGen, etc.).
    Acepta 6 elementos <hora> o 6 elementos <p1>..<p6>.
    Devuelve (lista de 6 textos, lista de errores de estructura).
    """
    errores: list[tuple[str, str]] = []
    if elem is None:
        return [], [("estructura_invalida", "Falta bloque")]
    hijos_por_tag = {}
    for e in elem:
        t = _tag_sin_namespace(e.tag)
        if t not in hijos_por_tag:
            hijos_por_tag[t] = []
        hijos_por_tag[t].append(e)
    # Opción 1: 6 <hora>
    horas = hijos_por_tag.get("hora", [])
    if len(horas) >= NUM_PERIODOS:
        valores = [(h.text or "").strip() for h in horas[:NUM_PERIODOS]]
        if all(v for v in valores):
            return valores, []
        errores.append(("estructura_invalida", "Algunos <hora> están vacíos"))
        return [], errores
    # Opción 2: <p1>..<p6>
    for pt in XML_TAGS_PERIODO_P:
        if pt not in hijos_por_tag or len(hijos_por_tag[pt]) == 0:
            return [], [("estructura_invalida", f"Faltan períodos: se esperan 6 <hora> o <p1>..<p6>. Falta <{pt}>")]
    valores = []
    for pt in XML_TAGS_PERIODO_P:
        v = (hijos_por_tag[pt][0].text or "").strip()
        valores.append(v)
        if not v:
            return [], [("estructura_invalida", f"El elemento <{pt}> está vacío")]
    return valores, []


def validar_estructura_xml_registro(reg) -> list[tuple[str, str]]:
    """
    Valida que un elemento <registro> tenga la estructura esperada:
      cupsCliente, instalacionGen, fechaDesde, fechaHasta, tipoAutoconsumo
      Bloques con 6 valores: <hora> x6 o <p1>..<p6> en energiaNetaGen, energiaAutoconsumida, pagoTDA.
    """
    errores: list[tuple[str, str]] = []
    for tag in XML_CAMPOS_OBLIGATORIOS:
        elem = _find_child(reg, tag)
        if elem is None:
            errores.append(("estructura_invalida", f"Falta elemento obligatorio: <{tag}>"))
        elif elem.text is None or not str(elem.text).strip():
            errores.append(("estructura_invalida", f"El elemento <{tag}> está vacío"))
    for bloque in XML_BLOQUES_6_HORAS:
        elem = _find_child(reg, bloque)
        _, err = _obtener_valores_periodo(elem)
        if err:
            errores.append((err[0][0], f"<{bloque}>: {err[0][1]}"))
    return errores


def _procesar_xml_autoconsumo_colectivo(db: Session, archivo_id: int, root, ruta_archivo_abs: str) -> None:
    """
    Procesa XML con raíz <AutoconsumoColectivo>: Cabecera (CUPS, TipoAutoconsumo, PeriodoFacturacion) + Registros (6 valores por bloque).
    Cada grupo de 6 <Registro> forma un registro de energía (EnergiaNetaGenerada, EnergiaAutoconsumida, PagoTDA).
    """
    cabecera = _find_child(root, "Cabecera")
    registros_cont = _find_child(root, "Registros")
    if not cabecera or not registros_cont:
        registrar_error(db, archivo_id, 1, "estructura_invalida", "AutoconsumoColectivo debe tener Cabecera y Registros")
        return
    cups_e = _find_child(cabecera, "CUPS")
    tipo_e = _find_child(cabecera, "TipoAutoconsumo")
    periodo = _find_child(cabecera, "PeriodoFacturacion")
    fecha_desde_e = _find_child(periodo, "FechaDesde") if periodo else None
    fecha_hasta_e = _find_child(periodo, "FechaHasta") if periodo else None
    if not all([cups_e, tipo_e, fecha_desde_e, fecha_hasta_e]):
        registrar_error(db, archivo_id, 1, "estructura_invalida", "Cabecera debe tener CUPS, TipoAutoconsumo y PeriodoFacturacion (FechaDesde, FechaHasta)")
        return
    cups = (cups_e.text or "").strip()
    tipo = (tipo_e.text or "").strip()
    fecha_desde = (fecha_desde_e.text or "").strip()
    fecha_hasta = (fecha_hasta_e.text or "").strip()
    registros = [e for e in registros_cont if _tag_sin_namespace(e.tag) == "Registro"]
    if len(registros) < NUM_PERIODOS:
        registrar_error(db, archivo_id, 2, "estructura_invalida", f"AutoconsumoColectivo debe tener al menos {NUM_PERIODOS} Registro. Encontrados: {len(registros)}")
        return
    row = {
        "cups_cliente": cups,
        "instalacion_gen": "",
        "fecha_desde_1": fecha_desde,
        "fecha_hasta_1": fecha_hasta,
        "tipo_autoconsumo": tipo,
    }
    def _txt(e):
        return (e.text or "").strip() if e is not None else ""
    for i in range(NUM_PERIODOS):
        reg = registros[i]
        row["energia_neta_gen_" + str(i + 1)] = _txt(_find_child(reg, "EnergiaNetaGenerada"))
        row["energia_autoconsumida_" + str(i + 1)] = _txt(_find_child(reg, "EnergiaAutoconsumida"))
        row["pago_tda_" + str(i + 1)] = _txt(_find_child(reg, "PagoTDA"))
    row = {k: (v.strip() if isinstance(v, str) else str(v)) for k, v in row.items()}
    errores = validar_linea(row, 2, db)
    if errores:
        for t, d in errores:
            registrar_error(db, archivo_id, 2, t, d, json.dumps(row))
        return
    try:
        insertar_energia(db, archivo_id, 2, row)
    except Exception as e:
        registrar_error(db, archivo_id, 2, "inconsistencia", str(e), json.dumps(row))


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
        # Archivos .txt pueden ser XML (p. ej. exportados como .txt)
        es_xml = False
        if ext == ".xml":
            es_xml = True
        elif ext == ".txt":
            with open(ruta_archivo_abs, "r", encoding="utf-8-sig", errors="replace") as f:
                peek = f.read(512)
            es_xml = peek.strip().startswith("<?xml") or (peek.strip().startswith("<") and "<" in peek and ">" in peek)

        if ext == ".xml" or es_xml:
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

            root_tag = _tag_sin_namespace(root.tag)
            # Soporte dos formatos XML: energiaExcedentaria (registro con 6 periodos) y AutoconsumoColectivo (Cabecera + Registros)
            if root_tag == "AutoconsumoColectivo":
                _procesar_xml_autoconsumo_colectivo(db, archivo_id, root, ruta_archivo_abs)
                archivo.estado = "completado"
                total_autoc = db.query(EnergiaExcedentaria).filter(EnergiaExcedentaria.archivo_id == archivo_id).count()
                total_err_autoc = db.query(RegistroErrores).filter(RegistroErrores.archivo_id == archivo_id).count()
                archivo.total_registros = total_autoc + total_err_autoc
                archivo.registros_exitosos = total_autoc
                archivo.registros_con_error = total_err_autoc
                db.commit()
                return
            if root_tag != XML_ROOT_TAG:
                registrar_error(
                    db, archivo_id, 1, "estructura_invalida",
                    f"Raíz del XML debe ser <{XML_ROOT_TAG}> o <AutoconsumoColectivo>. Encontrado: <{root_tag or root.tag}>"
                )
                archivo.estado = "error"
                db.commit()
                return

            # Obtener todos los <registro> (con o sin namespace)
            registros = [e for e in root if _tag_sin_namespace(e.tag) == XML_REGISTRO_TAG]
            if not registros:
                registrar_error(db, archivo_id, 1, "estructura_invalida", "No se encontró ningún elemento <registro> dentro de <energiaExcedentaria>")
                archivo.estado = "error"
                db.commit()
                return

            for num_linea, reg in enumerate(registros, start=2):
                total += 1
                # 1) Validar estructura del registro (campos obligatorios y 6 hora por bloque)
                errores_estructura = validar_estructura_xml_registro(reg)
                if errores_estructura:
                    for t, d in errores_estructura:
                        registrar_error(db, archivo_id, num_linea, t, d, None)
                    con_error += 1
                    continue

                # 2) Construir row desde la estructura validada (acepta <hora> o <p1>..<p6>)
                def _text(elm):
                    return (elm.text or "").strip() if elm is not None else ""
                row = {
                    "cups_cliente": _text(_find_child(reg, "cupsCliente")),
                    "instalacion_gen": _text(_find_child(reg, "instalacionGen")),
                    "fecha_desde_1": _text(_find_child(reg, "fechaDesde")),
                    "fecha_hasta_1": _text(_find_child(reg, "fechaHasta")),
                    "tipo_autoconsumo": _text(_find_child(reg, "tipoAutoconsumo")),
                }
                for campo_xml, campo_csv in [("energiaNetaGen", "energia_neta_gen"), ("energiaAutoconsumida", "energia_autoconsumida"), ("pagoTDA", "pago_tda")]:
                    elem = _find_child(reg, campo_xml)
                    valores, _ = _obtener_valores_periodo(elem)
                    for i in range(1, NUM_PERIODOS + 1):
                        row[f"{campo_csv}_{i}"] = valores[i - 1] if i <= len(valores) else ""

                errores = validar_linea(row, num_linea, db)
                if not errores:
                    try:
                        f_d = datetime.strptime(row["fecha_desde_1"], "%Y-%m-%d").date()
                        f_h = datetime.strptime(row["fecha_hasta_1"], "%Y-%m-%d").date()
                        if db.query(EnergiaExcedentaria).filter(
                            EnergiaExcedentaria.cups_cliente == row["cups_cliente"],
                            EnergiaExcedentaria.fecha_desde == f_d,
                            EnergiaExcedentaria.fecha_hasta == f_h,
                            EnergiaExcedentaria.instalacion_gen == row.get("instalacion_gen", ""),
                        ).first():
                            errores.append(("registro_duplicado", "Ya existe este periodo para este CUPS"))
                    except Exception:
                        pass

                if errores:
                    for t, d in errores:
                        registrar_error(db, archivo_id, num_linea, t, d, json.dumps(row))
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
                    dialect = None
                    if sample:
                        try:
                            dialect = csv.Sniffer().sniff(sample, delimiters=",;|")
                        except csv.Error:
                            pass
                    if dialect is None:
                        first_line = sample.split("\n")[0] if sample else ""
                        for delim in "|", ",", ";":
                            if first_line.count(delim) >= 4:
                                dialect = type("DelimDialect", (csv.Dialect,), {
                                    "delimiter": delim,
                                    "doublequote": True,
                                    "skipinitialspace": True,
                                    "lineterminator": "\r\n",
                                    "quoting": csv.QUOTE_MINIMAL,
                                })()
                                break
                    if dialect is None:
                        dialect = csv.excel
                    reader = csv.DictReader(f, dialect=dialect)
                    fieldnames = [fn.strip() for fn in (reader.fieldnames or []) if fn]
                    # Validar estructura CSV: debe tener columnas que permitan cups, fechas, tipo
                    posibles_cups = {"cups", "cups_cliente", "CUPS", "cupsCliente"}
                    posibles_fecha_desde = {"fecha_desde", "fecha_desde_1", "fechaDesde"}
                    posibles_fecha_hasta = {"fecha_hasta", "fecha_hasta_1", "fechaHasta"}
                    tiene_cups = any(c in fieldnames for c in posibles_cups)
                    tiene_fechas = any(f in fieldnames for f in posibles_fecha_desde) and any(f in fieldnames for f in posibles_fecha_hasta)
                    tiene_tipo = any(t in fieldnames for t in ("tipo", "tipo_autoconsumo", "tipoAutoconsumo"))
                    if not fieldnames or not (tiene_cups and tiene_fechas and tiene_tipo):
                        registrar_error(
                            db, archivo_id, 1, "estructura_invalida",
                            "CSV/TXT debe incluir columnas para CUPS, fechas (desde/hasta) y tipo autoconsumo (ej. cups, fecha_desde, fecha_hasta, tipo)"
                        )
                        archivo.estado = "error"
                        db.commit()
                        return

                    for num_linea, row in enumerate(reader, start=2):
                        total += 1
                        row = {k.strip(): v for k, v in row.items() if k}
                        mapping = {
                            "cups": "cups_cliente", "CUPS": "cups_cliente", "cupsCliente": "cups_cliente",
                            "tipo": "tipo_autoconsumo", "tipoAutoconsumo": "tipo_autoconsumo",
                            "fecha_desde": "fecha_desde_1", "fechaDesde": "fecha_desde_1",
                            "fecha_hasta": "fecha_hasta_1", "fechaHasta": "fecha_hasta_1",
                            "instalacion": "instalacion_gen", "instalacionGen": "instalacion_gen",
                        }
                        for ok, nk in mapping.items():
                            if ok in row and (nk not in row or not (row.get(nk) or "").strip()):
                                row[nk] = row.get(ok) or ""

                        for pref_ok, pref_nk in [("p", "energia_neta_gen_"), ("gen_p", "energia_neta_gen_"), ("cons_p", "energia_autoconsumida_")]:
                            for i in range(1, 7):
                                ok = f"{pref_ok}{i}"
                                nk = f"{pref_nk}{i}"
                                if ok in row and (nk not in row or not (row.get(nk) or "").strip()):
                                    row[nk] = row.get(ok) or ""

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
