# KinetiQ

Sistema web que mide la técnica de un golpe de tenis (saque, drive y revés) a partir de un video
grabado en cámara lenta con un celular, para jugadores de club, entrenadores y kinesiólogos.

Proyecto Final de Ingeniería en Informática, Facultad de Ingeniería, Universidad del Salvador (2026).
Autor: **Valentín Capello Ramil**.

- **Sistema en producción:** <https://kinetiqtennis.me>
- **Versión entregada:** etiqueta `entrega-final` (motor `0.5.5`, contrato del reporte `1.4`).

El sistema estima la pose del jugador cuadro a cuadro, lee la tasa real de captura del archivo, filtra
la señal sin desplazarla en el tiempo y calcula ángulos articulares, la separación entre cadera y
hombros y el instante en que cadera, tronco y brazo alcanzan su velocidad máxima. **Documenta lo que
mide, con su confianza y la versión del motor que lo produjo; no diagnostica, no predice lesiones ni
emite veredictos sobre la técnica** (ver `CLAUDE.md`, regla R2).

## Arquitectura

```
Navegador → Interfaz (React + TanStack Start, en Cloudflare Workers)
          → API y motor (FastAPI + MediaPipe, contenedor Docker en Render)
          → Supabase (PostgreSQL con RLS, autenticación y almacenamiento de videos)
```

| Carpeta | Contenido |
| --- | --- |
| `frontend/` | Interfaz web (TanStack Start, React 19, Tailwind 4, shadcn/ui). |
| `backend/` | Motor biomecánico (`app/engine/`), API FastAPI (`app/main.py`) y `Dockerfile` del contenedor. |
| `supabase/` | Migraciones SQL (esquema, políticas RLS, buckets) y plantillas de correo. |
| `tests/` | Pruebas del servidor y del motor (pytest), con generadores de clips sintéticos. |
| `tools/` | Utilidades: respaldo y restauración de la base, armado de pruebas desde el iPhone. |
| `docs/` | Plan, decisiones de arquitectura, bitácora, resultados medidos y guion de la demo. |
| `render.yaml` | Definición del servicio en Render (sin secretos). |

## Requisitos

- **Python 3.11** (MediaPipe no soporta versiones más nuevas y exige `numpy<2`).
- **ffmpeg y ffprobe** en el `PATH` (lectura de metadatos y artefactos del reporte).
- **Bun 1.x** (o Node 20) para la interfaz.
- Una cuenta de **Supabase** (el plan gratuito alcanza) y, para publicar, cuentas de **Render** y **Cloudflare**.
- Docker, opcional, para correr el contenedor del motor igual que en producción.

## Instalación

```bash
git clone https://github.com/vcapelloramil/motion-biomech-detect.git
cd motion-biomech-detect

# Servidor y motor
python3.11 -m venv backend/.venv          # en Windows: py -3.11 -m venv backend/.venv
source backend/.venv/bin/activate         # en Windows: backend\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt -r backend/requirements-dev.txt

# Interfaz
cd frontend && bun install && cd ..
```

## Configuración

1. **Base de datos.** Crear un proyecto en Supabase y aplicar, en orden de fecha, los archivos de
   `supabase/migrations/` desde el *SQL Editor* del panel. Crean las tablas, las políticas RLS y los
   buckets privados de videos y artefactos.
2. **Variables de entorno.** Copiar los ejemplos y completar los valores del panel de Supabase
   (*Project Settings → API*):

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

| Variable | Dónde | Qué es |
| --- | --- | --- |
| `SUPABASE_URL` | `backend/.env` | URL del proyecto (pública). |
| `SUPABASE_SERVICE_ROLE_KEY` | `backend/.env` | Clave **secreta** del servidor. Nunca va a la interfaz ni al repositorio. |
| `SUPABASE_ANON_KEY` | `backend/.env` | Clave pública; la usan las pruebas de aislamiento de RLS. |
| `KINETIQ_CORS_ORIGINS` | `backend/.env` | Orígenes de la interfaz habilitados, separados por comas. |
| `KINETIQ_DATA_DIR` | `backend/.env` | Opcional: carpeta del corpus de video, fuera del repositorio. |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | `frontend/.env` | Mismos valores públicos, para la interfaz. |
| `VITE_API_URL` | `frontend/.env` | URL de la API (local: `http://localhost:8000`). |

Los archivos `.env` están en `.gitignore`. Cada `.env.example` documenta el resto de las variables opcionales.

## Ejecución local

```bash
# Terminal 1: API y motor (desde backend/, con el entorno virtual activado)
cd backend
uvicorn app.main:app --reload --port 8000      # http://localhost:8000/health

# Terminal 2: interfaz
cd frontend
bun run dev                                    # la URL aparece en la consola
```

Para usar el sistema: registrarse en la interfaz, confirmar el correo e ir a **Cargar**. El video
tiene que estar grabado a **120 fps o más** (240 recomendado) y con el jugador de cuerpo entero; el
sistema lee la tasa real del archivo y rechaza los videos convertidos por el teléfono.

Con Docker, el motor corre igual que en Render:

```bash
docker build -t kinetiq-motor backend
docker run --rm -p 8000:8000 --env-file backend/.env kinetiq-motor
```

## Pruebas

```bash
# desde la raíz, con el entorno virtual activado
pytest -m "not slow"     # pruebas rápidas; los clips de prueba se generan con ffmpeg
pytest                   # todas; las que usan el corpus real se saltan si no hay KINETIQ_DATA_DIR

cd frontend && bun test     # pruebas de la interfaz (bun:test)
```

Los videos del corpus propio **no están en el repositorio** porque contienen datos personales
(Ley 25.326). Las pruebas que los necesitan se saltan solas. Las cifras medidas con ellos están en
`docs/resultados/`.

## Despliegue

- **Motor:** servicio Docker en Render definido en `render.yaml` (plan Standard, 1 CPU y 2 GB). Los
  secretos se cargan en el panel de Render, no en el archivo.
- **Interfaz:** `bun run build` y `wrangler deploy` desde `frontend/` (Cloudflare Workers).
- Pasos, prueba de humo y vuelta atrás: `docs/publicacion-y-vuelta-atras.md`. Respaldo de la base:
  `docs/respaldo-y-restauracion.md`.

## Documentación

| Archivo | Qué es |
| --- | --- |
| `CLAUDE.md` | Reglas del proyecto (tasa mínima, vocabulario, trazabilidad, alcance). |
| `docs/arquitectura.md` | Arquitectura del sistema. |
| `docs/decisiones/` | Registro de las decisiones de diseño, con fecha y motivo. |
| `docs/bitacora.md` | Qué se hizo en cada sesión de trabajo. |
| `docs/resultados/` | Mediciones de los criterios de éxito. |
| `docs/protocolo-grabacion.md` | Cómo grabar un golpe para que sea medible. |
| `docs/demo-guion.md` | Guion de la demostración. |

## Uso de inteligencia artificial

Parte del código y de la documentación se escribió con asistentes de IA (Claude Code, Anthropic) a
partir de instrucciones del autor, que tomó las decisiones de diseño y verificó los resultados. El
detalle está en la declaración de uso de IA del documento de la tesis.

## Licencia

Código publicado bajo la licencia MIT (ver `LICENSE`). Los videos y los datos de los jugadores no
forman parte del repositorio ni de la licencia.
