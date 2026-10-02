# Decisión 019 — Semilla de la API (FastAPI) para desplegar y medir el plan gratuito de Render

**Fecha:** 1 de octubre de 2026
**Estado:** vigente (decisión de Valentín)
**Afecta a:** tarea 4.5.4 (`docs/plan-desarrollo.md`) · Etapa 6 completa (API y procesamiento asincrónico,
construye sobre esta base, no la reemplaza) · apartado 4.2.5 y 4.4.2 de la tesis

---

## El problema

La tarea 4.5.3 dejó `app/procesar_video.py` como un script invocable por línea de comandos
(`python -m app.procesar_video <video_id>`). Eso alcanza para medir y probar localmente, pero no para
desplegar en Render: el hallazgo de la decisión 018 sobre el plan gratuito (0,1 vCPU, sin tipo de servicio
"Background Worker") obliga a envolver el motor en un servidor HTTP real para poder siquiera probarlo gratis.

## Decisión: no es un wrapper descartable, es la semilla de la Etapa 6

En vez de escribir el mínimo HTTP indispensable para la medición de hoy, se construye sobre la estructura ya
prevista por la decisión 003 (`backend/app/{main.py, security.py, routers/, workers/}`, vacía desde la Etapa
0) con cuatro condiciones de Valentín:

### 1. Endpoint protegido por token, con verificación de servicio pública aparte

`GET /health` (sin autenticación, apartado 4.2.5 "Verificación de servicio"): devuelve solo `estado` y
`version_motor`, nada más. `POST /analisis/{video_id}/procesar` (protegido): exige el header
`X-Kinetiq-Token` igual a la variable de entorno `KINETIQ_API_TOKEN`, comparado con
`secrets.compare_digest` (tiempo constante). Sin la variable configurada en el servidor, 500 (error de
configuración, no se confunde con "token inválido"); con la variable pero sin header o con uno distinto, 401.

**No es la autenticación real de usuario (Supabase Auth, tarea 7.4).** Vive en `backend/app/security.py`
exactamente para que ese día el reemplazo sea evidente: se cambia `verificar_token`, no conviven las dos.

### 2. Responde 202 de inmediato, procesa en segundo plano

`POST /analisis/{video_id}/procesar` marca `videos.estado = 'encolado'`, encola un `BackgroundTasks` de
FastAPI con `app/workers/procesamiento.py::procesar_en_segundo_plano` (que llama a `procesar_video`, ya
escrito en la 4.5.3) y responde 202 sin esperar a que termine. Es la decisión de MVP del apartado 4.4.2 de la
tesis (sin cola externa, mecanismo de `BackgroundTasks` + campo de estado) aplicada un hito antes de la
Etapa 6, porque es también la medición real que pide esta tarea: contra el plan gratuito de Render, si la
suspensión por inactividad corta el proceso de fondo mientras sigue corriendo, el video queda "procesando"
para siempre — eso es lo que hay que ver pasar (o no) contra el servicio desplegado, no algo simulable en
local. La mitigación (tarea 6.5, reencolar al arrancar lo que quedó en "procesando") queda explícitamente
pendiente, no es parte de esta semilla.

### 3. Ningún secreto en el repo

`render.yaml` (raíz del repo) declara `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` y `KINETIQ_API_TOKEN` con
`sync: false`: Render los pide al aplicar el blueprint, pero no los guarda el archivo ni el repo. Se cargan
a mano en el panel de Render (instrucciones en la bitácora de esta sesión y repetidas al pie de esta
decisión). El `Dockerfile` no cambia su mecanismo de configuración (sigue leyendo variables de entorno, igual
que `backend/app/config.py` ya hacía para Supabase desde la tarea 4.5.1).

### 4. Estructura reutilizable, no tirada

```
backend/app/
├── main.py                      # FastAPI(), incluye los routers
├── security.py                  # verificar_token() + get_admin_client()
├── schemas/api.py                # RespuestaSalud, RespuestaAnalisisEncolado (Pydantic)
├── routers/
│   ├── salud.py                  # GET /health
│   └── analisis.py               # POST /analisis/{video_id}/procesar
└── workers/
    └── procesamiento.py          # wrapper de procesar_video para BackgroundTasks
```

Es exactamente el árbol que la decisión 003 reservó para la Etapa 6 (`main.py`, `security.py`, `routers/`,
`workers/`, hasta ahora con solo `.gitkeep`). Las cinco operaciones restantes del apartado 4.2.5 (alta de
análisis, consulta de estado, reporte, listado, evolución) se agregan sobre esta misma base en la Etapa 6
propiamente dicha — agregar routers, no reorganizar nada.

## Comando de producción del contenedor

`backend/Dockerfile` pasa de `CMD ["bash"]` (abierto, sin definir, desde la tarea 4.5.3) a
`CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` — forma shell (no exec) a propósito, para que
`$PORT` se expanda (Render lo inyecta en tiempo de ejecución; si no está, cae a 8000 para `docker run` local).
La medición de tiempo/memoria de la tarea 4.5.3 sigue disponible aparte:
`docker run --entrypoint python <imagen> -m app.medir_contenedor ...`.

## Medición instrumentada desde adentro, no a ojo del panel

`app/procesar_video.py` ahora mide tiempo total y RSS pico con el mismo método que `medir_contenedor.py`
(decisión 017, `resource.getrusage`) y lo imprime en el log al terminar cada análisis. Así la medición real
que pide esta tarea (tiempo por golpe, memoria pico, contra el plan gratuito de Render) sale del log del
servicio desplegado, no de una lectura aparte del panel de métricas de Render — mismo principio de medir
desde dentro del proceso que ya justificó `medir_contenedor.py`.

## No verificado en Docker local antes de este despliegue

Docker Desktop no estaba corriendo en esta sesión (ver la tarea 4.5.3); no se insistió en levantarlo porque
el propio despliegue en Render construye la imagen y reporta cualquier error del `Dockerfile` en su log de
build — es una verificación real, no redundante con una local.

## Qué falta (pasos para Valentín)

1. Generar `KINETIQ_API_TOKEN`: cualquier cadena larga al azar, por ejemplo
   `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Guardarlo en algún lado (gestor de
   contraseñas); no hay que recordarlo de memoria, pero si se pierde se genera uno nuevo y se recarga en
   Render.
2. Conectar el repositorio a Render con el blueprint (`render.yaml` en la raíz) — pasos exactos en la
   bitácora de esta sesión y en el mensaje de cierre de la tarea 4.5.4.
3. Cargar a mano, en el panel de Render → el servicio `kinetiq-motor` → **Environment**: `SUPABASE_URL`,
   `SUPABASE_SERVICE_ROLE_KEY` (las mismas de `backend/.env`) y `KINETIQ_API_TOKEN` (el generado en el
   paso 1).
4. Confirmar `GET /health` (sin token) y disparar un análisis real con `POST /analisis/<video_id>/procesar`
   (con el header `X-Kinetiq-Token`), con un video ya cargado a Storage y registrado en `videos` — se puede
   insertar esa fila a mano, igual que hacen las pruebas de integración de la tarea 4.5.3.
5. Leer el log del servicio en Render para los números de tiempo/RSS pico, y observar si la suspensión por
   inactividad del plan gratis corta un análisis en curso. Si no cumple (más de 10 minutos por golpe, o la
   suspensión corta un análisis), pasar a Starter y actualizar `render.yaml` (`plan: starter`) y la decisión
   017 con los números reales.
