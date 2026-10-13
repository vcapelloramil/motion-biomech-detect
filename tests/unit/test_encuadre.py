"""``engine/encuadre``: el encuadre visto (giro de la línea de hombros en la preparación) contra el declarado (decisión 035, D)."""

from __future__ import annotations

import numpy as np
import pytest

from app.engine import encuadre as e
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import Punto


def _frame(giro_deg: float) -> dict:
    a = np.radians(giro_deg)
    izq = Punto(-0.2 * np.cos(a), 0.0, -0.2 * np.sin(a), 0.9)
    der = Punto(0.2 * np.cos(a), 0.0, 0.2 * np.sin(a), 0.9)
    return {A.HOMBRO_IZQ: izq, A.HOMBRO_DER: der}


def test_el_giro_de_hombros_es_el_angulo_con_el_plano_de_la_imagen():
    assert e.giro_hombros_grados([_frame(35.0)] * 60, 0, 59) == pytest.approx(35.0)
    assert e.giro_hombros_grados([_frame(120.0)] * 60, 0, 59) == pytest.approx(60.0)   # simétrico: 120° ≡ 60°


def test_con_pocos_fotogramas_validos_no_se_afirma_nada():
    assert e.giro_hombros_grados([_frame(40.0)] * 10, 0, 9) is None
    assert e.giro_hombros_grados([{}] * 60, 0, 59) is None


@pytest.mark.parametrize(("giro", "esperado"), [(26.0, "perfil"), (42.0, "perfil"), (45.0, None), (49.9, None), (50.0, "tres_cuartos"), (83.0, "tres_cuartos"), (None, None)])
def test_la_franja_del_medio_no_afirma_nada(giro, esperado):
    assert e.clasificar(giro) == esperado


def test_el_golpe_del_celular_del_12_10_cae_en_tres_cuartos():
    """59° (medido en el corpus propio): tres cuartos, aunque se declaró perfil."""
    v = e.encuadre_visto([_frame(59.0)] * 400, frame_pico_torso=300, fps=240.0)
    assert v["visto"] == "tres_cuartos" and v["giro_grados"] == pytest.approx(59.0)
    assert e.discrepa("saque", "perfil", v["visto"]) is True


def test_discrepa_solo_para_gestos_calibrados_y_visto_conocido():
    assert e.discrepa("saque", "perfil", "perfil") is False
    assert e.discrepa("saque", "perfil", None) is False          # franja intermedia o sin dato: no se afirma
    assert e.discrepa("drive", "perfil", "tres_cuartos") is False
    assert e.discrepa("saque", "espaldas", "perfil") is False


def test_el_aviso_se_entiende_sin_tecnicismos():
    t = e.aviso("perfil", "tres_cuartos")
    assert t == "El video parece grabado de tres cuartos, pero elegiste perfil. Revisá el encuadre antes de comparar tus resultados."
    assert not any(x in t.lower() for x in ("grados", "yaw", "umbral", "corpus", "pose"))
