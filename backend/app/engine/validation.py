"""E2b — Validación de los puntos de pose (plan, tarea 2.4).

Dos controles independientes sobre una ``SecuenciaPose``:

1. **Confianza baja.** Puntos por debajo de un umbral de confianza. No se descartan
   acá: se listan para que E3 los interpole o excluya antes de filtrar (tesis
   §3.4.2.6). Un dato de baja confianza que se hace pasar por bueno es peor que un
   dato faltante (regla R3, tesis §3.3.2.1).

2. **Saltos imposibles.** Un punto que se desplaza demasiado entre dos fotogramas
   consecutivos: eso no es movimiento, es un error de detección (un punto
   confiadamente equivocado, que la confianza sola no atrapa). El umbral se expresa
   en **fracciones de la longitud del torso** (distancia cadera-hombro), que es la
   regla interna: es de las magnitudes más estables (tesis §3.3.3.2) y evita
   depender de una escala métrica que el material descargado no tiene.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose

UMBRAL_CONFIANZA = 0.5
MAX_SALTO_TORSOS = 0.5


@dataclass(frozen=True)
class SaltoImposible:
    articulacion: ArticulacionCanonica
    frame_desde: int
    frame_hasta: int
    desplazamiento_torsos: float


@dataclass
class ResultadoValidacion:
    umbral_confianza: float
    max_salto_torsos: float
    puntos_baja_confianza: list[tuple[int, ArticulacionCanonica]] = field(default_factory=list)
    saltos_imposibles: list[SaltoImposible] = field(default_factory=list)
    # Fracción de fotogramas en que cada articulación está presente y por encima
    # del umbral de confianza. Se reporta por articulación, no como número único
    # (tesis §3.3.2.8).
    cobertura_auditable: dict[ArticulacionCanonica, float] = field(default_factory=dict)

    @property
    def n_baja_confianza(self) -> int:
        return len(self.puntos_baja_confianza)

    @property
    def n_saltos(self) -> int:
        return len(self.saltos_imposibles)


# Espacio de coordenadas sobre el que trabaja la validación. E3 usa "mundo"
# (métrico, centrado en caderas): quita la traslación por paneo de cámara, así un
# salto real se distingue mejor. Los backends 2D puros solo tienen "imagen".
_ESPACIOS = ("imagen", "mundo")


def _puntos(frame: PoseFrame, espacio: str) -> dict[ArticulacionCanonica, Punto]:
    return frame.puntos if espacio == "imagen" else frame.puntos_mundo


def _dist(a: Punto, b: Punto) -> float:
    dz = 0.0 if (a.z is None or b.z is None) else (a.z - b.z)
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + dz**2)


def largo_torso(frame: PoseFrame, *, espacio: str = "imagen") -> float | None:
    """Distancia media hombro-cadera (mismo lado). None si falta un lado completo."""
    puntos = _puntos(frame, espacio)
    lados = (
        (ArticulacionCanonica.HOMBRO_IZQ, ArticulacionCanonica.CADERA_IZQ),
        (ArticulacionCanonica.HOMBRO_DER, ArticulacionCanonica.CADERA_DER),
    )
    largos = [
        _dist(puntos[h], puntos[c])
        for h, c in lados
        if h in puntos and c in puntos
    ]
    return sum(largos) / len(largos) if largos else None


def marcar_baja_confianza(
    seq: SecuenciaPose, *, umbral: float = UMBRAL_CONFIANZA, espacio: str = "imagen"
) -> list[tuple[int, ArticulacionCanonica]]:
    marcados: list[tuple[int, ArticulacionCanonica]] = []
    for frame in seq.frames:
        for art, punto in _puntos(frame, espacio).items():
            if punto.confianza < umbral:
                marcados.append((frame.indice, art))
    return marcados


def detectar_saltos_imposibles(
    seq: SecuenciaPose, *, max_torsos: float = MAX_SALTO_TORSOS, espacio: str = "imagen"
) -> list[SaltoImposible]:
    saltos: list[SaltoImposible] = []
    for anterior, actual in zip(seq.frames, seq.frames[1:]):
        if not (anterior.detectado and actual.detectado):
            continue
        escala = largo_torso(actual, espacio=espacio) or largo_torso(
            anterior, espacio=espacio
        )
        if not escala or escala <= 0:
            continue  # sin escala interna no se puede juzgar
        p_ant = _puntos(anterior, espacio)
        for art, p_actual in _puntos(actual, espacio).items():
            if art not in p_ant:
                continue
            desplazamiento = _dist(p_ant[art], p_actual) / escala
            if desplazamiento > max_torsos:
                saltos.append(
                    SaltoImposible(
                        articulacion=art,
                        frame_desde=anterior.indice,
                        frame_hasta=actual.indice,
                        desplazamiento_torsos=desplazamiento,
                    )
                )
    return saltos


def _cobertura_auditable(
    seq: SecuenciaPose, umbral: float, espacio: str
) -> dict[ArticulacionCanonica, float]:
    if not seq.frames:
        return {}
    n = len(seq.frames)
    cobertura: dict[ArticulacionCanonica, float] = {}
    for art in seq.articulaciones:
        ok = sum(
            1
            for f in seq.frames
            if (p := _puntos(f, espacio).get(art)) is not None and p.confianza >= umbral
        )
        cobertura[art] = ok / n
    return cobertura


def validar(
    seq: SecuenciaPose,
    *,
    umbral_confianza: float = UMBRAL_CONFIANZA,
    max_salto_torsos: float = MAX_SALTO_TORSOS,
    espacio: str = "imagen",
) -> ResultadoValidacion:
    if espacio not in _ESPACIOS:
        raise ValueError(f"espacio debe ser uno de {_ESPACIOS}")
    return ResultadoValidacion(
        umbral_confianza=umbral_confianza,
        max_salto_torsos=max_salto_torsos,
        puntos_baja_confianza=marcar_baja_confianza(
            seq, umbral=umbral_confianza, espacio=espacio
        ),
        saltos_imposibles=detectar_saltos_imposibles(
            seq, max_torsos=max_salto_torsos, espacio=espacio
        ),
        cobertura_auditable=_cobertura_auditable(seq, umbral_confianza, espacio),
    )
