"""Unicidad de fotogramas sobre video real (decisión 001, verificación 2).

PENDIENTE DE REEMPLAZO OBLIGATORIO por material real cuando exista.
"""

from __future__ import annotations

import pytest

from app.engine.framehash import ratio_fotogramas_unicos
from video_fixtures import duplicar_fotogramas, generar_clip, requiere_ffmpeg

pytestmark = requiere_ffmpeg


def test_captura_real_da_ratio_cercano_a_1(tmp_path):
    clip = generar_clip(tmp_path / "sano.mp4", fps=240, segundos=1.0)
    r = ratio_fotogramas_unicos(clip, desde_s=0.0, hasta_s=999.0)
    assert r.ratio >= 0.95
    assert r.categoria == "captura_real"


def test_duplicacion_sistematica_da_un_tercio(tmp_path):
    base = generar_clip(tmp_path / "base30.mp4", fps=30, segundos=2.0)
    triplicado = duplicar_fotogramas(base, tmp_path / "trip90.mp4", fps_destino=90)
    r = ratio_fotogramas_unicos(triplicado, desde_s=0.0, hasta_s=999.0)
    assert r.ratio == pytest.approx(1 / 3, abs=0.05)
    assert r.categoria == "duplicacion_sistematica"


def test_ventana_central_por_defecto_no_recorre_todo(tmp_path):
    clip = generar_clip(tmp_path / "c.mp4", fps=60, segundos=4.0)
    r = ratio_fotogramas_unicos(clip)  # sin ventana explícita -> 60% central
    assert r.total < 60 * 4  # menos que el total del clip
    assert r.desde_s > 0
