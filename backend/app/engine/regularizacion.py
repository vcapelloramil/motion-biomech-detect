"""Regularización temporal: de marcas de tiempo irregulares a una grilla uniforme (decisión 029).

Un archivo "Actual" del iPhone trae las marcas de tiempo REALES de cada fotograma: nominal 240 fps (1/240 s) pero con fotogramas
perdidos (tasa real media ~199, intervalos de 1 o 3 períodos). El filtro de fase cero de E3 y las derivadas de E4 suponen muestreo
**uniforme**. Tratar esa serie como uniforme (lo que se hace con un archivo horneado) corre el tiempo de las poses: velocidades
infladas y picos corridos unos milisegundos (ver ``docs/resultados/tasa-real-sensibilidad.json``).

Esta etapa interpola las coordenadas de cada articulación a una grilla uniforme a la tasa nominal, **antes** de E3. Los fotogramas que
ya caen sobre la grilla se copian sin tocar; los que faltan se interpolan con un spline cúbico (error despreciable para el contenido
del gesto, < 20 Hz, con huecos de hasta 12,5 ms). **Nada se inventa más allá de un hueco máximo:** si faltan más de
``hueco_max_periodos`` períodos seguidos, ese punto de la grilla queda sin detectar y E3/E4 lo tratan como tramo no auditable (R3).

Regla R4: lo que esta etapa hizo queda en ``InfoRegularizacion`` (cuántos puntos se interpolaron, el hueco máximo, cuántos quedaron sin
dato), para que viaje en la trazabilidad del reporte.

Función pura sobre ``SecuenciaPose``: no toca archivos.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

import numpy as np

from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose

# Un fotograma fuente "cae sobre" un punto de la grilla si la diferencia es menor que esta fracción del período. Los iPhone marcan en una
# base de 1/2400 s y unos pocos fotogramas (~4 %) quedan ±0,4 ms fuera de la grilla de 1/240 s: con 0,15 períodos (0,6 ms) se copian
# en vez de recalcular, y el conteo de puntos interpolados es el de los fotogramas que de verdad faltan. 0,6 ms * 1000 °/s = 0,6°, por
# debajo del ruido de la pose.
_TOLERANCIA_PERIODO = 0.15
# Hueco máximo que se interpola, en períodos de la grilla. 6 períodos a 240 fps = 25 ms.
HUECO_MAX_PERIODOS = 6


@dataclass(frozen=True)
class InfoRegularizacion:
    """Qué hizo la regularización (trazabilidad, R4)."""

    n_fuente: int                 # fotogramas visibles de entrada
    n_grilla: int                 # puntos de la grilla uniforme de salida
    n_copiados: int               # puntos de la grilla que coinciden con un fotograma fuente
    n_interpolados: int           # puntos de la grilla calculados por interpolación
    n_sin_dato: int               # puntos de la grilla que quedaron sin detectar (hueco demasiado largo o sin detección)
    fps_grilla: float
    fps_real_medio: float
    hueco_maximo_ms: float        # el intervalo más largo entre fotogramas fuente consecutivos

    @property
    def fraccion_interpolada(self) -> float:
        return self.n_interpolados / self.n_grilla if self.n_grilla else 0.0

    def como_dict(self) -> dict:
        return {
            "fotogramas_fuente": self.n_fuente,
            "puntos_de_la_grilla": self.n_grilla,
            "puntos_copiados": self.n_copiados,
            "puntos_interpolados": self.n_interpolados,
            "puntos_interpolados_pct": round(100 * self.fraccion_interpolada, 2),
            "puntos_sin_dato": self.n_sin_dato,
            "fps_grilla": self.fps_grilla,
            "fps_real_medio": round(self.fps_real_medio, 3),
            "hueco_maximo_ms": round(self.hueco_maximo_ms, 2),
        }


def alinear_marcas(n_fotogramas: int, pts_paquetes, pts_decodificados) -> tuple[np.ndarray | None, str]:
    """Marcas de tiempo, una por fotograma decodificado, o ``(None, motivo)`` si no se puede asignar tiempo sin adivinar (R3).

    * Las cantidades coinciden con los paquetes visibles: se usan esas marcas.
    * No coinciden: se usan las de los fotogramas decodificados (``pts_decodificados``), pero SOLO si son exactamente
      ``n_fotogramas`` y cada una es una marca de algún paquete visible (subconjunto). Nada se supone: no se asume que lo que
      falta esté al final, se comprueba qué marcas existen.
    """
    paquetes = None if pts_paquetes is None else np.asarray(pts_paquetes, dtype=float)
    if paquetes is not None and paquetes.size == n_fotogramas:
        return paquetes, "coinciden"
    if pts_decodificados is None:
        return None, "las cantidades no coinciden y no se pudieron leer las marcas de los fotogramas decodificados"
    decod = np.asarray(pts_decodificados, dtype=float)
    if decod.size != n_fotogramas:
        return None, f"se decodificaron {n_fotogramas} fotogramas y ffprobe lista {decod.size}: no coinciden"
    if paquetes is not None and paquetes.size:
        # cada marca decodificada tiene que ser una marca de paquete (tolerancia de 1 µs por el redondeo del texto)
        idx = np.searchsorted(paquetes, decod)
        idx = np.clip(idx, 1, paquetes.size - 1)
        cerca = np.minimum(np.abs(paquetes[idx - 1] - decod), np.abs(paquetes[idx] - decod))
        if np.any(cerca > 1e-6):
            return None, "hay fotogramas decodificados cuya marca no está entre los paquetes visibles"
    return decod, "decodificados"


def _serie(frames: list[PoseFrame], espacio: str, art) -> tuple[np.ndarray, np.ndarray]:
    """(valores[n, 4] = x, y, z, confianza; validos[n]) de una articulación en un espacio ('puntos' o 'puntos_mundo')."""
    n = len(frames)
    vals = np.full((n, 4), np.nan)
    ok = np.zeros(n, dtype=bool)
    for i, f in enumerate(frames):
        p = getattr(f, espacio).get(art)
        if p is None:
            continue
        vals[i] = (p.x, p.y, np.nan if p.z is None else p.z, p.confianza)
        ok[i] = True
    return vals, ok


def _evaluar(t_fuente: np.ndarray, vals: np.ndarray, ok: np.ndarray, t_grilla: np.ndarray) -> np.ndarray:
    """Valores de una serie en ``t_grilla`` por spline cúbico sobre los puntos válidos (lineal si hay menos de 4)."""
    from scipy.interpolate import CubicSpline

    salida = np.full((t_grilla.size, 4), np.nan)
    idx = np.flatnonzero(ok)
    if idx.size < 2:
        return salida
    t = t_fuente[idx]
    for c in range(4):
        y = vals[idx, c]
        if np.all(np.isnan(y)):
            continue                                     # p. ej. z en un backend 2D
        if idx.size >= 4:
            salida[:, c] = CubicSpline(t, y, bc_type="not-a-knot")(t_grilla)
        else:
            salida[:, c] = np.interp(t_grilla, t, y)
    salida[:, 3] = np.clip(salida[:, 3], 0.0, 1.0)       # la confianza no se sale de [0, 1]
    return salida


def regularizar(
    seq: SecuenciaPose, pts: np.ndarray, fps_grilla: float, *, hueco_max_periodos: int = HUECO_MAX_PERIODOS
) -> tuple[SecuenciaPose, InfoRegularizacion]:
    """Remuestrea ``seq`` (un fotograma por marca de ``pts``) a una grilla uniforme de ``fps_grilla`` Hz.

    ``pts`` son las marcas de tiempo (segundos, crecientes) de los fotogramas visibles, una por fotograma de ``seq``.
    """
    pts = np.asarray(pts, dtype=float)
    if len(seq.frames) != pts.size:
        raise ValueError(
            f"la secuencia tiene {len(seq.frames)} fotogramas y hay {pts.size} marcas de tiempo: no se puede asignar tiempo"
        )
    if pts.size < 2 or np.any(np.diff(pts) <= 0):
        raise ValueError("las marcas de tiempo tienen que ser estrictamente crecientes y ser al menos dos")
    if fps_grilla <= 0:
        raise ValueError("la tasa de la grilla tiene que ser positiva")

    periodo = 1.0 / fps_grilla
    t0 = float(pts[0])
    n_grilla = int(np.floor((pts[-1] - t0) / periodo + 1e-9)) + 1
    t_grilla = t0 + periodo * np.arange(n_grilla)

    # Para cada punto de la grilla: el fotograma fuente anterior (i0), si coincide con uno, y el hueco que lo rodea.
    i0 = np.clip(np.searchsorted(pts, t_grilla + 1e-12, side="right") - 1, 0, pts.size - 1)
    i1 = np.clip(i0 + 1, 0, pts.size - 1)
    cae_sobre = np.abs(t_grilla - pts[i0]) <= _TOLERANCIA_PERIODO * periodo
    cae_sobre_sig = np.abs(t_grilla - pts[i1]) <= _TOLERANCIA_PERIODO * periodo
    fuente_exacta = np.where(cae_sobre, i0, np.where(cae_sobre_sig, i1, -1))
    hueco = pts[i1] - pts[i0]
    hueco_largo = (fuente_exacta < 0) & (hueco > hueco_max_periodos * periodo + 1e-12)

    articulaciones = seq.articulaciones
    espacios = ("puntos", "puntos_mundo")
    series = {(e, a): _serie(seq.frames, e, a) for e in espacios for a in articulaciones}
    interp = {
        (e, a): _evaluar(pts, series[(e, a)][0], series[(e, a)][1], t_grilla) for e in espacios for a in articulaciones
    }
    detectado_fuente = np.array([f.detectado for f in seq.frames], dtype=bool)

    nuevos: list[PoseFrame] = []
    n_sin_dato = 0
    for k in range(n_grilla):
        exacto = int(fuente_exacta[k])
        if exacto >= 0:
            f = seq.frames[exacto]
            nuevos.append(dataclasses.replace(f, indice=k))
            continue
        if hueco_largo[k] or not (detectado_fuente[i0[k]] and detectado_fuente[i1[k]]):
            nuevos.append(PoseFrame(indice=k, detectado=False))
            n_sin_dato += 1
            continue
        datos: dict[str, dict] = {"puntos": {}, "puntos_mundo": {}}
        for e in espacios:
            for a in articulaciones:
                _, ok = series[(e, a)]
                if not (ok[i0[k]] and ok[i1[k]]):
                    continue                       # la articulación no se vio en alguno de los dos vecinos: no se inventa
                x, y, z, c = interp[(e, a)][k]
                if np.isnan(x) or np.isnan(y):
                    continue
                datos[e][a] = Punto(float(x), float(y), None if np.isnan(z) else float(z), float(c))
        nuevos.append(PoseFrame(indice=k, detectado=True, puntos=datos["puntos"], puntos_mundo=datos["puntos_mundo"]))

    n_copiados = int(np.sum(fuente_exacta >= 0))
    info = InfoRegularizacion(
        n_fuente=int(pts.size),
        n_grilla=n_grilla,
        n_copiados=n_copiados,
        n_interpolados=n_grilla - n_copiados - n_sin_dato,
        n_sin_dato=n_sin_dato,
        fps_grilla=float(fps_grilla),
        fps_real_medio=float((pts.size - 1) / (pts[-1] - pts[0])),
        hueco_maximo_ms=float(np.max(np.diff(pts)) * 1000),
    )
    return dataclasses.replace(seq, frames=nuevos, fps_efectivos=float(fps_grilla)), info
