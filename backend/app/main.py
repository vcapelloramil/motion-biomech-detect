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

import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins, get_max_intentos, get_pausa_recuperacion_s
from app.routers import analisis, cuenta, salud, sesiones

def _recuperar_tras_pausa() -> None:
    """Al arrancar: reencola los golpes que quedaron ``encolado``/``procesando`` por un reinicio (``app.recuperacion``). Nunca tumba la API."""
    from app.recuperacion import recuperar
    from app.security import get_admin_client
    from app.workers.procesamiento import esta_en_este_proceso, procesar_en_segundo_plano, registrar_en_este_proceso

    try:
        pausa = get_pausa_recuperacion_s()
        if pausa is None:
            return
        time.sleep(pausa)
        admin = get_admin_client()

        def encolar(video_id: str) -> None:
            registrar_en_este_proceso(video_id)
            threading.Thread(target=procesar_en_segundo_plano, args=(admin, video_id), daemon=True).start()

        hecho = recuperar(admin, encolar, get_max_intentos(), esta_en_este_proceso)
        print(f"[recuperacion] {hecho}")
    except Exception as exc:  # noqa: BLE001 - sin credenciales (pruebas, desarrollo) o sin red: se informa y se sigue
        print(f"[recuperacion] no se pudo: {exc!r}")


@asynccontextmanager
async def _ciclo_de_vida(_app: FastAPI):
    threading.Thread(target=_recuperar_tras_pausa, daemon=True).start()
    yield


app = FastAPI(title="KinetiQ API", lifespan=_ciclo_de_vida)

# CORS acotado a los orígenes del frontend (KINETIQ_CORS_ORIGINS; sin valor, ninguno). La autenticación
# va en un header (Authorization), no en cookies: por eso allow_credentials=False y nada de comodines.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

app.include_router(salud.router)
app.include_router(analisis.router)
app.include_router(sesiones.router)
app.include_router(cuenta.router)
