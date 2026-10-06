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
_SUPABASE_URL_VAR = "SUPABASE_URL"
_SUPABASE_ANON_KEY_VAR = "SUPABASE_ANON_KEY"
_SUPABASE_SERVICE_ROLE_KEY_VAR = "SUPABASE_SERVICE_ROLE_KEY"

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


def _read_env_var(var: str) -> str | None:
    """Mismo orden de lectura que ``_read_raw_data_dir``: entorno del proceso primero,
    ``backend/.env`` después, sin pisar lo que ya haya en el entorno."""
    value = os.environ.get(var)
    if value:
        return value
    if _DOTENV_PATH.is_file():
        load_dotenv(_DOTENV_PATH, override=False)
        value = os.environ.get(var)
    return value


def get_supabase_url() -> str:
    """URL del proyecto Supabase. No es secreta (CLAUDE.md §4.5, Etapa 4.5)."""
    value = _read_env_var(_SUPABASE_URL_VAR)
    if not value:
        raise ConfigError(
            f"No se encontró la variable {_SUPABASE_URL_VAR}.\n"
            f"Configurala en backend/.env (ver backend/.env.example)."
        )
    return value


def get_supabase_anon_key() -> str:
    """Clave pública ('anon') del proyecto. Necesaria para autenticarse como un usuario
    normal (p. ej. en tests/integration/test_rls_aislamiento.py); distinta de
    SUPABASE_SERVICE_ROLE_KEY, que bypasea RLS y nunca debe usarse para esto."""
    value = _read_env_var(_SUPABASE_ANON_KEY_VAR)
    if not value:
        raise ConfigError(
            f"No se encontró la variable {_SUPABASE_ANON_KEY_VAR}.\n"
            f"Configurala en backend/.env (ver backend/.env.example)."
        )
    return value


def get_kinetiq_api_url() -> str:
    """URL base del servicio desplegado en Render (sin barra final). Solo la usan las
    pruebas contra el despliegue real; no es secreta pero tampoco se versiona."""
    value = _read_env_var("KINETIQ_API_URL")
    if not value:
        raise ConfigError(
            "No se encontró la variable KINETIQ_API_URL.\n"
            "Configurala en backend/.env (ver backend/.env.example)."
        )
    return value.rstrip("/")


def get_kinetiq_api_token() -> str:
    """Token compartido que protege POST /analisis/... (el mismo que está cargado como
    KINETIQ_API_TOKEN en el panel de Render). SECRETO: nunca se imprime ni se versiona."""
    value = _read_env_var("KINETIQ_API_TOKEN")
    if not value:
        raise ConfigError(
            "No se encontró la variable KINETIQ_API_TOKEN.\n"
            "Configurala en backend/.env (ver backend/.env.example)."
        )
    return value


_MAX_INTENTOS_VAR = "KINETIQ_MAX_INTENTOS"
_MAX_INTENTOS_POR_DEFECTO = 3


def get_max_intentos() -> int:
    """Tope de intentos para reintentar un video que falló por un error inesperado (decisión 022).
    Opcional: 3 si no está configurado. No es un secreto ni depende de la máquina; es un
    parámetro de operación para poder subirlo o bajarlo sin tocar código."""
    value = _read_env_var(_MAX_INTENTOS_VAR)
    if not value:
        return _MAX_INTENTOS_POR_DEFECTO
    try:
        intentos = int(value)
    except ValueError:
        raise ConfigError(f"{_MAX_INTENTOS_VAR} tiene que ser un entero, y es {value!r}.") from None
    if intentos < 1:
        raise ConfigError(f"{_MAX_INTENTOS_VAR} tiene que ser >= 1, y es {intentos}.")
    return intentos


def get_supabase_service_role_key() -> str:
    """Clave secreta que bypasea Row Level Security. Solo la usa el contenedor del motor
    o las pruebas que necesitan preparar datos de prueba como administrador — nunca el
    frontend. No se versiona (CLAUDE.md §4.5)."""
    value = _read_env_var(_SUPABASE_SERVICE_ROLE_KEY_VAR)
    if not value:
        raise ConfigError(
            f"No se encontró la variable {_SUPABASE_SERVICE_ROLE_KEY_VAR}.\n"
            f"Configurala en backend/.env (ver backend/.env.example)."
        )
    return value
