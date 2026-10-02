"""Operación "Verificación de servicio" del apartado 4.2.5 de la tesis: pública, sin
autenticación. Devuelve solo disponibilidad y versión del motor — nada más (ni conteo de
usuarios, ni estado de la base: eso no es lo que esta operación responde)."""

from __future__ import annotations

from fastapi import APIRouter

from app.engine.version import __version__ as VERSION_MOTOR
from app.schemas.api import RespuestaSalud

router = APIRouter(tags=["salud"])


@router.get("/health", response_model=RespuestaSalud)
def salud() -> RespuestaSalud:
    return RespuestaSalud(estado="ok", version_motor=VERSION_MOTOR)
