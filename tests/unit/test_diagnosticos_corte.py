"""diagnosticos_e3 corte-brazo: funciones puras del análisis del corte de Winter."""

import numpy as np

from app.diagnosticos_e3 import corte_de_serie, cortes_por_articulacion, tramo_mas_largo
from app.engine.pose.articulaciones import ArticulacionCanonica as A

FPS = 240.0
N = 480
T = np.arange(N) / FPS


def _movimiento_con_ruido(sigma: float = 0.01, semilla: int = 0) -> np.ndarray:
    rng = np.random.default_rng(semilla)
    return 0.15 * np.sin(2 * np.pi * 2.0 * T) + rng.normal(0.0, sigma, N)


def test_corte_de_serie_cae_en_una_banda_razonable_para_movimiento_lento_con_ruido():
    c = corte_de_serie(_movimiento_con_ruido(), fps=FPS)
    assert c is not None and 3.0 <= c <= 20.0


def test_corte_de_serie_corta_devuelve_none():
    assert corte_de_serie(_movimiento_con_ruido()[:30], fps=FPS) is None
    assert corte_de_serie(np.full(100, np.nan), fps=FPS) is None


def test_tramo_mas_largo():
    x = np.arange(20, dtype=float)
    x[3] = np.nan
    x[12:14] = np.nan
    # tramos continuos: [0, 2] (3), [4, 11] (8), [14, 19] (6) -> el más largo es [4, 11]
    assert np.array_equal(tramo_mas_largo(x), x[4:12])
    assert tramo_mas_largo(np.full(5, np.nan)).size == 0


def test_metodos_concatenado_y_tramo_dan_una_entrada_por_coordenada():
    s = _movimiento_con_ruido()
    s_hueco = s.copy()
    s_hueco[200:260] = np.nan
    series = {(A.CODO_DER, c): s_hueco for c in "xyz"}
    conc = cortes_por_articulacion(series, fps=FPS, metodo="concatenado")
    tram = cortes_por_articulacion(series, fps=FPS, metodo="tramo")
    assert len(conc[A.CODO_DER]) == 3 and len(tram[A.CODO_DER]) == 3
