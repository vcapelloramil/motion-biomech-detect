# KinetiQ

Sistema de análisis biomecánico preventivo para tenis mediante visión artificial y análisis
de la cadena cinética. Proyecto Final de Ingeniería en Informática, Universidad del Salvador.
Autor: Valentín Capello Ramil.

El sistema procesa videos pregrabados de jugadores de tenis, extrae puntos articulares con
estimación de pose, y **documenta** el orden temporal en que cada segmento del cuerpo
alcanza su velocidad máxima durante saque, drive y revés. No predice ni diagnostica; ver
`CLAUDE.md`.

## Estado

En desarrollo (Etapa 0 del plan). El monorepo y el contrato de datos están; el motor
biomecánico se construye etapa por etapa.

## Estructura

```
frontend/   prototipo de interfaz (TanStack Start + React, generado con Lovable)
backend/    motor biomecánico en Python y, más adelante, la API (FastAPI)
supabase/   migraciones y políticas (Etapa 7)
tests/      pruebas (pytest)
docs/       plan de desarrollo, protocolo de grabación, decisiones, bitácora, tesis
```

## Puesta en marcha

**Frontend:**

```bash
cd frontend
bun install
bun run dev
```

**Backend:** ver `backend/README.md` (requiere Python 3.11).

## Documentos

| Archivo | Qué es |
| --- | --- |
| `CLAUDE.md` | Reglas duras del proyecto. Leer primero. |
| `docs/plan-desarrollo.md` | Plan de 12 semanas por etapas. Incluye el contrato del reporte (Anexo A). |
| `docs/protocolo-grabacion.md` | Protocolo de captura del conjunto de datos propio. |
| `docs/decisiones/` | Registro de decisiones de arquitectura. |
| `docs/bitacora.md` | Qué se hizo en cada sesión de trabajo. |
| `docs/tesis/` | Marco teórico y marco tecnológico de la tesis. |

## Datos de video

Los videos **no están en este repositorio** y no deben estarlo. Viven en una carpeta aparte
(`kinetiq-data/`), cuya ubicación el backend toma de la variable `KINETIQ_DATA_DIR`. Ver
`docs/decisiones/002-config-ruta-corpus.md`.
