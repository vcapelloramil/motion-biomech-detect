"""Consistencia entre los golpes de una sesión (paso 3 del plan §8).

Una lectura calculada en el servidor y no un dato guardado: así nunca queda desactualizada si el usuario elimina un golpe o termina de
analizarse otro, y el frontend no calcula nada biomecánico (especificación §1.5). Mismo patrón de autenticación que ``analisis.py``: el
JWT de Supabase del usuario; la API usa ``service_role``, así que **comprueba ella misma que la sesión es de quien llama** y responde 404
(no 403) si no lo es.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client

from app.consistencia import resumen_de_sesion
from app.schemas.api import RespuestaConsistencia
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado

router = APIRouter(prefix="/sesiones", tags=["sesiones"])

_PG_TEXTO_INVALIDO = "22P02"


def _reporte_de(fila: dict) -> dict | None:
    r = fila.get("reportes_biomecanicos")
    r = r[0] if isinstance(r, list) and r else r
    rep = r.get("reporte") if isinstance(r, dict) else None
    return rep if isinstance(rep, dict) else None


@router.get("/{sesion_id}/consistencia", response_model=RespuestaConsistencia)
def consistencia(
    sesion_id: str,
    usuario: UsuarioAutenticado = Depends(usuario_autenticado),
    admin: Client = Depends(get_admin_client),
) -> RespuestaConsistencia:
    no_existe = HTTPException(status.HTTP_404_NOT_FOUND, f"No existe la sesión {sesion_id}")
    try:
        filas = admin.table("sesiones").select("id, usuario_id, gesto, encuadre, fecha").eq("id", sesion_id).execute().data
    except APIError as e:
        if getattr(e, "code", None) == _PG_TEXTO_INVALIDO:
            raise no_existe from None
        raise
    if not filas or str(filas[0].get("usuario_id")) != usuario.id:
        raise no_existe
    sesion = filas[0]

    videos = (
        admin.table("videos")
        .select("id, estado, creado_en, reportes_biomecanicos(reporte)")
        .eq("sesion_id", sesion_id)
        .order("creado_en")
        .execute()
        .data
    )
    golpes = [{"video_id": v["id"], "estado": v["estado"], "reporte": _reporte_de(v)} for v in videos]
    return RespuestaConsistencia(
        sesion_id=sesion_id,
        gesto=sesion["gesto"],
        encuadre=sesion["encuadre"],
        fecha=str(sesion["fecha"]),
        **resumen_de_sesion(golpes),
    )
