"""Semilla de la operación "Confirmación de carga" del apartado 4.2.5 (Etapa 6): confirma
que un video ya subido tiene que procesarse, y encola el trabajo.

**Simplificación deliberada de la tarea 4.5.4, no el diseño final de la Etapa 6:**

- Asume que el video YA está en Storage y YA tiene su fila en ``videos`` (lo da la tarea
  4.5.3, o un INSERT de prueba). La operación "Alta de análisis" (crear el registro y
  devolver la URL firmada de carga) es de la Etapa 6/8, cuando exista la pantalla de carga
  real conectada.
- Protegida por un token compartido (``app.security.verificar_token``), no por la
  autenticación de usuario real de Supabase — esa es la tarea 7.4. El día que exista, este
  router cambia de dependency, no agrega una segunda.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from supabase import Client

from app.schemas.api import RespuestaAnalisisEncolado
from app.security import get_admin_client, verificar_token
from app.workers.procesamiento import procesar_en_segundo_plano

router = APIRouter(
    prefix="/analisis", tags=["analisis"], dependencies=[Depends(verificar_token)]
)


@router.post(
    "/{video_id}/procesar",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RespuestaAnalisisEncolado,
)
def procesar(
    video_id: str,
    tareas: BackgroundTasks,
    admin: Client = Depends(get_admin_client),
) -> RespuestaAnalisisEncolado:
    """Responde 202 de inmediato; el procesamiento real corre en segundo plano (decisión
    de MVP del apartado 4.4.2, sin cola externa — ver app/workers/procesamiento.py)."""
    existe = admin.table("videos").select("id").eq("id", video_id).execute().data
    if not existe:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el video {video_id}")

    admin.table("videos").update({"estado": "encolado"}).eq("id", video_id).execute()
    tareas.add_task(procesar_en_segundo_plano, admin, video_id)
    return RespuestaAnalisisEncolado(video_id=video_id, estado="encolado")
