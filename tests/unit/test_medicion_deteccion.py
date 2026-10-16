"""Detección del tipo de golpe y del encuadre (``app.medicion_deteccion``, decisión 038, etapa 1): estadísticos, cortes y evaluación. Sin videos."""

from __future__ import annotations

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import Punto
from app.medicion_deteccion import (
    ajustar_cortes,
    ajustar_encuadre,
    ajustar_gesto,
    decidir,
    detectar_encuadre,
    detectar_gesto,
    estadisticos,
    resumen,
    wilson,
)

FPS = 240.0
N = 600
PICO = 400


def _p(x, y, z=0.0):
    return Punto(x, y, z, 0.9)


def _frames(*, muneca_d=(0.3, -0.7, 0.0), codo_d=(0.25, -0.5, 0.0), muneca_n=(-0.3, 0.0, 0.0), giro=0.0, n=N):
    """Un bailarín quieto: hombros a ±0,2 m (el eje y crece hacia abajo; nariz en y = -0,6), con la línea de hombros girando ``giro``
    grados en total durante la aceleración (de 0,3 s antes del pico al pico)."""
    frames = []
    for i in range(n):
        frac = min(1.0, max(0.0, (i - (PICO - 0.3 * FPS)) / (0.3 * FPS)))
        a = np.radians(giro * frac)
        # derecha = +x del jugador al principio; el giro la lleva hacia z
        hd = _p(0.2 * np.cos(a), -0.4, 0.2 * np.sin(a))
        hi = _p(-0.2 * np.cos(a), -0.4, -0.2 * np.sin(a))
        frames.append({
            A.NARIZ: _p(0.0, -0.6), A.HOMBRO_DER: hd, A.HOMBRO_IZQ: hi,
            A.CODO_DER: _p(*codo_d), A.MUNECA_DER: _p(*muneca_d), A.MUNECA_IZQ: _p(*muneca_n),
            A.CODO_IZQ: _p(-0.25, -0.3, 0.0),
        })
    return frames


def test_posicion_de_trofeo_da_s_saque_alto_y_el_resto_bajo():
    trofeo = estadisticos(_frames(muneca_d=(0.2, -0.8, 0.0), codo_d=(0.3, -0.5, 0.0)), PICO, FPS)
    abajo = estadisticos(_frames(muneca_d=(0.3, 0.0, 0.0), codo_d=(0.25, -0.2, 0.0)), PICO, FPS)
    assert trofeo["s_saque"] == 1.0
    assert abajo["s_saque"] == 0.0


def test_el_codo_bajo_el_hombro_no_es_trofeo_aunque_la_muneca_este_alta():
    est = estadisticos(_frames(muneca_d=(0.2, -0.8, 0.0), codo_d=(0.3, -0.2, 0.0)), PICO, FPS)
    assert est["s_saque"] == 0.0


def test_distancia_entre_munecas_en_anchos_de_hombros():
    # hombros a 0,4 m; muñecas a 0,6 m una de otra → 1,5 anchos
    est = estadisticos(_frames(muneca_d=(0.3, 0.0, 0.0), muneca_n=(-0.3, 0.0, 0.0)), PICO, FPS)
    assert abs(est["c2_munecas"] - 1.5) < 1e-6


def test_posicion_lateral_de_la_muneca_dominante_sobre_el_eje_de_los_hombros():
    del_lado = estadisticos(_frames(muneca_d=(0.5, 0.0, 0.0)), PICO, FPS)["c3_eje"]
    cruzada = estadisticos(_frames(muneca_d=(-0.3, 0.0, 0.0)), PICO, FPS)["c3_eje"]
    assert abs(del_lado - 1.25) < 1e-6 and cruzada < 0     # 0,5 m / 0,4 m
    assert del_lado > 0


def test_giro_neto_de_la_linea_de_hombros_con_el_signo_de_la_mano():
    est = estadisticos(_frames(giro=40.0), PICO, FPS, mano="der")
    # la definición compara la mediana de los primeros y de los últimos 0,05 s: en una rampa de 40° da algo menos que 40°
    assert 30.0 < est["c1_giro"] < 40.0
    sin_giro = estadisticos(_frames(giro=0.0), PICO, FPS)
    assert abs(sin_giro["c1_giro"]) < 1e-6


def test_giro_de_hombros_del_contraste_d_se_informa():
    est = estadisticos(_frames(), PICO, FPS)
    assert est["giro_hombros"] is not None and est["giro_hombros"] < 1.0   # hombros paralelos al plano de la imagen


def test_ventana_sin_datos_da_none_y_no_inventa():
    frames = [{} for _ in range(N)]
    est = estadisticos(frames, PICO, FPS)
    assert est == {"s_saque": None, "c1_giro": None, "c2_munecas": None, "c3_eje": None, "giro_hombros": None}


def test_cortes_por_extremos_y_franja_sin_afirmar():
    c = ajustar_cortes([10.0, 20.0, 30.0], [50.0, 60.0])
    assert c["separable"] and c["p"] == 30.0 and c["t"] == 50.0
    assert decidir(25.0, c) == "baja" and decidir(30.0, c) == "baja"
    assert decidir(40.0, c) is None
    assert decidir(50.0, c) == "alta" and decidir(99.0, c) == "alta"
    assert decidir(None, c) is None


def test_clases_solapadas_no_separan_y_la_zona_comun_no_se_afirma():
    c = ajustar_cortes([10.0, 45.0], [40.0, 60.0])
    assert not c["separable"]
    assert decidir(5.0, c) == "baja" and decidir(70.0, c) == "alta"
    assert decidir(42.0, c) is None


def test_sin_una_de_las_clases_no_hay_cortes():
    c = ajustar_cortes([], [1.0])
    assert c["p"] is None and decidir(1.0, c) is None


def _fila(gesto, encuadre, **v):
    base = {"gesto": gesto, "encuadre": encuadre, "s_saque": 0.0, "c1_giro": 0.0, "c2_munecas": 0.0, "c3_eje": 0.0, "giro_hombros": 30.0}
    base.update(v)
    return base


def test_gesto_saque_resto_y_drive_contra_reves_con_la_candidata_que_separa():
    ajuste = [
        _fila("saque", "perfil", s_saque=0.9), _fila("saque", "perfil", s_saque=0.7),
        _fila("drive", "perfil", s_saque=0.0, c3_eje=1.0, c2_munecas=0.9, c1_giro=10.0),
        _fila("drive", "perfil", s_saque=0.1, c3_eje=1.2, c2_munecas=0.5, c1_giro=-20.0),
        _fila("reves", "perfil", s_saque=0.0, c3_eje=-0.5, c2_munecas=0.7, c1_giro=-5.0),
        _fila("reves", "perfil", s_saque=0.1, c3_eje=-0.2, c2_munecas=0.6, c1_giro=15.0),
    ]
    aj = ajustar_gesto(ajuste)
    assert aj["saque"]["separable"]
    assert aj["candidatas"]["c3_eje"]["separable"] and not aj["candidatas"]["c2_munecas"]["separable"]
    assert aj["elegida"] == "c3_eje"
    assert detectar_gesto({"s_saque": 0.95, "c3_eje": 0.0}, aj)[0] == "saque"
    assert detectar_gesto({"s_saque": 0.0, "c3_eje": 2.0}, aj)[0] == "drive"
    assert detectar_gesto({"s_saque": 0.0, "c3_eje": -1.0}, aj)[0] == "reves"
    assert detectar_gesto({"s_saque": 0.0, "c3_eje": 0.4}, aj)[0] is None      # en la franja
    assert detectar_gesto(None, aj) == (None, "sin pico del tronco")


def test_sin_candidata_que_separe_drive_y_reves_queda_sin_determinar():
    ajuste = [
        _fila("saque", "perfil", s_saque=0.9),
        _fila("drive", "perfil", c1_giro=0.0, c2_munecas=1.0, c3_eje=1.0), _fila("drive", "perfil", c1_giro=30.0, c2_munecas=0.2, c3_eje=-1.0),
        _fila("reves", "perfil", c1_giro=10.0, c2_munecas=0.6, c3_eje=0.0), _fila("reves", "perfil", c1_giro=20.0, c2_munecas=0.7, c3_eje=0.5),
    ]
    aj = ajustar_gesto(ajuste)
    assert aj["elegida"] is None
    assert detectar_gesto({"s_saque": 0.0, "c1_giro": 5.0}, aj)[0] is None
    assert detectar_gesto({"s_saque": 1.0}, aj)[0] == "saque"          # el saque no depende de esa distinción


def test_encuadre_por_gesto_y_con_gesto_sin_determinar():
    ajuste = [
        _fila("saque", "perfil", giro_hombros=30.0), _fila("saque", "tres_cuartos", giro_hombros=55.0),
        _fila("drive", "perfil", giro_hombros=20.0), _fila("drive", "tres_cuartos", giro_hombros=70.0),
        _fila("reves", "perfil", giro_hombros=25.0), _fila("reves", "tres_cuartos", giro_hombros=60.0),
    ]
    ae = ajustar_encuadre(ajuste)
    assert detectar_encuadre({"giro_hombros": 22.0}, "saque", ae) == "perfil"
    assert detectar_encuadre({"giro_hombros": 65.0}, "saque", ae) == "tres_cuartos"
    assert detectar_encuadre({"giro_hombros": 42.0}, "saque", ae) is None
    assert detectar_encuadre({"giro_hombros": None}, "saque", ae) is None
    # con el gesto sin determinar solo se afirma si los cortes de todos los gestos coinciden
    assert detectar_encuadre({"giro_hombros": 10.0}, None, ae) == "perfil"
    assert detectar_encuadre({"giro_hombros": 80.0}, None, ae) == "tres_cuartos"
    assert detectar_encuadre({"giro_hombros": 28.0}, None, ae) is None      # perfil para el saque, franja para el drive


def test_resumen_cuenta_errores_solo_entre_los_determinados():
    pares = [("saque", "saque"), ("saque", "drive"), ("saque", None), ("drive", "drive"), ("reves", None)]
    r = resumen(pares, ("saque", "drive", "reves"))
    assert (r["n"], r["determinados"], r["errores"], r["no_determinados"]) == (5, 3, 1, 2)
    assert abs(r["error_entre_determinados"] - 1 / 3) < 1e-9 and abs(r["no_determinado_pct"] - 0.4) < 1e-9
    assert not r["cumple"]
    assert r["matriz"]["saque"] == {"saque": 1, "drive": 1, "reves": 0, "no_determinado": 1}


def test_criterio_de_aceptacion_5_y_20_por_ciento():
    ok = resumen([("perfil", "perfil")] * 9 + [("perfil", None)], ("perfil", "tres_cuartos"))
    assert ok["cumple"]                                                    # 0 % de error, 10 % de no determinado
    mucho_nd = resumen([("perfil", "perfil")] * 7 + [("perfil", None)] * 3, ("perfil", "tres_cuartos"))
    assert not mucho_nd["cumple"]                                          # 30 % de no determinado
    con_error = resumen([("perfil", "perfil")] * 9 + [("perfil", "tres_cuartos")], ("perfil", "tres_cuartos"))
    assert not con_error["cumple"]                                         # 10 % de error


def test_wilson():
    lo, hi = wilson(0, 76)
    assert lo == 0.0 and 0.04 < hi < 0.06
    assert wilson(0, 0) is None
