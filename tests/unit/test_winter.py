"""Análisis residual de Winter: elige el corte de forma objetiva (tesis §3.4.2.4)."""

import numpy as np
import pytest

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.winter import analizar_serie, elegir_corte

FPS = 240.0


def _serie(n=1500, semilla=0):
    t = np.arange(n) / FPS
    # movimiento real por debajo de ~4 Hz
    mov = np.sin(2 * np.pi * 1.5 * t) + 0.5 * np.sin(2 * np.pi * 3.5 * t)
    rng = np.random.default_rng(semilla)
    ruido = 0.08 * rng.standard_normal(n)
    return mov + ruido


def test_el_residuo_decrece_al_subir_el_corte():
    cortes, residuos, nivel = analizar_serie(_serie(), fps=FPS)
    assert residuos[0] > residuos[-1]
    assert nivel >= 0.0


def test_el_corte_elegido_cae_entre_la_señal_y_el_ruido():
    series = {
        (A.MUNECA_DER, "x"): _serie(semilla=1),
        (A.CODO_DER, "y"): _serie(semilla=2),
    }
    res = elegir_corte(series, fps=FPS)
    # la señal llega a 3.5 Hz; el corte debe dejarla pasar pero no todo el ruido
    assert 4.0 <= res.corte_elegido_hz <= 18.0
    assert res.n_series == 2


def test_sin_series_utiles_falla_claro():
    with pytest.raises(ValueError):
        elegir_corte({(A.MUNECA_DER, "x"): np.full(10, np.nan)}, fps=FPS)
