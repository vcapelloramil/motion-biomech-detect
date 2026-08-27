"""Contrato PoseBackend + estructura de SecuenciaPose, ejercitados con FakeBackend."""

from app.engine.pose.articulaciones import ARTICULACIONES_CORE, ArticulacionCanonica
from app.engine.pose.base import PoseBackend, PoseFrame, Punto, SecuenciaPose, hash_config
from app.engine.pose.fake_backend import FakeBackend

_KW = dict(ancho=1920, alto=1080, fps_efectivos=240.0)


def test_fake_3d_produce_secuencia_completa():
    seq = FakeBackend(dims=3).procesar(range(50), **_KW)
    assert isinstance(seq, SecuenciaPose)
    assert seq.n_frames == 50
    assert seq.dims == 3
    assert seq.cobertura == 1.0
    p = seq.frames[10].get(ArticulacionCanonica.MUNECA_DER)
    assert p is not None and p.z is not None


def test_fake_3d_tiene_coordenadas_metricas():
    seq = FakeBackend(dims=3).procesar(range(20), **_KW)
    assert seq.tiene_mundo is True
    pm = seq.frames[5].get_mundo(ArticulacionCanonica.CADERA_IZQ)
    assert pm is not None and pm.z is not None
    # pseudo-metros: magnitud plausible para un cuerpo
    assert abs(pm.x) < 2.0 and abs(pm.y) < 2.0


def test_fake_2d_no_tiene_z_ni_mundo_y_usa_solo_el_core():
    seq = FakeBackend(dims=2).procesar(range(20), **_KW)
    assert seq.dims == 2
    assert seq.tiene_mundo is False
    assert set(seq.articulaciones) == ARTICULACIONES_CORE
    for frame in seq.frames:
        assert frame.puntos_mundo == {}
        for punto in frame.puntos.values():
            assert punto.z is None


def test_max_frames_corta():
    seq = FakeBackend().procesar(range(1000), max_frames=12, **_KW)
    assert seq.n_frames == 12


def test_frames_sin_deteccion_bajan_la_cobertura():
    seq = FakeBackend(frames_sin_deteccion={2, 5, 7}).procesar(range(10), **_KW)
    assert seq.cobertura == 0.7
    assert seq.frames[5].detectado is False
    assert seq.frames[5].puntos == {}


def test_cobertura_articulacion_con_umbral():
    seq = FakeBackend(
        articulaciones_ocluidas={ArticulacionCanonica.TOBILLO_IZQ: 0.2}
    ).procesar(range(10), **_KW)
    assert seq.cobertura_articulacion(ArticulacionCanonica.TOBILLO_IZQ, umbral_confianza=0.5) == 0.0
    assert seq.cobertura_articulacion(ArticulacionCanonica.HOMBRO_DER, umbral_confianza=0.5) == 1.0


def test_context_manager_cierra():
    cerrado = []

    class B(FakeBackend):
        def cerrar(self):
            cerrado.append(True)

    with B() as b:
        b.procesar(range(3), **_KW)
    assert cerrado == [True]


def test_config_hash_estable_y_sensible():
    a = FakeBackend(dims=3).config_hash
    b = FakeBackend(dims=3).config_hash
    c = FakeBackend(dims=2).config_hash
    assert a == b
    assert a != c


def test_hash_config_determinista_e_independiente_del_orden():
    assert hash_config({"a": 1, "b": 2}) == hash_config({"b": 2, "a": 1})
    assert hash_config({"a": 1}) != hash_config({"a": 2})
