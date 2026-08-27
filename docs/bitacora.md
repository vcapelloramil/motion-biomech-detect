# Bitácora de desarrollo

Registro de cierre de cada sesión de trabajo con Claude Code. Una entrada por sesión, la
más reciente arriba. Cada entrada anota: **qué se hizo**, **qué quedó pendiente** y el
**siguiente paso concreto**.

---

## 2026-08-26 (sesión 2) — Etapa 1: Ingesta y validación de FPS

**Rama:** `etapa/1-ingesta` (desde `etapa/0-fundaciones`, todavía sin merge a `main`).
**Modelo:** Sonnet 5 Medio.

Antes de planificar se leyeron los apartados de tesis que sustentan la etapa
(`capitulo-3`: 3.3.1.1, 3.4.2.2, y 3.3.4.2) y se releyó `decisiones/001`, según la
convención fijada.

### Qué se hizo

- **1.1 / 1.2 / 1.3 · `engine/ingest.py`.** Núcleo puro separado de la entrada/salida:
  - `clasificar_fps()` — tabla de aptitud (≥240 completo, 120–239 reducido, 60–119 solo
    preparación, <60 rechazado).
  - `evaluar()` — `fps_efectivos = fps_declarados × factor`; propaga la frecuencia de
    **captura**, nunca la de reproducción. El factor es externo (catálogo o manual).
    `<60` devuelve un resultado con `motivo_rechazo`, no una excepción.
  - `detectar_inconsistencias()` — contrasta tasa declarada vs `nb_frames/duración` vs
    `avg_frame_rate` (verificación 1 de la decisión 001).
  - `probe()` — OpenCV + enriquecimiento con `ffprobe` si está. Archivo corrupto →
    `IngestaError`, sin crash.
  - `iterar_fotogramas()` — generador, memoria constante (tarea 1.4).
- **Decisión 001 en código · `engine/framehash.py`.** `ratio_fotogramas_unicos()` por
  huella md5 exacta sobre la ventana central (no `mpdecimate`). `interpretar_ratio()` →
  `captura_real` / `repeticion_aislada` / `duplicacion_sistematica`.
- **1.5 · `app/catalogador.py`.** `python -m app.catalogador` (desde `backend/`).
  Recorre el corpus, toma el factor del `catalogo.csv`, combina las dos verificaciones
  en un "uso" final, escribe `catalogo-verificado.csv`. **No toca `catalogo.csv`.**
  `--sin-hash` para una pasada rápida. Detectó que las 4 filas de `catalogo.csv` tienen
  13 columnas en vez de 14 (fila mal formada): lo reporta y no cruza semánticamente
  contra esas filas.
- **Contrato.** Se agregó `escala_temporal_conocida: bool` (obligatorio) a
  `Trazabilidad` en `schemas/reporte.py` + ejemplo JSON. Cambio al contrato de la
  Etapa 0, hecho antes de integrar nada a `main`. Registrado en decisión 004.
- **Versión del motor** → `0.1.0`.
- **Decisión 004** (`docs/decisiones/004-ingesta-fps-y-verificacion.md`), `arquitectura.md`
  y `backend/README.md` actualizados (ffmpeg como dependencia del catalogador, cómo
  correr el catalogador).

### Criterio de aceptación de la Etapa 1

| Punto | Estado |
| --- | --- |
| Archivos de 30/60/120/240 fps devuelven su tasa real | ✅ (test de integración con clips ffmpeg) |
| Clip ralentizado (240 exportado a 30, factor 8) resuelve a 240 efectivos | ✅ |
| Prueba de coherencia temporal (240 vs ralentizado: misma duración real) | ✅ **sintética** |
| Metadatos inconsistentes se detectan y advierten | ✅ |
| Archivo corrupto / formato no soportado: error claro sin caída | ✅ |
| Video 240 fps / 20 s: la iteración no acumula memoria | ✅ (`tracemalloc`, pico <100 MB) |
| El catalogador procesa la Fase A completa sin errores y clasifica cada clip | ✅ (`test_corpus_fase_a.py`, marcado `slow`, ~3–4 min) |
| Toda la lógica sobre la frecuencia efectiva, no la declarada | ✅ |

Corrida real del catalogador sobre `kinetiq-data/fase-a/`: los 3 segmentos de Zverev
(+ la compilación `sideview`) → `fps_efectivos 500`, `escala_temporal_conocida = False`,
`ratio_unicidad ≈ 1.0` (`captura_real`), `uso = E1-E4`.

### Pruebas

`pytest -m "not slow"` → **54 en verde** (incluye las 12 de la Etapa 0). Las 3 de
`test_corpus_fase_a.py` (`slow`) pasan sobre el material real (~3,7 min).

### Pendiente

- **PENDIENTE DE REEMPLAZO OBLIGATORIO:** todas las pruebas de integración de esta etapa
  usan clips sintéticos generados con ffmpeg (`tests/video_fixtures.py`) porque no hay
  material de control propio todavía. Cuando se suba el bloque de control del protocolo
  (30/60 fps, oclusión, cuerpo fuera de cuadro), esas pruebas pasan a usar el material
  real y las sintéticas se retiran — no conviven.
- La prueba de coherencia temporal necesita además un par real 240 fps + su ralentizado
  del mismo gesto (Fase B).
- `catalogo.csv` tiene las 4 filas con una columna de menos. No se toca desde acá (es de
  Valentín); el catalogador ya lo reporta en cada corrida.
- Hash md5 por fotograma sobre 1080p: ~1 min por clip de 30 s. Aceptable como
  herramienta offline; si el corpus crece, submuestrear la ventana.
- Integrar `etapa/1-ingesta` a `main` y etiquetar `v0.2.0-etapa1` — **pendiente del OK
  de Valentín** (la definición de terminado del plan pide integración + etiqueta).
- Sigue pendiente de la Etapa 0: decidir si `ajuste-tesis` se integra a `main`;
  `.gitattributes` con `eol=lf`.

### Siguiente paso concreto

Abrir la **Etapa 2 — Estimación de pose** (`docs/plan-desarrollo.md`). Por la
convención: antes de pedir el plan, leer `capitulo-3` apartados 3.3.2.3 a 3.3.2.9 (por
qué YOLOv8-Pose es 2D, MediaPipe como backend por defecto, tabla de error por
articulación) y el apartado 4.4.3 del `capitulo-4`. La Etapa 2 consume la salida de la
ingesta sobre los segmentos de Zverev.

---

## 2026-08-26 — Etapa 0: Fundaciones (tareas 0.1–0.4, 0.6, 0.7)

**Rama:** `etapa/0-fundaciones` (desde `4c954e8`). `main` sin tocar.

### Qué se hizo

- **Línea de base.** Primer commit (`10e1cb1`) consolidando el trabajo que vivía solo en el
  árbol de trabajo de `ajuste-tesis`: `CLAUDE.md`, `docs/` completo (plan, protocolo,
  decisión 001, capítulos 3 y 4 de la tesis) y los ajustes del prototipo Lovable. La rama
  `ajuste-tesis` queda intacta en `4c954e8`; qué se hace con ese contenido se decide en otra
  sesión.
- **0.4 · Higiene de git.** `.gitignore` ampliado: entornos virtuales, `__pycache__`,
  `.env` (se versiona solo `.env.example`), archivos de video, `package-lock.json` (el
  frontend usa bun; se descarta el lockfile de npm).
- **0.1 · Monorepo.** Todo el proyecto Lovable movido a `frontend/` con `git mv` (conserva
  historial). Creado el esqueleto `backend/`, `supabase/`, `tests/`, `.github/workflows/`
  según el apartado 4.3.5 de la tesis, transcripto en
  `docs/decisiones/003-estructura-monorepo.md`. El frontend **levanta y compila** desde la
  nueva ubicación (`bun run dev` y `bun run build` verificados).
- **0.2 · Entorno Python.** venv en `backend/.venv` creado con **`py -3.11`**.
  `requirements.txt` con versiones fijadas. **mediapipe instala y ejecuta en esta máquina**
  (CPU/XNNPACK; la GTX 1050ti no la usa la API de Python de mediapipe). Dos ajustes que
  hicieron falta:
  - `numpy` bajado a `1.26.4` porque mediapipe exige `numpy<2`.
  - Se usa `opencv-contrib-python` (no `opencv-python`): mediapipe depende de contrib, y
    tener las dos instaladas rompe el import de `cv2`.
- **Config de la ruta del corpus** (regla de arquitectura de esta sesión).
  `backend/app/config.py` → `get_data_dir()` lee `KINETIQ_DATA_DIR` del entorno o de
  `backend/.env`. Sin valor por defecto: si falta, error claro. `backend/.env` creado local
  (ignorado), `backend/.env.example` versionado. Decisión en
  `docs/decisiones/002-config-ruta-corpus.md`.
- **0.3 · Contrato del reporte congelado.** `backend/app/schemas/reporte.py` (Pydantic v2,
  `extra="forbid"`) transcribe el Anexo A. Ejemplo válido en
  `docs/contrato-reporte.ejemplo.json`.
- **0.6 · Decisiones.** `docs/decisiones/README.md` (plantilla + índice), ADR 002 y 003
  nuevas, ADR 001 corregida (venía con el markdown escapado y no renderizaba).
- **0.7 · Bitácora.** Este archivo.
- **Pruebas.** `pytest` → **12 pruebas en verde**: smoke, validación del contrato contra el
  ejemplo (y rechazo de datos mal formados), y resolución de `KINETIQ_DATA_DIR`.

### Criterio de aceptación de la Etapa 0

| Punto | Estado |
| --- | --- |
| `pytest` corre sin errores sobre una prueba trivial | ✅ 12/12 |
| El contrato del reporte valida un ejemplo ficticio | ✅ |
| El proyecto frontend levanta desde su nueva ubicación | ✅ `dev` y `build` |
| Corpus Fase A completo y verificado | ⏳ fuera de este chat (tarea 0.5, en curso) |
| Fase B agendada y equipo de captura probado | ⏳ fuera de este chat (hito C1, límite 22/9) |

### Pendiente

- **Detalle a no olvidar:** el `python` del sistema es 3.14; el venv se crea **siempre** con
  `py -3.11`. Anotado también en `backend/README.md`.
- Decidir en otra sesión si el contenido de `ajuste-tesis` se integra a `main`.
- Integrar `etapa/0-fundaciones` a `main` y etiquetar (`v0.1.0-etapa1` corresponde a la E1;
  para el cierre de E0 se puede usar `v0.1.0-etapa0` si se quiere un punto de retorno).
- `.gitattributes` con `eol=lf`: git avisa de conversiones CRLF/LF en Windows. No es
  urgente pero conviene fijarlo antes de que se sumen colaboradores.
- Revisar con Valentín el encabezado de `catalogo.csv` (no tiene columnas propias para
  "verificado por huella" ni "etapas"): lo formaliza el catalogador de la Etapa 1 (tarea 1.5).

### Siguiente paso concreto

Abrir la **Etapa 1 — Ingesta y validación de FPS** (`docs/plan-desarrollo.md`). Antes de
pedir el plan de esa etapa, leer el apartado de la tesis que cita su sección "Por qué"
(convención fijada esta sesión). La Etapa 1 trabaja sobre los 3 segmentos de Zverev ya
catalogados en `kinetiq-data/fase-a/segmentos/`.
