# Arquitectura

Documento vivo. Se completa contra lo efectivamente construido (tarea 10.4 del plan). Por
ahora resume lo que ya está definido y remite a las fuentes.

## Visión general

```
Usuario → Frontend (React/TanStack) → API (FastAPI) → Motor Python → Supabase
```

Ver `CLAUDE.md` sección 4 para las reglas de arquitectura completas. Las dos que gobiernan
todo lo demás:

- El **frontend no calcula nada biomecánico**: solo representa datos ya evaluados por el motor.
- El **motor (`backend/app/engine/`) no importa bibliotecas web**: recibe rutas de archivo y
  devuelve estructuras de datos.

## Pipeline del motor

(Numeración del plan de desarrollo, E0–E5 del motor.)

| Etapa | Módulo | Qué hace | Estado |
| --- | --- | --- | --- |
| E1 · Ingesta | `engine/ingest.py`, `engine/framehash.py`, `app/catalogador.py` | Lee FPS reales, resuelve el caso de cámara lenta, clasifica por frecuencia efectiva, verifica unicidad de fotogramas | **construido** |
| E2 · Pose | `engine/pose/` (`base`, `articulaciones`, `mediapipe_backend`, `fake_backend`, `cache`), `app/extraer_pose.py`, `app/bench_pose.py` | Estimación de pose (MediaPipe por defecto) detrás de una interfaz común; caché de coordenadas; medición de velocidad de inferencia | **construido** |
| E2b · Validación | `engine/validation.py` | Marcado de puntos por confianza, saltos imposibles e inversiones de profundidad (z) | **construido** |
| E3 · Elevación | — | No aplica: MediaPipe entrega 3D directo; no hay modelo de elevación | descartado |
| E3 · Filtrado | `engine/dsp.py`, `engine/preparacion.py`, `engine/winter.py`, `engine/pipeline.py` | Remoción de atípicos, corte objetivo (Winter), Butterworth de fase cero sobre coordenadas métricas | **construido** |
| E4 | `engine/kinematics.py`, `engine/sequencing.py` | Ángulos, velocidades, orden de picos | pendiente |
| E5 | `engine/audit.py`, `engine/render.py` | Auditoría, alertas, reporte, overlay | pendiente |

Orden del procesamiento: detección → remoción de atípicos → filtrado → cálculo de
velocidades. (El paso "elevación 3D" del orden canónico de la tesis no existe acá: MediaPipe
da 3D directo.) El filtrado va **antes** de las velocidades y es de fase cero (adelante y
atrás); un filtro unidireccional corre los picos en el tiempo y destruye justamente lo que
se mide.

### E1 — Ingesta y validación de FPS

`engine/ingest.py` separa el núcleo puro (clasificar, contrastar metadatos, calcular la
frecuencia de captura efectiva) de la entrada/salida (`probe()`, `iterar_fotogramas()`).

- **Se propaga siempre la frecuencia de captura, nunca la de reproducción.**
  `fps_efectivos = fps_declarados × factor`. El factor de ralentización es externo (del
  catálogo o pasado a mano): para material descargado no puede inferirse de los metadatos.
- **`escala_temporal_conocida`**: `False` cuando `fps_efectivos` es una estimación. Viaja
  hasta `Trazabilidad` en el reporte. Sirve para el orden de los picos, no para
  velocidades absolutas.
- **Aptitud por frecuencia efectiva** (`AptitudFaseRapida`): ≥240 `COMPLETO`, 120–239
  `REDUCIDO`, 60–119 `SOLO_PREPARACION`, <60 `RECHAZADO` (resultado con motivo, no
  excepción).
- **Dos verificaciones independientes** (decisión 001): metadatos (`ffprobe`) y unicidad
  de fotogramas por huella md5 exacta (`engine/framehash.py`, no `mpdecimate`).
- **`app/catalogador.py`** (`python -m app.catalogador` desde `backend/`) recorre el
  corpus, combina ambas verificaciones en un "uso" final y escribe
  `catalogo-verificado.csv`. No toca `catalogo.csv`.

Ver `docs/decisiones/004-ingesta-fps-y-verificacion.md`.

### E2 — Estimación de pose

Contrato intercambiable: `engine/pose/base.PoseBackend` (ABC). Cada backend solo
implementa `estimar_frame`; la clase base arma la `SecuenciaPose`. E3/E4 no saben qué
backend se usó.

- **`MediaPipeBackend`** por defecto (§4.4.3): 33 puntos, 3D directo. `static_image_mode=True`
  (señal cruda; el suavizado lo hace E3), `model_complexity=2`.
- **Mapa articular canónico** (`engine/pose/articulaciones.py`): 19 `ArticulacionCanonica`;
  MediaPipe (33) y COCO-17 se traducen al mismo vocabulario. `SecuenciaPose.dims` (2/3)
  indica si `z` está poblado.
- **`FakeBackend`**: backend sintético (sin modelo) para pruebas; simula también el caso
  2D-solo (`dims=2`, `z=None`). La Vía A real (YOLOv8-Pose + elevación) se difiere al plan
  de repliegue de E4.
- **Coordenadas**: imagen normalizada `[0,1]` + `z` relativo (o `None`) + `confianza [0,1]`.
- **`engine/validation.py`**: puntos de baja confianza + saltos imposibles (umbral en
  fracciones de la longitud del torso) + **inversiones de profundidad** (cambio de signo
  de `z` dominado por `z`, decisión 009) + cobertura auditable por articulación.
- **Caché** (`engine/pose/cache.py`, `KINETIQ_CACHE_DIR` / `backend/.cache/`): `.pose.npz`
  + `.pose.json`. `python -m app.extraer_pose` la puebla; `python -m app.bench_pose` mide
  la velocidad de inferencia y la registra en `docs/resultados/`.

Ver `docs/decisiones/005-percepcion-pose.md`.

### E3 — Procesamiento de señales

`engine/pipeline.procesar_e3(seq) -> SecuenciaFiltrada` encadena, en orden fijo:

1. **`validation.validar(seq, espacio="mundo")`** — baja confianza + saltos imposibles.
2. **`preparacion.preparar_series`** — excluye lo no confiable; interpola huecos ≤ 5
   fotogramas; los más largos quedan como `TramoExcluido` (no se estiman).
3. **`winter.elegir_corte`** — análisis residual → un `corte_hz` para todo el clip
   (simplificación deliberada por el contrato congelado).
4. **`dsp.butterworth_fase_cero`** — Butterworth de 4º orden con `filtfilt` (nunca
   `lfilter`), sobre la **secuencia completa** (E4 recorta las repeticiones después).

Se filtra el espacio **métrico** (`puntos_mundo`, metros) cuando existe; los backends
2D puros caen a `puntos` (imagen). El overlay de E5 usa `puntos` **sin filtrar**.
`SecuenciaFiltrada.trazabilidad_filtro()` produce el bloque `trazabilidad.filtro` del
reporte; los `TramoExcluido` alimentan `cobertura.tramos_no_auditables`.

Ver `docs/decisiones/007-filtrado-de-senales.md`.

## Contrato del reporte

Estructura JSON de salida, congelada en la Etapa 0:

- Definición: `backend/app/schemas/reporte.py` (Pydantic).
- Ejemplo válido: `docs/contrato-reporte.ejemplo.json`.
- Especificación: Anexo A de `docs/plan-desarrollo.md`.
- Cambios posteriores: Etapa 1 agregó `trazabilidad.escala_temporal_conocida`
  (decisión 004). Todo cambio al contrato se registra en `docs/decisiones/`.

La unidad de medición es la **repetición**, no el archivo: un video contiene varias
repeticiones del mismo gesto, cada una se evalúa por separado y después se agregan.

## Configuración dependiente de la máquina

`backend/app/config.py` resuelve la ubicación del corpus de video desde `KINETIQ_DATA_DIR`
(variable de entorno o `backend/.env`). Ver `docs/decisiones/002-config-ruta-corpus.md`.

## Decisiones registradas

Ver `docs/decisiones/`.
