"""Fixtures compartidas. Los helpers de generación de clips viven en
``tests/video_fixtures.py`` para poder importarse también fuera de fixtures.
"""

from __future__ import annotations

import pytest

from video_fixtures import generar_clip


@pytest.fixture
def clip_factory(tmp_path):
    """Devuelve una función para crear clips dentro del tmp_path de la prueba."""

    def _crear(nombre: str, **kwargs):
        return generar_clip(tmp_path / nombre, **kwargs)

    return _crear
