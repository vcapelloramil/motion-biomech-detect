"""Prueba de coherencia temporal (criterio de aceptación de la Etapa 1).

Un mismo gesto grabado a 240 fps y su versión ralentizada (mismos fotogramas,
contenedor a 30 fps) deben producir la MISMA frecuencia de captura efectiva y la
MISMA duración real del movimiento. Es la verificación de que el manejo de cámara
lenta es correcto.

Versión sintética. PENDIENTE DE REEMPLAZO OBLIGATORIO por un par real (240 fps + su
ralentizado del mismo gesto) del material de la Fase B.
"""

from __future__ import annotations

import pytest

from app.engine.ingest import evaluar, probe
from video_fixtures import generar_clip, ralentizar, requiere_ffmpeg

pytestmark = requiere_ffmpeg

FACTOR = 8


def test_240fps_y_su_ralentizado_dan_la_misma_captura_efectiva(tmp_path):
    nativo = generar_clip(tmp_path / "nativo240.mp4", fps=240, segundos=1.0)
    lento = ralentizar(nativo, tmp_path / "lento30.mp4", factor=FACTOR, fps_salida=30)

    # El clip nativo: escala conocida, factor 1.
    r_nativo = evaluar(probe(nativo), factor=1.0, escala_conocida=True)
    # El ralentizado: declara 30 fps, factor 8 aportado desde afuera.
    r_lento = evaluar(
        probe(lento), factor=FACTOR, escala_conocida=False, origen_factor="manual"
    )

    assert r_nativo.fps_efectivos == pytest.approx(240, rel=0.02)
    assert r_lento.fps_efectivos == pytest.approx(240, rel=0.02)
    assert r_nativo.aptitud is r_lento.aptitud

    # Misma duración real del movimiento (nb_frames / fps_efectivos), aunque el
    # archivo lento dure 8 veces más en reproducción.
    assert r_lento.metadatos.duracion_s == pytest.approx(
        r_nativo.metadatos.duracion_s * FACTOR, rel=0.05
    )
    assert r_lento.duracion_real_s == pytest.approx(r_nativo.duracion_real_s, rel=0.03)
