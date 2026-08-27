"""Tabla de aptitud por frecuencia efectiva (plan, tarea 1.3). Lógica pura."""

import pytest

from app.engine.ingest import AptitudFaseRapida, clasificar_fps


@pytest.mark.parametrize(
    ("fps", "esperado"),
    [
        (30.0, AptitudFaseRapida.RECHAZADO),
        (59.9, AptitudFaseRapida.RECHAZADO),
        (60.0, AptitudFaseRapida.SOLO_PREPARACION),
        (119.99, AptitudFaseRapida.SOLO_PREPARACION),
        (120.0, AptitudFaseRapida.REDUCIDO),
        (239.99, AptitudFaseRapida.REDUCIDO),
        (240.0, AptitudFaseRapida.COMPLETO),
        (500.0, AptitudFaseRapida.COMPLETO),
    ],
)
def test_clasificacion_en_los_limites(fps, esperado):
    assert clasificar_fps(fps) is esperado
