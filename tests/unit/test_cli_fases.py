"""extraer_pose y analizar: recorren fase-a y fase-b, y rotulan la fuente del clip.

Lógica pura sobre archivos vacíos y un catalogo.csv mínimo: no se lee video ni se
infiere pose.
"""

from __future__ import annotations

import pytest

from app.analizar import es_corpus_publico, lado_dominante_de
from app.extraer_pose import _listar_clips


@pytest.fixture
def datos(tmp_path):
    for rel in (
        "fase-a/segmentos/a.mp4",
        "fase-a/compilaciones/fuente_a.mp4",
        "fase-b/sesion-01/saque/recortes/b_rep01.mov",
        "fase-b/sesion-01/saque/originales/fuente_b.mov",
        "fase-b/sesion-01/saque/originales/cortes.txt",
    ):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()
    return tmp_path


def test_lista_ambas_fases_y_saltea_originales(datos):
    clips = _listar_clips([datos / "fase-a", datos / "fase-b"], None)
    assert {p.name for p in clips} == {"a.mp4", "b_rep01.mov"}


def test_una_fase_inexistente_se_ignora(datos):
    clips = _listar_clips([datos / "fase-a", datos / "fase-c"], None)
    assert {p.name for p in clips} == {"a.mp4"}


def test_seleccion_por_nombre_encuentra_clips_de_fase_b(datos):
    clips = _listar_clips([datos / "fase-a", datos / "fase-b"], ["b_rep01.mov"])
    assert [p.name for p in clips] == ["b_rep01.mov"]


def test_seleccion_de_un_original_falla_con_mensaje(datos):
    with pytest.raises(SystemExit, match="fuente_b.mov"):
        _listar_clips([datos / "fase-a", datos / "fase-b"], ["fuente_b.mov"])


@pytest.fixture
def catalogo(tmp_path):
    ruta = tmp_path / "catalogo.csv"
    ruta.write_text(
        "archivo,fuente,lado_dominante\n"
        "propio.mov,propio,der\n"
        "publico.mp4,youtube,izq\n"
        "sin_fuente.mp4,,der\n",
        encoding="utf-8",
    )
    return ruta


def test_material_propio_no_es_corpus_publico(catalogo):
    assert es_corpus_publico(catalogo, "propio.mov") is False


def test_material_de_terceros_o_sin_fuente_conserva_el_caveat(catalogo, tmp_path):
    assert es_corpus_publico(catalogo, "publico.mp4") is True
    assert es_corpus_publico(catalogo, "sin_fuente.mp4") is True   # ante la duda, caveat
    assert es_corpus_publico(catalogo, "no_esta.mp4") is True
    assert es_corpus_publico(tmp_path / "no_existe.csv", "x.mp4") is True


def test_lado_dominante_sigue_leyendose_del_catalogo(catalogo):
    assert lado_dominante_de(catalogo, "propio.mov") == "der"
    assert lado_dominante_de(catalogo, "publico.mp4") == "izq"
    assert lado_dominante_de(catalogo, "no_esta.mp4") is None
