"""Pipeline de la Etapa 3 sobre una secuencia de pose real (de la caché).

`slow` + se salta si no hay corpus o si la caché no está en el esquema nuevo.
"""

from __future__ import annotations

import numpy as np
import pytest

try:
    from app.config import get_cache_dir, get_data_dir

    _DATA = get_data_dir()
    _CACHE = get_cache_dir()
except Exception:
    _DATA = _CACHE = None


def _cargar_zverev():
    if _DATA is None:
        return None
    from app.engine.pose import cache as pose_cache
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    video = _DATA / "fase-a" / "segmentos" / "zverev_saque_lateral_01.mp4"
    if not video.is_file():
        return None
    b = MediaPipeBackend()
    return pose_cache.cargar_si_vigente(_CACHE, video, b.id, b.config_hash)


_SEQ = _cargar_zverev()

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(_SEQ is None, reason="No hay caché de pose (esquema nuevo) para Zverev"),
]


def test_pipeline_produce_secuencia_filtrada_coherente():
    from app.engine.pipeline import procesar_e3

    res = procesar_e3(_SEQ)

    assert res.espacio == "mundo"
    assert res.metodo_corte == "winter"
    # corte plausible para movimiento humano (§3.4.2)
    assert 3.0 <= res.corte_hz <= 18.0
    assert res.secuencia.n_frames == _SEQ.n_frames

    # el bloque de trazabilidad tiene la forma del contrato
    tz = res.trazabilidad_filtro()
    assert tz["tipo"] == "butterworth" and tz["fase_cero"] is True
    assert tz["orden"] == res.orden


def test_el_filtro_reduce_la_energia_de_alta_frecuencia():
    from app.engine.pipeline import procesar_e3
    from app.engine.pose.articulaciones import ArticulacionCanonica as A

    res = procesar_e3(_SEQ)

    # CADERA_IZQ: cobertura completa y sin saltos -> comparación alineada por índice.
    art = A.CADERA_IZQ
    por_indice_cruda = {
        f.indice: f.get_mundo(art).x for f in _SEQ.frames if f.get_mundo(art) is not None
    }
    comunes = [
        f.indice
        for f in res.secuencia.frames
        if f.get_mundo(art) is not None and f.indice in por_indice_cruda
    ]
    assert len(comunes) > 0.9 * _SEQ.n_frames  # casi todos los fotogramas

    cruda = np.array([por_indice_cruda[i] for i in comunes])
    filtrada = np.array(
        [f.get_mundo(art).x for f in res.secuencia.frames if f.indice in set(comunes)]
    )
    # varianza de la diferencia de primer orden (proxy de alta frecuencia): baja
    assert np.var(np.diff(filtrada)) < np.var(np.diff(cruda))
