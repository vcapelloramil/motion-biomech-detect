"""Análisis exploratorio posterior de la detección (``app.medicion_deteccion_exploratorio``): funciones puras. Sin videos."""

from __future__ import annotations

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.medicion_deteccion_exploratorio import (
    ARTS,
    corte_mitad,
    decidir_mitad,
    evaluar_binaria,
    exploratorio,
    frames_desde_series,
    muneca_alta_en_contacto,
)

FPS = 240.0


def _series(n=600, muneca_y=0.0):
    s = {a.value: np.full((n, 3), np.nan) for a in ARTS}
    s[A.NARIZ.value][:] = [0.0, -0.6, 0.0]
    s[A.MUNECA_DER.value][:] = [0.3, muneca_y, 0.0]
    return s


def test_frames_desde_series_omite_lo_que_tiene_nan():
    frames = frames_desde_series(_series(n=5))
    assert len(frames) == 5
    assert A.NARIZ in frames[0] and A.MUNECA_DER in frames[0] and A.CODO_DER not in frames[0]
    assert frames[0][A.MUNECA_DER].y == 0.0


def test_muneca_sobre_la_nariz_en_el_contacto():
    alta = muneca_alta_en_contacto(frames_desde_series(_series(muneca_y=-0.9)), 400, FPS)
    baja = muneca_alta_en_contacto(frames_desde_series(_series(muneca_y=0.0)), 400, FPS)
    assert alta == 1.0 and baja == 0.0


def test_sin_muneca_no_hay_dato():
    s = _series()
    s[A.MUNECA_DER.value][:] = np.nan
    assert muneca_alta_en_contacto(frames_desde_series(s), 400, FPS) is None


def test_corte_por_la_mitad_de_las_medianas_y_su_orientacion():
    assert corte_mitad([0.0, 2.0], [8.0, 10.0]) == 5.0
    assert corte_mitad([], [1.0]) is None
    assert decidir_mitad(6.0, 5.0, True) is True and decidir_mitad(4.0, 5.0, True) is False
    assert decidir_mitad(4.0, 5.0, False) is True and decidir_mitad(6.0, 5.0, False) is False
    assert decidir_mitad(None, 5.0, True) is None


def _f(rep, sesion, gesto, valor):
    return {"repeticion": rep, "sesion": sesion, "gesto": gesto, "encuadre": "perfil", "k": valor}


def test_evaluar_binaria_ajusta_en_una_sesion_y_evalua_en_la_otra():
    filas = [
        _f("a", 1, "drive", 10.0), _f("b", 1, "drive", 12.0), _f("c", 1, "reves", 0.0), _f("d", 1, "reves", 2.0),
        _f("e", 2, "drive", 11.0), _f("f", 2, "reves", 1.0), _f("g", 2, "reves", 9.0),
    ]
    r = evaluar_binaria(filas, "k", "drive", "gesto", sesion_ajuste=1)
    assert r["corte"] == 6.0 and r["alta_es_mayor"]
    pred = {rep: p for _, p, rep in r["pares"]}
    assert pred == {"e": "drive", "f": "reves", "g": "drive"}          # g es un error (revés con valor alto)


def test_clase_alta_menor_se_orienta_sola():
    filas = [_f("a", 1, "drive", 0.0), _f("b", 1, "reves", 10.0), _f("c", 2, "drive", 1.0), _f("d", 2, "reves", 9.0)]
    r = evaluar_binaria(filas, "k", "drive", "gesto", sesion_ajuste=1)
    assert not r["alta_es_mayor"]
    assert {rep: p for _, p, rep in r["pares"]} == {"c": "drive", "d": "reves"}


def test_exploratorio_corre_con_filas_minimas():
    filas = []
    for s in (1, 2):
        for g, v in (("saque", 1.0), ("drive", 0.0), ("reves", 0.0)):
            for e in ("perfil", "tres_cuartos"):
                filas.append({
                    "repeticion": f"{s}{g}{e}", "sesion": s, "gesto": g, "encuadre": e, "x_muneca_alta": v, "c1_giro": 0.0, "c2_munecas": v,
                    "c3_eje": v, "giro_hombros": 30.0 if e == "perfil" else 60.0,
                })
    r = exploratorio(filas)
    assert r["saque_contra_resto_muneca_alta_en_contacto"]["errores"] == 0
    assert r["encuadre_saque_giro_hombros"]["errores"] == 0
