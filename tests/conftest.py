"""Fixtures compartidas. Los helpers de generación de clips viven en
``tests/video_fixtures.py`` para poder importarse también fuera de fixtures.
"""

from __future__ import annotations

import pytest

from video_fixtures import generar_clip


def pytest_collection_modifyitems(config, items):
    """Las pruebas contra el servicio DESPLEGADO en Render (marcador ``requiere_render``)
    solo corren cuando se piden a propósito: ``pytest -m requiere_render``. En cualquier
    otra corrida —la suite normal, ``-m requiere_supabase``, un ``pytest`` pelado— se
    saltan: pegan a un servicio real que se duerme y despierta (~1 min) y no tienen por qué
    correr en cada ciclo de desarrollo."""
    if "requiere_render" in (config.getoption("-m") or ""):
        return
    salto = pytest.mark.skip(reason="prueba contra Render: correr a propósito con  pytest -m requiere_render")
    for item in items:
        if "requiere_render" in item.keywords:
            item.add_marker(salto)


@pytest.fixture
def clip_factory(tmp_path):
    """Devuelve una función para crear clips dentro del tmp_path de la prueba."""

    def _crear(nombre: str, **kwargs):
        return generar_clip(tmp_path / nombre, **kwargs)

    return _crear
