"""diagnosticos_e3: funciones puras (sin video ni pose real)."""

import numpy as np
import pytest

from app.diagnosticos_e3 import (
    filtrar_e3_nuevo,
    filtrar_e3_viejo,
    omega_k,
    p99,
    vector_unitario,
)
from app.engine.pose.articulaciones import ArticulacionCanonica as A

FPS = 240.0
N = 480
T = np.arange(N) / FPS


def _series_giratorias(grados_por_s: float, ruido: float = 0.0, semilla: int = 0, hueco=None):
    """Hombro fijo en el origen; codo a 0,3 m girando en el plano x-z."""
    rng = np.random.default_rng(semilla)
    ang = np.radians(grados_por_s) * T
    codo = {"x": 0.3 * np.cos(ang), "y": np.zeros(N), "z": 0.3 * np.sin(ang)}
    series = {(A.HOMBRO_DER, c): np.zeros(N) for c in "xyz"}
    for c in "xyz":
        s = codo[c] + rng.normal(0.0, ruido, N)
        if hueco:
            s[hueco[0]:hueco[1]] = np.nan
        series[(A.CODO_DER, c)] = s
    return series


def test_omega_de_un_giro_uniforme_es_independiente_de_k():
    u = vector_unitario(_series_giratorias(300.0), A.HOMBRO_DER, A.CODO_DER)
    for k in (1, 2, 4, 8):
        assert p99(omega_k(u, FPS, k)) == pytest.approx(300.0, rel=1e-3)


def test_el_ruido_cae_como_1_sobre_k_y_el_giro_real_no():
    u = vector_unitario(_series_giratorias(100.0, ruido=0.01), A.HOMBRO_DER, A.CODO_DER)
    w1, w8 = p99(omega_k(u, FPS, 1)), p99(omega_k(u, FPS, 8))
    assert w1 > 5 * w8          # dominado por ruido: cae fuerte con k


def test_vector_unitario_devuelve_nan_si_falta_una_coordenada():
    series = _series_giratorias(100.0, hueco=(100, 120))
    u = vector_unitario(series, A.HOMBRO_DER, A.CODO_DER)
    assert np.isnan(u[100:120]).all() and not np.isnan(u[:100]).any()
    assert np.all(np.isnan(vector_unitario({(A.HOMBRO_DER, "x"): np.zeros(5)}, A.HOMBRO_DER, A.CODO_DER)))


def test_e3_viejo_deja_cruda_la_serie_con_hueco_y_el_nuevo_la_filtra():
    series = _series_giratorias(60.0, ruido=0.01, hueco=(200, 240))
    clave = (A.CODO_DER, "x")
    viejo = filtrar_e3_viejo(series, fps=FPS, corte_hz=8.0)
    nuevo = filtrar_e3_nuevo(series, fps=FPS, corte_hz=8.0)
    assert np.array_equal(viejo[clave], series[clave], equal_nan=True)      # cruda entera
    rug = lambda x: float(np.nanstd(np.diff(x[:190], n=2)))
    assert rug(nuevo[clave]) < 0.2 * rug(series[clave])
    # una serie completa se filtra igual en ambos
    assert np.allclose(viejo[(A.HOMBRO_DER, "x")], nuevo[(A.HOMBRO_DER, "x")])


def test_p99_de_un_vector_sin_datos_es_none():
    assert p99(np.full(5, np.nan)) is None
