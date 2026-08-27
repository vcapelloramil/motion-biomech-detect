"""Preparación de series antes de filtrar: excluir no confiables, interpolar huecos."""

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.preparacion import TramoExcluido, _interpolar_huecos_cortos, preparar_series
from app.engine.validation import ResultadoValidacion, validar
from app.engine.pose.fake_backend import FakeBackend

_KW = dict(ancho=1920, alto=1080, fps_efectivos=240.0)


def test_interpola_hueco_corto_y_deja_el_largo():
    s = np.arange(20, dtype=float)
    s[5:8] = np.nan       # hueco de 3 -> interpola
    s[12:19] = np.nan     # hueco de 7 -> queda
    out = _interpolar_huecos_cortos(s, gap_max=5)
    assert not np.isnan(out[5:8]).any()
    assert np.allclose(out[5:8], [5, 6, 7])
    assert np.isnan(out[12:19]).all()


def test_excluye_baja_confianza_y_salto_imposible():
    seq = FakeBackend(dims=3, articulaciones_ocluidas={A.MUNECA_DER: 0.2}).procesar(
        range(80), **_KW
    )
    val = validar(seq, espacio="mundo")  # marca MUNECA_DER en todos los frames
    series, tramos = preparar_series(seq, val, espacio="mundo")
    # MUNECA_DER quedó completamente excluida -> tramo largo, sin serie filtrable útil
    muñeca = [t for t in tramos if t.articulacion is A.MUNECA_DER]
    assert muñeca
    # una articulación sana sigue completa
    assert not np.isnan(series[(A.CADERA_IZQ, "x")]).any()


def test_frames_sin_deteccion_cortos_se_interpolan():
    seq = FakeBackend(dims=3, frames_sin_deteccion={40, 41, 42}).procesar(range(120), **_KW)
    val = validar(seq, espacio="mundo")
    series, tramos = preparar_series(seq, val, espacio="mundo", gap_max=5)
    serie = series[(A.HOMBRO_DER, "x")]
    assert not np.isnan(serie).any()  # hueco de 3 interpolado
    assert not any(t.articulacion is A.HOMBRO_DER for t in tramos)


def test_frames_sin_deteccion_largos_quedan_como_tramo():
    faltantes = set(range(40, 55))  # 15 seguidos
    seq = FakeBackend(dims=3, frames_sin_deteccion=faltantes).procesar(range(140), **_KW)
    val = validar(seq, espacio="mundo")
    series, tramos = preparar_series(seq, val, espacio="mundo", gap_max=5)
    assert np.isnan(series[(A.HOMBRO_DER, "x")]).any()
    tr = next(t for t in tramos if t.articulacion is A.HOMBRO_DER and t.coordenada == "x")
    assert tr.largo >= 15
