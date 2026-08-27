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


def test_brazo_depende_del_lado_dominante_y_de_brazo_via():
    # default: codo (eslabón anatómico correcto de la cadena)
    assert vector_segmento(SegmentoCadena.BRAZO, "der") == (A.HOMBRO_DER, A.CODO_DER)
    assert vector_segmento(SegmentoCadena.BRAZO, "izq") == (A.HOMBRO_IZQ, A.CODO_IZQ)
    # configurable: muñeca (para re-testear con tres cuartos en la Fase B)
    assert vector_segmento(SegmentoCadena.BRAZO, "der", brazo_via="muneca") == (
        A.HOMBRO_DER,
        A.MUNECA_DER,
    )


def test_lado_o_brazo_via_invalidos_fallan_claro():
    with pytest.raises(ValueError):
        validar_lado("")
    with pytest.raises(ValueError):
        validar_lado("derecha")
    with pytest.raises(ValueError):
        vector_segmento(SegmentoCadena.BRAZO, "der", brazo_via="hombro")


def test_articulaciones_de_segmento():
    assert set(articulaciones_de_segmento(SegmentoCadena.BRAZO, "der")) == {
        A.HOMBRO_DER,
        A.CODO_DER,
    }
