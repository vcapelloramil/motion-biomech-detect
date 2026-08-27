"""El mapa articular canónico traduce MediaPipe (33) y COCO (17) al mismo vocabulario."""

from app.engine.pose.articulaciones import (
    ARTICULACIONES_CORE,
    COCO_A_CANONICO,
    MEDIAPIPE_A_CANONICO,
    ArticulacionCanonica,
    articulaciones_de,
)


def test_mediapipe_indices_en_rango_y_sin_duplicar_destino():
    assert all(0 <= i <= 32 for i in MEDIAPIPE_A_CANONICO)
    destinos = list(MEDIAPIPE_A_CANONICO.values())
    assert len(destinos) == len(set(destinos))  # ninguna articulación mapeada dos veces


def test_coco_indices_en_rango_y_sin_duplicar_destino():
    assert all(0 <= i <= 16 for i in COCO_A_CANONICO)
    destinos = list(COCO_A_CANONICO.values())
    assert len(destinos) == len(set(destinos))


def test_ambos_backends_cubren_el_core():
    assert ARTICULACIONES_CORE <= set(MEDIAPIPE_A_CANONICO.values())
    assert ARTICULACIONES_CORE <= set(COCO_A_CANONICO.values())


def test_coco_no_promete_puntos_de_mano_ni_pie():
    solo_mediapipe = {
        ArticulacionCanonica.INDICE_IZQ,
        ArticulacionCanonica.INDICE_DER,
        ArticulacionCanonica.MENIQUE_IZQ,
        ArticulacionCanonica.MENIQUE_DER,
        ArticulacionCanonica.PIE_IZQ,
        ArticulacionCanonica.PIE_DER,
    }
    assert solo_mediapipe.isdisjoint(COCO_A_CANONICO.values())
    assert solo_mediapipe <= set(MEDIAPIPE_A_CANONICO.values())


def test_articulaciones_de_devuelve_orden_estable():
    a = articulaciones_de(MEDIAPIPE_A_CANONICO)
    b = articulaciones_de(MEDIAPIPE_A_CANONICO)
    assert a == b
    assert a == tuple(x for x in ArticulacionCanonica if x in a)
