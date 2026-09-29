"""Catalogador sobre un directorio sintético con casos controlados.

Complementa test_corpus_fase_a.py (corpus real): acá se arman casos que el corpus no
tiene —duplicación sistemática de fotogramas, subcarpeta de origen a saltear— y se
verifica la escritura del CSV y el modo --sin-hash sin depender del material real.
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
    generar_clip(d / "parcial_60.mp4", fps=60, segundos=1.0)
    # tripla los fotogramas partiendo de 240 fps -> 720 fps declarados (rápido por
    # tasa) pero con 2/3 de fotogramas duplicados: solo el hash puede detectarlo.
    duplicar_fotogramas(nativo, d / "triplicado_720.mp4", fps_destino=720)
    # material de origen: debe saltarse por defecto
    generar_clip(d / "compilaciones" / "fuente_larga.mp4", fps=240, segundos=1.0)

    catalogo = tmp_path / "catalogo.csv"
    catalogo.write_text(
        "archivo,fps_declarados,escala_temporal,factor_estimado,fps_efectivos,uso\n"
        "sano_240.mp4,240,conocida,1,240,E1-E4\n"
        "lento_30.mp4,30,desconocida,8,240,E1-E4\n"
        "malo_30.mp4,30,conocida,1,30,rechazado\n"
        "parcial_60.mp4,60,conocida,1,60,E1-E2 (solo preparacion)\n"
        # triplicado_720.mp4 a propósito NO está en el catálogo
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

    parcial = por_nombre["parcial_60.mp4"]
    assert parcial.aptitud_fps == "solo_preparacion"
    assert parcial.uso_final == "E1-E2 (solo preparacion)"

    trip = por_nombre["triplicado_720.mp4"]
    assert trip.categoria_unicidad == "duplicacion_sistematica"
    assert trip.uso_final == "E1-E2"
    assert "sin fila en catalogo.csv" in trip.avisos


def test_salta_la_carpeta_de_compilaciones(corpus):
    directorio, catalogo = corpus
    filas, _ = catalogar_directorio(directorio, catalogo=catalogo)
    assert "fuente_larga.mp4" not in {f.archivo for f in filas}

    filas_todo, _ = catalogar_directorio(directorio, catalogo=catalogo, incluir_todo=True)
    assert "fuente_larga.mp4" in {f.archivo for f in filas_todo}


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
    trip = next(f for f in filas if f.archivo == "triplicado_720.mp4")
    assert trip.uso_final.startswith("E1-E4")


# --- Fase B: estructura fase-b/<sesion>/<gesto>/{recortes,originales}/ ---------------

@pytest.fixture
def datos_con_fase_b(tmp_path):
    base = tmp_path / "datos"
    nativo = generar_clip(base / "fase-a" / "segmentos" / "a_240.mp4", fps=240, segundos=1.0)
    rec = base / "fase-b" / "sesion-01" / "saque" / "recortes"
    ori = base / "fase-b" / "sesion-01" / "saque" / "originales"
    ralentizar(nativo, rec / "b_rep01.mp4", factor=8, fps_salida=30)
    generar_clip(rec / "control_060.mp4", fps=60, segundos=1.0)
    generar_clip(ori / "fuente_larga.mp4", fps=240, segundos=1.0)
    catalogo = base / "catalogo.csv"
    catalogo.write_text(
        "archivo,fps_declarados,escala_temporal,factor_estimado,fps_efectivos,uso\n"
        "a_240.mp4,240,conocida,1,240,E1-E4\n"
        "b_rep01.mp4,30,conocida,8,240,E1-E4\n"
        "control_060.mp4,60,conocida,1,60,E1-E2 (solo preparacion)\n",
        encoding="utf-8",
    )
    return base, catalogo


def test_recorre_fase_a_y_fase_b_y_saltea_originales(datos_con_fase_b):
    base, catalogo = datos_con_fase_b
    filas, avisos = catalogar_directorio(
        base, catalogo=catalogo, subcarpetas=("fase-a", "fase-b")
    )
    por_nombre = {f.archivo: f for f in filas}
    assert set(por_nombre) == {"a_240.mp4", "b_rep01.mp4", "control_060.mp4"}
    assert por_nombre["b_rep01.mp4"].ruta_relativa == "fase-b/sesion-01/saque/recortes/b_rep01.mp4"
    b = por_nombre["b_rep01.mp4"]
    assert b.fps_efectivos == pytest.approx(240, rel=0.02)
    assert b.escala_temporal_conocida is True
    assert b.uso_final == "E1-E4"
    # ninguna fila del catálogo queda huérfana ni hay avisos globales
    assert avisos == []


def test_incluir_todo_recorre_originales(datos_con_fase_b):
    base, catalogo = datos_con_fase_b
    filas, _ = catalogar_directorio(
        base, catalogo=catalogo, subcarpetas=("fase-a", "fase-b"), incluir_todo=True
    )
    assert "fuente_larga.mp4" in {f.archivo for f in filas}


def test_subcarpeta_inexistente_se_avisa_y_no_falla(datos_con_fase_b):
    base, catalogo = datos_con_fase_b
    filas, avisos = catalogar_directorio(
        base, catalogo=catalogo, subcarpetas=("fase-a", "fase-c")
    )
    assert {f.archivo for f in filas} == {"a_240.mp4"}
    assert any("fase-c" in a for a in avisos)


def test_avisa_si_fps_declarados_del_catalogo_no_coincide_con_el_archivo(tmp_path):
    d = tmp_path / "clips"
    generar_clip(d / "x_60.mp4", fps=60, segundos=1.0)
    catalogo = tmp_path / "catalogo.csv"
    catalogo.write_text(
        "archivo,fps_declarados,escala_temporal,factor_estimado,fps_efectivos,uso\n"
        "x_60.mp4,30,conocida,1,60,E1-E2 (solo preparacion)\n",
        encoding="utf-8",
    )
    filas, _ = catalogar_directorio(d, catalogo=catalogo, con_hash=False)
    assert "fps_declarados del catálogo" in filas[0].avisos
