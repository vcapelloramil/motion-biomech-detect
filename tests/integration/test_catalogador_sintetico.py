"""Catalogador sobre un directorio sintético con casos conocidos.

PENDIENTE DE REEMPLAZO OBLIGATORIO por el material del bloque de control cuando exista.
"""

from __future__ import annotations

import csv

import pytest

from app.catalogador import catalogar_directorio, escribir_csv
from video_fixtures import (
    duplicar_fotogramas,
    generar_clip,
    ralentizar,
    requiere_ffmpeg,
)

pytestmark = requiere_ffmpeg


@pytest.fixture
def corpus(tmp_path):
    d = tmp_path / "clips"
    d.mkdir()
    nativo = generar_clip(d / "sano_240.mp4", fps=240, segundos=1.0)
    ralentizar(nativo, d / "lento_30.mp4", factor=8, fps_salida=30)
    generar_clip(d / "malo_30.mp4", fps=30, segundos=1.0)
    base = generar_clip(tmp_path / "base30.mp4", fps=30, segundos=2.0)
    duplicar_fotogramas(base, d / "triplicado_90.mp4", fps_destino=90)

    catalogo = tmp_path / "catalogo.csv"
    catalogo.write_text(
        "archivo,fps_declarados,escala_temporal,factor_estimado,fps_efectivos,uso\n"
        "sano_240.mp4,240,conocida,1,240,E1-E4\n"
        "lento_30.mp4,30,desconocida,8,240,E1-E4\n"
        "malo_30.mp4,30,conocida,1,30,rechazado\n"
        # triplicado_90.mp4 a propósito NO está en el catálogo
        , encoding="utf-8",
    )
    return d, catalogo


def test_clasifica_cada_caso(corpus):
    directorio, catalogo = corpus
    filas, _ = catalogar_directorio(directorio, catalogo=catalogo)
    por_nombre = {f.archivo: f for f in filas}

    sano = por_nombre["sano_240.mp4"]
    assert sano.aptitud_fps == "completo"
    assert sano.uso_final == "E1-E4"
    assert sano.categoria_unicidad == "captura_real"

    lento = por_nombre["lento_30.mp4"]
    assert lento.fps_efectivos == pytest.approx(240, rel=0.02)
    assert lento.origen_factor == "catalogo"
    assert lento.escala_temporal_conocida is False
    assert lento.uso_final.startswith("E1-E4")

    malo = por_nombre["malo_30.mp4"]
    assert malo.aptitud_fps == "rechazado"
    assert malo.uso_final == "rechazado"

    trip = por_nombre["triplicado_90.mp4"]
    assert trip.categoria_unicidad == "duplicacion_sistematica"
    assert trip.uso_final == "E1-E2"
    assert "sin fila en catalogo.csv" in trip.avisos


def test_no_toca_el_catalogo_manual(corpus):
    directorio, catalogo = corpus
    antes = catalogo.read_bytes()
    catalogar_directorio(directorio, catalogo=catalogo)
    assert catalogo.read_bytes() == antes


def test_escribir_csv_produce_encabezado_y_filas(corpus, tmp_path):
    directorio, catalogo = corpus
    filas, _ = catalogar_directorio(directorio, catalogo=catalogo)
    salida = tmp_path / "catalogo-verificado.csv"
    escribir_csv(filas, salida)

    with salida.open(encoding="utf-8", newline="") as f:
        leidas = list(csv.DictReader(f))
    assert len(leidas) == len(filas)
    assert "uso_final" in leidas[0]
    assert "escala_temporal_conocida" in leidas[0]


def test_sin_hash_no_calcula_unicidad(corpus):
    directorio, catalogo = corpus
    filas, _ = catalogar_directorio(directorio, catalogo=catalogo, con_hash=False)
    assert all(f.ratio_unicidad is None for f in filas)
    # sin el dato de unicidad, el uso no puede degradar a E1-E2
    trip = next(f for f in filas if f.archivo == "triplicado_90.mp4")
    assert trip.uso_final.startswith("E1-E4")
