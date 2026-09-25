"""Filtrado por segmentos: series con huecos (NaN).

Antes de 0.4.1 toda serie con algún NaN se dejaba ENTERA sin filtrar; el ruido del
codo entraba crudo a E4 (decisión 010). Estas pruebas fijan el comportamiento nuevo con
señales sintéticas de resultado conocido: un movimiento lento (1,5 y 3 Hz) + ruido, con
un hueco interno de NaN rodeado de señal limpia.
"""

import numpy as np
import pytest
from scipy.signal import filtfilt

from app.engine.dsp import (
    _coeficientes,
    butterworth_fase_cero,
    butterworth_fase_cero_por_segmentos,
    largo_minimo_segmento,
    segmentos_continuos,
)

FPS = 240.0
N = 480
T = np.arange(N) / FPS
LIMPIA = 0.15 * np.sin(2 * np.pi * 1.5 * T) + 0.05 * np.sin(2 * np.pi * 3.0 * T + 0.7)
G0, G1 = 200, 239                       # hueco interno de 40 muestras
IDX = np.arange(N)
BORDE = ((IDX >= G0 - 5) & (IDX < G0)) | ((IDX > G1) & (IDX <= G1 + 5))
INTERIOR = ((IDX > 40) & (IDX < G0 - 40)) | ((IDX > G1 + 40) & (IDX < N - 40))


def _con_hueco(base: np.ndarray) -> np.ndarray:
    x = base.copy()
    x[G0 : G1 + 1] = np.nan
    return x


def _rms(err: np.ndarray, mascara: np.ndarray) -> float:
    return float(np.sqrt(np.mean(err[mascara] ** 2)))


def test_el_hueco_se_conserva_y_no_se_rellena():
    y, cortos = butterworth_fase_cero_por_segmentos(_con_hueco(LIMPIA), fps=FPS, corte_hz=8.0)
    assert np.isnan(y[G0 : G1 + 1]).all()                    # nada inventado dentro del hueco
    assert not np.isnan(y[:G0]).any() and not np.isnan(y[G1 + 1 :]).any()
    assert cortos == []


def test_senal_limpia_no_genera_transitorios_en_el_borde_del_hueco():
    y, _ = butterworth_fase_cero_por_segmentos(_con_hueco(LIMPIA), fps=FPS, corte_hz=8.0)
    err = np.abs(y - LIMPIA)
    assert np.nanmax(err[BORDE]) < 0.01 * float(np.ptp(LIMPIA))   # < 1 % de la amplitud pico a pico


def test_rellenar_el_hueco_con_ceros_SI_arrastra_artefactos():
    # La prueba demuestra que el problema existe: la alternativa ingenua falla donde el
    # filtrado por segmentos no.
    z = LIMPIA.copy()
    z[G0 : G1 + 1] = 0.0
    b, a = _coeficientes(FPS, 8.0, 4)
    err_ingenuo = np.abs(filtfilt(b, a, z) - LIMPIA)
    y, _ = butterworth_fase_cero_por_segmentos(_con_hueco(LIMPIA), fps=FPS, corte_hz=8.0)
    err_seg = np.abs(y - LIMPIA)
    assert err_ingenuo[BORDE].max() > 10 * np.nanmax(err_seg[BORDE])


def test_con_ruido_reduce_el_error_en_el_interior_y_nunca_empeora_en_el_borde():
    rng = np.random.default_rng(0)
    ruidosa = LIMPIA + rng.normal(0.0, 0.02, N)
    y, _ = butterworth_fase_cero_por_segmentos(_con_hueco(ruidosa), fps=FPS, corte_hz=8.0)
    err = np.abs(y - LIMPIA)
    ruido_crudo = _rms(np.abs(ruidosa - LIMPIA), INTERIOR | BORDE)
    assert _rms(err, INTERIOR) < 0.4 * ruido_crudo
    # En el extremo de un segmento el filtro atenúa menos el ruido (limitación conocida),
    # pero no puede dejarlo peor que el dato crudo.
    assert _rms(err, BORDE) < ruido_crudo


@pytest.mark.parametrize("distancia", [8, 15, 25, 40])
def test_un_pico_cerca_del_borde_del_hueco_conserva_su_instante(distancia):
    # Es el sentido de "fase cero": el pico no se corre aunque esté pegado al hueco.
    pico = G0 - distancia
    pulso = np.exp(-0.5 * ((IDX - pico) / 6.0) ** 2)
    y, _ = butterworth_fase_cero_por_segmentos(_con_hueco(pulso), fps=FPS, corte_hz=8.0)
    assert abs(int(np.nanargmax(y)) - pico) <= 1


def test_segmento_demasiado_corto_no_se_deja_crudo_se_marca_y_pasa_a_nan():
    minimo = largo_minimo_segmento(fps=FPS, corte_hz=8.0)
    x = LIMPIA.copy()
    x[10:200] = np.nan               # deja [0, 9]: 10 muestras < mínimo
    x[220:225] = np.nan              # deja [200, 219]: 20 muestras >= mínimo
    assert 10 < minimo <= 20
    y, cortos = butterworth_fase_cero_por_segmentos(x, fps=FPS, corte_hz=8.0)
    assert cortos == [(0, 9)]
    assert np.isnan(y[0:10]).all()                            # no quedó crudo
    assert not np.isnan(y[200:220]).any()                     # el segmento válido sí se filtró


def test_serie_sin_huecos_equivale_a_butterworth_fase_cero():
    y, cortos = butterworth_fase_cero_por_segmentos(LIMPIA, fps=FPS, corte_hz=8.0)
    assert cortos == []
    assert np.allclose(y, butterworth_fase_cero(LIMPIA, fps=FPS, corte_hz=8.0))


def test_segmentos_continuos():
    x = np.array([1, 2, np.nan, np.nan, 5, 6, 7, np.nan, 9.0])
    assert segmentos_continuos(x) == [(0, 1), (4, 6), (8, 8)]
    assert segmentos_continuos(np.full(4, np.nan)) == []
