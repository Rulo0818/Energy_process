# REPORTE DEL PROYECTO

## Datos Generales
- **Proyecto:** Microservicios (Energy Processor)
- **Semana:** 2
- **Nombre del responsable:** Raull Polvo Montes
- **Rol:** Desarrollador
- **Fecha:** 30/01/26

## Objetivo del Módulo Desarrollado
El objetivo principal de este desarrollo fue **seleccionar tecnologías, frameworks y definir la estructura base del proyecto de microservicios**, asegurando una arquitectura escalable y mantenible.

Adicionalmente, el módulo `energy_processor` implementa la funcionalidad de procesar archivos de peajes de energía en formato XML, gestionando la ingesta de datos, validación y consulta histórica.

## Funcionalidades Implementadas
1.  **Definición de Arquitectura y Stack Tecnológico:**
    -   Selección de **Python** con **FastAPI** como framework principal para alto rendimiento.
    -   Implementación de **SQLModel** para ORM y validación de datos.
    -   Estructura modular (`app/api`, `app/services`, `app/models`) escalable para microservicios.
    -   Containerización con **Docker** y **Docker Compose**.

2.  **Autenticación de Usuarios (Sencilla):**
    -   Endpoint para inicio de sesión (`POST /api/login`) que genera un token de acceso (mock) para credenciales predefinidas.

3.  **Carga y Procesamiento de Archivos (XML):**
    -   Endpoint de subida de archivos (`POST /api/process-file/`).
    -   Parsing de archivos XML para extraer:
        -   Código CUPS.
        -   Datos de instalación de autoconsumo (`InstalacionGenAutoconsumo`).
        -   Periodos de facturación (`FechaDesde`, `FechaHasta`).
        -   Valores de energía neta (`ValorEnergiaNetaGen`).
        -   Valores de energía autoconsumida (`ValorEnergiaAutoconsumida`).
        -   Pago TDA (`PagoTDA`).

4.  **Validaciones de Negocio:**
    -   **Unicidad de Archivo:** Verificación para evitar procesar el mismo archivo (por nombre) más de una vez.
    -   **Existencia de Cliente:** Validación de que el CUPS del archivo corresponda a un cliente existente en la base de datos.
    -   **Tipos de Autoconsumo:** Soporte y validación para tipos de autoconsumo específicos: 12, 41, 42, 43, 51.

5.  **Consulta de Historial:**
    -   Endpoint (`GET /api/energy-records/`) para listar todos los registros energéticos procesados exitosamente.
    -   Manejo de respuestas vacías (retorna lista vacía si no hay datos).

6.  **Infraestructura y Despliegue:**
    -   Configuración de Docker y Docker Compose para levantar el servicio y la base de datos fácilmente.
    -   Interfaz frontend básica (HTML/JS) para probar la carga y visualización.

## Incidencias Detectadas
Durante el análisis del código se identificaron las siguientes observaciones técnicas/incidencias:

1.  **Manejo de Errores en Parsing (Silencioso):**
    -   En `parser.py`, el bucle que procesa los periodos (líneas 65-82) utiliza `try...except` con `pass` para la extracción de valores numéricos (`ValorEnergiaNetaGen`, etc.). Esto puede causar que errores de formato en los datos numéricos pasen desapercibidos, guardando ceros en lugar de alertar sobre el error.

2.  **Validación de Fechas Generica:**
    -   Si falla el parsing de las fechas (`FechaDesde`, `FechaHasta`), el sistema asigna la fecha actual (`datetime.now()`) en lugar de rechazar el archivo o notificar el error específico (líneas 56-59 de `parser.py`). Esto podría generar inconsistencias en los datos históricos.

3.  **Credenciales en Código (Hardcoded):**
    -   El sistema de autenticación (`auth.py`) utiliza credenciales quemadas en el código (`admin` / `0823`), lo cual es inseguro para un entorno productivo y debe migrarse a variables de entorno o base de datos.

## Observaciones Finales
El módulo cumple con los requisitos funcionales principales de procesamiento y validación de archivos de energía. La estructura del proyecto está modularizada correctamente siguiendo el patrón de microservicios con FastAPI. Se recomienda refactorizar el manejo de excepciones en el parser para asegurar una mayor calidad de datos y externalizar la configuración de seguridad antes de fases posteriores.
