"""medicion_criterio1: lógica pura de la decisión 014 (ordenable, 1a, 1b, 1c)."""

import pytest

from app.medicion_criterio1 import (
    clasificar,
    orden_y_separacion,
    parse_toma,
    resumir,
    wilson,
)


def test_parse_toma():
    assert parse_toma("20260925_VCR_saque_trescuartos_240_02_rep01.mov") == "02"
    assert parse_toma("20260925_VCR_saque_trescuartos_240_02b_rep03.mov") == "02b"
    assert parse_toma("20260924_VCR_drive_perfil_240_01_rep01.mov") == "01"
    assert parse_toma("zverev.mp4") is None


def test_orden_y_separacion_del_par_y_de_la_cadena():
    assert orden_y_separacion({"p": 100, "t": 110, "b": 130}, "ptb") == ("ptb", 10)
    assert orden_y_separacion({"p": 120, "t": 110, "b": 130}, "ptb") == ("tpb", 10)
    assert orden_y_separacion({"p": 100, "t": 108, "b": None}, "pt") == ("pt", 8)
    assert orden_y_separacion({"p": 100, "t": 108, "b": None}, "ptb") == (None, None)   # falta el brazo


def test_ordenable_exige_mas_de_tau_fotogramas():
    f = {"p": 100, "t": 102, "b": None}                       # 2 fotogramas de separación
    assert clasificar(f, True, "pt", tau=1)["ordenable"] is True       # 2 > 1
    assert clasificar(f, True, "pt", tau=2)["ordenable"] is False      # 2 no es > 2
    f1 = {"p": 100, "t": 101, "b": None}                      # 1 fotograma
    assert clasificar(f1, True, "pt", tau=1)["ordenable"] is False     # 1 no es > 1
    empate = {"p": 100, "t": 100, "b": None}
    assert clasificar(empate, True, "pt", tau=1)["ordenable"] is False


def test_la_cadena_usa_la_menor_separacion_entre_picos_consecutivos():
    f = {"p": 100, "t": 110, "b": 111}                        # el par torso-brazo está a 1 fotograma
    assert clasificar(f, True, "ptb", tau=1)["ordenable"] is False
    assert clasificar(f, True, "pt", tau=1)["ordenable"] is True


def test_una_repeticion_no_valida_no_es_ordenable():
    assert clasificar({"p": 1, "t": 50, "b": 90}, False, "ptb", tau=1)["ordenable"] is False


def _grupo(ordenes, tau=1):
    """Repeticiones sintéticas del par a partir de los órdenes deseados ('pt'/'tp'/None = no válida)."""
    out = []
    for o in ordenes:
        if o is None:
            out.append(clasificar({"p": None, "t": None}, False, "pt", tau))
        else:
            out.append(clasificar({"p": 100, "t": 110} if o == "pt" else {"p": 110, "t": 100}, True, "pt", tau))
    return out


def test_repetible_pero_invertido_no_cuenta_como_fallo_del_criterio_1():
    # 9 de 10 con el orden INVERTIDO (tp): repetible, ordenable, y no coincide con el esperado.
    r = resumir(_grupo(["tp"] * 9 + ["pt"]), esperado="pt")
    assert r["criterio_1_cumplido"] is True            # 1a = 1,0 y 1b = 0,9
    assert r["1b_orden_modal"] == "tp" and r["1b_repetibilidad"] == pytest.approx(0.9)
    assert r["1c_coincidencia"] == pytest.approx(0.1)  # 1c se informa aparte


def test_las_no_validas_bajan_1a_sobre_todas_pero_no_1a_sobre_validas():
    r = resumir(_grupo(["pt"] * 6 + [None] * 4), esperado="pt")
    assert r["1a_sobre_todas"] == pytest.approx(0.6)
    assert r["1a_sobre_validas"] == pytest.approx(1.0)
    assert r["criterio_1_cumplido"] is False           # la regla usa todas las repeticiones


def test_orden_no_repetible_no_cumple_aunque_todo_sea_ordenable():
    r = resumir(_grupo(["pt"] * 5 + ["tp"] * 5), esperado="pt")
    assert r["1a_sobre_todas"] == 1.0 and r["1b_repetibilidad"] == pytest.approx(0.5)
    assert r["criterio_1_cumplido"] is False


def test_grupo_vacio_o_sin_ordenables():
    assert resumir([], "pt")["criterio_1_cumplido"] is False
    assert resumir(_grupo([None, None]), "pt")["1b_repetibilidad"] is None


def test_wilson():
    lo, hi = wilson(8, 10)
    assert 0.49 < lo < 0.50 and 0.94 < hi < 0.95
    assert wilson(0, 0) is None
    assert wilson(10, 10)[1] == 1.0
