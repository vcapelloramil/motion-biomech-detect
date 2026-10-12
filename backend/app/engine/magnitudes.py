"""E4 — Magnitudes articulares del reporte, con la definición con que se VALIDARON (plan §8, punto 3).

Tres magnitudes que la tabla 4.7 de la tesis pone en el núcleo y el reporte todavía no traía:

* **Separación cadera-hombro máxima** (°): el máximo, dentro de la ventana de la repetición, del ángulo entre el eje de las caderas y el
  de los hombros; 3D, series filtradas por E3. Es la métrica (i) del Criterio 3 (decisión 014).
* **Ángulo de la rodilla** y **ángulo del codo** (°) en el instante del pico del tronco: ángulo interior en el vértice, **en el plano de
  la imagen** (píxeles, con el ancho y el alto del video) y del lado con mayor confianza mínima, exigiendo >= 0,6 en los tres puntos.
  Es exactamente la medición que se comparó contra la goniometría manual en el Criterio 2 (decisión 015: error medio de 8,5° en la rodilla y
  12,5° en el codo, p95 de 19,2° y 36,4°). **El ángulo 3D no está validado** y no se informa.

Funciones puras sobre estructuras de pose; sin archivos ni red.
"""

from __future__ import annotations

import math

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A

UMBRAL_CONFIANZA_ANGULO = 0.6          # la misma elegibilidad que el Criterio 2
COBERTURA_MIN_SEPARACION = 0.75        # fracción de la ventana con dato, igual que el pico de un segmento

TRIPLETES = {
    "rodilla": {"izq": (A.CADERA_IZQ, A.RODILLA_IZQ, A.TOBILLO_IZQ), "der": (A.CADERA_DER, A.RODILLA_DER, A.TOBILLO_DER)},
    "codo": {"izq": (A.HOMBRO_IZQ, A.CODO_IZQ, A.MUNECA_IZQ), "der": (A.HOMBRO_DER, A.CODO_DER, A.MUNECA_DER)},
}
ARTICULACIONES_SEPARACION = (A.CADERA_IZQ, A.CADERA_DER, A.HOMBRO_IZQ, A.HOMBRO_DER)

# Error medido contra goniometría manual ciega (decisión 015, Criterio 2): lo que el reporte muestra junto al valor (R4).
ERROR_VALIDADO = {
    "rodilla": {"media_grados": 8.5, "p95_grados": 19.2},
    "codo": {"media_grados": 12.5, "p95_grados": 36.4},
}


def angulo_en_vertice(a, v, c) -> float:
    """Ángulo interior (0–180°) en el vértice ``v`` entre los segmentos v→a y v→c (2D o 3D)."""
    u, w = np.asarray(a, float) - np.asarray(v, float), np.asarray(c, float) - np.asarray(v, float)
    nu, nw = np.linalg.norm(u), np.linalg.norm(w)
    if nu == 0 or nw == 0:
        return float("nan")
    return float(np.degrees(np.arccos(np.clip(np.dot(u, w) / (nu * nw), -1.0, 1.0))))


def mejor_lado(frame_puntos: dict, angulo: str) -> tuple[str, float] | None:
    """Lado ('izq'/'der') con mayor confianza mínima de los tres puntos del ángulo; ``None`` si en ninguno están los tres."""
    mejor = None
    for lado, arts in TRIPLETES[angulo].items():
        if not all(a in frame_puntos for a in arts):
            continue
        conf = min(frame_puntos[a].confianza for a in arts)
        if mejor is None or conf > mejor[1]:
            mejor = (lado, float(conf))
    return mejor


def angulo_2d(frame_puntos: dict, angulo: str, lado: str, ancho: int, alto: int) -> float:
    """Ángulo en el plano de la imagen (en píxeles: x * ancho, y * alto) del ``angulo`` ('rodilla' | 'codo') del ``lado``."""
    a, v, c = ((frame_puntos[x].x * ancho, frame_puntos[x].y * alto) for x in TRIPLETES[angulo][lado])
    return angulo_en_vertice(a, v, c)


def angulo_en_el_frame(frame_puntos: dict, angulo: str, ancho: int, alto: int) -> dict:
    """``{"lado", "valor", "confianza", "auditable"}``: el ángulo del mejor lado del fotograma, o no auditable si falta un punto o
    la confianza mínima no llega a ``UMBRAL_CONFIANZA_ANGULO`` (nunca se estima ni se rellena, R3)."""
    m = mejor_lado(frame_puntos, angulo)
    if m is None:
        return {"lado": None, "valor": None, "confianza": 0.0, "auditable": False}
    lado, conf = m
    if conf < UMBRAL_CONFIANZA_ANGULO:
        return {"lado": lado, "valor": None, "confianza": conf, "auditable": False}
    valor = angulo_2d(frame_puntos, angulo, lado, ancho, alto)
    if not math.isfinite(valor):
        return {"lado": lado, "valor": None, "confianza": conf, "auditable": False}
    return {"lado": lado, "valor": valor, "confianza": conf, "auditable": True}


def separacion_cadera_hombro_en(frame_puntos_mundo: dict) -> float:
    """Ángulo (°) entre el eje de las caderas y el de los hombros en un fotograma (coordenadas métricas); NaN si falta un punto."""
    if not all(a in frame_puntos_mundo for a in ARTICULACIONES_SEPARACION):
        return float("nan")

    def xyz(p):
        return np.array([p.x, p.y, np.nan if p.z is None else p.z], dtype=float)

    pelvis = xyz(frame_puntos_mundo[A.CADERA_DER]) - xyz(frame_puntos_mundo[A.CADERA_IZQ])
    hombros = xyz(frame_puntos_mundo[A.HOMBRO_DER]) - xyz(frame_puntos_mundo[A.HOMBRO_IZQ])
    return angulo_en_vertice(pelvis, np.zeros(3), hombros)


def separacion_cadera_hombro_max(frames_mundo: list[dict], desde: int, hasta: int) -> dict:
    """Máximo de la separación cadera-hombro en [desde, hasta] (inclusive) de la serie ``frames_mundo`` (lista de ``puntos_mundo``).

    ``{"valor", "frame", "cobertura", "auditable"}``: no auditable si se midió menos del ``COBERTURA_MIN_SEPARACION`` de la ventana
    (un máximo de una parte de la ventana no es el máximo de la ventana)."""
    serie = np.array(
        [separacion_cadera_hombro_en(frames_mundo[i]) for i in range(max(0, desde), min(len(frames_mundo) - 1, hasta) + 1)]
    )
    if serie.size == 0:
        return {"valor": None, "frame": None, "cobertura": 0.0, "auditable": False}
    validos = ~np.isnan(serie)
    cobertura = float(validos.mean())
    if not validos.any() or cobertura < COBERTURA_MIN_SEPARACION:
        return {"valor": None, "frame": None, "cobertura": cobertura, "auditable": False}
    k = int(np.nanargmax(serie))
    return {"valor": float(serie[k]), "frame": max(0, desde) + k, "cobertura": cobertura, "auditable": True}
