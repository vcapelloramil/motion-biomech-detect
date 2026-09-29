"""explorar_fase_b: funciones puras (sin video ni pose real)."""

import numpy as np
import pytest

from app.explorar_fase_b import PASOS, pico_p99_por_paso, resumir_grupo

FPS = 240.0


def _vectores_girando(grados_por_s: float, n: int = 200) -> np.ndarray:
    ang = np.radians(grados_por_s) * np.arange(n) / FPS
    return np.stack([np.cos(ang), np.zeros(n), np.sin(ang)], axis=1)


def test_giro_uniforme_da_la_misma_velocidad_para_todo_paso():
    # Movimiento sostenido: ω_k no depende de k (a diferencia del ruido).
    picos = pico_p99_por_paso(_vectores_girando(300.0), FPS)
    assert len(picos) == len(PASOS)
    assert picos == pytest.approx([300.0] * len(PASOS), rel=1e-3)


def test_un_glitch_de_pocos_fotogramas_cae_al_aumentar_el_paso():
    # Vector quieto con una oscilación de 30° en los fotogramas 100 y 102 (4 saltos de
    # 1 fotograma: alcanza el p99 de 199 muestras). Con k=8 el mismo desvío se reparte
    # en 8 fotogramas y la velocidad cae ~8 veces: el ruido no sobrevive al paso.
    u = _vectores_girando(0.0)
    ang = np.radians(30.0)
    for i in (100, 102):
        u[i] = [np.cos(ang), 0.0, np.sin(ang)]
    p_k1, *_, p_k8 = pico_p99_por_paso(u, FPS)
    assert p_k1 > 4 * p_k8


def test_resumir_grupo_ignora_clips_no_auditables():
    def clip(p, t, b, inv=3):
        return {"pico_p99_por_paso": {"pelvis": [p] * 4, "torso": [t] * 4, "brazo": [b] * 4},
                "inversiones_z": inv}
    r = resumir_grupo([clip(1000, 500, 3000), clip(800, 400, 2000, inv=5), {"no_auditable": "x"}])
    assert r["clips"] == 2
    assert r["clips_no_auditables"] == 1
    assert r["pelvis_sobre_torso_mediana"] == pytest.approx(2.0)
    assert r["inversiones_z_mediana"] == pytest.approx(4.0)
    assert r["caida_pelvis_k1_a_k8_pct"] == pytest.approx(0.0)


def test_resumir_grupo_sin_clips_utilizables():
    assert resumir_grupo([{"no_auditable": "x"}]) == {"clips": 0, "clips_no_auditables": 1}


def _rep(orden, fuera=None):
    return {"orden": orden, "brazo_global_fuera_de_ventana": fuera}


def test_resumir_ordenes_cuenta_correctas_brazo_primero_y_fuera_de_ventana():
    from app.explorar_fase_b import resumir_ordenes

    clips = [
        {"repeticiones": [_rep(["pelvis", "torso", "brazo"], False)], "ancla_torso_vs_pelvis_ms": 10.0},
        {"repeticiones": [_rep(["brazo", "torso", "pelvis"], True)], "ancla_torso_vs_pelvis_ms": 30.0},
        {"repeticiones": [_rep(None, None)], "ancla_torso_vs_pelvis_ms": None},
        {"no_auditable": "sin series"},
    ]
    o = resumir_ordenes(clips)
    assert o["repeticiones"] == 3
    assert o["auditables"] == 2
    assert o["pelvis_torso_brazo"] == 1
    assert o["brazo_primero"] == 1
    assert o["brazo_global_fuera_de_ventana"] == 1
    assert o["anclas_torso_vs_pelvis_dif_mediana_ms"] == pytest.approx(20.0)
