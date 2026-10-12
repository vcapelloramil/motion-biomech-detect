"""``engine/magnitudes``: los ángulos con la definición validada (Criterio 2) y la separación cadera-hombro (Criterio 3)."""

from __future__ import annotations

import numpy as np
import pytest

from app.engine import magnitudes as m
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import Punto


def _p(x, y, conf=0.9, z=None):
    return Punto(x, y, z, conf)


def test_el_angulo_interior_de_una_rodilla_a_90_grados():
    puntos = {A.CADERA_DER: _p(0.5, 0.4), A.RODILLA_DER: _p(0.5, 0.6), A.TOBILLO_DER: _p(0.7, 0.6)}
    # en píxeles de un video de 1000 x 1000: cadera (500, 400), rodilla (500, 600), tobillo (700, 600)
    assert m.angulo_2d(puntos, "rodilla", "der", 1000, 1000) == pytest.approx(90.0)


def test_el_angulo_usa_los_pixeles_y_no_las_coordenadas_normalizadas():
    """En un video apaisado 1920 x 1080 las coordenadas normalizadas deforman el ángulo; hay que multiplicar por el ancho y el alto."""
    puntos = {A.HOMBRO_IZQ: _p(0.5, 0.2), A.CODO_IZQ: _p(0.5, 0.5), A.MUNECA_IZQ: _p(0.6, 0.5)}
    con_pixeles = m.angulo_2d(puntos, "codo", "izq", 1920, 1080)
    # vértice en (960, 540); hombro a (0, -324) y muñeca a (192, 0): ángulo recto
    assert con_pixeles == pytest.approx(90.0)


def test_elige_el_lado_con_mayor_confianza_minima():
    puntos = {
        A.CADERA_IZQ: _p(0.4, 0.4, 0.95), A.RODILLA_IZQ: _p(0.4, 0.6, 0.55), A.TOBILLO_IZQ: _p(0.4, 0.8, 0.9),
        A.CADERA_DER: _p(0.6, 0.4, 0.8), A.RODILLA_DER: _p(0.6, 0.6, 0.7), A.TOBILLO_DER: _p(0.6, 0.8, 0.9),
    }
    assert m.mejor_lado(puntos, "rodilla") == ("der", pytest.approx(0.7))
    r = m.angulo_en_el_frame(puntos, "rodilla", 1000, 1000)
    assert r["auditable"] and r["lado"] == "der" and r["valor"] == pytest.approx(180.0)


def test_con_poca_confianza_no_se_informa_el_angulo():
    puntos = {A.HOMBRO_DER: _p(0.5, 0.2, 0.9), A.CODO_DER: _p(0.5, 0.5, 0.59), A.MUNECA_DER: _p(0.6, 0.5, 0.9)}
    r = m.angulo_en_el_frame(puntos, "codo", 1000, 1000)
    assert r["auditable"] is False and r["valor"] is None and r["lado"] == "der" and r["confianza"] == pytest.approx(0.59)


def test_con_un_punto_faltante_no_hay_lado():
    r = m.angulo_en_el_frame({A.HOMBRO_DER: _p(0.5, 0.2)}, "codo", 1000, 1000)
    assert r == {"lado": None, "valor": None, "confianza": 0.0, "auditable": False}


def _mundo(giro_hombros_deg: float, giro_caderas_deg: float = 0.0) -> dict:
    def eje(deg, r):
        a = np.radians(deg)
        return (-r * np.cos(a), 0.0, -r * np.sin(a)), (r * np.cos(a), 0.0, r * np.sin(a))

    ci, cd = eje(giro_caderas_deg, 0.15)
    hi, hd = eje(giro_hombros_deg, 0.2)
    return {
        A.CADERA_IZQ: _p(*ci[:2], z=ci[2]), A.CADERA_DER: _p(*cd[:2], z=cd[2]),
        A.HOMBRO_IZQ: _p(*hi[:2], z=hi[2]), A.HOMBRO_DER: _p(*hd[:2], z=hd[2]),
    }


def test_la_separacion_cadera_hombro_es_el_angulo_entre_los_dos_ejes():
    assert m.separacion_cadera_hombro_en(_mundo(40.0, 0.0)) == pytest.approx(40.0)
    assert m.separacion_cadera_hombro_en(_mundo(10.0, 25.0)) == pytest.approx(15.0)
    assert np.isnan(m.separacion_cadera_hombro_en({A.CADERA_IZQ: _p(0, 0, z=0)}))


def test_el_maximo_de_la_ventana_y_su_fotograma():
    serie = [_mundo(g) for g in (0, 10, 25, 42, 30, 12)]
    r = m.separacion_cadera_hombro_max(serie, 0, 5)
    assert r["auditable"] and r["valor"] == pytest.approx(42.0) and r["frame"] == 3 and r["cobertura"] == 1.0


def test_con_la_ventana_a_medio_medir_no_se_informa_el_maximo():
    serie = [_mundo(g) for g in (0, 10, 25, 42)] + [{}] * 6
    r = m.separacion_cadera_hombro_max(serie, 0, 9)
    assert r["auditable"] is False and r["valor"] is None and r["cobertura"] == pytest.approx(0.4)


def test_el_error_validado_es_el_del_criterio_2():
    assert m.ERROR_VALIDADO["rodilla"] == {"media_grados": 8.5, "p95_grados": 19.2}
    assert m.ERROR_VALIDADO["codo"]["media_grados"] == 12.5 and m.ERROR_VALIDADO["codo"]["p95_grados"] == 36.4
