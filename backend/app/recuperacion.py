"""Recuperación al arrancar (tarea 6.5 del plan, adelantada el 13/10/2026).

El procesamiento corre en segundo plano dentro del proceso de la API (``workers/procesamiento.py``): si el servicio se reinicia (un
despliegue, un corte de la instancia), los golpes que estaban en ``procesando`` o esperando en ``encolado`` quedan así **para siempre**.
Al arrancar, y después de una pausa corta (para no pisar al proceso anterior si todavía está terminando durante un despliegue), se los
vuelve a poner en la cola.

Reglas:

* ``encolado``: nunca empezó; se vuelve a encolar tal cual (no cuenta como intento).
* ``procesando``: estaba corriendo cuando el proceso murió, así que es el sospechoso (un golpe que agota la memoria mata el proceso y se
  reanudaría en bucle). Se vuelve a encolar **y suma un intento**; con ``intentos`` ya en el tope pasa a ``fallido`` (``error_inesperado``)
  en lugar de reanudarse otra vez.
* Los que ya están en este proceso (llegaron mientras corría la pausa) no se tocan.
* La tabla se actualiza con *compare-and-swap* sobre el estado leído: si otro proceso ya lo movió, no se hace nada.

Función de decisión pura (``decidir``) y el barrido (``recuperar``), que recibe el cliente y la función que encola, para probarlos sin red.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from app.reintento import MOTIVO_ERROR_INESPERADO

REENCOLAR = "reencolar"
FALLAR = "fallar"


def decidir(estado: str, intentos: int, max_intentos: int) -> str:
    """``reencolar`` o ``fallar`` para un video que quedó ``encolado`` o ``procesando`` en un proceso que ya no está."""
    if estado == "procesando" and intentos >= max_intentos:
        return FALLAR
    return REENCOLAR


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def recuperar(
    admin: Any,
    encolar: Callable[[str], None],
    max_intentos: int,
    ya_en_este_proceso: Callable[[str], bool] = lambda _id: False,
) -> dict[str, list[str]]:
    """Barre los videos ``encolado`` / ``procesando`` y los reencola o los marca ``fallido``. Devuelve qué hizo con cada uno."""
    filas = (
        admin.table("videos")
        .select("id, estado, intentos, encolado_en")
        .in_("estado", ["encolado", "procesando"])
        .order("encolado_en")
        .execute()
        .data
    )
    hecho: dict[str, list[str]] = {"reencolados": [], "fallidos": [], "omitidos": []}
    for f in filas:
        video_id, estado, intentos = str(f["id"]), f["estado"], int(f.get("intentos") or 0)
        if ya_en_este_proceso(video_id):
            hecho["omitidos"].append(video_id)
            continue
        if decidir(estado, intentos, max_intentos) == FALLAR:
            cambiadas = (
                admin.table("videos")
                .update({"estado": "fallido", "motivo_fallo": MOTIVO_ERROR_INESPERADO, "fin_procesamiento_en": _ahora()})
                .eq("id", video_id)
                .eq("estado", estado)
                .execute()
                .data
            )
            (hecho["fallidos"] if cambiadas else hecho["omitidos"]).append(video_id)
            continue
        if estado == "procesando":
            cambiadas = (
                admin.table("videos")
                .update({"estado": "encolado", "intentos": intentos + 1, "inicio_procesamiento_en": None, "fin_procesamiento_en": None})
                .eq("id", video_id)
                .eq("estado", "procesando")
                .execute()
                .data
            )
            if not cambiadas:
                hecho["omitidos"].append(video_id)
                continue
        encolar(video_id)
        hecho["reencolados"].append(video_id)
    return hecho
