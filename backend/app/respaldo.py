"""Respaldo lógico de la base y de Storage de KinetiQ (paso 7 del plan §8).

Supabase Free **no incluye respaldos**. Esta herramienta exporta, con la clave ``service_role`` del servidor:

* las nueve tablas de ``public`` (una línea JSON por fila, ordenadas por ``id``);
* las cuentas de ``auth.users`` (id, correo, fechas y metadatos; **no** las contraseñas: la API de administración no las expone;
  tras una restauración los usuarios usan "Olvidé mi contraseña");
* todos los archivos de los buckets ``videos`` y ``artefactos``;
* un ``manifiesto.json`` con conteos y SHA-256 de cada archivo, para poder **verificar** la copia.

Uso (desde ``backend/``)::

    PYTHONPATH=. .venv/Scripts/python.exe -m app.respaldo exportar --salida "C:/Users/<vos>/kinetiq-data/respaldos"
    PYTHONPATH=. .venv/Scripts/python.exe -m app.respaldo verificar "C:/Users/<vos>/kinetiq-data/respaldos/respaldo-AAAAMMDD-HHMMSS"

**El respaldo contiene datos personales** (correos, videos de personas): la carpeta de salida **no puede estar dentro del repositorio**
(la herramienta se niega) y no se sube a ningún lado. La restauración probada (``tools/respaldo/restaurar_prueba.py``) y el procedimiento
completo están en ``docs/respaldo-y-restauracion.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Orden de claves foráneas: lo que se restaura primero va primero.
TABLAS = [
    "usuarios",
    "atletas",
    "sesiones",
    "versiones_motor",
    "videos",
    "reportes_biomecanicos",
    "metricas",
    "alertas",
    "reportes_sesion",
]
BUCKETS = ["videos", "artefactos"]
PAGINA = 1000
VERSION_FORMATO = 1

RAIZ_REPO = Path(__file__).resolve().parents[2]


def _sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def _linea(fila: dict[str, Any]) -> str:
    return json.dumps(fila, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def fuera_del_repo(salida: Path) -> bool:
    """``True`` si ``salida`` no está dentro del repositorio (los respaldos tienen datos personales)."""
    destino = salida.resolve()
    return RAIZ_REPO != destino and RAIZ_REPO not in destino.parents


def _migraciones_del_repo() -> list[str]:
    return sorted(p.name for p in (RAIZ_REPO / "supabase" / "migrations").glob("*.sql"))


def _commit() -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ_REPO, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except Exception:  # noqa: BLE001 - es solo un dato del manifiesto
        return None


# --- exportar ------------------------------------------------------------------------------------------------------


def exportar_tabla(admin, tabla: str, destino: Path) -> tuple[int, str]:
    """Escribe ``<tabla>.jsonl`` y devuelve (filas, sha256)."""
    n = 0
    with destino.open("w", encoding="utf-8", newline="\n") as f:
        desde = 0
        while True:
            filas = admin.table(tabla).select("*").order("id").range(desde, desde + PAGINA - 1).execute().data or []
            for fila in filas:
                f.write(_linea(fila) + "\n")
                n += 1
            if len(filas) < PAGINA:
                break
            desde += PAGINA
    return n, _sha256_archivo(destino)


def exportar_usuarios_auth(admin, destino: Path) -> tuple[int, str]:
    n = 0
    with destino.open("w", encoding="utf-8", newline="\n") as f:
        pagina = 1
        while True:
            lista = admin.auth.admin.list_users(page=pagina, per_page=PAGINA)
            usuarios = getattr(lista, "users", lista) or []
            for u in usuarios:
                fila = {
                    "id": str(u.id),
                    "email": u.email,
                    "created_at": str(u.created_at) if u.created_at else None,
                    "email_confirmed_at": str(u.email_confirmed_at) if getattr(u, "email_confirmed_at", None) else None,
                    "last_sign_in_at": str(u.last_sign_in_at) if getattr(u, "last_sign_in_at", None) else None,
                    "user_metadata": dict(u.user_metadata or {}),
                    "app_metadata": dict(u.app_metadata or {}),
                }
                f.write(_linea(fila) + "\n")
                n += 1
            if len(usuarios) < PAGINA:
                break
            pagina += 1
    return n, _sha256_archivo(destino)


def listar_bucket(admin, bucket: str) -> list[dict[str, Any]]:
    """Todos los objetos del bucket (recorre las carpetas) como ``{"ruta", "tamano"}``."""
    objs: list[dict[str, Any]] = []
    pila = [""]
    while pila:
        prefijo = pila.pop()
        desde = 0
        while True:
            items = admin.storage.from_(bucket).list(prefijo, {"limit": 100, "offset": desde}) or []
            for it in items:
                ruta = f"{prefijo}/{it['name']}" if prefijo else it["name"]
                if it.get("id") is None:
                    pila.append(ruta)
                else:
                    objs.append({"ruta": ruta, "tamano": int((it.get("metadata") or {}).get("size") or 0)})
            if len(items) < 100:
                break
            desde += 100
    return sorted(objs, key=lambda o: o["ruta"])


def exportar(salida_base: Path, admin=None) -> Path:
    if not fuera_del_repo(salida_base):
        raise SystemExit(
            f"La carpeta de salida ({salida_base}) está dentro del repositorio. Los respaldos tienen datos personales: "
            "elegí una carpeta fuera del repositorio (por ejemplo kinetiq-data/respaldos)."
        )
    if admin is None:
        from app.security import get_admin_client

        admin = get_admin_client()

    ahora = datetime.now(timezone.utc)
    carpeta = salida_base / f"respaldo-{ahora.strftime('%Y%m%d-%H%M%S')}"
    (carpeta / "tablas").mkdir(parents=True)
    (carpeta / "auth").mkdir()

    manifiesto: dict[str, Any] = {
        "version_formato": VERSION_FORMATO,
        "creado_utc": ahora.isoformat(),
        "commit_repositorio": _commit(),
        "migraciones_esperadas": _migraciones_del_repo(),
        "tablas": {},
        "auth": {},
        "storage": {},
        "nota": "No incluye contraseñas ni claves de ningún tipo; contiene datos personales (correos, videos): no subir ni compartir.",
    }
    for t in TABLAS:
        n, h = exportar_tabla(admin, t, carpeta / "tablas" / f"{t}.jsonl")
        manifiesto["tablas"][t] = {"filas": n, "sha256": h}
        print(f"  tabla {t:24s} {n:5d} filas")
    n, h = exportar_usuarios_auth(admin, carpeta / "auth" / "usuarios.jsonl")
    manifiesto["auth"] = {"usuarios": n, "sha256": h}
    print(f"  auth.users {'':14s} {n:5d} cuentas")

    for b in BUCKETS:
        archivos = []
        total = 0
        for o in listar_bucket(admin, b):
            destino = carpeta / "storage" / b / o["ruta"]
            destino.parent.mkdir(parents=True, exist_ok=True)
            datos = admin.storage.from_(b).download(o["ruta"])
            destino.write_bytes(datos)
            h = hashlib.sha256(datos).hexdigest()
            archivos.append({"ruta": o["ruta"], "bytes": len(datos), "bytes_listados": o["tamano"], "sha256": h})
            total += len(datos)
        manifiesto["storage"][b] = {"archivos": len(archivos), "bytes": total, "lista": archivos}
        print(f"  bucket {b:11s} {len(archivos):5d} archivos, {total / 1e6:8.1f} MB")

    (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return carpeta


# --- verificar -----------------------------------------------------------------------------------------------------


def verificar(carpeta: Path) -> list[str]:
    """Vuelve a calcular lo que dice el manifiesto. Devuelve la lista de problemas (vacía = la copia está íntegra)."""
    problemas: list[str] = []
    man = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
    for t, d in man["tablas"].items():
        p = carpeta / "tablas" / f"{t}.jsonl"
        if not p.exists():
            problemas.append(f"falta la tabla {t}")
            continue
        if _sha256_archivo(p) != d["sha256"]:
            problemas.append(f"la tabla {t} no coincide con su huella")
        n = sum(1 for _ in p.open(encoding="utf-8"))
        if n != d["filas"]:
            problemas.append(f"la tabla {t} tiene {n} filas y el manifiesto dice {d['filas']}")
    pa = carpeta / "auth" / "usuarios.jsonl"
    if not pa.exists() or _sha256_archivo(pa) != man["auth"]["sha256"]:
        problemas.append("las cuentas de auth no coinciden con su huella")
    for b, d in man["storage"].items():
        for a in d["lista"]:
            p = carpeta / "storage" / b / a["ruta"]
            if not p.exists():
                problemas.append(f"falta {b}/{a['ruta']}")
            elif p.stat().st_size != a["bytes"] or _sha256_archivo(p) != a["sha256"]:
                problemas.append(f"{b}/{a['ruta']} no coincide con su huella")
            elif a["bytes_listados"] and a["bytes_listados"] != a["bytes"]:
                problemas.append(f"{b}/{a['ruta']}: Storage listaba {a['bytes_listados']} bytes y se descargaron {a['bytes']}")

    # Referencias: cada archivo que dice la base existe en la copia.
    existentes = {(b, a["ruta"]) for b, d in man["storage"].items() for a in d["lista"]}
    for fila in map(json.loads, (carpeta / "tablas" / "videos.jsonl").open(encoding="utf-8")):
        if fila.get("ruta_almacenamiento") and ("videos", fila["ruta_almacenamiento"]) not in existentes:
            problemas.append(f"el video {fila['id']} apunta a un archivo que no está en videos/")
        for campo in ("ruta_fotograma_pelvis", "ruta_fotograma_torso", "ruta_fotograma_brazo"):
            if fila.get(campo) and ("artefactos", fila[campo]) not in existentes:
                problemas.append(f"el video {fila['id']} ({campo}) apunta a un archivo que no está en artefactos/")
    return problemas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="app.respaldo", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exportar", help="exporta tablas, cuentas y archivos a una carpeta fuera del repositorio")
    e.add_argument("--salida", required=True, type=Path)
    v = sub.add_parser("verificar", help="vuelve a calcular las huellas de un respaldo")
    v.add_argument("carpeta", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "exportar":
        carpeta = exportar(args.salida)
        problemas = verificar(carpeta)
        print(f"\nRespaldo en {carpeta}")
        print("Verificación: " + ("ÍNTEGRO" if not problemas else f"{len(problemas)} problema(s)"))
        for p in problemas:
            print("  -", p)
        return 0 if not problemas else 1
    problemas = verificar(args.carpeta)
    print("ÍNTEGRO" if not problemas else f"{len(problemas)} problema(s)")
    for p in problemas:
        print("  -", p)
    return 0 if not problemas else 1


if __name__ == "__main__":
    sys.exit(main())
