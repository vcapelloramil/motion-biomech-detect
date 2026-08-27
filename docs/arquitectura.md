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

| Etapa | Módulo | Qué hace |
| --- | --- | --- |
| E0 | `engine/ingest.py` | Ingesta: FPS reales, fotogramas, resolución |
| E1 | `engine/pose/` | Estimación de pose (MediaPipe por defecto) detrás de una interfaz común |
| E1b | `engine/validation.py` | Marcado de puntos por confianza y saltos imposibles |
| E2 | `engine/lifting.py` | Elevación 2D→3D (opcional) |
| E3 | `engine/dsp.py` | Filtrado Butterworth de fase cero (bidireccional) |
| E4 | `engine/kinematics.py`, `engine/sequencing.py` | Ángulos, velocidades, orden de picos |
| E5 | `engine/audit.py`, `engine/render.py` | Auditoría, alertas, reporte, overlay |

Orden del procesamiento: detección → remoción de atípicos → (elevación 3D) → filtrado →
cálculo de velocidades. El filtrado va **después** de la elevación y **antes** de las
velocidades, y es de fase cero (adelante y atrás); un filtro unidireccional corre los picos
en el tiempo y destruye justamente lo que se mide.

## Contrato del reporte

Estructura JSON de salida, **congelada en la Etapa 0**:

- Definición: `backend/app/schemas/reporte.py` (Pydantic).
- Ejemplo válido: `docs/contrato-reporte.ejemplo.json`.
- Especificación: Anexo A de `docs/plan-desarrollo.md`.

La unidad de medición es la **repetición**, no el archivo: un video contiene varias
repeticiones del mismo gesto, cada una se evalúa por separado y después se agregan.

## Configuración dependiente de la máquina

`backend/app/config.py` resuelve la ubicación del corpus de video desde `KINETIQ_DATA_DIR`
(variable de entorno o `backend/.env`). Ver `docs/decisiones/002-config-ruta-corpus.md`.

## Decisiones registradas

Ver `docs/decisiones/`.
