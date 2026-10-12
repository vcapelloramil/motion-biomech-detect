"""Selección de repeticiones del Paso B (``app.medicion_paso_b``): qué se mide, en qué orden y qué se excluye. Sin videos."""

from __future__ import annotations

from app.medicion_paso_b import elegir_repeticiones, prioridad


def _rep(nombre, real="IMG_6376.MOV", ventana=(100, 900), meseta=True):
    return {"repeticion": nombre, "real": real, "ventana_real": list(ventana), "entera_en_la_meseta": meseta}


def _cat(*nombres, lado="der"):
    return {n: {"fuente": "propio", "lado_dominante": lado} for n in nombres}


def test_orden_de_prioridad_primero_lo_que_decide_la_035():
    assert prioridad("saque", "perfil") < prioridad("saque", "trescuartos") < prioridad("drive", "perfil")
    assert prioridad("reves", "trescuartos") > prioridad("drive", "trescuartos")
    assert prioridad("volea", "perfil") > prioridad("reves", "trescuartos")


def test_se_miden_las_repeticiones_validas_en_orden_y_con_su_lado():
    n1 = "20260925_VCR_drive_perfil_240_02_rep01.mov"
    n2 = "20260925_VCR_saque_perfil_240_02_rep01.mov"
    ali = {"repeticiones": [_rep(n1), _rep(n2, real="IMG_6377.MOV")]}
    medir, excl = elegir_repeticiones(ali, _cat(n1, n2, lado="izq"))
    assert [m["repeticion"] for m in medir] == [n2, n1]          # el saque de perfil va primero
    assert medir[0]["gesto"] == "saque" and medir[0]["encuadre"] == "perfil" and medir[0]["lado"] == "izq"
    assert medir[0]["fecha"] == "20260925" and medir[0]["toma"] == "02" and medir[0]["ventana_real"] == [100, 900]
    assert excl == []


def test_se_excluyen_y_se_informan_la_rampa_y_el_original_incompleto():
    r1 = "20260924_VCR_saque_perfil_240_01_rep01.mov"
    r2 = "20260925_VCR_saque_trescuartos_240_02_rep01.mov"
    r3 = "20260925_VCR_saque_trescuartos_240_02b_rep01.mov"
    ali = {"repeticiones": [_rep(r1, meseta=False), _rep(r2, real="IMG_6391.mov"), _rep(r3, real="IMG_6392.MOV")]}
    medir, excl = elegir_repeticiones(ali, _cat(r1, r2, r3))
    assert [m["repeticion"] for m in medir] == [r3]
    assert {e["repeticion"]: e["motivo"] for e in excl} == {
        r1: "empieza en la rampa de velocidad",
        r2: "el original IMG_6391.mov llegó incompleto",
    }


def test_los_controles_fuera_de_cuadro_y_de_espaldas_y_lo_que_no_esta_en_el_catalogo_no_entran():
    fuera = "20260924_VCR_saque_fueracuadro_240_01_rep01.mov"
    sin_cat = "20260925_VCR_reves_perfil_240_02_rep01.mov"
    ali = {"repeticiones": [_rep(fuera), _rep(sin_cat)]}
    medir, excl = elegir_repeticiones(ali, _cat(fuera))
    assert medir == [] and excl == []
