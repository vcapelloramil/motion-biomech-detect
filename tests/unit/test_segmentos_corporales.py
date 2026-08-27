"""Definición de los segmentos de la cadena cinética."""

import pytest

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.segmentos_corporales import (
    ORDEN_ESPERADO,
    SegmentoCadena,
    articulaciones_de_segmento,
    validar_lado,
    vector_segmento,
)


def test_orden_esperado_es_pelvis_torso_brazo():
    assert ORDEN_ESPERADO == (
        SegmentoCadena.PELVIS,
        SegmentoCadena.TORSO,
        SegmentoCadena.BRAZO,
    )


def test_pelvis_y_torso_son_ejes_transversales():
    assert vector_segmento(SegmentoCadena.PELVIS, "der") == (A.CADERA_IZQ, A.CADERA_DER)
    assert vector_segmento(SegmentoCadena.TORSO, "izq") == (A.HOMBRO_IZQ, A.HOMBRO_DER)


def test_brazo_depende_del_lado_dominante():
    assert vector_segmento(SegmentoCadena.BRAZO, "der") == (A.HOMBRO_DER, A.MUNECA_DER)
    assert vector_segmento(SegmentoCadena.BRAZO, "izq") == (A.HOMBRO_IZQ, A.MUNECA_IZQ)


def test_lado_invalido_o_vacio_falla_claro():
    with pytest.raises(ValueError):
        validar_lado("")
    with pytest.raises(ValueError):
        validar_lado("derecha")


def test_articulaciones_de_segmento():
    assert set(articulaciones_de_segmento(SegmentoCadena.BRAZO, "der")) == {
        A.HOMBRO_DER,
        A.MUNECA_DER,
    }
