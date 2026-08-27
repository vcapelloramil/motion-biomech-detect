"""Normalización de tasas NTSC (59.94 -> 60, etc.). Lógica pura.

Sin esto, un clip a 59.94 fps (60000/1001, material "60p" de transmisión) quedaría
por debajo del umbral de 60 y se rechazaría por un redondeo, no por una limitación
real de muestreo.
"""

import pytest

from app.engine.ingest import (
    AptitudFaseRapida,
    MetadatosVideo,
    evaluar,
    normalizar_fps,
)


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        (59.94, 60.0),
        (59.97, 60.0),
        (29.97, 30.0),
        (23.976, 24.0),
        (119.88, 120.0),
        (239.76, 240.0),
        (25.0, 25.0),      # exacto, no se toca
        (500.0, 500.0),    # no está cerca de ninguna estándar
        (0.0, 0.0),
    ],
)
def test_normalizar_fps(crudo, esperado):
    assert normalizar_fps(crudo) == pytest.approx(esperado)


def _md(fps: float) -> MetadatosVideo:
    return MetadatosVideo(
        ruta="x.mp4", fps_declarados=fps, nb_frames=600, duracion_s=10.0,
        ancho=1920, alto=1080,
    )


def test_5994_fps_no_se_rechaza_por_redondeo():
    r = evaluar(_md(59.94), factor=1.0, escala_conocida=True)
    assert r.fps_declarados_normalizado == 60.0
    assert r.fps_efectivos == 60.0
    assert r.aptitud is AptitudFaseRapida.SOLO_PREPARACION  # no RECHAZADO


def test_2997_fps_sigue_rechazado():
    r = evaluar(_md(29.97), factor=1.0, escala_conocida=True)
    assert r.fps_declarados_normalizado == 30.0
    assert r.aptitud is AptitudFaseRapida.RECHAZADO
