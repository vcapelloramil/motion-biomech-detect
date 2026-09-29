"""Cinemática: ángulos entre tres puntos, separación cadera-hombro, velocidad angular."""

import numpy as np
import pytest

from app.engine.kinematics import (
    angulo_tres_puntos,
    serie_separacion_cadera_hombro,
    velocidad_angular_segmento,
)
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.segmentos_corporales import SegmentoCadena


def _seq(frames, fps=240.0):
    return SecuenciaPose(
        "test", "test-0", tuple(A), 3, 100, 100, fps, "x", frames
    )


def test_angulo_recto():
    a = angulo_tres_puntos([1, 0, 0], [0, 0, 0], [0, 1, 0])
    assert a == pytest.approx(90.0)


def test_angulo_colineal():
    assert angulo_tres_puntos([1, 0, 0], [0, 0, 0], [-1, 0, 0]) == pytest.approx(180.0)
    assert angulo_tres_puntos([1, 0, 0], [0, 0, 0], [2, 0, 0]) == pytest.approx(0.0)


def test_angulo_con_punto_faltante_es_nan():
    assert np.isnan(angulo_tres_puntos([0, 0, 0], [0, 0, 0], [1, 0, 0]))


def test_separacion_cadera_hombro_de_ejes_perpendiculares():
    # caderas sobre el eje x, hombros sobre el eje z -> 90°
    pts = {
        A.CADERA_IZQ: Punto(-0.1, 0.5, 0.0, 0.9),
        A.CADERA_DER: Punto(0.1, 0.5, 0.0, 0.9),
        A.HOMBRO_IZQ: Punto(0.0, 0.3, -0.1, 0.9),
        A.HOMBRO_DER: Punto(0.0, 0.3, 0.1, 0.9),
    }
    seq = _seq([PoseFrame(0, True, puntos_mundo=pts)])
    assert serie_separacion_cadera_hombro(seq)[0] == pytest.approx(90.0)


def test_velocidad_angular_de_una_rotacion_constante():
    fps = 240.0
    omega_real = 200.0  # °/s
    n = 120
    frames = []
    for i in range(n):
        phi = np.radians(omega_real) * (i / fps)  # rad
        c, s = np.cos(phi), np.sin(phi)
        pts = {
            A.CADERA_IZQ: Punto(-0.12 * c, 0.5, -0.12 * s, 0.9),
            A.CADERA_DER: Punto(0.12 * c, 0.5, 0.12 * s, 0.9),
        }
        frames.append(PoseFrame(i, True, puntos_mundo=pts))
    omega = velocidad_angular_segmento(_seq(frames, fps), SegmentoCadena.PELVIS, "der")
    assert np.nanmean(omega[1:]) == pytest.approx(omega_real, rel=0.02)
