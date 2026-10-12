"""Funciones puras del arnés del Paso A (``app.medicion_paso_a``): tolerancia en ms compartida con el producto,
distribución de Δ y desfase entre ω. Sin pose ni video."""

from __future__ import annotations

import numpy as np
import pytest

from app.engine.tolerancia_orden import TOLERANCIA_ORDEN_S, TOLERANCIAS_SENSIBILIDAD_S, es_ordenable
from app.medicion_paso_a import (
    FPS_MUESTREO_REAL,
    clasificar_ms,
    correlacion_y_desfase,
    delta_torso_menos_pelvis_ms,
    omega_giro_axial,
    pico_en_ventana,
    resumen_deltas,
)

T = TOLERANCIA_ORDEN_S


def test_la_tolerancia_es_la_unica_constante_del_producto_y_del_recalculo():
    from app import ensamblar_reporte, medicion_paso_a

    assert medicion_paso_a.TOLERANCIA_ORDEN_S * 1000.0 == pytest.approx(ensamblar_reporte.TOLERANCIA_ORDEN_MS)
    assert T == pytest.approx(1 / 120)
    assert [round(t * 1000, 1) for t in TOLERANCIAS_SENSIBILIDAD_S] == [4.2, 12.5, 16.7]


def test_es_ordenable_es_estricto():
    assert not es_ordenable(T)           # igual a la tolerancia: no
    assert not es_ordenable(-T)
    assert not es_ordenable(2 / 240.0)   # dos fotogramas de la grilla de 240 Hz
    assert es_ordenable(3 / 240.0)


def test_un_fotograma_a_120_2_fps_no_es_ordenable_con_la_tolerancia_primaria_y_dos_si():
    un_fotograma = 1.0 / FPS_MUESTREO_REAL        # 8,319 ms < 8,333 ms
    assert not es_ordenable(un_fotograma)
    assert es_ordenable(2 * un_fotograma)


def test_clasifica_en_ms_con_pares_y_cadena():
    inst = {"p": 0.300, "t": 0.300 + 3 / FPS_MUESTREO_REAL, "b": 0.500}
    c = clasificar_ms(inst, True, "pt", T)
    assert c["orden"] == "pt" and c["ordenable"] and c["separacion_min"] == pytest.approx(3 / FPS_MUESTREO_REAL * 1000)
    # tronco primero, a un fotograma: se ordena (el orden está dado) pero no es ordenable
    c = clasificar_ms({"p": 0.3083, "t": 0.3, "b": 0.5}, True, "pt", T)
    assert c["orden"] == "tp" and not c["ordenable"]
    # la cadena es ordenable solo si TODOS los pares consecutivos lo son
    c = clasificar_ms({"p": 0.300, "t": 0.320, "b": 0.325}, True, "ptb", T)
    assert c["orden"] == "ptb" and not c["ordenable"]


def test_un_pico_ausente_o_una_repeticion_invalida_no_se_clasifica():
    assert clasificar_ms({"p": 0.3, "t": None, "b": 0.5}, True, "pt", T)["orden"] is None
    assert not clasificar_ms({"p": 0.3, "t": 0.4, "b": 0.5}, False, "pt", T)["ordenable"]


def test_delta_positivo_es_cadera_primero():
    assert delta_torso_menos_pelvis_ms({"p": 0.30, "t": 0.32, "b": None}) == pytest.approx(20.0)
    assert delta_torso_menos_pelvis_ms({"p": 0.32, "t": 0.30, "b": None}) == pytest.approx(-20.0)
    assert delta_torso_menos_pelvis_ms({"p": None, "t": 0.30, "b": None}) is None


def test_resumen_de_deltas():
    r = resumen_deltas([-20.0, -10.0, -5.0, 0.0, 5.0, 25.0])
    assert r["n"] == 6 and r["tronco_primero"] == 2 and r["cadera_primero"] == 1 and r["dentro_de_la_tolerancia"] == 3
    assert r["mediana_ms"] == pytest.approx(-2.5)
    assert resumen_deltas([]) == {"n": 0}


def _gauss(n: int, centro: float, ancho: float = 6.0) -> np.ndarray:
    x = np.arange(n)
    return np.exp(-0.5 * ((x - centro) / ancho) ** 2)


def test_el_desfase_de_omega_se_mide_con_signo_y_en_ms():
    fps = 120.0
    cadera = _gauss(120, 50)
    tronco = _gauss(120, 56)               # el tronco llega 6 fotogramas (50 ms) después
    r = correlacion_y_desfase(cadera, tronco, fps)
    assert r["desfase_ms"] == pytest.approx(50.0, abs=1e-6)
    assert r["correlacion_en_el_desfase"] > 0.99 and r["correlacion"] < r["correlacion_en_el_desfase"]
    # al revés: el tronco se adelanta
    assert correlacion_y_desfase(tronco, cadera, fps)["desfase_ms"] == pytest.approx(-50.0, abs=1e-6)


def test_series_degeneradas_no_rompen_la_correlacion():
    assert correlacion_y_desfase(np.full(50, np.nan), np.arange(50.0), 120.0)["correlacion"] is None
    assert correlacion_y_desfase(np.ones(50), np.arange(50.0), 120.0)["correlacion"] is None
    assert correlacion_y_desfase(np.arange(3.0), np.arange(3.0), 120.0)["desfase_ms"] is None


def _linea(n: int, fps: float, omega_deg_s: float, inclinacion_deg_s: float = 0.0):
    """Una línea izquierda → derecha de 0,3 m que gira alrededor de la vertical a ``omega`` y, opcionalmente, se inclina."""
    t = np.arange(n) / fps
    yaw = np.radians(omega_deg_s) * t
    incl = np.radians(inclinacion_deg_s) * t
    izq = np.zeros((n, 3))
    der = np.stack([0.3 * np.cos(yaw) * np.cos(incl), 0.3 * np.sin(incl), 0.3 * np.sin(yaw) * np.cos(incl)], axis=1)
    return izq, der


def test_el_giro_axial_recupera_la_velocidad_de_rotacion_alrededor_de_la_vertical():
    izq, der = _linea(60, 120.0, 300.0)
    w = omega_giro_axial(izq, der, 120.0)
    assert np.nanmedian(w) == pytest.approx(300.0, rel=0.01)


def test_la_inclinacion_lateral_no_suma_al_giro_axial():
    """Es la razón del control: el vector que usa el motor mide la velocidad angular TOTAL, que incluye la inclinación."""
    izq, der = _linea(60, 120.0, 100.0, inclinacion_deg_s=200.0)
    assert np.nanmedian(omega_giro_axial(izq, der, 120.0)) == pytest.approx(100.0, rel=0.05)


def test_el_giro_axial_atraviesa_los_saltos_de_pi_y_los_huecos():
    izq, der = _linea(200, 120.0, 400.0)       # da más de media vuelta: cruza ±180°
    der[50:55] = np.nan
    w = omega_giro_axial(izq, der, 120.0)
    assert np.isnan(w[52]) and np.nanmax(w) < 450 and np.nanmin(w) > 350
    assert np.all(np.isnan(omega_giro_axial(np.full((2, 3), np.nan), np.full((2, 3), np.nan), 120.0)))


def test_el_pico_en_ventana_pide_fotogramas_validos():
    w = np.zeros(100)
    w[40] = 5.0
    assert pico_en_ventana(w, 20, 80, 100.0) == pytest.approx(0.40)
    w2 = w.copy()
    w2[30:60] = np.nan
    assert pico_en_ventana(w2, 20, 80, 100.0) is None
