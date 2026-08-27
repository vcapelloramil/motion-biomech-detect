"""E3 — Análisis residual de Winter (plan, tarea 3.2; tesis §3.4.2.4).

Elige la frecuencia de corte de forma objetiva en vez de arbitraria. Para cada
corte candidato se filtra la señal y se mide el residuo RMS (cruda − filtrada). A
cortes altos el residuo es solo ruido que se saca y decrece de forma casi lineal;
extrapolando esa recta a corte→0 se estima el nivel de ruido. El corte elegido es
el más bajo cuyo residuo ya bajó hasta ese nivel: saca el ruido sin empezar a
comerse el movimiento real.

**Un corte por clip** (no por articulación): simplificación deliberada porque el
contrato del reporte, congelado en la Etapa 0, tiene un solo
``trazabilidad.filtro.corte_hz``. No es una limitación técnica —el análisis se
hace por serie— y si la Etapa 4 lo necesita, se pasa a un corte por articulación.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from app.engine.dsp import ORDEN_POR_DEFECTO, butterworth_fase_cero
from app.engine.pose.articulaciones import ArticulacionCanonica

# Multiplicador sobre el nivel de ruido estimado: el corte es donde el residuo
# baja a (nivel * este factor). 1.0 = exactamente el nivel de ruido.
FACTOR_NIVEL_RUIDO = 1.05

# Articulaciones rápidas: fijan el corte (necesitan la banda más ancha).
ARTICULACIONES_RAPIDAS = (
    ArticulacionCanonica.MUNECA_DER,
    ArticulacionCanonica.MUNECA_IZQ,
    ArticulacionCanonica.CODO_DER,
    ArticulacionCanonica.CODO_IZQ,
)


@dataclass(frozen=True)
class ResultadoWinter:
    corte_elegido_hz: float
    cortes_hz: list[float] = field(default_factory=list)
    residuos_rms: list[float] = field(default_factory=list)
    nivel_ruido_estimado: float = 0.0
    n_series: int = 0


def _cortes_por_defecto(fps: float) -> np.ndarray:
    # El movimiento humano relevante vive por debajo de ~15 Hz (§3.4.2). Se prueba
    # hasta cerca de ahí o de Nyquist, lo que sea menor.
    tope = min(20.0, fps / 2.0 - 1.0)
    if tope <= 2.0:
        return np.array([tope]) if tope > 0 else np.array([1.0])
    return np.arange(2.0, tope + 1e-9, 1.0)


def residuo_rms(serie: np.ndarray, *, fps: float, corte_hz: float, orden: int) -> float:
    filtrada = butterworth_fase_cero(serie, fps=fps, corte_hz=corte_hz, orden=orden)
    return float(np.sqrt(np.mean((serie - filtrada) ** 2)))


def analizar_serie(
    serie: np.ndarray,
    *,
    fps: float,
    cortes_hz: np.ndarray | None = None,
    orden: int = ORDEN_POR_DEFECTO,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Devuelve (cortes, residuos_rms, nivel_ruido_estimado) para una serie 1D."""
    serie = np.asarray(serie, dtype=float)
    serie = serie[~np.isnan(serie)]
    cortes = _cortes_por_defecto(fps) if cortes_hz is None else np.asarray(cortes_hz, float)
    residuos = np.array(
        [residuo_rms(serie, fps=fps, corte_hz=fc, orden=orden) for fc in cortes]
    )
    # Recta de ruido: ajustada a la mitad superior de cortes (zona dominada por ruido).
    mitad = max(2, len(cortes) // 2)
    pend, ordenada = np.polyfit(cortes[-mitad:], residuos[-mitad:], 1)
    nivel = float(max(ordenada, 0.0))  # extrapolación a corte -> 0
    return cortes, residuos, nivel


def elegir_corte(
    series: dict[tuple[ArticulacionCanonica, str], np.ndarray],
    *,
    fps: float,
    articulaciones: tuple[ArticulacionCanonica, ...] = ARTICULACIONES_RAPIDAS,
    cortes_hz: np.ndarray | None = None,
    orden: int = ORDEN_POR_DEFECTO,
    factor_nivel: float = FACTOR_NIVEL_RUIDO,
) -> ResultadoWinter:
    """Un corte para toda la secuencia: el máximo de los cortes por serie rápida."""
    relevantes = [
        s
        for (art, _coord), s in series.items()
        if art in articulaciones and np.count_nonzero(~np.isnan(s)) > 30
    ]
    if not relevantes:
        relevantes = [s for s in series.values() if np.count_nonzero(~np.isnan(s)) > 30]
    if not relevantes:
        raise ValueError("no hay series suficientemente largas para el análisis de Winter.")

    cortes_ref: np.ndarray | None = None
    residuos_prom = None
    cortes_por_serie: list[float] = []
    for serie in relevantes:
        cortes, residuos, nivel = analizar_serie(
            serie, fps=fps, cortes_hz=cortes_hz, orden=orden
        )
        cortes_ref = cortes
        residuos_prom = residuos if residuos_prom is None else residuos_prom + residuos
        umbral = nivel * factor_nivel
        bajo = np.where(residuos <= umbral)[0]
        cortes_por_serie.append(float(cortes[bajo[0]] if len(bajo) else cortes[-1]))

    corte = max(cortes_por_serie)
    residuos_prom = residuos_prom / len(relevantes)
    _, _, nivel_global = analizar_serie(
        relevantes[0], fps=fps, cortes_hz=cortes_hz, orden=orden
    )
    return ResultadoWinter(
        corte_elegido_hz=corte,
        cortes_hz=[float(c) for c in cortes_ref],
        residuos_rms=[float(r) for r in residuos_prom],
        nivel_ruido_estimado=nivel_global,
        n_series=len(relevantes),
    )
