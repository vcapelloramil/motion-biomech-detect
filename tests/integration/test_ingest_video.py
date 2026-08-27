"""Ingesta sobre archivos de video reales (generados con ffmpeg).

PENDIENTE DE REEMPLAZO OBLIGATORIO por material del bloque de control cuando exista.
"""

from __future__ import annotations

import inspect
import tracemalloc

import pytest

from app.engine.ingest import IngestaError, iterar_fotogramas, probe
from video_fixtures import generar_clip, requiere_ffmpeg

pytestmark = requiere_ffmpeg


@pytest.mark.parametrize("fps", [30, 60, 120, 240])
def test_probe_lee_la_tasa_declarada_de_cada_clip(tmp_path, fps):
    clip = generar_clip(tmp_path / f"c{fps}.mp4", fps=fps, segundos=1.0)
    md = probe(clip)
    assert md.fps_declarados == pytest.approx(fps, rel=0.01)
    assert md.nb_frames == pytest.approx(fps, abs=2)  # 1 segundo de video
    assert md.ancho == 320 and md.alto == 240


def test_archivo_inexistente_da_error_claro(tmp_path):
    with pytest.raises(IngestaError):
        probe(tmp_path / "no-existe.mp4")


def test_archivo_corrupto_da_error_sin_crash(tmp_path):
    basura = tmp_path / "roto.mp4"
    basura.write_bytes(b"esto no es un video" * 200)
    with pytest.raises(IngestaError):
        probe(basura)


def test_iterador_es_perezoso_y_cuenta_bien(tmp_path):
    clip = generar_clip(tmp_path / "c.mp4", fps=120, segundos=1.0)
    it = iterar_fotogramas(clip)
    assert inspect.isgenerator(it)
    n = sum(1 for _ in it)
    assert n == pytest.approx(120, abs=2)


def test_iterador_no_carga_el_video_entero_en_memoria(tmp_path):
    # Un clip de 240 fps y 20 s son 4800 fotogramas; cargarlos todos a 320x240x3
    # serían ~1 GB. Si la iteración es perezosa, el pico se mantiene chico.
    clip = generar_clip(tmp_path / "largo.mp4", fps=240, segundos=20.0)
    tracemalloc.start()
    try:
        n = 0
        for _ in iterar_fotogramas(clip):
            n += 1
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert n == pytest.approx(4800, abs=10)
    assert pico < 100 * 1024 * 1024  # < 100 MB: no se acumulan los fotogramas
