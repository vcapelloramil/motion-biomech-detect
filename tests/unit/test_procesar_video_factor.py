"""`app.procesar_video._factor_y_motivo` — decisión 020 (ajuste del 2/10/2026).

Prueba pura, sin red ni archivos: la lógica de combinar el modo de captura que declara
el usuario con el fps real del contenedor. El caso central de la corrección de Valentín
es el primero: "normal" NUNCA falla, sea cual sea el fps del contenedor.
"""

from __future__ import annotations

import pytest

from app.procesar_video import MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE, _factor_y_motivo


@pytest.mark.parametrize("fps_contenedor", [23.976, 24, 29.97, 30, 59.94, 60, 120, 240, 480])
def test_normal_nunca_falla_sea_cual_sea_el_fps(fps_contenedor):
    """El punto central de la corrección: "normal" significa "sin cámara lenta", no
    "fps bajo". Hay teléfonos que graban 120+ fps en modo normal, y eso es válido."""
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("normal", fps_contenedor)
    assert motivo_fallo is None
    assert factor == 1.0
    assert escala_conocida is True
    assert origen == "declaracion_usuario"


def test_camara_lenta_240_sobre_contenedor_30_da_factor_8():
    """El caso real que disparó la decisión 020: un iPhone en cámara lenta declara 30 fps
    en el contenedor aunque la captura real sea 240."""
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("camara_lenta_240", 30.0)
    assert motivo_fallo is None
    assert factor == 8.0
    assert escala_conocida is True


def test_camara_lenta_120_sobre_contenedor_30_da_factor_4():
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("camara_lenta_120", 30.0)
    assert motivo_fallo is None
    assert factor == 4.0
    assert escala_conocida is True


def test_camara_lenta_240_sobre_contenedor_ntsc_normaliza_antes_de_dividir():
    """29.97 fps (NTSC) tiene que normalizarse a 30 ANTES de calcular el factor — si no,
    240/29.97 = 8.008... no da un entero por un redondeo, no por una cámara lenta real."""
    factor, _, _, motivo_fallo = _factor_y_motivo("camara_lenta_240", 29.97)
    assert motivo_fallo is None
    assert factor == 8.0


@pytest.mark.parametrize(
    "modo,fps_contenedor",
    [
        ("camara_lenta_240", 25.0),  # 240/25 = 9.6, no entero
        ("camara_lenta_120", 240.0),  # 120/240 = 0.5, redondea a 0 (< 1)
        ("camara_lenta_240", 100.0),  # 240/100 = 2.4, no entero
    ],
)
def test_combinacion_inconsistente_falla_con_codigo_cerrado(modo, fps_contenedor):
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo(modo, fps_contenedor)
    assert motivo_fallo == MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE
    assert escala_conocida is False
    # El código es del vocabulario cerrado de videos.motivo_fallo (migración
    # 20261002000000): nunca texto libre con el detalle técnico.
    assert " " not in motivo_fallo


# --- Archivo que llega en tiempo real (caso "a") --------------------------------------------------
# Un iPhone que recorta un golpe del medio de una cámara lenta en Fotos entrega el archivo con su
# frecuencia de captura real (240 fps, marcas de tiempo de tiempo real) y sin la indicación de
# reproducción lenta. Para el usuario "lo grabé en cámara lenta" sigue siendo verdad. El factor tiene
# que ser 1, no 8, y los fps efectivos 240.


def _metadatos(fps: float, nb_frames: int = 360):
    from pathlib import Path

    from app.engine.ingest import MetadatosVideo

    return MetadatosVideo(
        ruta=Path("clip.mov"), fps_declarados=fps, nb_frames=nb_frames, duracion_s=nb_frames / fps, ancho=1920, alto=1080
    )


@pytest.mark.parametrize("fps_contenedor", [240.0, 239.76, 240.24], ids=["exacto", "ntsc_abajo", "ntsc_arriba"])
def test_camara_lenta_240_sobre_contenedor_240_en_tiempo_real_da_factor_1(fps_contenedor):
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("camara_lenta_240", fps_contenedor)
    assert motivo_fallo is None
    assert factor == 1.0
    assert escala_conocida is True
    assert origen == "declaracion_usuario"


def test_camara_lenta_240_sobre_240_en_tiempo_real_da_240_fps_efectivos_y_aptitud_completa():
    """De punta a punta por la ingesta: el factor 1 se combina con el contenedor de 240 y no con 30."""
    from app.engine import ingest
    from app.engine.ingest import AptitudFaseRapida

    md = _metadatos(240.0)
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("camara_lenta_240", md.fps_declarados)
    assert motivo_fallo is None
    resultado = ingest.evaluar(md, factor=factor, escala_conocida=escala_conocida, origen_factor=origen)
    assert resultado.fps_efectivos == 240.0
    assert resultado.aptitud is AptitudFaseRapida.COMPLETO
    assert resultado.habilita_fase_rapida


def test_camara_lenta_120_sobre_contenedor_120_en_tiempo_real_da_factor_1():
    factor, _, _, motivo_fallo = _factor_y_motivo("camara_lenta_120", 120.0)
    assert motivo_fallo is None
    assert factor == 1.0


def test_el_mismo_archivo_en_tiempo_real_declarado_normal_tambien_da_240_efectivos():
    """Declarar "normal" un archivo de 240 fps reales no falla ni lo degrada (decisión 020): los fps
    efectivos son los del contenedor. La diferencia con "camara_lenta_240" es que esta declaración
    además sirve cuando el MISMO golpe llega horneado a 30 fps (factor 8), y "normal" no."""
    from app.engine import ingest

    md = _metadatos(240.0)
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo("normal", md.fps_declarados)
    assert motivo_fallo is None and factor == 1.0
    assert ingest.evaluar(md, factor=factor, escala_conocida=escala_conocida, origen_factor=origen).fps_efectivos == 240.0


@pytest.mark.parametrize(
    "caso,fps_contenedor,modo,fps_efectivos_esperados",
    [
        ("a: tiempo real a 240", 240.0, "camara_lenta_240", 240.0),
        ("b: cámara lenta horneada a 30", 30.0, "camara_lenta_240", 240.0),
    ],
)
def test_los_dos_formatos_validos_del_mismo_golpe_dan_los_mismos_fps_efectivos(
    caso, fps_contenedor, modo, fps_efectivos_esperados
):
    """El mismo golpe grabado a 240 fps llega en la forma (a) o en la (b) y declarando
    "camara_lenta_240" las dos dan 240 fps efectivos. El caso (c) (30 fps reales con fotogramas
    descartados) NO se distingue de (b) por esta función: 30 x 8 = 240 también cierra. Lo cubre,
    de forma condicional, la plausibilidad de velocidades (decisión 020)."""
    from app.engine import ingest

    md = _metadatos(fps_contenedor)
    factor, escala_conocida, origen, motivo_fallo = _factor_y_motivo(modo, fps_contenedor)
    assert motivo_fallo is None, caso
    assert ingest.evaluar(md, factor=factor, escala_conocida=escala_conocida, origen_factor=origen).fps_efectivos == (
        fps_efectivos_esperados
    )
