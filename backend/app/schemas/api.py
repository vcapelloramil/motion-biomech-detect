"""Esquemas Pydantic de entrada y salida de la API — Etapa 6 (tarea 6.2), sembrados en la
tarea 4.5.4.

No es ``schemas/reporte.py``: ese es el contrato congelado del reporte del motor (Etapa
0, no se toca). Estos son los wrappers HTTP de las operaciones del apartado 4.2.5, libres
de evolucionar junto con la API sin romper el contrato del motor.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RespuestaSalud(BaseModel):
    """GET /health — operación "Verificación de servicio" del apartado 4.2.5 (sin auth)."""

    estado: str
    version_motor: str


class RespuestaAnalisisEncolado(BaseModel):
    """POST /analisis/{video_id}/procesar — respuesta inmediata (202): el trabajo recién
    se encoló, no que haya terminado. El resultado se consulta aparte (operación "Consulta
    de estado" del apartado 4.2.5, todavía no implementada — Etapa 6)."""

    video_id: str
    estado: str


class RespuestaConsistencia(BaseModel):
    """GET /sesiones/{sesion_id}/consistencia — cuánto se parecen entre sí los golpes de una sesión (``app.consistencia``)."""

    sesion_id: str
    gesto: str
    encuadre: str
    fecha: str
    version_regla: str
    golpes: dict[str, int]
    separacion_cadera_hombro: dict[str, Any]
    orden: dict[str, Any]
    golpe_tipico: str | None
    golpes_que_se_apartan: list[str]
    versiones_motor: list[str]
    mezcla_de_versiones: bool
    minimos: dict[str, int]
