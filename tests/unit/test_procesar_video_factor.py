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
