"""Aplicación FastAPI — Etapa 6 (tarea 6.1), sembrada en la tarea 4.5.4.

Expone dos operaciones: "Verificación de servicio" (pública, ``routers/salud.py``) y
"Confirmación de carga / reintento" (``routers/analisis.py``), que exige el JWT de Supabase
del usuario y que el video sea suyo (tarea 7.4, decisión 025). Las demás operaciones del
apartado 4.2.5 no son de la API: alta, estado, reporte y listado son lecturas directas a
Supabase con RLS (decisión 025).

Comando de producción (ver ``backend/Dockerfile``):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins
from app.routers import analisis, salud

app = FastAPI(title="KinetiQ API")

# CORS acotado a los orígenes del frontend (KINETIQ_CORS_ORIGINS; sin valor, ninguno). La autenticación
# va en un header (Authorization), no en cookies: por eso allow_credentials=False y nada de comodines.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

app.include_router(salud.router)
app.include_router(analisis.router)
