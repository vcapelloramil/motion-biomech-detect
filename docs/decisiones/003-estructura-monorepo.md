# Decisión 003 — Estructura del monorepo

**Fecha:** 26 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 0 (tarea 0.1) · todas las etapas siguientes

---

## El problema

El repositorio venía siendo solo el prototipo de interfaz generado con Lovable, con todo
en la raíz. El motor biomecánico (Python) y, más adelante, la capa de plataforma (API,
Supabase) necesitan un lugar propio. Hace falta fijar la estructura **antes** de empezar a
crear módulos, para no reacomodar carpetas a mitad de camino.

---

## Decisión

Se adopta **tal cual** la estructura declarada en el apartado 4.3.5 del Capítulo 4 de la
tesis (`docs/tesis/capitulo-4-marco-tecnologico.md`). Transcripción literal:

```
sistema-biomecanico-tenis/
├── README.md
├── .github/workflows/
├── frontend/
│   └── src/
│       ├── lib/
│       ├── components/
│       ├── pages/
│       └── types/
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       ├── security.py
│       ├── schemas/
│       ├── routers/
│       ├── workers/
│       └── engine/              # NÚCLEO BIOMECÁNICO — sin dependencias web
│           ├── version.py
│           ├── ingest.py         # E0
│           ├── pose/             # E1 — contrato + backends intercambiables
│           ├── validation.py     # E1b
│           ├── lifting.py        # E2
│           ├── dsp.py            # E3
│           ├── kinematics.py     # E4
│           ├── sequencing.py     # E4
│           ├── audit.py          # E5
│           └── render.py         # E5
├── supabase/
│   ├── migrations/
│   └── policies/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/videos/
└── docs/
    ├── arquitectura.md
    ├── decisiones/
    └── plan-desarrollo.md
```

### Regla que no puede perderse

`backend/app/engine/` **no importa nada de FastAPI, de Supabase, ni de HTTP.** Solo recibe
rutas de archivo y devuelve estructuras de datos. Eso es lo que permite ejecutarlo y
probarlo en un cuaderno de trabajo antes de que exista API, y lo que habilita el plan de
repliegue de la Etapa 4 si hace falta cambiar de backend de pose sin tocar el resto.
(Ya estaba en el `CLAUDE.md`, sección 4; se repite acá porque es la razón de ser de esta
estructura.)

---

## Qué se creó en la Etapa 0 y qué queda diferido

La estructura de arriba es el **destino**. En esta etapa se creó solo lo que se usa ya:

| Ya existe | Diferido a |
| --- | --- |
| `frontend/` con todo el proyecto Lovable movido | — |
| `backend/app/__init__.py`, `backend/app/config.py` | — |
| `backend/app/engine/__init__.py`, `engine/version.py`, `engine/pose/` | los módulos `ingest.py`, `dsp.py`, etc. los crea su etapa |
| `backend/app/schemas/__init__.py`, `schemas/reporte.py` (contrato) | `main.py`, `security.py`, `routers/`, `workers/` → Etapa 6 |
| `tests/unit/` con las pruebas de la Etapa 0 | `tests/integration/`, `tests/fixtures/videos/` se llenan desde la Etapa 1 |
| `supabase/` (carpetas vacías) | contenido → Etapa 7 |
| `.github/workflows/` (carpeta vacía) | pipeline de CI cuando haya algo que correr |
| `docs/arquitectura.md` | se completa contra lo efectivamente construido (Etapa 10.4) |
| `backend/Dockerfile` | Etapa 6+. No se crea un placeholder para no dejar infraestructura sin uso (criterio de MVP del `CLAUDE.md`). |

Las carpetas que hoy están vacías llevan un archivo `.gitkeep` para que git las conserve.

## Diferencias con el prototipo actual, aceptadas

- El frontend de Lovable usa `src/routes/` (TanStack Router), no `src/pages/`, y tiene
  además `src/hooks/` y `src/assets/`. No se reorganiza el interior de `frontend/` en esta
  etapa: se movió el proyecto como estaba. La estructura `frontend/src/{lib,components,
  pages,types}` del apartado 4.3.5 es orientativa.
- El nombre del repositorio es `motion-biomech-detect`, no `sistema-biomecanico-tenis`. Es
  solo el nombre de la carpeta/repo; la estructura interna es la que importa.

## Dónde vive el contrato del reporte

En `backend/app/schemas/reporte.py` (no dentro de `engine/`). Es Pydantic puro, sin
dependencias web, así que el motor puede importarlo sin romper la regla de pureza; y es el
mismo esquema que la API reutiliza como salida en la Etapa 6 (tarea 6.2 del plan).

---

## Consecuencias

- Motor e interfaz pueden avanzar en paralelo: la interfaz contra
  `docs/contrato-reporte.ejemplo.json`, el motor produciendo esa misma estructura.
- `pytest` se corre desde la raíz del repo; `pytest.ini` pone `backend/` en el path para
  poder importar `app.*` sin instalar el paquete.
- Romper la sincronización con Lovable es un costo aceptado (el desarrollo sigue en Claude
  Code, no en Lovable).
