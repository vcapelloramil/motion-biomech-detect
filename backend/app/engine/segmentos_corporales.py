"""Segmentos de la cadena cinética (plan, tareas 4.2–4.5; tesis §3.3.3.1).

La energía se transmite suelo → piernas y caderas → tronco → brazo. El sistema mide
el **orden** en que estos tres segmentos alcanzan su velocidad angular máxima:

    pelvis → torso → brazo

Cada segmento se representa por un vector director entre dos articulaciones
canónicas. `pelvis` y `torso` son ejes transversales (izquierda → derecha).

`brazo` va del hombro a la articulación distal del **lado dominante** (que se lee de
`catalogo.csv`, columna `lado_dominante`; no hay valor por defecto — decisión de
esta etapa, para no medir el brazo equivocado en silencio con un zurdo). Por
defecto la distal es el **codo** (`brazo_via="codo"`): es el eslabón anatómicamente
correcto del segmento "brazo" de la cadena, y la muñeca de la raqueta se pierde por
desenfoque de movimiento en el instante de mayor velocidad (hallazgo de la
validación cualitativa; ver decisión 008). `brazo_via="muneca"` queda disponible
para re-testear con el encuadre de tres cuartos en la Fase B.
"""

from __future__ import annotations

from enum import Enum

from app.engine.pose.articulaciones import ArticulacionCanonica as A

LADOS_VALIDOS = ("der", "izq")
BRAZO_VIA_VALIDOS = ("codo", "muneca")


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


def validar_brazo_via(brazo_via: str) -> str:
    if brazo_via not in BRAZO_VIA_VALIDOS:
        raise ValueError(f"brazo_via debe ser uno de {BRAZO_VIA_VALIDOS} (se recibió {brazo_via!r}).")
    return brazo_via


def vector_segmento(
    seg: SegmentoCadena, lado_dominante: str, *, brazo_via: str = "codo"
) -> tuple[A, A]:
    """(origen, extremo) del vector director del segmento."""
    validar_lado(lado_dominante)
    if seg is SegmentoCadena.PELVIS:
        return (A.CADERA_IZQ, A.CADERA_DER)
    if seg is SegmentoCadena.TORSO:
        return (A.HOMBRO_IZQ, A.HOMBRO_DER)
    validar_brazo_via(brazo_via)
    dom = "DER" if lado_dominante == "der" else "IZQ"
    distal = "CODO" if brazo_via == "codo" else "MUNECA"
    return (A[f"HOMBRO_{dom}"], A[f"{distal}_{dom}"])


def articulaciones_de_segmento(
    seg: SegmentoCadena, lado_dominante: str, *, brazo_via: str = "codo"
) -> tuple[A, ...]:
    """Articulaciones de las que depende el segmento (para propagar 'no auditable')."""
    return vector_segmento(seg, lado_dominante, brazo_via=brazo_via)
