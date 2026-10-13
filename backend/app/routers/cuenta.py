"""Eliminar la cuenta y todos sus datos (paso 5 del plan §8). Ver ``app.cuenta``.

Autenticación como el resto de la API: el JWT de Supabase del usuario; el router actúa SOLO sobre la cuenta del ``sub`` del token (no hay
forma de pedir el borrado de otra). La confirmación explícita viaja en el cuerpo: un ``DELETE`` sin ella no hace nada.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.cuenta import eliminar_cuenta
from app.schemas.api import PedidoEliminarCuenta, RespuestaCuentaEliminada
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado

router = APIRouter(prefix="/cuenta", tags=["cuenta"])

CONFIRMACION = "ELIMINAR"


@router.delete("", response_model=RespuestaCuentaEliminada)
def eliminar(
    pedido: PedidoEliminarCuenta,
    usuario: UsuarioAutenticado = Depends(usuario_autenticado),
    admin: Client = Depends(get_admin_client),
) -> RespuestaCuentaEliminada:
    if pedido.confirmacion != CONFIRMACION:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"codigo": "confirmacion_incorrecta"})
    try:
        hecho = eliminar_cuenta(admin, usuario.id)
    except Exception as exc:  # noqa: BLE001 - la cuenta NO se borró (los archivos van primero): se puede reintentar
        print(f"[cuenta] no se pudo eliminar la cuenta {usuario.id}: {exc!r}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail={"codigo": "no_se_pudo_eliminar"}) from None
    return RespuestaCuentaEliminada(**hecho)
