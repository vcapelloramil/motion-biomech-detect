"""resumen_criterio1: solo formatea; comprueba la estructura y que rotule lo descriptivo como tal."""

from app.medicion_criterio1 import clasificar, resumir
from app.resumen_criterio1 import descriptivo, generar, tabla_tau


def _json():
    reps = [{"clip": f"c{i}", "gesto": "saque", "encuadre": "trescuartos", "toma": "02", "valida": True,
             "frames": {"p": 100, "t": 110, "b": 140}} for i in range(4)]
    res = {"saque|trescuartos": {
        "par_pelvis_torso": resumir([clasificar(r["frames"], True, "pt", 1) for r in reps], "pt"),
        "cadena": resumir([clasificar(r["frames"], True, "ptb", 1) for r in reps], "ptb")}}
    return {"sesion": 2, "rol": "MEDICIÓN (conjunto de medición)", "version_motor": "0.4.1", "commit": "abcdef0123456789",
            "arbol_sucio": False, "tau_primaria": 1, "taus": [1], "repeticiones": reps, "resultado_por_tau": {"1": res}}


def test_la_tabla_incluye_1a_1b_y_1c_por_separado():
    filas = tabla_tau(_json()["resultado_por_tau"]["1"])
    assert "1a (todas)" in filas[0] and "1b (orden modal)" in filas[0] and "1c (esperado)" in filas[0]
    assert len(filas) == 2 + 2                                    # encabezado + 2 filas (par y cadena)
    assert "**cumple**" in filas[2]


def test_el_complemento_descriptivo_queda_rotulado_y_calcula_las_medianas():
    filas = descriptivo(_json()["repeticiones"])
    assert "10.0" in filas[2] and "30.0" in filas[2]              # |pelvis-torso| = 10, torso->brazo = 30
    md = generar([_json()])
    assert "DESCRIPTIVO (no pre-registrado)" in md and "PRIMARIA" in md and "Sesión 2" in md
