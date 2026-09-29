"""criterio2: funciones puras del protocolo ciego (decisión 014)."""

import numpy as np
import pytest

from app.criterio2 import (
    META_ERROR_GRADOS,
    angulo_en_vertice,
    es_elegible,
    mejor_lado,
    resumen_errores,
    seleccionar_por_estrato,
)
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import Punto


def test_angulo_en_vertice_de_geometrias_conocidas():
    assert angulo_en_vertice((1, 0), (0, 0), (0, 1)) == pytest.approx(90.0)
    assert angulo_en_vertice((1, 0), (0, 0), (2, 0)) == pytest.approx(0.0)
    assert angulo_en_vertice((1, 0), (0, 0), (-1, 0)) == pytest.approx(180.0)
    assert angulo_en_vertice((1, 0, 0), (0, 0, 0), (0, 0, 1)) == pytest.approx(90.0)     # también 3D
    assert np.isnan(angulo_en_vertice((0, 0), (0, 0), (1, 1)))


def _puntos(conf_izq: float, conf_der: float, faltan=()):
    pts = {}
    for lado, c in (("IZQ", conf_izq), ("DER", conf_der)):
        for art in ("CADERA", "RODILLA", "TOBILLO", "HOMBRO", "CODO", "MUNECA"):
            a = A[f"{art}_{lado}"]
            if a not in faltan:
                pts[a] = Punto(0.5, 0.5, None, c)
    return pts


def test_mejor_lado_toma_la_mayor_confianza_minima():
    pts = _puntos(0.9, 0.4)
    assert mejor_lado(pts, "rodilla") == ("izq", pytest.approx(0.9))
    pts[A.TOBILLO_IZQ] = Punto(0.5, 0.5, None, 0.2)          # el tobillo izquierdo baja la mínima del lado
    # izq: min(0.9, 0.9, 0.2) = 0.2; der: min(0.4, 0.4, 0.4) = 0.4 -> gana der
    assert mejor_lado(pts, "rodilla") == ("der", pytest.approx(0.4))


def test_elegible_exige_ambos_angulos_con_confianza_minima_de_0_6():
    assert es_elegible(_puntos(0.9, 0.9)) is not None
    assert es_elegible(_puntos(0.5, 0.5)) is None                                     # ninguna alcanza 0,6
    # rodilla visible (izq) pero codos ambos tapados
    pts = _puntos(0.9, 0.9)
    for a in (A.CODO_IZQ, A.CODO_DER):
        pts[a] = Punto(0.5, 0.5, None, 0.3)
    assert es_elegible(pts) is None                                                    # falta el codo
    assert es_elegible(_puntos(0.9, 0.9, faltan=(A.CODO_IZQ, A.CODO_DER))) is None    # punto ausente


def test_seleccion_es_determinista_uno_por_clip_y_respeta_k():
    cand = {"saque|perfil": {f"c{i}": [{"frame": i, "offset_ms": 0}, {"frame": i + 1, "offset_ms": -150}]
                             for i in range(8)},
            "drive|perfil": {"a": [{"frame": 1, "offset_ms": 0}], "b": []}}
    s1 = seleccionar_por_estrato(cand, semilla=7, k=3)
    s2 = seleccionar_por_estrato(cand, semilla=7, k=3)
    assert s1 == s2
    assert len(s1["saque|perfil"]) == 3 and len({c for c, _ in s1["saque|perfil"]}) == 3
    assert s1["drive|perfil"] == [("a", {"frame": 1, "offset_ms": 0})]      # menos de k: se toman todos
    assert seleccionar_por_estrato(cand, semilla=8, k=3) != s1               # otra semilla, otra selección


def test_resumen_errores_media_contra_la_meta():
    ok = resumen_errores([5.0, 10.0, 15.0], [1.0, -2.0, 3.0])
    assert ok["media"] == pytest.approx(10.0) and ok["cumple"] is True and ok["sesgo_medio"] == pytest.approx(2 / 3)
    mal = resumen_errores([25.0, 30.0], [25.0, 30.0])
    assert mal["cumple"] is False and mal["media"] > META_ERROR_GRADOS
    assert resumen_errores([], []) == {"n": 0}
