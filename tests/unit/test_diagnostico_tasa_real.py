"""Funciones puras del diagnóstico de tasa real (decisión 029): quitar fotogramas según una huella de pérdidas, y la huella medida."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from app.diagnostico_tasa_real_corpus import indices_con_perdidas, quitar_fotogramas

_HUELLA = Path(__file__).resolve().parents[2] / "docs" / "resultados" / "tasa-real-iphone-huella.json"


def test_sin_huella_se_conservan_todos_los_fotogramas():
    assert indices_con_perdidas(5, [], 0) == [0, 1, 2, 3, 4]


def test_la_huella_quita_los_fotogramas_que_faltan():
    # Intervalos 1, 1, 3: después de dos fotogramas consecutivos faltan dos.
    assert indices_con_perdidas(12, [1, 1, 3], 0) == [0, 1, 2, 5, 6, 7, 10, 11]


def test_el_desplazamiento_arranca_la_huella_en_otro_punto_del_patron():
    assert indices_con_perdidas(10, [1, 1, 3], 2) == [0, 3, 4, 5, 8, 9]


def test_los_indices_son_crecientes_y_dentro_del_rango():
    idx = indices_con_perdidas(300, [1, 3, 1, 1, 3], 4)
    assert idx[0] == 0 and idx == sorted(set(idx)) and idx[-1] < 300


def test_quitar_fotogramas_reindexa_en_orden_consecutivo():
    @dataclasses.dataclass(frozen=True)
    class Frame:
        indice: int

    @dataclasses.dataclass(frozen=True)
    class Seq:
        frames: list

    seq = Seq([Frame(i) for i in range(10)])
    nueva = quitar_fotogramas(seq, [0, 3, 4, 8])
    assert [f.indice for f in nueva.frames] == [0, 1, 2, 3]   # lo que ve un archivo horneado: fotogramas consecutivos
    assert len(seq.frames) == 10                               # la secuencia original no se modifica


@pytest.mark.skipif(not _HUELLA.is_file(), reason="falta la huella medida")
def test_la_huella_medida_es_coherente_consigo_misma():
    h = json.loads(_HUELLA.read_text(encoding="utf-8"))
    iv = h["intervalos_en_periodos"]
    assert set(iv) <= {1, 2, 3, 4} and len(iv) + 1 == h["fotogramas_visibles"]
    # tasa real media = fotogramas por segundo, con el tiempo = períodos / frecuencia nominal
    real = len(iv) / (sum(iv) / h["fps_nominal"])
    assert real == pytest.approx(h["fps_real_media"], rel=0.01)
    assert h["fotogramas_perdidos_pct"] == pytest.approx(100 * (1 - h["fps_real_media"] / h["fps_nominal"]), abs=0.2)
