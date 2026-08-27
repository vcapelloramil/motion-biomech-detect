"""Factor de ralentización y propagación de la frecuencia de captura efectiva.

El sistema propaga SIEMPRE la frecuencia de captura, nunca la de reproducción
(tesis 3.3.1.1). Lógica pura, sin video.
"""

import pytest

from app.engine.ingest import (
    AptitudFaseRapida,
    MetadatosVideo,
    evaluar,
)


def _md(fps_declarados: float, nb_frames: int = 750, duracion_s: float = 30.0) -> MetadatosVideo:
    return MetadatosVideo(
        ruta="x.mp4",
        fps_declarados=fps_declarados,
        nb_frames=nb_frames,
        duracion_s=duracion_s,
        ancho=1920,
        alto=1080,
    )


def test_factor_1_no_cambia_nada():
    r = evaluar(_md(240.0), factor=1.0, escala_conocida=True)
    assert r.fps_efectivos == 240.0
    assert r.aptitud is AptitudFaseRapida.COMPLETO
    assert r.escala_temporal_conocida is True


def test_caso_zverev_camara_lenta_declarada():
    # 25 fps declarados x factor 20 (estimado a ojo) = 500 fps efectivos.
    # La escala temporal NO es confiable: sirve para el orden, no para velocidades.
    r = evaluar(_md(25.0), factor=20.0, escala_conocida=False, origen_factor="catalogo")
    assert r.fps_efectivos == 500.0
    assert r.aptitud is AptitudFaseRapida.COMPLETO
    assert r.escala_temporal_conocida is False
    assert r.origen_factor == "catalogo"
    assert r.habilita_fase_rapida is True


def test_rechazo_es_resultado_no_excepcion():
    r = evaluar(_md(30.0), factor=1.0)
    assert r.aptitud is AptitudFaseRapida.RECHAZADO
    assert r.motivo_rechazo is not None
    assert "30.0 fps" in r.motivo_rechazo
    assert r.habilita_fase_rapida is False
    assert r.habilita_preparacion is False


def test_60_fps_habilita_preparacion_pero_no_fase_rapida():
    r = evaluar(_md(60.0), factor=1.0)
    assert r.aptitud is AptitudFaseRapida.SOLO_PREPARACION
    assert r.habilita_preparacion is True
    assert r.habilita_fase_rapida is False
    assert r.motivo_rechazo is None


def test_factor_invalido_es_error_de_programacion():
    with pytest.raises(ValueError):
        evaluar(_md(25.0), factor=0.0)
    with pytest.raises(ValueError):
        evaluar(_md(25.0), factor=-8.0)


def test_duracion_real_des_estira_el_eje_temporal():
    # 750 fotogramas capturados a 500 fps efectivos = 1.5 s de movimiento real,
    # aunque el archivo dure 30 s en reproducción.
    r = evaluar(_md(25.0, nb_frames=750, duracion_s=30.0), factor=20.0)
    assert r.duracion_real_s == pytest.approx(1.5)
