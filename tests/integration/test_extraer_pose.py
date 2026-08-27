"""extraer_pose: corre un backend sobre clips reales y cachea el resultado.

Usa FakeBackend (instantáneo) sobre clips sintéticos: prueba el flujo completo
ingesta -> backend -> caché sin pagar inferencia real ni depender del corpus.
"""

from __future__ import annotations

from app.engine.pose import cache as pose_cache
from app.engine.pose.fake_backend import FakeBackend
from app.extraer_pose import extraer
from video_fixtures import generar_clip, requiere_ffmpeg

pytestmark = requiere_ffmpeg


def test_extrae_y_cachea(tmp_path):
    video = generar_clip(tmp_path / "clip.mp4", fps=120, segundos=1.0)
    cache_dir = tmp_path / "cache"

    seq, hit = extraer(video, FakeBackend(dims=3), cache_dir=cache_dir,
                       fps_efectivos=240.0, max_frames=25)
    assert hit is False
    assert seq.n_frames == 25
    assert seq.fps_efectivos == 240.0

    # Los archivos de caché quedaron escritos.
    base = pose_cache.ruta_base(cache_dir, video, "fake", FakeBackend(dims=3).config_hash)
    assert pose_cache._p_npz(base).is_file()
    assert pose_cache._p_json(base).is_file()


def test_segunda_corrida_usa_la_cache(tmp_path):
    video = generar_clip(tmp_path / "clip.mp4", fps=120, segundos=1.0)
    cache_dir = tmp_path / "cache"
    kw = dict(cache_dir=cache_dir, fps_efectivos=240.0, max_frames=25)

    extraer(video, FakeBackend(dims=3), **kw)
    _, hit = extraer(video, FakeBackend(dims=3), **kw)
    assert hit is True


def test_forzar_reinfiere(tmp_path):
    video = generar_clip(tmp_path / "clip.mp4", fps=120, segundos=1.0)
    cache_dir = tmp_path / "cache"
    kw = dict(cache_dir=cache_dir, fps_efectivos=240.0, max_frames=10)

    extraer(video, FakeBackend(dims=3), **kw)
    _, hit = extraer(video, FakeBackend(dims=3), forzar=True, **kw)
    assert hit is False


def test_2d_solo_se_cachea_y_recupera_sin_z(tmp_path):
    video = generar_clip(tmp_path / "clip.mp4", fps=60, segundos=1.0)
    cache_dir = tmp_path / "cache"

    seq, _ = extraer(video, FakeBackend(dims=2), cache_dir=cache_dir,
                     fps_efectivos=60.0, max_frames=15)
    assert seq.dims == 2

    recuperada = pose_cache.cargar_si_vigente(
        cache_dir, video, "fake", FakeBackend(dims=2).config_hash
    )
    assert recuperada is not None
    assert all(p.z is None for f in recuperada.frames for p in f.puntos.values())
