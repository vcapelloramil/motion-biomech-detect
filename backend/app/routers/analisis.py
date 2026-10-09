"""Semilla de la operación "Confirmación de carga" del apartado 4.2.5 (Etapa 6): confirma
que un video ya subido tiene que procesarse, y encola el trabajo. Desde la decisión 022 también
es el "reintento manual" (``fallido -> encolado``) del apartado 4.2.4: mismo endpoint, validado
por el estado de origen (``app.reintento``).

**Simplificación deliberada de la tarea 4.5.4, no el diseño final de la Etapa 6:**

- Asume que el video YA está en Storage y YA tiene su fila en ``videos`` (lo da la tarea
  4.5.3, o un INSERT de prueba). La operación "Alta de análisis" (crear el registro y
  devolver la URL firmada de carga) es de la Etapa 6/8, cuando exista la pantalla de carga
  real conectada.
- **Autenticación (tarea 7.4, decisión 025):** el JWT de Supabase del usuario, validado contra
  el JWKS del proyecto (``app.security.usuario_autenticado``). El token compartido se retiró.
  La API usa ``service_role``, que ignora RLS: por eso el router comprueba él mismo que el video
  es de quien llama, y responde 404 (no 403) si no lo es, igual que si no existiera.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client

from app.config import get_max_intentos
from app.reintento import CODIGO_ESTADO_NO_REINTENTABLE, decidir_reintento
from app.schemas.api import RespuestaAnalisisEncolado
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado
from app.workers.procesamiento import procesar_en_segundo_plano

router = APIRouter(prefix="/analisis", tags=["analisis"])

# Código de Postgres "invalid_text_representation": el id no tiene forma de uuid. Es "no existe", no un 500.
_PG_TEXTO_INVALIDO = "22P02"


def _conflicto(codigo: str, estado_actual: str) -> HTTPException:
    """409 con un código cerrado: el texto en lenguaje llano lo resuelve el frontend (R2)."""
    return HTTPException(
        status.HTTP_409_CONFLICT, detail={"codigo": codigo, "estado_actual": estado_actual}
    )


@router.post(
    "/{video_id}/procesar",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RespuestaAnalisisEncolado,
)
def procesar(
    video_id: str,
    tareas: BackgroundTasks,
    usuario: UsuarioAutenticado = Depends(usuario_autenticado),
    admin: Client = Depends(get_admin_client),
) -> RespuestaAnalisisEncolado:
    """Responde 202 de inmediato; el procesamiento real corre en segundo plano (decisión
    de MVP del apartado 4.4.2, sin cola externa — ver app/workers/procesamiento.py).

    404 si el video no existe **o no es del usuario autenticado** (mismo mensaje: no se revela qué
    ids existen). 409 si el video no se puede encolar ahora (``app.reintento.decidir_reintento``):
    ya está en curso, ya está analizado, falló por la declaración y no se corrigió, o agotó los
    intentos."""
    no_existe = HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el video {video_id}")
    try:
        filas = (
            admin.table("videos")
            .select("id, usuario_id, estado, motivo_fallo, modo_captura_intentado, intentos, sesiones(modo_captura)")
            .eq("id", video_id)
            .execute()
            .data
        )
    except APIError as e:
        if getattr(e, "code", None) == _PG_TEXTO_INVALIDO:
            raise no_existe from None
        raise
    # La propiedad se compara con el `sub` del token, no con nada que mande el cliente.
    if not filas or str(filas[0].get("usuario_id")) != usuario.id:
        raise no_existe
    video = filas[0]

    decision = decidir_reintento(
        estado=video["estado"],
        motivo_fallo=video["motivo_fallo"],
        modo_intentado=video["modo_captura_intentado"],
        modo_actual=video["sesiones"]["modo_captura"],
        intentos=video["intentos"],
        max_intentos=get_max_intentos(),
    )
    if not decision.permitido:
        raise _conflicto(decision.codigo, video["estado"])

    # Compare-and-swap: el UPDATE solo pega si el video sigue como se leyó (mismo estado e
    # intentos). Dos pedidos simultáneos leen lo mismo, pero solo uno cambia la fila; el otro
    # no actualiza nada y recibe 409. Incluir `intentos` cierra el caso en que, entre la lectura
    # y la escritura, otro pedido encoló, el análisis terminó y volvió a quedar en el mismo
    # estado. Se limpian los resultados de la corrida anterior (no se arrastran a la nueva).
    actualizadas = (
        admin.table("videos")
        .update(
            {
                "estado": "encolado",
                "motivo_fallo": None,
                "fps_real": None,
                "apto_fase_rapida": None,
                "intentos": video["intentos"] + 1,
            }
        )
        .eq("id", video_id)
        .eq("estado", video["estado"])
        .eq("intentos", video["intentos"])
        .execute()
        .data
    )
    if not actualizadas:
        raise _conflicto(CODIGO_ESTADO_NO_REINTENTABLE, video["estado"])

    tareas.add_task(procesar_en_segundo_plano, admin, video_id)
    return RespuestaAnalisisEncolado(video_id=video_id, estado="encolado")
