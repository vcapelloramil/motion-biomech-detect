"""Traducción ratio -> categoría (decisión 001, tabla "Cómo se lee"). Lógica pura."""

import pytest

from app.engine.framehash import interpretar_ratio


@pytest.mark.parametrize(
    ("ratio", "esperado"),
    [
        (1.00, "captura_real"),        # 750/750, el material de Zverev
        (0.98, "captura_real"),
        (0.90, "repeticion_aislada"),  # ~70-95%
        (0.60, "repeticion_aislada"),
        (0.50, "duplicacion_sistematica"),  # cada cuadro repetido 2 veces
        (0.333, "duplicacion_sistematica"),  # cada cuadro repetido 3 veces
    ],
)
def test_interpretacion(ratio, esperado):
    assert interpretar_ratio(ratio) == esperado
