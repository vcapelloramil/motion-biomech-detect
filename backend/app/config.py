"""Configuración que depende de la máquina donde corre el proyecto.

Regla de arquitectura fijada en la Etapa 0: el motor NUNCA tiene una ruta de
video hardcodeada. La ubicación del corpus de datos (la carpeta ``kinetiq-data``,
que vive fuera del repositorio) se recibe por configuración:

  1. la variable de entorno ``KINETIQ_DATA_DIR`` del proceso, o
  2. el archivo ``backend/.env`` (que no se versiona).

Así el mismo código funciona en cualquier máquina y ``kinetiq-data`` se puede
mudar de lugar sin tocar una sola línea. Ver
``docs/decisiones/002-config-ruta-corpus.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ENV_VAR = "KINETIQ_DATA_DIR"
_CACHE_ENV_VAR = "KINETIQ_CACHE_DIR"

# Este archivo es backend/app/config.py -> parents[1] es la carpeta backend/.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_DOTENV_PATH = _BACKEND_DIR / ".env"
_CACHE_DIR_POR_DEFECTO = _BACKEND_DIR / ".cache"


class ConfigError(RuntimeError):
    """La configuración necesaria no está disponible o no es válida."""


def _read_raw_data_dir() -> str | None:
    """Devuelve el valor crudo de KINETIQ_DATA_DIR, o None si no está en ningún lado."""
    # 1) La variable de entorno del proceso gana siempre.
    value = os.environ.get(_ENV_VAR)
    if value:
        return value
    # 2) Si existe backend/.env, se carga y se vuelve a mirar.
    #    override=False: no pisa una variable que ya venga del entorno.
    if _DOTENV_PATH.is_file():
        load_dotenv(_DOTENV_PATH, override=False)
        value = os.environ.get(_ENV_VAR)
        if value:
            return value
    return None


def get_data_dir() -> Path:
    """Ruta absoluta a la carpeta raíz del corpus de datos.

    Lanza ``ConfigError`` con un mensaje accionable si la variable no está
    configurada o si apunta a una carpeta que no existe. No hay valor por
    defecto a propósito: preferimos fallar de forma clara antes que adivinar
    una ruta. Es la misma lógica de la regla R3 del CLAUDE.md ("un dato
    equivocado presentado como bueno es peor que un dato faltante"), aplicada
    a la configuración.
    """
    raw = _read_raw_data_dir()
    if not raw:
        raise ConfigError(
            f"No se encontró la variable {_ENV_VAR}.\n"
            f"Configurala de una de estas dos formas:\n"
            f"  - Variable de entorno:  set {_ENV_VAR}=C:/ruta/a/kinetiq-data\n"
            f"  - Archivo de config:    copiá backend/.env.example a backend/.env "
            f"y editá el valor.\n"
        )

    data_dir = Path(raw).expanduser().resolve()
    if not data_dir.is_dir():
        raise ConfigError(
            f"{_ENV_VAR} apunta a '{data_dir}', que no es una carpeta existente.\n"
            f"Revisá la ruta en backend/.env o en la variable de entorno."
        )
    return data_dir


def get_cache_dir() -> Path:
    """Carpeta donde el motor guarda resultados intermedios costosos (coordenadas
    de pose extraídas, sobre todo).

    A diferencia del corpus, esta carpeta se **crea** si no existe: es contenido
    regenerable, no un insumo. Se toma de ``KINETIQ_CACHE_DIR`` (entorno o
    ``backend/.env``); si no está, se usa ``backend/.cache/`` (ignorada por git).
    """
    raw = os.environ.get(_CACHE_ENV_VAR)
    if not raw and _DOTENV_PATH.is_file():
        load_dotenv(_DOTENV_PATH, override=False)
        raw = os.environ.get(_CACHE_ENV_VAR)

    cache_dir = Path(raw).expanduser().resolve() if raw else _CACHE_DIR_POR_DEFECTO
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
