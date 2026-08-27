"""E4 sobre pose real del corpus público (validación cualitativa; plan Etapa 4, arranque).

NO asevera que el orden sea correcto —eso es el Criterio 1, diferido a la Fase B—.
Solo verifica que el pipeline completo produce una estructura coherente sin romperse.
`slow`; se salta si no hay caché de pose (esquema nuevo).
"""

from __future__ import annotations

import itertools

import pytest

try:
    from app.config import get_cache_dir, get_data_dir

    _DATA, _CACHE = get_data_dir(), get_cache_dir()
except Exception:
    _DATA = _CACHE = None


def _cargar(nombre):
    if _DATA is None:
        return None
    from app.engine.pose import cache as pc
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    v = _DATA / "fase-a" / "segmentos" / nombre
    if not v.is_file():
        return None
    b = MediaPipeBackend()
    return pc.cargar_si_vigente(_CACHE, v, b.id, b.config_hash)


_SEQ = _cargar("zverev_saque_lateral_01.mp4")

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(_SEQ is None, reason="No hay caché de pose para el corpus"),
]


def test_pipeline_e4_produce_estructura_coherente():
    from app.engine.pipeline import procesar_e3
    from app.engine.segmentos_corporales import ORDEN_ESPERADO, SegmentoCadena
    from app.engine.sequencing import secuenciar

    filt = procesar_e3(_SEQ)
    resultados, resumen = secuenciar(
        filt.secuencia, lado_dominante="der",
        tramos_excluidos=filt.tramos_excluidos, corpus_publico=True,
    )

    assert len(resultados) >= 1
    permutaciones = set(itertools.permutations(ORDEN_ESPERADO))
    for r in resultados:
        assert set(r.picos) == set(ORDEN_ESPERADO)
        assert r.orden_observado is None or tuple(r.orden_observado) in permutaciones
        # coherencia: auditable <=> hay orden observado
        assert r.auditable == (r.orden_observado is not None)

    assert resumen.repeticiones_evaluadas == len(resultados)
    assert resumen.nota  # el caveat de corpus público viaja en el resumen
