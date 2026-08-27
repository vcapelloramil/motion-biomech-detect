"""Preparación de series antes de filtrar: excluir no confiables, interpolar huecos."""

import numpy as np
import pytest

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.preparacion import TramoExcluido, _interpolar_huecos_cortos, preparar_series
from app.engine.validation import InversionZ, ResultadoValidacion, validar
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


def test_inversion_z_excluye_los_dos_frames_del_par():
    seq = FakeBackend(dims=3).procesar(range(60), **_KW)
    val = validar(seq, espacio="mundo")  # secuencia sana -> sin inversiones reales
    val.inversiones_z = [InversionZ(A.CODO_DER, 20, 21, 0.4, 0.1, -0.1)]

    crudo_20 = seq.frames[20].get_mundo(A.CODO_DER).x
    series, _ = preparar_series(seq, val, espacio="mundo")
    s = series[(A.CODO_DER, "x")]

    # hueco corto de 2 -> se interpola; el valor en 20 ya no es el crudo, es el de
    # la recta entre 19 y 22.
    assert not np.isnan(s).any()
    esperado = np.interp(20, [19, 22], [s[19], s[22]])
    assert s[20] == pytest.approx(esperado)
    assert abs(s[20] - crudo_20) > 0  # se usó la interpolación, no el dato crudo


def test_frames_sin_deteccion_largos_quedan_como_tramo():
    faltantes = set(range(40, 55))  # 15 seguidos
    seq = FakeBackend(dims=3, frames_sin_deteccion=faltantes).procesar(range(140), **_KW)
    val = validar(seq, espacio="mundo")
    series, tramos = preparar_series(seq, val, espacio="mundo", gap_max=5)
    assert np.isnan(series[(A.HOMBRO_DER, "x")]).any()
    tr = next(t for t in tramos if t.articulacion is A.HOMBRO_DER and t.coordenada == "x")
    assert tr.largo >= 15
