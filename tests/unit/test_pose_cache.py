"""Round-trip de la caché de pose: guardar y cargar no pierde ni cambia nada."""

import numpy as np
import pytest

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.pose.cache import (
    cargar,
    cargar_si_vigente,
    clave_cache,
    guardar,
    ruta_base,
)
from app.engine.pose.fake_backend import FakeBackend

_KW = dict(ancho=1920, alto=1080, fps_efectivos=240.0)


def _iguales(s1: SecuenciaPose, s2: SecuenciaPose) -> None:
    assert s1.backend_id == s2.backend_id
    assert s1.dims == s2.dims
    assert s1.articulaciones == s2.articulaciones
    assert s1.n_frames == s2.n_frames
    for f1, f2 in zip(s1.frames, s2.frames):
        assert f1.indice == f2.indice and f1.detectado == f2.detectado
        assert f1.puntos.keys() == f2.puntos.keys()
        for art in f1.puntos:
            p1, p2 = f1.puntos[art], f2.puntos[art]
            assert p1.x == pytest.approx(p2.x) and p1.y == pytest.approx(p2.y)
            assert p1.confianza == pytest.approx(p2.confianza)
            if p1.z is None:
                assert p2.z is None
            else:
                assert p1.z == pytest.approx(p2.z)


def test_roundtrip_3d(tmp_path):
    seq = FakeBackend(dims=3).procesar(range(25), **_KW)
    guardar(seq, tmp_path / "c")
    _iguales(seq, cargar(tmp_path / "c"))


def test_roundtrip_2d_conserva_z_none(tmp_path):
    seq = FakeBackend(dims=2).procesar(range(15), **_KW)
    guardar(seq, tmp_path / "c")
    reload = cargar(tmp_path / "c")
    _iguales(seq, reload)
    assert all(p.z is None for f in reload.frames for p in f.puntos.values())


def test_roundtrip_frames_sin_deteccion(tmp_path):
    seq = FakeBackend(frames_sin_deteccion={1, 4}).procesar(range(6), **_KW)
    guardar(seq, tmp_path / "c")
    reload = cargar(tmp_path / "c")
    assert reload.frames[1].detectado is False and reload.frames[1].puntos == {}


def test_roundtrip_articulacion_ausente_en_un_frame(tmp_path):
    arts = (A.HOMBRO_IZQ, A.CODO_IZQ)
    f0 = PoseFrame(0, True, {A.HOMBRO_IZQ: Punto(0.4, 0.4, 0.1, 0.9)})  # falta CODO_IZQ
    f1 = PoseFrame(1, True, {A.HOMBRO_IZQ: Punto(0.4, 0.4, 0.1, 0.9),
                             A.CODO_IZQ: Punto(0.5, 0.6, 0.2, 0.8)})
    seq = SecuenciaPose("t", "t-0", arts, 3, 100, 100, 240.0, "x", [f0, f1])
    guardar(seq, tmp_path / "c")
    reload = cargar(tmp_path / "c")
    assert set(reload.frames[0].puntos) == {A.HOMBRO_IZQ}
    assert set(reload.frames[1].puntos) == {A.HOMBRO_IZQ, A.CODO_IZQ}


def test_cargar_si_vigente_detecta_video_cambiado(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"contenido original 12345")
    seq = FakeBackend(dims=3)
    base = ruta_base(tmp_path / "cache", video, seq.id, seq.config_hash)
    guardar(seq.procesar(range(5), **_KW), base, video=video)

    ok = cargar_si_vigente(tmp_path / "cache", video, seq.id, seq.config_hash)
    assert ok is not None and ok.n_frames == 5

    video.write_bytes(b"contenido MODIFICADO diferente")
    assert cargar_si_vigente(tmp_path / "cache", video, seq.id, seq.config_hash) is None


def test_cargar_si_vigente_none_si_no_existe(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    assert cargar_si_vigente(tmp_path / "cache", video, "fake", "deadbeef") is None


def test_clave_cache_estable_y_separa_configs():
    from pathlib import Path

    v = Path("/x/zverev_saque_lateral_01.mp4")
    assert clave_cache(v, "mediapipe", "abc123def456") == clave_cache(v, "mediapipe", "abc123def456")
    assert clave_cache(v, "mediapipe", "aaa") != clave_cache(v, "mediapipe", "bbb")
