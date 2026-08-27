"""Secuenciación: recuperación del orden con sesgo, no auditables, segmentación."""

import numpy as np
import pytest

from app.engine.preparacion import TramoExcluido
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import (
    MARGEN_PLAUSIBILIDAD,
    _FLEISIG_MAX,
    evaluar_repeticion,
    secuenciar,
    segmentar,
    techo_velocidad,
)

FPS = 240.0
CENTRO = np.array([0.0, 0.0, 0.0])


def _sigmoide(t, t0, tau=0.06):
    return 1.0 / (1.0 + np.exp(-(t - t0) / tau))


def _seq_con_picos(t_pelvis, t_torso, t_brazo, *, n=180, offset=(0.05, 0.03, -0.02),
                   ruido=0.002, semilla=0):
    """Construye una secuencia donde cada segmento gira con un perfil sigmoide
    centrado en su instante -> la velocidad angular pica ahí. Suma un desvío fijo
    a todas las articulaciones (sesgo sistemático de los centros articulares) y
    ruido gaussiano."""
    rng = np.random.default_rng(semilla)
    off = np.array(offset)
    frames = []
    for i in range(n):
        t = i / FPS
        ph_p = np.radians(120) * _sigmoide(t, t_pelvis)
        ph_t = np.radians(140) * _sigmoide(t, t_torso)
        ph_b = np.radians(160) * _sigmoide(t, t_brazo)

        def eje(centro, ph, r=0.14):
            return (
                centro + np.array([-r * np.cos(ph), 0, -r * np.sin(ph)]),
                centro + np.array([r * np.cos(ph), 0, r * np.sin(ph)]),
            )

        ci, cd = eje(np.array([0, 0.5, 0]), ph_p)
        hi, hd = eje(np.array([0, 0.2, 0]), ph_t, r=0.16)
        # brazo: codo y muñeca derechos barren un arco desde el hombro derecho
        hombro_d = hd
        codo_d = hombro_d + np.array([0.01, -0.22 * np.cos(ph_b), -0.22 * np.sin(ph_b)])
        muneca_d = hombro_d + np.array([0.02, -0.45 * np.cos(ph_b), -0.45 * np.sin(ph_b)])

        pts = {}
        for art, xyz in [
            (A.CADERA_IZQ, ci), (A.CADERA_DER, cd),
            (A.HOMBRO_IZQ, hi), (A.HOMBRO_DER, hd),
            (A.CODO_DER, codo_d), (A.MUNECA_DER, muneca_d),
        ]:
            p = xyz + off + rng.normal(0, ruido, 3)
            pts[art] = Punto(float(p[0]), float(p[1]), float(p[2]), 0.9)
        frames.append(PoseFrame(i, True, puntos_mundo=pts))
    return SecuenciaPose("t", "t-0", tuple(A), 3, 100, 100, FPS, "x", frames)


def test_recupera_el_orden_correcto_pese_al_sesgo_y_al_ruido():
    seq = _seq_con_picos(0.25, 0.42, 0.60, semilla=1)
    resultados, resumen = secuenciar(seq, lado_dominante="der", corpus_publico=True)
    assert len(resultados) >= 1
    r = resultados[0]
    assert r.auditable is True
    assert r.orden_observado == (S.PELVIS, S.TORSO, S.BRAZO)
    assert r.correcto is True
    assert resumen.nota  # el caveat de corpus público está presente


def test_orden_invertido_se_detecta_como_incorrecto():
    seq = _seq_con_picos(0.60, 0.42, 0.25, semilla=2)  # brazo primero
    resultados, _ = secuenciar(seq, lado_dominante="der")
    r = resultados[0]
    assert r.orden_observado == (S.BRAZO, S.TORSO, S.PELVIS)
    assert r.correcto is False


def test_pico_en_tramo_no_auditable_no_se_reporta():
    seq = _seq_con_picos(0.25, 0.42, 0.60, semilla=3)
    # excluir la franja donde pica el torso (~frame 100) para sus articulaciones
    tramos = [
        TramoExcluido(A.HOMBRO_IZQ, "x", 90, 115),
        TramoExcluido(A.HOMBRO_DER, "x", 90, 115),
    ]
    r = evaluar_repeticion(
        seq, segmentar(seq, "der")[0], 1, lado_dominante="der",
        tramos_excluidos=tramos,
    )
    assert r.picos[S.TORSO].auditable is False
    assert "no auditable" in r.picos[S.TORSO].motivo
    assert r.auditable is False  # falta el torso -> la repetición no es auditable
    assert r.orden_observado is None


def test_techo_por_segmento_deriva_de_fleisig():
    # ordenados como en §3.4.2.2: pelvis < torso < brazo
    assert _FLEISIG_MAX[S.PELVIS] < _FLEISIG_MAX[S.TORSO] < _FLEISIG_MAX[S.BRAZO]
    assert techo_velocidad(S.PELVIS) == pytest.approx(440.0 * MARGEN_PLAUSIBILIDAD)
    assert techo_velocidad(S.BRAZO) == pytest.approx(2368.0 * MARGEN_PLAUSIBILIDAD)
    # un pico plausible de brazo (~2000 °/s) queda por debajo del techo; uno de
    # 25000 °/s (glitch de profundidad) queda muy por encima
    assert 2000.0 < techo_velocidad(S.BRAZO) < 25000.0


def test_pico_implausible_por_segmento_no_se_reporta():
    seq = _seq_con_picos(0.25, 0.42, 0.60, semilla=7)
    # inflar artificialmente la muñeca/codo derechos en un frame -> ω enorme
    frames = list(seq.frames)
    i = 90
    p = frames[i].puntos_mundo
    from dataclasses import replace
    from app.engine.pose.base import Punto
    p2 = dict(p)
    p2[A.CODO_DER] = Punto(p[A.CODO_DER].x + 3.0, p[A.CODO_DER].y, p[A.CODO_DER].z, 0.9)
    frames[i] = replace(frames[i], puntos_mundo=p2)
    seq2 = replace(seq, frames=frames)
    r = evaluar_repeticion(
        seq2, segmentar(seq2, "der")[0], 1, lado_dominante="der", tramos_excluidos=[]
    )
    assert r.picos[S.BRAZO].auditable is False
    assert "implausible" in r.picos[S.BRAZO].motivo


def test_segmentacion_manual_respeta_las_ventanas():
    seq = _seq_con_picos(0.25, 0.42, 0.60)
    ventanas = segmentar(seq, "der", manual=[(0.0, 0.3), (0.35, 0.75)])
    assert len(ventanas) == 2
    assert ventanas[0].desde_frame == 0
    assert ventanas[1].hasta_frame == int(round(0.75 * FPS))
