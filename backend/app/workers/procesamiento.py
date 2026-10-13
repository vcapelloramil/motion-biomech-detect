"""Orquestación en segundo plano — Etapa 6 (tarea 6.3), sembrada en la tarea 4.5.4.

Decisión de MVP del apartado 4.4.2 de la tesis: sin cola externa (Celery/Redis). El
mecanismo de ``BackgroundTasks`` de FastAPI, combinado con el campo ``estado`` en
``videos``, cumple la misma función con una fracción de la complejidad operativa. La
limitación conocida y aceptada: un reinicio del proceso pierde el trabajo en curso (esa
fila queda en 'procesando' para siempre hasta que algo la retome). La tarea 6.5
("recuperación al arranque: los análisis en estado procesando se vuelven a encolar") es
justamente la mitigación — no está implementada todavía, es la próxima pieza de la Etapa 6.

Es también, a propósito, la medición real que pide la tarea 4.5.4: contra el plan gratis
de Render, si la suspensión por inactividad corta el proceso mientras esta tarea de fondo
sigue corriendo, el video queda "procesando" — exactamente lo que hay que ver pasar (o no)
contra el servicio desplegado de verdad, no algo que se pueda simular localmente.
"""

from __future__ import annotations

import threading

from supabase import Client

from app.config import get_max_analisis_simultaneos
from app.procesar_video import procesar_video

# Cupo de análisis simultáneos del proceso (``KINETIQ_MAX_ANALISIS_SIMULTANEOS``, 1 por defecto). Con una carga de varios golpes la API
# recibe una orden por golpe casi a la vez; sin cupo, todos correrían en paralelo y la memoria de la instancia (2 GB) no alcanza. Los que
# esperan siguen en ``encolado`` (el estado que ve el usuario) y arrancan de a uno.
_CUPO: threading.BoundedSemaphore | None = None
_CUPO_CANDADO = threading.Lock()


def _cupo() -> threading.BoundedSemaphore:
    global _CUPO
    with _CUPO_CANDADO:
        if _CUPO is None:
            _CUPO = threading.BoundedSemaphore(get_max_analisis_simultaneos())
        return _CUPO


# Videos que este proceso tiene en cola o procesando: la recuperación al arrancar (``app.recuperacion``) no los reencola dos veces.
_EN_ESTE_PROCESO: set[str] = set()
_REGISTRO_CANDADO = threading.Lock()


def registrar_en_este_proceso(video_id: str) -> None:
    """Se llama al encolar (antes de que arranque la tarea), para que la recuperación no lo vea como huérfano."""
    with _REGISTRO_CANDADO:
        _EN_ESTE_PROCESO.add(video_id)


def esta_en_este_proceso(video_id: str) -> bool:
    with _REGISTRO_CANDADO:
        return video_id in _EN_ESTE_PROCESO


def procesar_en_segundo_plano(admin: Client, video_id: str) -> None:
    """Wrapper de ``procesar_video`` para ``BackgroundTasks``. ``procesar_video`` ya deja
    ``videos.estado = 'fallido'`` en la fila si algo revienta; acá solo se evita que la
    excepción se pierda en silencio en el log del contenedor (CLAUDE.md §6.6: distinguir
    fallas visibles, no tragárselas)."""
    registrar_en_este_proceso(video_id)
    try:
        with _cupo():
            procesar_video(admin, video_id)
    except Exception as exc:  # noqa: BLE001 - ver docstring: es intencional no relanzar acá.
        print(f"[workers.procesamiento] video {video_id} fallo: {exc!r}")
    finally:
        with _REGISTRO_CANDADO:
            _EN_ESTE_PROCESO.discard(video_id)
