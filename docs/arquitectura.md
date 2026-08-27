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
| E2 · Pose | `engine/pose/` | Estimación de pose (MediaPipe por defecto) detrás de una interfaz común | pendiente |
| E2b · Validación | `engine/validation.py` | Marcado de puntos por confianza y saltos imposibles | pendiente |
| E3 · Elevación | `engine/lifting.py` | Elevación 2D→3D (opcional) | pendiente |
| E3 · Filtrado | `engine/dsp.py` | Filtrado Butterworth de fase cero (bidireccional) | pendiente |
| E4 | `engine/kinematics.py`, `engine/sequencing.py` | Ángulos, velocidades, orden de picos | pendiente |
| E5 | `engine/audit.py`, `engine/render.py` | Auditoría, alertas, reporte, overlay | pendiente |

Orden del procesamiento: detección → remoción de atípicos → (elevación 3D) → filtrado →
cálculo de velocidades. El filtrado va **después** de la elevación y **antes** de las
velocidades, y es de fase cero (adelante y atrás); un filtro unidireccional corre los picos
en el tiempo y destruye justamente lo que se mide.

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
