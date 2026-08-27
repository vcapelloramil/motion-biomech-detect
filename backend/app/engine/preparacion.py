"""E3 — Preparación de las series antes de filtrar (plan, tarea 3.3; tesis §3.4.2.5).

El filtro no elimina un dato disparatado: lo desparrama sobre los fotogramas
vecinos. Así que **antes** de filtrar hay que sacar los datos no confiables:

- fotogramas sin detección,
- puntos por debajo del umbral de confianza (de ``engine.validation``),
- puntos marcados como salto imposible (de ``engine.validation``).

Los huecos cortos (hasta ``GAP_MAX_INTERPOLABLE`` fotogramas) se interpolan
linealmente. Los más largos se dejan como ``NaN`` y se registran como tramos
excluidos: no se estiman (regla R3).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import SecuenciaPose
from app.engine.validation import ResultadoValidacion

# A ~500 fps efectivos son ~10 ms; a 240 fps, ~20 ms. Punto de partida acordado.
GAP_MAX_INTERPOLABLE = 5

_COORDS = ("x", "y", "z")


@dataclass(frozen=True)
class TramoExcluido:
    articulacion: ArticulacionCanonica
    coordenada: str
    desde_frame: int
    hasta_frame: int  # inclusive

    @property
    def largo(self) -> int:
        return self.hasta_frame - self.desde_frame + 1


def _tramos_nan(mascara_nan: np.ndarray, indices: np.ndarray) -> list[tuple[int, int]]:
    """Rangos [desde, hasta] (en índices de fotograma) donde la máscara es True."""
    tramos: list[tuple[int, int]] = []
    inicio = None
    for k, es_nan in enumerate(mascara_nan):
        if es_nan and inicio is None:
            inicio = k
        elif not es_nan and inicio is not None:
            tramos.append((int(indices[inicio]), int(indices[k - 1])))
            inicio = None
    if inicio is not None:
        tramos.append((int(indices[inicio]), int(indices[-1])))
    return tramos


def _interpolar_huecos_cortos(serie: np.ndarray, gap_max: int) -> np.ndarray:
    """Interpola linealmente los tramos de NaN de largo <= gap_max. Deja el resto."""
    serie = serie.copy()
    n = serie.size
    es_nan = np.isnan(serie)
    if not es_nan.any() or es_nan.all():
        return serie
    k = 0
    while k < n:
        if not es_nan[k]:
            k += 1
            continue
        j = k
        while j < n and es_nan[j]:
            j += 1
        # hueco [k, j-1]; bordes válidos en k-1 y j
        if k > 0 and j < n and (j - k) <= gap_max:
            izq, der = serie[k - 1], serie[j]
            serie[k:j] = np.linspace(izq, der, j - k + 2)[1:-1]
        k = j
    return serie


def preparar_series(
    seq: SecuenciaPose,
    validacion: ResultadoValidacion,
    *,
    espacio: str = "mundo",
    gap_max: int = GAP_MAX_INTERPOLABLE,
) -> tuple[dict[tuple[ArticulacionCanonica, str], np.ndarray], list[TramoExcluido]]:
    """Devuelve (series, tramos_excluidos).

    ``series[(articulacion, coord)]`` es un ``np.ndarray`` (n,) listo para filtrar:
    con los datos no confiables puestos en NaN, los huecos cortos interpolados, y
    los largos todavía en NaN (registrados en ``tramos_excluidos``).
    """
    frames = seq.frames
    n = len(frames)
    indices = np.array([f.indice for f in frames], dtype=np.int64)

    bajos = set(validacion.puntos_baja_confianza)  # (indice_frame, art)
    saltos = {(s.frame_hasta, s.articulacion) for s in validacion.saltos_imposibles}

    def _pts(frame):
        return frame.puntos if espacio == "imagen" else frame.puntos_mundo

    series: dict[tuple[ArticulacionCanonica, str], np.ndarray] = {}
    tramos: list[TramoExcluido] = []

    span_completo = (int(indices[0]), int(indices[-1]))

    for art in seq.articulaciones:
        crudas = {c: np.full(n, np.nan) for c in _COORDS}
        veces_presente = 0
        coord_tuvo_dato = {c: False for c in _COORDS}
        for i, frame in enumerate(frames):
            if not frame.detectado:
                continue
            p = _pts(frame).get(art)
            if p is None:
                continue
            veces_presente += 1
            coord_tuvo_dato["x"] = coord_tuvo_dato["y"] = True
            if p.z is not None:
                coord_tuvo_dato["z"] = True
            if (frame.indice, art) in bajos or (frame.indice, art) in saltos:
                continue  # el punto existe pero no es confiable
            crudas["x"][i] = p.x
            crudas["y"][i] = p.y
            if p.z is not None:
                crudas["z"][i] = p.z

        if veces_presente == 0:
            continue  # la articulación nunca se vio

        for coord in _COORDS:
            if not coord_tuvo_dato[coord]:
                continue  # la coordenada no existe (p. ej. z en un backend 2D)
            serie = crudas[coord]
            if np.isnan(serie).all():
                # existía pero todo quedó excluido: no auditable en todo el clip
                tramos.append(TramoExcluido(art, coord, *span_completo))
                continue
            preparada = _interpolar_huecos_cortos(serie, gap_max)
            series[(art, coord)] = preparada
            for desde, hasta in _tramos_nan(np.isnan(preparada), indices):
                tramos.append(TramoExcluido(art, coord, desde, hasta))

    return series, tramos
