"""Filtro Butterworth de fase cero (tesis §3.4.2.3). Incluye la prueba de aceptación."""

import numpy as np
import pytest

from app.engine.dsp import (
    ParametroDSPInvalido,
    _filtro_unidireccional,
    butterworth_fase_cero,
)

FPS = 240.0


def _senal_con_pico(n=480, pico_s=1.0, sigma=0.12):
    t = np.arange(n) / FPS
    lenta = np.exp(-((t - pico_s) ** 2) / (2 * sigma**2))
    ruido = 0.05 * np.sin(2 * np.pi * 40 * t) + 0.03 * np.sin(2 * np.pi * 70 * t)
    return t, lenta + ruido, int(round(pico_s * FPS))


def test_fase_cero_conserva_el_instante_del_pico_y_la_unidireccional_no():
    _, senal, pico_real = _senal_con_pico()

    fz = butterworth_fase_cero(senal, fps=FPS, corte_hz=6.0, orden=4)
    uni = _filtro_unidireccional(senal, fps=FPS, corte_hz=6.0, orden=4)

    # Fase cero: el máximo se queda donde estaba.
    assert abs(int(np.argmax(fz)) - pico_real) <= 1
    # La MISMA verificación sobre el filtrado unidireccional falla: el pico se corrió.
    assert abs(int(np.argmax(uni)) - pico_real) > 1


def test_reduce_el_ruido_sin_tocar_la_componente_lenta():
    t = np.arange(1200) / FPS
    lenta = np.sin(2 * np.pi * 1.5 * t)
    rng = np.random.default_rng(0)
    ruido = 0.2 * rng.standard_normal(t.size)
    filtrada = butterworth_fase_cero(lenta + ruido, fps=FPS, corte_hz=6.0, orden=4)

    rms_ruido_antes = np.sqrt(np.mean(((lenta + ruido) - lenta) ** 2))
    rms_ruido_despues = np.sqrt(np.mean((filtrada - lenta) ** 2))
    assert rms_ruido_despues < 0.3 * rms_ruido_antes
    # la componente lenta se conserva (correlación alta)
    assert np.corrcoef(filtrada, lenta)[0, 1] > 0.99


def test_rechaza_corte_por_encima_de_nyquist():
    serie = np.zeros(500)
    with pytest.raises(ParametroDSPInvalido):
        butterworth_fase_cero(serie, fps=FPS, corte_hz=FPS / 2, orden=4)
    with pytest.raises(ParametroDSPInvalido):
        butterworth_fase_cero(serie, fps=60.0, corte_hz=45.0, orden=4)


def test_rechaza_corte_no_positivo():
    with pytest.raises(ParametroDSPInvalido):
        butterworth_fase_cero(np.zeros(500), fps=FPS, corte_hz=0.0, orden=4)


def test_rechaza_serie_con_nan():
    serie = np.zeros(500)
    serie[10] = np.nan
    with pytest.raises(ParametroDSPInvalido):
        butterworth_fase_cero(serie, fps=FPS, corte_hz=6.0, orden=4)


def test_rechaza_serie_demasiado_corta():
    with pytest.raises(ParametroDSPInvalido):
        butterworth_fase_cero(np.zeros(10), fps=FPS, corte_hz=6.0, orden=4)
