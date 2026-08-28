"""Criterio de aceptación de la Etapa 1, sobre el corpus real de la Fase A.

El catalogador procesa el corpus completo sin errores y clasifica cada clip según
la tabla de aptitud. Reemplaza a las pruebas sintéticas de 30/60 fps y de oclusión:
ahora hay material real equivalente en `kinetiq-data/fase-a/`.

Se salta si no hay corpus configurado (p. ej. en CI sin KINETIQ_DATA_DIR).
"""

from __future__ import annotations

import pytest

from video_fixtures import FFMPEG

try:
    from app.config import get_data_dir

    _DATA_DIR = get_data_dir()
except Exception:  # ConfigError u otra: no hay corpus disponible
    _DATA_DIR = None

_SEGMENTOS = _DATA_DIR / "fase-a" / "segmentos" if _DATA_DIR else None
_HAY_CORPUS = bool(_SEGMENTOS and _SEGMENTOS.is_dir() and any(_SEGMENTOS.glob("*.mp4")))

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not _HAY_CORPUS, reason="No hay corpus Fase A (KINETIQ_DATA_DIR)"),
    pytest.mark.skipif(FFMPEG is None, reason="ffmpeg no está en el PATH"),
]

# fps de captura efectivos esperados por clip de gesto (declarados x factor).
_FPS_EFECTIVOS_GESTOS = {
    "zverev_saque_lateral_01.mp4": 500,
    "zverev_saque_lateral_02.mp4": 500,
    "zverev_saque_lateral_03.mp4": 500,
    "drive_lateral_01.mp4": 480,
    "reves_lateral_01.mp4": 300,
    "drive_trescuartos_01.mp4": 240,   # 30 (NTSC) x 8
    "saque_trescuartos_01.mp4": 240,
}


@pytest.fixture(scope="module")
def catalogo_fase_a():
    from app.catalogador import catalogar_directorio

    filas, avisos = catalogar_directorio(
        _DATA_DIR / "fase-a", catalogo=_DATA_DIR / "catalogo.csv"
    )
    return filas, avisos, {f.archivo: f for f in filas}


def test_no_hay_errores_de_lectura(catalogo_fase_a):
    filas, _, _ = catalogo_fase_a
    con_error = [f.archivo for f in filas if f.aptitud_fps == "ERROR"]
    assert not con_error, f"clips que no se pudieron leer: {con_error}"


def test_se_catalogan_los_14_clips_reales(catalogo_fase_a):
    filas, _, _ = catalogo_fase_a
    # 7 gestos en segmentos/ (5 laterales + 2 tres cuartos) + 7 en control/
    assert len(filas) == 14


def test_los_gestos_en_camara_lenta_son_aptos_para_fase_rapida(catalogo_fase_a):
    _, _, por_nombre = catalogo_fase_a
    for nombre, fps_esp in _FPS_EFECTIVOS_GESTOS.items():
        f = por_nombre[nombre]
        assert f.uso_final.startswith("E1-E4"), (nombre, f.uso_final)
        assert f.fps_efectivos == pytest.approx(fps_esp, rel=0.05), nombre
        assert f.escala_temporal_conocida is False, nombre  # material descargado
        assert f.ratio_unicidad is not None and f.ratio_unicidad >= 0.95, nombre
        assert f.categoria_unicidad == "captura_real", nombre


def test_los_controles_de_fps_bajo_se_clasifican_bien(catalogo_fase_a):
    _, _, por_nombre = catalogo_fase_a
    de_30 = [f for f in por_nombre.values()
             if f.fps_declarados == 30 and f.archivo.startswith("control_")]
    de_60 = [f for f in por_nombre.values()
             if f.fps_declarados == 60 and f.archivo.startswith("control_")]
    assert de_30 and de_60
    for f in de_30:
        assert f.aptitud_fps == "rechazado", f.archivo
        assert f.uso_final == "rechazado", f.archivo
    for f in de_60:
        assert f.aptitud_fps == "solo_preparacion", f.archivo
        assert "preparacion" in f.uso_final, f.archivo


def test_el_catalogo_no_tiene_inconsistencias(catalogo_fase_a):
    filas, avisos, _ = catalogo_fase_a
    # La nota de normalización NTSC (59.94 -> 60) es informativa, no una inconsistencia.
    def relevante(texto: str) -> bool:
        return bool(texto) and "NTSC" not in texto

    con_avisos = [f.archivo for f in filas if relevante(f.avisos) or f.inconsistencias]
    assert not avisos, avisos
    assert not con_avisos, con_avisos
