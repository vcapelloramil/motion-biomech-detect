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
| El catalogador procesa la Fase A completa sin errores y clasifica cada clip | ✅ lee y clasifica los 12; marca las inconsistencias del `catalogo.csv` (ver abajo) |
| Toda la lógica sobre la frecuencia efectiva, no la declarada | ✅ |

Corrida real del catalogador sobre `kinetiq-data/fase-a/` (12 clips, `compilaciones/`
excluida): 5 gestos en cámara lenta → `fps_efectivos` 500/480/300,
`escala_temporal_conocida = False`, `ratio_unicidad ≈ 1.0` (`captura_real`), `uso = E1-E4`;
4 controles a 30 fps → `rechazado`; 3 a 60 fps → `solo preparación`.

### Pruebas

`pytest -m "not slow"` → **64 en verde** (incluye las 12 de la Etapa 0). `-m slow` →
4 pasan sobre el material real + 1 `xfail` (catálogo con inconsistencias, ver abajo).
~2 min.

### Pendiente

- Sigue con la única prueba sintética sin equivalente real: duplicación sistemática de
  fotogramas (ningún clip real la tiene) y el par de coherencia temporal 240 vs
  ralentizado (depende de la Fase B, plazo 22/9). Marcadas en el código.
- Hash md5 por fotograma sobre 1080p: ~1 min por clip de 30 s. Aceptable como
  herramienta offline; si el corpus crece, submuestrear la ventana.
- `.gitattributes` con `eol=lf` (arrastre de la Etapa 0).

### Correcciones tras la revisión (misma sesión)

El corpus de la Fase A se amplió a **12 clips reales** (3 saques + 1 drive + 1 revés en
cámara lenta; 7 de control: 4 a 30 fps, 3 a 60 fps, con oclusión en varios). Al correr
el catalogador sobre el corpus nuevo aparecieron dos bugs propios, ya arreglados:

- **Tasas NTSC.** `59.94` fps (= 60000/1001) quedaba por debajo del umbral de 60 y se
  rechazaba por redondeo. Se agregó `normalizar_fps()`: ajusta a la tasa nominal si cae
  a <0.5%. Ahora `59.94 → 60 → solo preparación`, `29.97 → 30 → rechazado`.
- **Material de origen.** El catalogador escaneaba `fase-a/compilaciones/` (videos largos
  de los que se recortan los segmentos). Ahora salta `compilaciones/` por defecto
  (`--incluir-todo` para no saltearla).
- Alineado el vocabulario: `SOLO_PREPARACION` → `uso = "E1-E2 (solo preparacion)"`
  (**sin tilde**, por pedido de Valentín: es un token que viaja al CSV y se compara
  contra `catalogo.csv`; se mantiene ASCII para no depender de la codificación de la
  consola en Windows/Git Bash). Barrido del resto del código: los otros usos de la
  palabra con tilde son comentarios y prosa de docs (se dejan con ortografía correcta);
  la única otra cadena *generada* era `motivo_rechazo` en `ingest.py`, ya pasada a ASCII.
- El catalogador ahora reporta filas del `catalogo.csv` que no tienen archivo.

**Pruebas sintéticas retiradas** (había material real equivalente): parámetros 30/60 fps
de `test_ingest_video.py`. Se mantienen las sintéticas que no tienen equivalente real:
duplicación sistemática de fotogramas (ningún clip real la tiene) y el par de coherencia
temporal 240 vs ralentizado (depende de la Fase B, plazo 22/9).

`test_corpus_fase_a.py` reescrita contra los 12 clips reales: 5 gestos aptos E1-E4
(`escala_temporal_conocida = False`, sin duplicación), controles de 30 fps → rechazado,
de 60 fps → solo preparación.

### Cierre del `catalogo.csv` y merge

Valentín arregló el `catalogo.csv`: renombró la fila fantasma a
`control_reves_30fps_01.mp4`, quitó la fila de `zverev_saque_sideview.mp4` (compilación),
y puso `uso = rechazado` en los 4 controles a 30 fps. Quedan **12 filas parejas**.

`python -m app.catalogador` sobre el corpus final: **sin avisos globales, sin
inconsistencias**. Los únicos avisos por clip son las notas informativas de
normalización NTSC (`29.97 → 30`, `59.94 → 60`). Resultado:

| grupo | clips | uso |
| --- | --- | --- |
| gestos en cámara lenta | zverev ×3 (500 fps ef.), drive_lateral_01 (480), reves_lateral_01 (300) | `E1-E4`, `escala_temporal_conocida=False`, `captura_real` |
| control 60 fps | control_rally_60fps_01/02, control_oclusion_03 | `E1-E2 (solo preparacion)` |
| control 30 fps | control_drive_30fps_01, control_reves_30fps_01/02, control_oclusion_02 | `rechazado` |

Se quitó el `xfail` de `test_el_catalogo_no_tiene_inconsistencias` (ahora pasa como
prueba real). `pytest -m "not slow"` → 64 en verde; `-m slow` → 5 en verde.

**Merge hecho:** `etapa/0-fundaciones` → `main`, etiqueta `v0.1.0-etapa0`;
`etapa/1-ingesta` → `main`, etiqueta `v0.2.0-etapa1`. `main` funcional. Sin `push`
(local). **Etapa 1 cerrada.**

### Siguiente paso concreto

**Etapa 2 — Estimación de pose**, rama `etapa/2-pose` desde `main`. Plan ya propuesto y
aprobado en su forma general (lecturas hechas: `capitulo-3` 3.3.2.3–3.3.2.9, `capitulo-4`
4.4.3). Pendiente de confirmar 4 puntos de diseño antes de escribir código:
`static_image_mode`, alcance de la Vía A (YOLOv8-Pose), `docs/resultados/` desde E2, y el
umbral de "salto imposible" sin escala métrica.

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
