"""ventana-brazo: el pico del brazo dentro de una ventana [torso − adelanto, torso + post]."""

import numpy as np

from app.diagnosticos_e3 import pico_brazo_en_ventana

FPS = 240.0


def _omega_dos_picos() -> np.ndarray:
    """Pico grande y temprano (frame 60) y pico chico y tardío (frame 150); torso en 130."""
    w = np.full(300, 50.0)
    w[58:63] = [300.0, 700.0, 1200.0, 700.0, 300.0]
    w[148:153] = [200.0, 500.0, 800.0, 500.0, 200.0]
    return w


def test_con_adelanto_amplio_gana_el_pico_temprano_y_con_adelanto_cero_el_tardio():
    w, ft = _omega_dos_picos(), 130
    kw = dict(post_ms=300, fps=FPS, excluidos=set(), techo=7104.0)
    f300, _ = pico_brazo_en_ventana(w, ft, adelanto_ms=300, **kw)     # ventana [58, 202]
    f0, _ = pico_brazo_en_ventana(w, ft, adelanto_ms=0, **kw)         # ventana [130, 202]
    assert f300 == 60           # 70 fotogramas antes que el torso
    assert f0 == 150            # con adelanto 0, "brazo antes que torso" es imposible


def test_los_frames_excluidos_y_el_techo_se_respetan():
    w, ft = _omega_dos_picos(), 130
    fr, motivo = pico_brazo_en_ventana(w, ft, adelanto_ms=300, post_ms=300, fps=FPS,
                                       excluidos={60}, techo=7104.0)
    assert fr is None                                            # el pico cae en un frame no auditable
    fr, motivo = pico_brazo_en_ventana(w, ft, adelanto_ms=300, post_ms=300, fps=FPS,
                                       excluidos=set(), techo=1000.0)
    assert fr is None and "implausible" in motivo
