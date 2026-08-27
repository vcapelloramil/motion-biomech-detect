"""MediaPipeBackend sobre video real del corpus (plan, pruebas de la Etapa 2).

- Video con el jugador visible: cobertura de detección > 95 %.
- Video con oclusión / paneo: puntos de baja confianza o fotogramas sin detección.
- El backend produce la misma estructura que cualquier otro (SecuenciaPose).

`slow`: corre inferencia real. Se salta si no hay corpus.
"""

from __future__ import annotations

import pytest

try:
    from app.config import get_data_dir

    _FASE_A = get_data_dir() / "fase-a"
except Exception:
    _FASE_A = None

_SEG = _FASE_A / "segmentos" if _FASE_A else None
_CTRL = _FASE_A / "control" if _FASE_A else None
_HAY_CORPUS = bool(_SEG and _SEG.is_dir() and any(_SEG.glob("*.mp4")))

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not _HAY_CORPUS, reason="No hay corpus Fase A (KINETIQ_DATA_DIR)"),
]

MAX_FRAMES = 40


def _procesar(nombre_dir, nombre_archivo):
    from app.engine.ingest import iterar_fotogramas, probe
    from app.engine.pose.base import SecuenciaPose
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    video = nombre_dir / nombre_archivo
    md = probe(video)
    with MediaPipeBackend() as backend:
        seq = backend.procesar(
            iterar_fotogramas(video), ancho=md.ancho, alto=md.alto,
            fps_efectivos=md.fps_declarados, max_frames=MAX_FRAMES,
        )
    assert isinstance(seq, SecuenciaPose)
    return seq


@pytest.fixture(scope="module")
def seq_zverev():
    return _procesar(_SEG, "zverev_saque_lateral_01.mp4")


def test_jugador_visible_cobertura_alta(seq_zverev):
    assert seq_zverev.n_frames == MAX_FRAMES
    assert seq_zverev.dims == 3
    assert seq_zverev.cobertura > 0.95


def test_entrega_puntos_3d_del_vocabulario_canonico(seq_zverev):
    from app.engine.pose.articulaciones import ArticulacionCanonica

    frame = next(f for f in seq_zverev.frames if f.detectado)
    assert ArticulacionCanonica.CADERA_IZQ in frame.puntos
    p = frame.puntos[ArticulacionCanonica.CADERA_IZQ]
    assert p.z is not None
    assert 0.0 <= p.confianza <= 1.0


def test_entrega_coordenadas_metricas_de_mundo(seq_zverev):
    from app.engine.pose.articulaciones import ArticulacionCanonica

    assert seq_zverev.tiene_mundo is True
    frame = next(f for f in seq_zverev.frames if f.detectado)
    pm = frame.get_mundo(ArticulacionCanonica.HOMBRO_DER)
    assert pm is not None and pm.z is not None
    # world landmarks en metros, centrados en las caderas: un hombro cae a < ~1 m.
    assert abs(pm.x) < 1.5 and abs(pm.y) < 1.5 and abs(pm.z) < 1.5


def test_backend_version_va_al_reporte(seq_zverev):
    assert seq_zverev.backend_id == "mediapipe"
    assert seq_zverev.backend_version.startswith("mediapipe-")


def test_clip_con_oclusion_produce_datos_no_auditables():
    from app.engine.validation import validar

    seq = _procesar(_CTRL, "control_oclusion_02.mp4")
    r = validar(seq)
    # Con paneo de cámara y cuerpo parcialmente fuera de cuadro, algo tiene que ceder:
    # o hay fotogramas sin detección, o puntos por debajo del umbral de confianza.
    assert seq.cobertura < 1.0 or r.n_baja_confianza > 0
