"""E3 — Filtrado de fase cero (plan, tarea 3.1; tesis §3.4.2.1 y §3.4.2.3).

El movimiento real es de baja frecuencia; el ruido de la estimación de pose es de
alta frecuencia. Un pasa-bajos Butterworth conserva uno y elimina el otro sin
deformar la banda de paso.

**Fase cero es obligatorio.** Un filtro aplicado en un solo sentido corre la señal
en el tiempo, y el corrimiento depende del contenido frecuencial de cada segmento
—cambia el orden aparente de los picos, que es justo lo que el sistema mide—. La
solución es aplicarlo hacia adelante y hacia atrás (`filtfilt`), para que los
corrimientos se cancelen. **Nunca `lfilter`** en el pipeline.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, lfilter

ORDEN_POR_DEFECTO = 4


class ParametroDSPInvalido(ValueError):
    """Un parámetro del filtro no es admisible (corte fuera de Nyquist, serie corta)."""


def _coeficientes(fps: float, corte_hz: float, orden: int) -> tuple[np.ndarray, np.ndarray]:
    nyquist = fps / 2.0
    if corte_hz <= 0:
        raise ParametroDSPInvalido(f"corte_hz debe ser > 0 (se recibió {corte_hz}).")
    if corte_hz >= nyquist:
        raise ParametroDSPInvalido(
            f"corte_hz = {corte_hz} Hz >= Nyquist ({nyquist} Hz para fps = {fps}). "
            f"Ningún filtro puede separar frecuencias por encima de la mitad de la "
            f"tasa de muestreo (teorema del muestreo, §3.4.2.2)."
        )
    return butter(orden, corte_hz / nyquist, btype="low")


def _largo_minimo(b: np.ndarray, a: np.ndarray) -> int:
    # filtfilt necesita más muestras que el padlen por defecto (3 * max(len(a), len(b))).
    return 3 * max(len(a), len(b)) + 1


def butterworth_fase_cero(
    serie: np.ndarray,
    *,
    fps: float,
    corte_hz: float,
    orden: int = ORDEN_POR_DEFECTO,
) -> np.ndarray:
    """Pasa-bajos Butterworth aplicado adelante y atrás (`filtfilt`) → fase cero.

    ``serie`` es 1D (una coordenada de una articulación a lo largo del tiempo), sin
    NaN (los huecos se resuelven antes, en ``engine.preparacion``).
    """
    serie = np.asarray(serie, dtype=float)
    if serie.ndim != 1:
        raise ParametroDSPInvalido("la serie debe ser 1D.")
    if np.isnan(serie).any():
        raise ParametroDSPInvalido(
            "la serie tiene NaN; hay que preparar los huecos antes de filtrar."
        )
    b, a = _coeficientes(fps, corte_hz, orden)
    if serie.size < _largo_minimo(b, a):
        raise ParametroDSPInvalido(
            f"la serie tiene {serie.size} muestras; se necesitan al menos "
            f"{_largo_minimo(b, a)} para filtfilt con orden {orden}."
        )
    return filtfilt(b, a, serie)


def largo_minimo_segmento(*, fps: float, corte_hz: float, orden: int = ORDEN_POR_DEFECTO) -> int:
    """Muestras mínimas de un segmento continuo para poder filtrarlo con ``filtfilt``."""
    b, a = _coeficientes(fps, corte_hz, orden)
    return _largo_minimo(b, a)


def segmentos_continuos(serie: np.ndarray) -> list[tuple[int, int]]:
    """Rangos [desde, hasta] (posiciones, inclusive) de valores no-NaN consecutivos."""
    valido = ~np.isnan(np.asarray(serie, dtype=float))
    if not valido.any():
        return []
    bordes = np.flatnonzero(np.diff(valido.astype(np.int8)))
    inicios = [0] if valido[0] else []
    fines: list[int] = []
    for k in bordes:
        if valido[k + 1]:
            inicios.append(int(k + 1))
        else:
            fines.append(int(k))
    if valido[-1]:
        fines.append(len(valido) - 1)
    return list(zip(inicios, fines))


def butterworth_fase_cero_por_segmentos(
    serie: np.ndarray,
    *,
    fps: float,
    corte_hz: float,
    orden: int = ORDEN_POR_DEFECTO,
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    """Filtra de fase cero cada segmento continuo de una serie que tiene huecos (NaN).

    Devuelve ``(filtrada, no_filtrables)``:

    - los NaN se conservan exactamente donde estaban (no se interpola ni se rellena a
      través de un hueco: rellenar con ceros o con una recta inventaría movimiento y
      el filtro lo desparramaría hacia los datos buenos);
    - cada segmento con al menos ``largo_minimo_segmento`` muestras se filtra por
      separado con ``butterworth_fase_cero``;
    - un segmento MÁS CORTO no se puede filtrar y **no se deja crudo**: pasa a NaN
      (no auditable) y se devuelve en ``no_filtrables`` como rango [desde, hasta] de
      posiciones. Dejarlo crudo mezclaría datos ruidosos con datos filtrados sin
      avisar (regla R3).

    Antes de esta función, toda serie con algún NaN se dejaba entera sin filtrar.
    """
    serie = np.asarray(serie, dtype=float)
    if serie.ndim != 1:
        raise ParametroDSPInvalido("la serie debe ser 1D.")
    minimo = largo_minimo_segmento(fps=fps, corte_hz=corte_hz, orden=orden)
    salida = np.full_like(serie, np.nan)
    no_filtrables: list[tuple[int, int]] = []
    for desde, hasta in segmentos_continuos(serie):
        if hasta - desde + 1 >= minimo:
            salida[desde : hasta + 1] = butterworth_fase_cero(
                serie[desde : hasta + 1], fps=fps, corte_hz=corte_hz, orden=orden
            )
        else:
            no_filtrables.append((desde, hasta))
    return salida, no_filtrables


def _filtro_unidireccional(
    serie: np.ndarray,
    *,
    fps: float,
    corte_hz: float,
    orden: int = ORDEN_POR_DEFECTO,
) -> np.ndarray:
    """Solo para pruebas: filtrado en un sentido (`lfilter`), que SÍ corre los picos.

    Existe para que la prueba de fase cero pueda demostrar que el corrimiento que
    ``butterworth_fase_cero`` evita es real. **No usar en el pipeline.**
    """
    b, a = _coeficientes(fps, corte_hz, orden)
    return lfilter(b, a, np.asarray(serie, dtype=float))
