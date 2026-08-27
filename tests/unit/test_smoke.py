"""Prueba trivial. Solo confirma que pytest corre y encuentra el paquete backend.

Criterio de aceptación de la Etapa 0: "pytest corre sin errores sobre una prueba
trivial".
"""

from app.engine.version import __version__


def test_pytest_funciona():
    assert 1 + 1 == 2


def test_se_puede_importar_el_motor():
    # Si esto importa, el pythonpath del pytest.ini está bien configurado.
    assert isinstance(__version__, str)
