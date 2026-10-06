"""Arma la carpeta ``publicar/`` de la página de prueba del iPhone: ``index.html`` + ``config.js``.

``config.js`` lleva la URL del proyecto y la clave **anon** (las dos públicas por diseño: es lo mismo que va al
navegador en el frontend real). Este script **no lee ni escribe nunca** ``SUPABASE_SERVICE_ROLE_KEY``; si por error
``SUPABASE_ANON_KEY`` tuviera una clave de servidor, se detiene.

Uso (desde la raíz del repositorio):
    python tools/prueba-iphone/armar.py

La carpeta resultante (``tools/prueba-iphone/publicar/``) no se versiona. Se publica en Cloudflare ver
``docs/plan-mvp-punta-a-punta.md`` (prueba de riesgo del iPhone).
"""

from __future__ import annotations

import base64
import json
import shutil
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[2]
_ENV = _RAIZ / "backend" / ".env"
_SALIDA = Path(__file__).resolve().parent / "publicar"


def _leer_env(clave: str) -> str | None:
    if not _ENV.is_file():
        return None
    for linea in _ENV.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith(clave + "="):
            return linea.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def _rol_del_jwt(clave: str) -> str | None:
    """Rol que declara una clave en formato JWT (``anon`` / ``service_role``); None si no es un JWT."""
    partes = clave.split(".")
    if len(partes) != 3:
        return None
    try:
        cuerpo = partes[1] + "=" * (-len(partes[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(cuerpo)).get("role")
    except (ValueError, json.JSONDecodeError):
        return None


def main() -> int:
    url = _leer_env("SUPABASE_URL")
    anon = _leer_env("SUPABASE_ANON_KEY")
    if not url or not anon:
        print(f"Faltan SUPABASE_URL y/o SUPABASE_ANON_KEY en {_ENV}.")
        return 1
    if anon.startswith("sb_secret_") or _rol_del_jwt(anon) == "service_role":
        print("SUPABASE_ANON_KEY contiene una clave de servidor. Se detiene: esa clave nunca va a una página pública.")
        return 1

    if _SALIDA.exists():
        shutil.rmtree(_SALIDA)
    _SALIDA.mkdir(parents=True)
    shutil.copy(Path(__file__).resolve().parent / "index.html", _SALIDA / "index.html")
    config = {"url": url.rstrip("/"), "anon": anon}
    (_SALIDA / "config.js").write_text(f"window.KINETIQ_CONFIG = {json.dumps(config)};\n", encoding="utf-8")

    print(f"Listo: {_SALIDA}")
    print(f"  index.html + config.js (proyecto {url.rstrip('/')}, clave anon de {len(anon)} caracteres)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
