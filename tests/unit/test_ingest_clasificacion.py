"""Tabla de aptitud por frecuencia efectiva (plan, tarea 1.3). Lógica pura."""

import pytest

from app.engine.ingest import AptitudFaseRapida, clasificar_fps


@pytest.mark.parametrize(
    ("fps", "esperado"),
    [
        (30.0, AptitudFaseRapida.RECHAZADO),
        (56.99, AptitudFaseRapida.RECHAZADO),
        # Tolerancia del 5 % sobre los pisos de 60 y 120 (decisión 029, actualización del 9/10): 57 y 114.
        (57.0, AptitudFaseRapida.SOLO_PREPARACION),
        (59.26, AptitudFaseRapida.SOLO_PREPARACION),  # el clip de 60 fps con un hueco de 3 fotogramas
        (113.99, AptitudFaseRapida.SOLO_PREPARACION),
        (114.0, AptitudFaseRapida.REDUCIDO),
        (118.6, AptitudFaseRapida.REDUCIDO),           # 120 fps legítimo con fotogramas perdidos
        (239.99, AptitudFaseRapida.REDUCIDO),  # el techo del impacto completo NO tiene tolerancia
        (240.0, AptitudFaseRapida.COMPLETO),
        (500.0, AptitudFaseRapida.COMPLETO),
    ],
)
def test_clasificacion_en_los_limites(fps, esperado):
    assert clasificar_fps(fps) is esperado
