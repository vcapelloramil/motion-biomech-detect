"""Criterio de aceptación de la Etapa 1, sobre el corpus real de la Fase A.

El catalogador procesa el corpus de la Fase A sin errores y clasifica cada clip.
Hoy la Fase A tiene solo los 3 segmentos de saque de Zverev (25 fps declarados,
factor ~20, escala temporal desconocida, verificados sin duplicados). Deben
aceptarse y quedar aptos para fase rápida.

Se salta si no hay corpus configurado (p. ej. en CI sin KINETIQ_DATA_DIR).
"""

from __future__ import annotations

import pytest

from video_fixtures import FFMPEG

try:
    from app.config import ConfigError, get_data_dir

    _DATA_DIR = get_data_dir()
except Exception:  # ConfigError u otra: no hay corpus disponible
    _DATA_DIR = None

_SEGMENTOS = _DATA_DIR / "fase-a" / "segmentos" if _DATA_DIR else None
_HAY_SEGMENTOS = bool(_SEGMENTOS and _SEGMENTOS.is_dir() and any(_SEGMENTOS.glob("*.mp4")))

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not _HAY_SEGMENTOS, reason="No hay corpus Fase A (KINETIQ_DATA_DIR)"),
    pytest.mark.skipif(FFMPEG is None, reason="ffmpeg no está en el PATH"),
]


@pytest.fixture(scope="module")
def catalogo_fase_a():
    from app.catalogador import catalogar_directorio

    filas, avisos = catalogar_directorio(
        _DATA_DIR / "fase-a", catalogo=_DATA_DIR / "catalogo.csv"
    )
    return filas, avisos


def test_no_hay_errores_de_lectura(catalogo_fase_a):
    filas, _ = catalogo_fase_a
    con_error = [f.archivo for f in filas if f.aptitud_fps == "ERROR"]
    assert not con_error, f"clips que no se pudieron leer: {con_error}"


def test_los_segmentos_de_zverev_son_aptos_para_fase_rapida(catalogo_fase_a):
    filas, _ = catalogo_fase_a
    segmentos = [f for f in filas if "segmentos/" in f.ruta_relativa]
    assert segmentos, "no se encontraron los segmentos de Zverev"
    for f in segmentos:
        assert f.uso_final.startswith("E1-E4"), (f.archivo, f.uso_final)
        assert f.fps_efectivos == pytest.approx(500, rel=0.05), f.archivo
        assert f.escala_temporal_conocida is False, f.archivo


def test_los_segmentos_no_tienen_fotogramas_duplicados(catalogo_fase_a):
    filas, _ = catalogo_fase_a
    segmentos = [f for f in filas if "segmentos/" in f.ruta_relativa]
    for f in segmentos:
        assert f.ratio_unicidad is not None and f.ratio_unicidad >= 0.95, (
            f.archivo, f.ratio_unicidad
        )
        assert f.categoria_unicidad == "captura_real", f.archivo
