### Swagger / OpenAPI de la API `energy-process`

Este documento explica **cómo usar la interfaz Swagger** (`/docs`) de tu backend FastAPI y **cómo verificar que funciona cada grupo de endpoints**.

Por defecto, Swagger está disponible en:

- Local: `http://localhost:8000/docs`
- En Docker: la misma URL si has publicado el puerto `8000:8000`

En la parte superior de Swagger verás:

- El botón **`Authorize`** para poner el token `Bearer`.
- El listado de **grupos de endpoints (tags)**: `auth`, `archivos`, `energia`, `errores`, `stats`, `usuarios`, `clientes`, etc.

---

### 1. Autenticación (`auth`)

**Objetivo**: obtener un `access_token` JWT y comprobar los datos del usuario logueado.

- **POST `/api/v1/auth/login`**
  - Cuerpo (`application/json`):
    - `username`: p.ej. `"admin"`
    - `password`: p.ej. `"admin123"`
  - Respuesta esperada `200`:
    - `access_token`: string JWT.
    - `token_type`: `"bearer"`.
    - `user`: objeto con `id`, `username`, `email`, `rol`, etc.
  - Verificación:
    1. En Swagger, despliega `auth` → `POST /api/v1/auth/login` → **Try it out**.
    2. Envía un JSON válido.
    3. Comprueba que devuelve `200` y un `access_token`.

- **POST `/api/v1/auth/login/form`**
  - Pensado para OAuth2 desde Swagger (form-data).
  - Similar al anterior pero usando campos de formulario `username` y `password`.

- **GET `/api/v1/auth/me`**
  - Protegido: requiere token.
  - Verificación:
    1. Haz login (endpoint anterior) y copia el `access_token`.
    2. En Swagger, pulsa **Authorize** y pega el token (sin `Bearer`).
    3. Ejecuta `GET /api/v1/auth/me`.
    4. Debe responder `200` con la info del usuario actual.

- **POST `/api/v1/auth/change-password`**
  - Cambia la contraseña del usuario actual (requiere token).
  - Verificación:
    1. Haz login y autoriza Swagger con el token.
    2. Envía JSON con:
       - `current_password`: contraseña actual.
       - `new_password`: nueva contraseña.
    3. Debe responder `200` con mensaje de éxito.

---

### 2. Archivos (`archivos`)

**Objetivo**: subir archivos XML/CSV/TXT de energía y ver su estado/errores.

- **GET `/api/v1/archivos`**
  - Parámetros:
    - `limit` (query, opcional, por defecto 20): máximo de archivos a devolver.
  - Respuesta: lista de archivos procesados, ordenados del más reciente al más antiguo.
  - Verificación:
    - Ejecuta sin parámetros.
    - Debe devolver lista (posiblemente vacía) con campos como `id`, `nombre_archivo`, `estado`, `registros_exitosos`, etc.

- **POST `/api/v1/archivos/upload`**
  - Sube un archivo para procesar en background (Celery o hilo).
  - Parámetros:
    - `file` (form-data, tipo file): el archivo a subir.
    - `usuario_id` (form-data, opcional, por defecto 1): ID de usuario que sube el archivo.
  - Respuesta `202`:
    - `archivo_id`, `nombre_archivo`, `estado="pendiente"`, `mensaje`.
  - Verificación:
    1. En Swagger, en la sección `archivos`, abre `POST /api/v1/archivos/upload`.
    2. **Try it out** → selecciona un archivo de prueba (ej. alguno de `backend/uploads/`).
    3. Envía la petición y comprueba que devuelve `202` y un `archivo_id`.

- **GET `/api/v1/archivos/{archivo_id}`**
  - Consulta el estado de un archivo concreto.
  - Parámetros:
    - `archivo_id` (path): ID devuelto por el upload.
  - Verificación:
    1. Usa el `archivo_id` devuelto por el upload anterior.
    2. Ejecuta el GET.
    3. Observa el campo `estado` (`pendiente`, `procesando`, `completado`, `error`) y los contadores de registros.

---

### 3. Energía (`energia`)

**Objetivo**: consultar registros de energía excedentaria con filtros.

- **GET `/api/v1/energia`**
  - Parámetros de query (todos opcionales):
    - `cups`: filtrar por CUPS del cliente.
    - `fecha_desde`, `fecha_hasta`: rangos de fechas.
    - `tipo_autoconsumo`: código (12, 41, 42, 43, 51, etc.).
    - `archivo_id`: ver solo los registros OK de un archivo concreto.
  - Respuesta:
    - `total`: número de registros devueltos.
    - `registros`: lista de registros con campos como `cups_cliente`, `fecha_desde`, `total_neta_gen`, `total_autoconsumida`, `total_pago`, etc.
  - Verificación:
    1. Ejecuta sin parámetros → comprueba que devuelve datos de prueba (si has corrido `init_db.py`).
    2. Vuelve a probar con `archivo_id` de un archivo real.
    3. Usa `cups` de un cliente existente para ver el filtrado.

---

### 4. Errores (`errores`)

**Objetivo**: ver los errores detectados en el procesamiento de un archivo.

- **GET `/api/v1/errores/{archivo_id}`**
  - Parámetro:
    - `archivo_id` (path): ID de archivo.
  - Respuesta:
    - Lista de errores con `id`, `linea_archivo`, `tipo_error`, `descripcion`, etc.
  - Verificación:
    1. Sube un archivo con errores (o usa los de prueba).
    2. Llama a este endpoint con su `archivo_id`.
    3. Debes ver las filas de error asociadas a ese archivo.

---

### 5. Estadísticas (`stats`)

**Objetivo**: obtener un resumen global para el dashboard.

- **GET `/api/v1/stats`**
  - Sin parámetros.
  - Respuesta:
    - `total_archivos`, `total_registros_energia`, `total_errores`, etc.
  - Verificación:
    - Ejecuta el GET y comprueba que los números cuadran con lo que ves en el dashboard del frontend (`Dashboard.jsx`).

---

### 6. Usuarios (`usuarios`)

**Objetivo**: gestionar y consultar usuarios de la aplicación.

- **GET `/api/v1/usuarios`**
  - Parámetros:
    - `skip`, `limit`: paginación.
    - `activo` (bool, opcional): filtrar por activos/inactivos.
  - Verificación:
    - Ejecuta con y sin `activo` y revisa que los recuentos cambien según el filtro.

- **GET `/api/v1/usuarios/{usuario_id}`**
  - Devuelve los datos de un usuario específico.

- **POST `/api/v1/usuarios`**
  - Crea un usuario nuevo.
  - Cuerpo:
    - Campos definidos en `UsuarioCreate` (incluye `username`, `email`, `nombre_completo`, `rol`, `activo`, `password_hash`).
    - En un entorno real, lo ideal es enviar `password` plano y hashearlo en servidor, pero actualmente este esquema espera el hash.
  - Verificación:
    1. Crea un usuario de prueba.
    2. Luego recupéralo con `GET /api/v1/usuarios` o `GET /api/v1/usuarios/{id}`.

- **PUT `/api/v1/usuarios/{usuario_id}`**
  - Actualiza campos existentes de un usuario (rol, activo, etc.).

- **DELETE `/api/v1/usuarios/{usuario_id}`**
  - “Borrado lógico”: marca `activo = False`.

- **GET `/api/v1/usuarios/stats/resumen`**
  - Devuelve:
    - `total`, `activos`, `inactivos`, y un diccionario `por_rol`.
  - Verificación:
    - Comprueba que coincide con los datos mostrados en el dashboard (tarjeta de **Usuarios activos**).

---

### 7. Clientes (`clientes`)

**Objetivo**: gestionar clientes y sus puntos de suministro (CUPS) y ver su energía asociada.

- **GET `/api/v1/clientes`**
  - Filtros:
    - `activo`, `municipio`, `provincia`, `skip`, `limit`.
  - Verificación:
    - Ejecuta sin filtros y luego probando por `municipio`/`provincia`.

- **GET `/api/v1/clientes/{cliente_id}`**
  - Devuelve un cliente por ID.

- **GET `/api/v1/clientes/cups/{cups}`**
  - Busca un cliente por su CUPS.

- **POST `/api/v1/clientes`**
  - Crea cliente nuevo (valida que el CUPS no exista).

- **PUT `/api/v1/clientes/{cliente_id}`**
  - Actualiza datos de un cliente.

- **DELETE `/api/v1/clientes/{cliente_id}`**
  - Marcado como inactivo (soft delete).

- **GET `/api/v1/clientes/stats/resumen`**
  - Devuelve:
    - `total`, `activos`, `inactivos`, `por_provincia`.

- **GET `/api/v1/clientes/{cliente_id}/energia`**
  - Devuelve el cliente más estadísticas agregadas de energía:
    - `total_registros`, `total_energia_generada`, `total_energia_autoconsumida`, `total_pago_tda`.
  - Verificación:
    1. Ejecuta con un `cliente_id` que tenga registros de energía (de los de prueba).
    2. Comprueba que los totales coinciden con lo que ves en el frontend (por ejemplo en `DataViewer` o en la vista de cliente si la conectas).

---

### 8. Cómo verificar “de punta a punta” con Swagger

1. **Arranca backend y BD** (con Docker o localmente).
2. Abre `http://localhost:8000/docs`.
3. **Login** con `POST /api/v1/auth/login` (`admin` / `admin123`).
4. Pulsa **Authorize** y pega el token.
5. Sube un archivo en `POST /api/v1/archivos/upload`.
6. Consulta su estado en `GET /api/v1/archivos/{archivo_id}`.
7. Mira sus registros OK en `GET /api/v1/energia?archivo_id=...`.
8. Mira sus errores en `GET /api/v1/errores/{archivo_id}`.
9. Consulta estadísticas globales en `GET /api/v1/stats`, `GET /api/v1/usuarios/stats/resumen` y `GET /api/v1/clientes/stats/resumen`.

Si todas estas peticiones funcionan desde Swagger, tienes comprobado que **la API está bien configurada y responde correctamente** para todos los apartados principales.

