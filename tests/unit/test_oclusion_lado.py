"""oclusion-lado: métricas de confianza/cobertura por tramo y resumen pareado (funciones puras)."""

import numpy as np
import pytest

from app.diagnosticos_e3 import (
    lado_cercano,
    mascaras_tramos,
    metricas_mascara,
    resumen_pareado,
    sesion_de,
)
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose


def test_metricas_confianza_media_solo_donde_el_punto_esta_y_cobertura_sobre_todos():
    conf = np.array([0.9, 0.9, np.nan, 0.2, 0.6])          # 1 ausente, 1 bajo el umbral
    media, cob = metricas_mascara(conf, np.ones(5, dtype=bool))
    assert media == pytest.approx((0.9 + 0.9 + 0.2 + 0.6) / 4)
    assert cob == pytest.approx(3 / 5)                       # 0.9, 0.9, 0.6 >= 0.5; el ausente cuenta como fallo


def test_metricas_respetan_la_mascara_y_una_mascara_vacia_da_none():
    conf = np.array([0.9, 0.1, 0.1, 0.9])
    m = np.array([True, False, False, True])
    assert metricas_mascara(conf, m) == (pytest.approx(0.9), pytest.approx(1.0))
    assert metricas_mascara(conf, np.zeros(4, dtype=bool)) == (None, None)


def test_mascaras_ventana_y_reposo_son_disjuntas_y_sin_ancla_solo_hay_clip():
    fps = 240.0
    m = mascaras_tramos(600, 300, fps)
    assert not np.any(m["ventana"] & m["reposo"])
    assert m["ventana"].sum() == 2 * int(0.3 * fps) + 1
    assert set(mascaras_tramos(600, None, fps)) == {"clip"}


def test_resumen_pareado_detecta_un_sesgo_sistematico_y_no_uno_al_azar():
    sistematico = resumen_pareado([-0.3, -0.2, -0.25, -0.4, -0.15, -0.3, -0.2, -0.35, -0.1, -0.2])
    assert sistematico["frac_neg"] == 1.0 and sistematico["p_signo"] < 0.05 and sistematico["mediana"] < -0.15
    azar = resumen_pareado([-0.1, 0.1, -0.05, 0.05, -0.2, 0.2, -0.1, 0.1])
    assert azar["p_signo"] > 0.5
    assert resumen_pareado([]) == {"n": 0}
    assert resumen_pareado([None, float("nan")]) == {"n": 0}


def test_sesion_de_usa_la_fecha_del_nombre():
    fechas = ["20260924", "20260925"]
    assert sesion_de("20260924_VCR_saque_perfil_240_01_rep01.mov", fechas) == 1
    assert sesion_de("20260925_VCR_drive_perfil_240_02_rep01.mov", fechas) == 2


def test_lado_cercano_segun_la_z_de_los_hombros():
    def frame(i, z_der, z_izq):
        pts = {A.HOMBRO_DER: Punto(0.4, 0.3, z_der, 0.9), A.HOMBRO_IZQ: Punto(0.6, 0.3, z_izq, 0.9)}
        return PoseFrame(i, True, puntos=pts, puntos_mundo={})

    def seq(z_der, z_izq):
        return SecuenciaPose(backend_id="s", backend_version="0", articulaciones=[A.HOMBRO_DER, A.HOMBRO_IZQ],
                             dims=3, ancho=1, alto=1, fps_efectivos=240.0, config_hash="x",
                             frames=[frame(i, z_der, z_izq) for i in range(5)])

    todos = np.ones(5, dtype=bool)
    assert lado_cercano(seq(-0.2, 0.2), todos) == "der"       # z menor = más cerca de la cámara
    assert lado_cercano(seq(0.2, -0.2), todos) == "izq"


def test_ancla_cruda_cae_donde_gira_mas_rapido_el_eje_de_hombros():
    from app.diagnosticos_e3 import ancla_cruda

    n, fps = 300, 240.0
    frames = []
    for i in range(n):
        # el eje de hombros gira lento salvo un giro rápido entre 140 y 160
        ang = np.radians(0.5 * i + (60.0 * np.clip((i - 140) / 20.0, 0, 1)))
        pm = {A.HOMBRO_IZQ: Punto(-0.2 * np.cos(ang), 0.0, -0.2 * np.sin(ang), 1.0),
              A.HOMBRO_DER: Punto(0.2 * np.cos(ang), 0.0, 0.2 * np.sin(ang), 1.0)}
        frames.append(PoseFrame(i, True, puntos={}, puntos_mundo=pm))
    seq = SecuenciaPose(backend_id="s", backend_version="0", articulaciones=[A.HOMBRO_IZQ, A.HOMBRO_DER],
                        dims=3, ancho=1, alto=1, fps_efectivos=fps, config_hash="x", frames=frames)
    assert 140 <= ancla_cruda(seq) <= 160
