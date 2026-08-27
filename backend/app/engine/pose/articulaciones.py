"""Mapa articular canónico interno (plan, tarea 2.3).

MediaPipe entrega 33 puntos y YOLOv8-Pose (COCO) entrega 17. Para que ambos
alimenten el mismo motor sin que E3/E4 sepan qué backend se usó, cada backend
traduce sus índices a este vocabulario común.

Nombres en español, laterales `IZQ`/`DER` según la etiqueta que da el modelo (que
es la izquierda/derecha anatómica del jugador, no la de la imagen).

Referencias de tesis:
- §3.3.2.3 / §4.4.3: YOLOv8-Pose son 17 puntos (x, y, visibilidad), sin profundidad.
- §3.3.3.4: el ángulo entre tres puntos sirve para codo y rodilla (bisagra), no
  para la rotación del hombro; con los 17 de COCO (sin puntos en la mano) esa
  rotación no se puede estimar. Los puntos de mano de MediaPipe (índice, meñique)
  habilitan un indicador indirecto.
- §3.3.2.8: la cadera es lo más confiable; muñecas y tobillos, lo menos.
"""

from __future__ import annotations

from enum import Enum


class ArticulacionCanonica(str, Enum):
    NARIZ = "nariz"

    HOMBRO_IZQ = "hombro_izq"
    HOMBRO_DER = "hombro_der"
    CODO_IZQ = "codo_izq"
    CODO_DER = "codo_der"
    MUNECA_IZQ = "muneca_izq"
    MUNECA_DER = "muneca_der"

    CADERA_IZQ = "cadera_izq"
    CADERA_DER = "cadera_der"
    RODILLA_IZQ = "rodilla_izq"
    RODILLA_DER = "rodilla_der"
    TOBILLO_IZQ = "tobillo_izq"
    TOBILLO_DER = "tobillo_der"

    # Solo los provee MediaPipe (33 puntos). Habilitan indicadores de mano/pie.
    INDICE_IZQ = "indice_izq"
    INDICE_DER = "indice_der"
    MENIQUE_IZQ = "menique_izq"
    MENIQUE_DER = "menique_der"
    PIE_IZQ = "pie_izq"
    PIE_DER = "pie_der"


# Articulaciones que cualquier backend (incluido COCO-17) debe poder entregar.
ARTICULACIONES_CORE: frozenset[ArticulacionCanonica] = frozenset(
    {
        ArticulacionCanonica.NARIZ,
        ArticulacionCanonica.HOMBRO_IZQ,
        ArticulacionCanonica.HOMBRO_DER,
        ArticulacionCanonica.CODO_IZQ,
        ArticulacionCanonica.CODO_DER,
        ArticulacionCanonica.MUNECA_IZQ,
        ArticulacionCanonica.MUNECA_DER,
        ArticulacionCanonica.CADERA_IZQ,
        ArticulacionCanonica.CADERA_DER,
        ArticulacionCanonica.RODILLA_IZQ,
        ArticulacionCanonica.RODILLA_DER,
        ArticulacionCanonica.TOBILLO_IZQ,
        ArticulacionCanonica.TOBILLO_DER,
    }
)


# --- MediaPipe Pose: 33 landmarks -> canónico -------------------------------
# Índices según mediapipe.solutions.pose.PoseLandmark.
MEDIAPIPE_A_CANONICO: dict[int, ArticulacionCanonica] = {
    0: ArticulacionCanonica.NARIZ,
    11: ArticulacionCanonica.HOMBRO_IZQ,
    12: ArticulacionCanonica.HOMBRO_DER,
    13: ArticulacionCanonica.CODO_IZQ,
    14: ArticulacionCanonica.CODO_DER,
    15: ArticulacionCanonica.MUNECA_IZQ,
    16: ArticulacionCanonica.MUNECA_DER,
    17: ArticulacionCanonica.MENIQUE_IZQ,
    18: ArticulacionCanonica.MENIQUE_DER,
    19: ArticulacionCanonica.INDICE_IZQ,
    20: ArticulacionCanonica.INDICE_DER,
    23: ArticulacionCanonica.CADERA_IZQ,
    24: ArticulacionCanonica.CADERA_DER,
    25: ArticulacionCanonica.RODILLA_IZQ,
    26: ArticulacionCanonica.RODILLA_DER,
    27: ArticulacionCanonica.TOBILLO_IZQ,
    28: ArticulacionCanonica.TOBILLO_DER,
    31: ArticulacionCanonica.PIE_IZQ,
    32: ArticulacionCanonica.PIE_DER,
}

# --- COCO-17 (YOLOv8-Pose) -> canónico -------------------------------------
COCO_A_CANONICO: dict[int, ArticulacionCanonica] = {
    0: ArticulacionCanonica.NARIZ,
    5: ArticulacionCanonica.HOMBRO_IZQ,
    6: ArticulacionCanonica.HOMBRO_DER,
    7: ArticulacionCanonica.CODO_IZQ,
    8: ArticulacionCanonica.CODO_DER,
    9: ArticulacionCanonica.MUNECA_IZQ,
    10: ArticulacionCanonica.MUNECA_DER,
    11: ArticulacionCanonica.CADERA_IZQ,
    12: ArticulacionCanonica.CADERA_DER,
    13: ArticulacionCanonica.RODILLA_IZQ,
    14: ArticulacionCanonica.RODILLA_DER,
    15: ArticulacionCanonica.TOBILLO_IZQ,
    16: ArticulacionCanonica.TOBILLO_DER,
}


def articulaciones_de(mapa: dict[int, ArticulacionCanonica]) -> tuple[ArticulacionCanonica, ...]:
    """Articulaciones canónicas que produce un mapa, en orden estable."""
    vistas = {art for art in mapa.values()}
    return tuple(a for a in ArticulacionCanonica if a in vistas)
