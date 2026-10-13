"""Evolución: un jugador frente a sí mismo (paso 6 del plan §8). Una lectura calculada en el servidor (``app.consistencia.serie_de_evolucion``).

Solo se comparan sesiones del MISMO jugador, golpe y encuadre (especificación §3). Mismo patrón de autenticación que ``sesiones.py``: el JWT
del usuario; la API usa ``service_role`` y por eso filtra ella misma por el ``sub`` del token."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.consistencia import serie_de_evolucion
from app.routers.sesiones import _reporte_de
from app.schemas.api import RespuestaEvolucion
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado

router = APIRouter(prefix="/evolucion", tags=["evolucion"])


@router.get("", response_model=RespuestaEvolucion)
def evolucion(
    atleta_id: str = Query(..., min_length=1),
    gesto: Literal["saque", "drive", "reves"] = Query(...),
    encuadre: Literal["perfil", "tres_cuartos"] = Query(...),
    usuario: UsuarioAutenticado = Depends(usuario_autenticado),
    admin: Client = Depends(get_admin_client),
) -> RespuestaEvolucion:
    filas = (
        admin.table("sesiones")
        .select("id, fecha, creado_en, lado_camara, videos(id, estado, reportes_biomecanicos(reporte))")
        .eq("usuario_id", usuario.id)
        .eq("atleta_id", atleta_id)
        .eq("gesto", gesto)
        .eq("encuadre", encuadre)
        .order("fecha")
        .order("creado_en")
        .execute()
        .data
    )
    sesiones = [
        {
            "sesion_id": s["id"],
            "fecha": s["fecha"],
            "lado_camara": s.get("lado_camara"),
            "golpes": [{"video_id": v["id"], "estado": v["estado"], "reporte": _reporte_de(v)} for v in s.get("videos") or []],
        }
        for s in filas
    ]
    return RespuestaEvolucion(atleta_id=atleta_id, gesto=gesto, encuadre=encuadre, **serie_de_evolucion(sesiones))
