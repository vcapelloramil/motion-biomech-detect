"""E4 — Cinemática: ángulos y velocidades angulares (plan, tareas 4.1–4.3).

Todo opera sobre `puntos_mundo` (métrico, ya filtrado por E3).

- **Ángulo entre tres puntos** (4.1): producto escalar. Funciona para bisagras —
  rodilla, codo, tronco-muslo (§3.3.3.4). Inmune al desvío fijo y a la escala
  (§3.3.4.2, fila 2).
- **Separación cadera-hombro** (4.2): ángulo entre el eje de la pelvis y el eje de
  los hombros. De las magnitudes más confiables (§3.3.4.2, fila 3).
- **Velocidad angular de un segmento** (4.3): tasa de cambio de la orientación 3D
  del vector director del segmento, como escalar (sin elegir plano):
  ω(t) ≈ ∠(u(t), u(t+1)) · fps. En °/s. Para clips con `escala_temporal_conocida
  = False` el valor absoluto es aproximado (fps estimado); el **instante** del
  pico no se afecta (§3.3.4.2, fila 6).
"""

from __future__ import annotations

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import SecuenciaPose
from app.engine.segmentos_corporales import SegmentoCadena, vector_segmento

# Ángulos articulares: (proximal, vértice, distal) por lado, con nombres base.
_TRIPLETES = {
    "rodilla": ("CADERA", "RODILLA", "TOBILLO"),
    "codo": ("HOMBRO", "CODO", "MUNECA"),
    "tronco_muslo": ("HOMBRO", "CADERA", "RODILLA"),
}


def _lateral(base: str, lado: str) -> A:
    return A[f"{base}_{'DER' if lado == 'der' else 'IZQ'}"]


def _xyz(punto) -> np.ndarray:
    z = np.nan if punto.z is None else punto.z
    return np.array([punto.x, punto.y, z], dtype=float)


def angulo_tres_puntos(prox: np.ndarray, vert: np.ndarray, dist: np.ndarray) -> float:
    """Ángulo en `vert` (grados) entre los segmentos vert→prox y vert→dist."""
    u = np.asarray(prox, float) - np.asarray(vert, float)
    v = np.asarray(dist, float) - np.asarray(vert, float)
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu == 0 or nv == 0 or np.isnan(nu) or np.isnan(nv):
        return float("nan")
    cos = np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))


def _puntos(frame, espacio: str):
    return frame.puntos if espacio == "imagen" else frame.puntos_mundo


def serie_angulo_articular(
    seq: SecuenciaPose, nombre: str, lado: str, *, espacio: str = "mundo"
) -> np.ndarray:
    """Serie temporal (grados) del ángulo articular. NaN donde falta algún punto."""
    if nombre not in _TRIPLETES:
        raise ValueError(f"ángulo desconocido: {nombre!r}. Opciones: {list(_TRIPLETES)}")
    prox, vert, dist = (_lateral(a, lado) for a in _TRIPLETES[nombre])
    salida = np.full(seq.n_frames, np.nan)
    for i, frame in enumerate(seq.frames):
        pts = _puntos(frame, espacio)
        if prox in pts and vert in pts and dist in pts:
            salida[i] = angulo_tres_puntos(
                _xyz(pts[prox]), _xyz(pts[vert]), _xyz(pts[dist])
            )
    return salida


def serie_separacion_cadera_hombro(
    seq: SecuenciaPose, *, espacio: str = "mundo"
) -> np.ndarray:
    """Ángulo (grados) entre el eje de la pelvis y el eje de los hombros, por fotograma."""
    salida = np.full(seq.n_frames, np.nan)
    for i, frame in enumerate(seq.frames):
        pts = _puntos(frame, espacio)
        if not all(
            a in pts for a in (A.CADERA_IZQ, A.CADERA_DER, A.HOMBRO_IZQ, A.HOMBRO_DER)
        ):
            continue
        pelvis = _xyz(pts[A.CADERA_DER]) - _xyz(pts[A.CADERA_IZQ])
        hombros = _xyz(pts[A.HOMBRO_DER]) - _xyz(pts[A.HOMBRO_IZQ])
        np_, nh = np.linalg.norm(pelvis), np.linalg.norm(hombros)
        if np_ == 0 or nh == 0:
            continue
        cos = np.clip(np.dot(pelvis, hombros) / (np_ * nh), -1.0, 1.0)
        salida[i] = np.degrees(np.arccos(cos))
    return salida


def _angulo_entre(u: np.ndarray, v: np.ndarray) -> float:
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu == 0 or nv == 0 or np.isnan(nu) or np.isnan(nv):
        return float("nan")
    return float(np.arccos(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0)))


def velocidad_angular_segmento(
    seq: SecuenciaPose,
    seg: SegmentoCadena,
    lado_dominante: str,
    *,
    espacio: str = "mundo",
) -> np.ndarray:
    """Velocidad angular del segmento en °/s, alineada a los fotogramas de `seq`.

    ω[i] = ∠(u[i-1], u[i]) · fps ; ω[0] se copia de ω[1]. NaN donde falte un extremo.
    """
    origen_art, extremo_art = vector_segmento(seg, lado_dominante)
    fps = seq.fps_efectivos
    n = seq.n_frames
    u = np.full((n, 3), np.nan)
    for i, frame in enumerate(seq.frames):
        pts = _puntos(frame, espacio)
        if origen_art in pts and extremo_art in pts:
            d = _xyz(pts[extremo_art]) - _xyz(pts[origen_art])
            nd = np.linalg.norm(d)
            if nd > 0:
                u[i] = d / nd

    omega = np.full(n, np.nan)
    for i in range(1, n):
        if not (np.isnan(u[i]).any() or np.isnan(u[i - 1]).any()):
            omega[i] = np.degrees(_angulo_entre(u[i - 1], u[i])) * fps
    if n > 1:
        omega[0] = omega[1]
    return omega
