"""Aplicación FastAPI — Etapa 6 (tarea 6.1), sembrada en la tarea 4.5.4.

Expone hoy solo dos de las siete operaciones del apartado 4.2.5 de la tesis:
"Verificación de servicio" (pública, ``routers/salud.py``) y una versión acotada de
"Confirmación de carga" (protegida por token, ``routers/analisis.py``). Las cinco
operaciones restantes (alta de análisis, consulta de estado, reporte, listado,
evolución) se agregan sobre esta misma estructura en la Etapa 6 propiamente dicha — no
hay que reorganizar nada para sumarlas, solo agregar routers.

Comando de producción (ver ``backend/Dockerfile``):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

from fastapi import FastAPI

from app.routers import analisis, salud

app = FastAPI(title="KinetiQ API")

app.include_router(salud.router)
app.include_router(analisis.router)
