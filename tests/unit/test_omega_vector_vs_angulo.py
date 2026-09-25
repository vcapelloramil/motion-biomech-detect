"""Qué mide ω sobre el vector hombro→codo (y qué NO mide).

ω = ∠(u[i-1], u[i]) · fps con u = dirección del vector: es la velocidad con que cambia la
ORIENTACIÓN de un segmento en el espacio. Consecuencias que fijan estas pruebas, con
geometrías de resultado conocido (decisión 011):

  1. balanceo del brazo (el codo gira alrededor del hombro): sí se mide, ω = velocidad real;
  2. extensión de codo (el antebrazo gira alrededor del codo, el brazo quieto): el vector
     hombro→codo NO cambia de dirección, ω = 0; solo lo ve el ÁNGULO de tres puntos;
  3. rotación axial pura (giro alrededor del propio vector, como la rotación interna del
     hombro): ni el vector ni el ángulo de codo cambian; ω = 0 en ambos.

Por eso los 2368 °/s de Fleisig para la rotación interna del hombro no son comparables con
esta ω, y los 1510 °/s de la extensión de codo lo son con el ángulo, no con el vector.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.engine.kinematics import serie_angulo_articular, velocidad_angular_segmento
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.segmentos_corporales import SegmentoCadena as S

FPS = 240.0
N = 120
T = np.arange(N) / FPS
GRADOS_POR_S = 300.0


def _seq(hombro, codo, muneca) -> SecuenciaPose:
    """Cada argumento es un array (N, 3) de posiciones (m) del lado derecho."""
    frames = []
    for i in range(N):
        pm = {
            A.HOMBRO_DER: Punto(*hombro[i], 1.0),
            A.CODO_DER: Punto(*codo[i], 1.0),
            A.MUNECA_DER: Punto(*muneca[i], 1.0),
        }
        frames.append(PoseFrame(i, True, puntos={}, puntos_mundo=pm))
    return SecuenciaPose(
        backend_id="sintetico", backend_version="0", articulaciones=list(pm), dims=3,
        ancho=1920, alto=1080, fps_efectivos=FPS, config_hash="x", frames=frames,
    )


def _fijo(p) -> np.ndarray:
    return np.tile(np.array(p, float), (N, 1))


def _arco(centro, radio, ang_rad, plano=(0, 2)) -> np.ndarray:
    """Punto que gira alrededor de ``centro`` en el plano dado (ejes x-z por defecto)."""
    out = np.tile(np.array(centro, float), (N, 1))
    out[:, plano[0]] += radio * np.cos(ang_rad)
    out[:, plano[1]] += radio * np.sin(ang_rad)
    return out


def _omega_vector(seq) -> float:
    w = velocidad_angular_segmento(seq, S.BRAZO, "der", brazo_via="codo")
    return float(np.nanmedian(w))


def _omega_angulo(seq) -> float:
    th = serie_angulo_articular(seq, "codo", "der")
    return float(np.nanmedian(np.abs(np.diff(th))) * FPS)


def test_balanceo_del_brazo_se_mide_con_su_velocidad_real():
    ang = np.radians(GRADOS_POR_S) * T
    seq = _seq(_fijo((0, 0, 0)), _arco((0, 0, 0), 0.3, ang), _fijo((0.3, 0.3, 0)))
    assert _omega_vector(seq) == pytest.approx(GRADOS_POR_S, rel=1e-3)


def test_extension_de_codo_no_la_ve_el_vector_hombro_codo_pero_si_el_angulo():
    # Brazo quieto (hombro y codo fijos); el antebrazo gira alrededor del codo.
    ang = np.radians(GRADOS_POR_S) * T
    codo = (0.3, 0.0, 0.0)
    # El antebrazo gira en el plano x-z, que CONTIENE al brazo (eje x): cambia su ángulo con él.
    seq = _seq(_fijo((0, 0, 0)), _fijo(codo), _arco(codo, 0.25, ang, plano=(0, 2)))
    assert _omega_vector(seq) == pytest.approx(0.0, abs=1e-6)          # el vector no cambia de dirección
    assert _omega_angulo(seq) == pytest.approx(GRADOS_POR_S, rel=0.02)  # el ángulo del codo sí


def test_rotacion_axial_pura_es_invisible_para_el_vector_y_para_el_angulo_del_codo():
    # Giro del antebrazo alrededor del eje del brazo (x): como la rotación interna del hombro.
    # El ángulo hombro-codo-muñeca no cambia (el antebrazo conserva su ángulo con el brazo).
    ang = np.radians(GRADOS_POR_S) * T
    codo = np.array([0.3, 0.0, 0.0])
    muneca = np.tile(codo, (N, 1)) + np.stack(
        [0.1 * np.ones(N), 0.25 * np.cos(ang), 0.25 * np.sin(ang)], axis=1)
    seq = _seq(_fijo((0, 0, 0)), _fijo(codo), muneca)
    assert _omega_vector(seq) == pytest.approx(0.0, abs=1e-6)
    assert _omega_angulo(seq) == pytest.approx(0.0, abs=1e-3)
