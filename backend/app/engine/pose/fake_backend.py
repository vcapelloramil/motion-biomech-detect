"""Backend de pose sintético: genera poses deterministas sin modelo.

Sirve para dos cosas:

1. Probar el contrato ``PoseBackend`` y todo lo que consume una ``SecuenciaPose``
   (validación, caché, E3/E4) sin pagar el costo de una inferencia real.
2. Cubrir hoy el escenario **2D-solo** (``dims=2``, ``z=None``), para que la
   interfaz ya esté ejercitada contra ese caso cuando se implemente la Vía A real
   (YOLOv8-Pose + elevación).

No es un caso trivial: las trayectorias son suaves y continuas (sinusoides con
fase por articulación), admite simular oclusión (articulaciones con confianza
baja) y fotogramas sin detección.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np

from app.engine.pose.articulaciones import ARTICULACIONES_CORE, ArticulacionCanonica
from app.engine.pose.base import PoseBackend, PoseFrame, Punto

_TODAS_3D: tuple[ArticulacionCanonica, ...] = tuple(ArticulacionCanonica)
# Core en orden estable (mismo criterio que articulaciones_de()).
_CORE_ORDENADO: tuple[ArticulacionCanonica, ...] = tuple(
    a for a in ArticulacionCanonica if a in ARTICULACIONES_CORE
)

_A = ArticulacionCanonica
# Posición nominal de cada articulación (figura de pie, coords normalizadas, y hacia
# abajo). Da un esqueleto plausible: la longitud del torso se mantiene ~constante.
_NOMINAL: dict[ArticulacionCanonica, tuple[float, float, float]] = {
    _A.NARIZ: (0.50, 0.12, 0.00),
    _A.HOMBRO_IZQ: (0.42, 0.25, 0.00), _A.HOMBRO_DER: (0.58, 0.25, 0.00),
    _A.CODO_IZQ: (0.38, 0.40, 0.02), _A.CODO_DER: (0.62, 0.40, 0.02),
    _A.MUNECA_IZQ: (0.35, 0.55, 0.04), _A.MUNECA_DER: (0.65, 0.55, 0.04),
    _A.MENIQUE_IZQ: (0.34, 0.585, 0.05), _A.MENIQUE_DER: (0.66, 0.585, 0.05),
    _A.INDICE_IZQ: (0.36, 0.585, 0.05), _A.INDICE_DER: (0.64, 0.585, 0.05),
    _A.CADERA_IZQ: (0.45, 0.52, 0.00), _A.CADERA_DER: (0.55, 0.52, 0.00),
    _A.RODILLA_IZQ: (0.45, 0.72, 0.01), _A.RODILLA_DER: (0.55, 0.72, 0.01),
    _A.TOBILLO_IZQ: (0.45, 0.92, 0.02), _A.TOBILLO_DER: (0.55, 0.92, 0.02),
    _A.PIE_IZQ: (0.44, 0.96, 0.03), _A.PIE_DER: (0.56, 0.96, 0.03),
}


def _fase(art: ArticulacionCanonica) -> float:
    """Fase estable en [0, 2π) derivada del nombre de la articulación."""
    h = int(hashlib.sha1(art.value.encode()).hexdigest()[:8], 16)
    return (h % 3600) / 3600.0 * 2.0 * math.pi


class FakeBackend(PoseBackend):
    def __init__(
        self,
        *,
        dims: int = 3,
        articulaciones: tuple[ArticulacionCanonica, ...] | None = None,
        frames_sin_deteccion: set[int] | None = None,
        articulaciones_ocluidas: dict[ArticulacionCanonica, float] | None = None,
        confianza_base: float = 0.9,
    ) -> None:
        if dims not in (2, 3):
            raise ValueError("dims debe ser 2 o 3")
        self.dims = dims
        if articulaciones is None:
            # En 2D, por defecto solo el conjunto que también da COCO-17.
            articulaciones = _CORE_ORDENADO if dims == 2 else _TODAS_3D
        self._articulaciones = articulaciones
        self._sin_deteccion = frames_sin_deteccion or set()
        self._ocluidas = articulaciones_ocluidas or {}
        self._conf_base = confianza_base

    id = "fake"
    version = "fake-1"

    @property
    def articulaciones_disponibles(self) -> tuple[ArticulacionCanonica, ...]:
        return self._articulaciones

    def _config(self) -> dict:
        return {
            "dims": self.dims,
            "articulaciones": [a.value for a in self._articulaciones],
            "sin_deteccion": sorted(self._sin_deteccion),
            "ocluidas": {a.value: c for a, c in sorted(self._ocluidas.items())},
            "confianza_base": self._conf_base,
        }

    def estimar_frame(self, frame_bgr: np.ndarray, indice: int) -> PoseFrame:  # noqa: ARG002
        if indice in self._sin_deteccion:
            return PoseFrame(indice=indice, detectado=False, puntos={})

        t = indice / 30.0  # "segundos" arbitrarios para la sinusoide
        vaiven = 0.03 * math.sin(2.0 * math.pi * 0.15 * t)  # balanceo global del cuerpo
        puntos: dict[ArticulacionCanonica, Punto] = {}
        puntos_mundo: dict[ArticulacionCanonica, Punto] = {}
        for art in self._articulaciones:
            bx, by, bz = _NOMINAL[art]
            ph = _fase(art)
            x = bx + vaiven + 0.02 * math.sin(2.0 * math.pi * 0.5 * t + ph)
            y = by + 0.012 * math.cos(2.0 * math.pi * 0.4 * t + ph)
            z = None if self.dims == 2 else bz + 0.03 * math.sin(2.0 * math.pi * 0.35 * t + ph)
            conf = self._ocluidas.get(art, self._conf_base)
            puntos[art] = Punto(x=x, y=y, z=z, confianza=conf)
            if self.dims == 3:
                # Pseudo-metros: normalizado centrado en 0.5, escala ~1.8 m de alto.
                puntos_mundo[art] = Punto(
                    x=(x - 0.5) * 1.8, y=(y - 0.5) * 1.8, z=z * 1.8, confianza=conf
                )
        return PoseFrame(
            indice=indice, detectado=True, puntos=puntos, puntos_mundo=puntos_mundo
        )
