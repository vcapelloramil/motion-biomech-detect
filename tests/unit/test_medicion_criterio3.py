"""medicion_criterio3: lógica pura (decisión 014)."""

import numpy as np
import pytest

from app.medicion_criterio3 import (
    comparar_sesiones,
    diferencia_relativa,
    fraccion_consistente,
    fraccion_sin_evidencia,
    mad_sigma,
)


def test_mad_sigma_de_una_normal_se_parece_a_su_desvio():
    x = np.random.default_rng(0).normal(10.0, 2.0, 5000)
    assert mad_sigma(x) == pytest.approx(2.0, rel=0.05)
    assert mad_sigma([5.0, 5.0, 5.0]) == 0.0
    assert np.isnan(mad_sigma([]))
    assert mad_sigma([1.0, None, float("nan"), 3.0, 5.0]) == pytest.approx(mad_sigma([1.0, 3.0, 5.0]))


def test_un_corrimiento_grande_es_inconsistente_y_su_p_de_permutacion_es_chico():
    rng = np.random.default_rng(1)
    a = rng.normal(40.0, 3.0, 12)
    corrido = comparar_sesiones(a, a + rng.normal(0, 0.5, 12) + 30.0, n_boot=500)
    assert corrido["consistente"] is False and corrido["delta"] > corrido["sigma_w"]
    assert corrido["delta_ic95"][0] > 0
    assert corrido["p_permutacion"] < 0.01 and corrido["sin_evidencia_de_diferencia"] is False


def test_caracteristica_operativa_de_la_regla_delta_menor_que_sigma_w():
    # Documenta la propiedad que motivó agregar el p de permutación (decisión 014): con n = 6 por sesión,
    # sesiones del MISMO proceso salen "consistentes" solo ~76 % de las veces (no ~100 %).
    rng = np.random.default_rng(123)
    ok = sum(comparar_sesiones(rng.normal(40, 3, 6), rng.normal(40, 3, 6), n_boot=50)["consistente"]
             for _ in range(400))
    assert 0.65 < ok / 400 < 0.88


def test_el_p_de_permutacion_esta_calibrado_bajo_el_mismo_proceso():
    rng = np.random.default_rng(7)
    sin = sum(comparar_sesiones(rng.normal(40, 3, 6), rng.normal(40, 3, 6), n_boot=200)["sin_evidencia_de_diferencia"]
              for _ in range(300))
    assert 0.90 < sin / 300 <= 1.0                      # ~95 % sin evidencia cuando no hay diferencia


def test_comparar_con_datos_insuficientes_no_decide():
    assert comparar_sesiones([1.0], [2.0, 3.0])["consistente"] is None
    assert comparar_sesiones([], [])["n1"] == 0


def test_la_comparacion_es_determinista_con_la_misma_semilla():
    a, b = [1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]
    assert comparar_sesiones(a, b, n_boot=200) == comparar_sesiones(a, b, n_boot=200)


def test_fraccion_consistente_ignora_las_no_evaluables():
    rs = [{"consistente": True}, {"consistente": False}, {"consistente": True}, {"consistente": None}]
    assert fraccion_consistente(rs) == (2, 3, pytest.approx(2 / 3))
    assert fraccion_consistente([{"consistente": None}]) == (0, 0, None)


def test_fraccion_sin_evidencia():
    rs = [{"sin_evidencia_de_diferencia": True}, {"sin_evidencia_de_diferencia": False},
          {"sin_evidencia_de_diferencia": None}]
    assert fraccion_sin_evidencia(rs) == (1, 2, 0.5)


def test_diferencia_relativa():
    assert diferencia_relativa(100.0, 100.0) == 0.0
    assert diferencia_relativa(100.0, 120.0) == pytest.approx(20 / 110)
    assert diferencia_relativa(0.0, 0.0) == 0.0
