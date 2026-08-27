"""Segmentos de la cadena cinética (plan, tareas 4.2–4.5; tesis §3.3.3.1).

La energía se transmite suelo → piernas y caderas → tronco → brazo. El sistema mide
el **orden** en que estos tres segmentos alcanzan su velocidad angular máxima:

    pelvis → torso → brazo

Cada segmento se representa por un vector director entre dos articulaciones
canónicas. `pelvis` y `torso` son ejes transversales (izquierda → derecha);
`brazo` va del hombro a la muñeca del **lado dominante** (que se lee de
`catalogo.csv`, columna `lado_dominante`; no hay valor por defecto — decisión de
esta etapa, para no medir el brazo equivocado en silencio con un zurdo).
"""

from __future__ import annotations

from enum import Enum

from app.engine.pose.articulaciones import ArticulacionCanonica as A

LADOS_VALIDOS = ("der", "izq")


class SegmentoCadena(str, Enum):
    PELVIS = "pelvis"
    TORSO = "torso"
    BRAZO = "brazo"


ORDEN_ESPERADO: tuple[SegmentoCadena, ...] = (
    SegmentoCadena.PELVIS,
    SegmentoCadena.TORSO,
    SegmentoCadena.BRAZO,
)


def validar_lado(lado_dominante: str) -> str:
    if lado_dominante not in LADOS_VALIDOS:
        raise ValueError(
            f"lado_dominante debe ser uno de {LADOS_VALIDOS} (se recibió "
            f"{lado_dominante!r}). Se lee de la columna 'lado_dominante' del "
            f"catalogo.csv; si está vacía, hay que completarla."
        )
    return lado_dominante


def vector_segmento(seg: SegmentoCadena, lado_dominante: str) -> tuple[A, A]:
    """(origen, extremo) del vector director del segmento."""
    validar_lado(lado_dominante)
    if seg is SegmentoCadena.PELVIS:
        return (A.CADERA_IZQ, A.CADERA_DER)
    if seg is SegmentoCadena.TORSO:
        return (A.HOMBRO_IZQ, A.HOMBRO_DER)
    dom = "DER" if lado_dominante == "der" else "IZQ"
    return (getattr(A, f"HOMBRO_{dom}"), getattr(A, f"MUNECA_{dom}"))


def articulaciones_de_segmento(seg: SegmentoCadena, lado_dominante: str) -> tuple[A, ...]:
    """Articulaciones de las que depende el segmento (para propagar 'no auditable')."""
    return vector_segmento(seg, lado_dominante)
