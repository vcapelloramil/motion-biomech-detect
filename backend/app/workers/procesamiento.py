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

from supabase import Client

from app.procesar_video import procesar_video


def procesar_en_segundo_plano(admin: Client, video_id: str) -> None:
    """Wrapper de ``procesar_video`` para ``BackgroundTasks``. ``procesar_video`` ya deja
    ``videos.estado = 'fallido'`` en la fila si algo revienta; acá solo se evita que la
    excepción se pierda en silencio en el log del contenedor (CLAUDE.md §6.6: distinguir
    fallas visibles, no tragárselas)."""
    try:
        procesar_video(admin, video_id)
    except Exception as exc:  # noqa: BLE001 - ver docstring: es intencional no relanzar acá.
        print(f"[workers.procesamiento] video {video_id} fallo: {exc!r}")
