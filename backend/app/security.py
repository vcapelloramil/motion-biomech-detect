"""Seguridad de la API — Etapa 6, sembrada en la tarea 4.5.4.

Hoy protege el disparo de análisis con un token compartido simple, mientras no existe la
verificación de JWT de Supabase Auth (tarea 7.4). El día que la Etapa 7 la implemente,
``verificar_token`` se REEMPLAZA por la verificación real, no convive con ella — este
archivo es exactamente donde ese reemplazo tiene que pasar, por eso el nombre.

El token esperado (``KINETIQ_API_TOKEN``) vive solo en la variable de entorno del
servidor, cargada a mano en el panel de Render — nunca en el repo ni en ``render.yaml``
(ver ese archivo y la tarea 4.5.4 en la bitácora).
"""

from __future__ import annotations

import os
import secrets

from fastapi import Header, HTTPException, status
from supabase import Client, create_client

from app.config import get_supabase_service_role_key, get_supabase_url

_TOKEN_ENV_VAR = "KINETIQ_API_TOKEN"


def get_admin_client() -> Client:
    """Cliente de Supabase con ``service_role``. Lo usa solo el propio servidor para leer
    y escribir resultados — nunca se expone al cliente HTTP (``backend/.env.example``
    explica por qué esta clave nunca va al frontend)."""
    return create_client(get_supabase_url(), get_supabase_service_role_key())


def verificar_token(x_kinetiq_token: str = Header(default="")) -> None:
    """Dependency de FastAPI: 401 si falta el header o no coincide con
    ``KINETIQ_API_TOKEN``. Comparación de tiempo constante (``secrets.compare_digest``)
    para no filtrar el token por temporización, aunque acá el costo de hacerlo bien es
    nulo."""
    esperado = os.environ.get(_TOKEN_ENV_VAR)
    if not esperado:
        # Server mal configurado (olvidaron cargar la variable en Render) no es lo mismo
        # que "token inválido": se informa distinto para no esconder el error real.
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"El servidor no tiene {_TOKEN_ENV_VAR} configurado.",
        )
    if not x_kinetiq_token or not secrets.compare_digest(x_kinetiq_token, esperado):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o ausente.")
