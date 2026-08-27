"""Resolución de la ruta del corpus por configuración (regla de arquitectura E0).

Se prueba sin tocar la máquina real: se manipula la variable de entorno y se
apunta a carpetas temporales.
"""

import pytest

from app import config
from app.config import ConfigError, get_data_dir


@pytest.fixture(autouse=True)
def _aislar_entorno(monkeypatch, tmp_path):
    # Quita la variable real y desactiva la lectura de backend/.env,
    # para que cada test parta de cero.
    monkeypatch.delenv("KINETIQ_DATA_DIR", raising=False)
    monkeypatch.setattr(config, "_DOTENV_PATH", tmp_path / "no-existe.env")


def test_devuelve_la_ruta_cuando_la_variable_esta(monkeypatch, tmp_path):
    corpus = tmp_path / "kinetiq-data"
    corpus.mkdir()
    monkeypatch.setenv("KINETIQ_DATA_DIR", str(corpus))
    assert get_data_dir() == corpus.resolve()


def test_error_claro_cuando_no_esta_configurada():
    with pytest.raises(ConfigError) as exc:
        get_data_dir()
    assert "KINETIQ_DATA_DIR" in str(exc.value)


def test_error_cuando_la_ruta_no_existe(monkeypatch, tmp_path):
    monkeypatch.setenv("KINETIQ_DATA_DIR", str(tmp_path / "carpeta_inexistente"))
    with pytest.raises(ConfigError):
        get_data_dir()


def test_no_hay_ruta_por_defecto_hardcodeada(monkeypatch):
    # Si alguien mete un fallback a una ruta fija, este test lo detecta.
    with pytest.raises(ConfigError):
        get_data_dir()
