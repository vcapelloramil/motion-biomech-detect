"""Validación de pose: confianza baja, saltos imposibles, cobertura por articulación."""

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.pose.fake_backend import FakeBackend
from app.engine.validation import (
    detectar_saltos_imposibles,
    largo_torso,
    marcar_baja_confianza,
    validar,
)

_KW = dict(ancho=1920, alto=1080, fps_efectivos=240.0)


def _seq(frames, articulaciones):
    return SecuenciaPose(
        backend_id="test", backend_version="test-0", articulaciones=tuple(articulaciones),
        dims=2, ancho=100, alto=100, fps_efectivos=240.0, config_hash="x", frames=frames,
    )


def test_secuencia_sana_no_dispara_nada():
    seq = FakeBackend(dims=3).procesar(range(60), **_KW)
    r = validar(seq)
    assert r.puntos_baja_confianza == []
    assert r.saltos_imposibles == []
    assert all(v == 1.0 for v in r.cobertura_auditable.values())


def test_oclusion_marca_baja_confianza_y_baja_la_cobertura():
    seq = FakeBackend(articulaciones_ocluidas={A.MUNECA_DER: 0.2}).procesar(range(15), **_KW)
    marcados = marcar_baja_confianza(seq, umbral=0.5)
    assert {art for _, art in marcados} == {A.MUNECA_DER}
    assert len(marcados) == 15
    r = validar(seq)
    assert r.cobertura_auditable[A.MUNECA_DER] == 0.0
    assert r.cobertura_auditable[A.CADERA_IZQ] == 1.0


def test_salto_imposible_se_detecta():
    arts = [A.HOMBRO_IZQ, A.CADERA_IZQ, A.MUNECA_DER]
    torso = {A.HOMBRO_IZQ: Punto(0.5, 0.3, None, 0.9), A.CADERA_IZQ: Punto(0.5, 0.5, None, 0.9)}
    f0 = PoseFrame(0, True, {**torso, A.MUNECA_DER: Punto(0.50, 0.50, None, 0.9)})
    f1 = PoseFrame(1, True, {**torso, A.MUNECA_DER: Punto(0.90, 0.90, None, 0.9)})  # salto enorme
    saltos = detectar_saltos_imposibles(_seq([f0, f1], arts))
    assert len(saltos) == 1
    assert saltos[0].articulacion is A.MUNECA_DER
    assert saltos[0].desplazamiento_torsos > 0.5


def test_movimiento_normal_no_se_marca_como_salto():
    arts = [A.HOMBRO_IZQ, A.CADERA_IZQ, A.MUNECA_DER]
    torso = {A.HOMBRO_IZQ: Punto(0.5, 0.3, None, 0.9), A.CADERA_IZQ: Punto(0.5, 0.5, None, 0.9)}
    f0 = PoseFrame(0, True, {**torso, A.MUNECA_DER: Punto(0.50, 0.50, None, 0.9)})
    f1 = PoseFrame(1, True, {**torso, A.MUNECA_DER: Punto(0.52, 0.51, None, 0.9)})
    assert detectar_saltos_imposibles(_seq([f0, f1], arts)) == []


def test_sin_torso_no_se_puede_juzgar_el_salto():
    arts = [A.MUNECA_DER]
    f0 = PoseFrame(0, True, {A.MUNECA_DER: Punto(0.1, 0.1, None, 0.9)})
    f1 = PoseFrame(1, True, {A.MUNECA_DER: Punto(0.9, 0.9, None, 0.9)})
    assert detectar_saltos_imposibles(_seq([f0, f1], arts)) == []


def test_largo_torso_none_si_falta_un_lado():
    f = PoseFrame(0, True, {A.HOMBRO_IZQ: Punto(0.5, 0.3, None, 0.9)})
    assert largo_torso(f) is None
