"""El detector de inversión de z atrapa el caso real de zverev_saque_lateral_02.

Es el clip con el que se calibró el umbral (decisión 009): CODO_DER invierte la
coordenada z alrededor del frame 566. `slow`; se salta si no hay caché de pose.
"""

from __future__ import annotations

import pytest

try:
    from app.config import get_cache_dir, get_data_dir

    _DATA, _CACHE = get_data_dir(), get_cache_dir()
except Exception:
    _DATA = _CACHE = None


def _seq():
    if _DATA is None:
        return None
    from app.engine.pose import cache as pc
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    v = _DATA / "fase-a" / "segmentos" / "zverev_saque_lateral_02.mp4"
    if not v.is_file():
        return None
    b = MediaPipeBackend()
    return pc.cargar_si_vigente(_CACHE, v, b.id, b.config_hash)


_SEQ = _seq()

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(_SEQ is None, reason="No hay caché de pose para zverev_saque_lateral_02"),
]


def test_detecta_la_inversion_del_codo_derecho_cerca_del_frame_566():
    from app.engine.pose.articulaciones import ArticulacionCanonica as A
    from app.engine.validation import detectar_inversiones_z

    invs = detectar_inversiones_z(_SEQ, espacio="mundo")
    codo = [
        inv for inv in invs
        if inv.articulacion is A.CODO_DER and 555 <= inv.frame_hasta <= 575
    ]
    assert codo, "no se detectó la inversión de z del codo derecho cerca del frame 566"
    inv = codo[0]
    assert inv.z_antes > 0 > inv.z_despues
    assert inv.dz_torsos > 0.18


def test_la_franja_invertida_queda_como_tramo_no_auditable_en_e3():
    """La franja invertida (~frames 566–573) supera el hueco interpolable de 5
    fotogramas, así que E3 la deja como TramoExcluido: no se estima (R3)."""
    from app.engine.pipeline import procesar_e3
    from app.engine.pose.articulaciones import ArticulacionCanonica as A

    assert _SEQ.frames[566].get_mundo(A.CODO_DER).z < 0  # el glitch está en los datos

    filt = procesar_e3(_SEQ)
    cubre_566 = any(
        t.articulacion is A.CODO_DER and t.desde_frame <= 566 <= t.hasta_frame
        for t in filt.tramos_excluidos
    )
    assert cubre_566
