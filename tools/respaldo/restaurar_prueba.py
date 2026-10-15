"""Prueba de restauración de un respaldo de KinetiQ en un Postgres LOCAL y descartable (paso 7 del plan §8).

No toca Supabase ni producción. Qué hace:

1. levanta un Postgres embebido (paquete ``pgserver``) en una carpeta temporal;
2. crea lo mínimo de la plataforma que las migraciones suponen (roles ``anon``/``authenticated``/``service_role``, ``auth.users``,
   ``auth.uid()``, ``storage.buckets``, ``storage.objects`` y ``storage.foldername``);
3. aplica **todas** las migraciones de ``supabase/migrations`` en orden (si una no aplica sobre una base vacía, la restauración real tampoco);
4. carga las cuentas y las nueve tablas del respaldo (con los disparadores apagados, como haría un volcado);
5. **compara fila por fila** lo restaurado con lo respaldado;
6. registra los archivos del respaldo en ``storage.objects`` y comprueba que cada ruta que dice la base existe;
7. prueba que las políticas de acceso restauradas aíslan a los usuarios (cada cuenta ve solo lo suyo).

Requisitos (solo para esta prueba, no son del backend)::

    python -m venv venv_respaldo && venv_respaldo/Scripts/pip install pgserver "psycopg[binary]"
    venv_respaldo/Scripts/python tools/respaldo/restaurar_prueba.py "<carpeta del respaldo>" [--salida informe.json]

Sale con código 0 solo si todas las comprobaciones pasan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pgserver
import psycopg
from psycopg.types.json import Jsonb

RAIZ = Path(__file__).resolve().parents[2]
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

PLATAFORMA = """
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;

create schema auth;
create table auth.users (
    id uuid primary key,
    email text,
    raw_user_meta_data jsonb not null default '{}'::jsonb,
    raw_app_meta_data jsonb not null default '{}'::jsonb,
    created_at timestamptz default now(),
    email_confirmed_at timestamptz,
    last_sign_in_at timestamptz
);
create function auth.uid() returns uuid language sql stable as
    $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;

create schema storage;
create table storage.buckets (
    id text primary key,
    name text not null,
    public boolean default false,
    file_size_limit bigint,
    allowed_mime_types text[]
);
create table storage.objects (
    id uuid primary key default gen_random_uuid(),
    bucket_id text references storage.buckets (id),
    name text not null,
    owner uuid,
    metadata jsonb,
    unique (bucket_id, name)
);
alter table storage.objects enable row level security;
create function storage.foldername(name text) returns text[] language sql immutable as
    $$ select (string_to_array(name, '/'))[1:greatest(array_length(string_to_array(name, '/'), 1) - 1, 0)] $$;

grant usage on schema auth, storage, public to anon, authenticated, service_role;
grant select on all tables in schema storage to authenticated;
grant execute on function auth.uid() to anon, authenticated, service_role;
"""


def iguales(a: Any, b: Any) -> bool:
    """Igualdad tolerante a las diferencias de formato entre PostgREST y Postgres (números, fechas, orden de claves)."""
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(iguales(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(iguales(x, y) for x, y in zip(a, b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(a)))
    if isinstance(a, str) and isinstance(b, str):
        if a == b:
            return True
        try:
            return datetime.fromisoformat(a.replace("Z", "+00:00")) == datetime.fromisoformat(b.replace("Z", "+00:00"))
        except ValueError:
            return False
    return a == b


def leer_jsonl(p: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def aplicar_migraciones(con: psycopg.Connection) -> tuple[list[str], list[str]]:
    """Aplica las migraciones en orden. Devuelve (aplicadas, desviaciones del arnés).

    Única desviación posible: el Postgres embebido no trae la extensión ``pgcrypto``. Las migraciones solo la piden para
    ``gen_random_uuid()``, que desde PostgreSQL 13 es parte del servidor; se omite esa línea y se deja constancia en el informe.
    """
    desviaciones: list[str] = []
    hay_pgcrypto = con.execute("select count(*) from pg_available_extensions where name = 'pgcrypto'").fetchone()[0] > 0
    aplicadas = []
    for p in sorted((RAIZ / "supabase" / "migrations").glob("*.sql")):
        sql = p.read_text(encoding="utf-8")
        linea = "create extension if not exists pgcrypto;"
        if not hay_pgcrypto and linea in sql:
            sql = sql.replace(linea, "-- (omitida en la prueba local: pgcrypto no está en el Postgres embebido; gen_random_uuid() es nativo)")
            desviaciones.append(f"{p.name}: se omitió '{linea}' (gen_random_uuid() es nativo desde PostgreSQL 13)")
        con.execute(sql)
        aplicadas.append(p.name)
    return aplicadas, desviaciones


def columnas(con: psycopg.Connection, tabla: str) -> dict[str, str]:
    filas = con.execute(
        "select column_name, data_type from information_schema.columns where table_schema = 'public' and table_name = %s", (tabla,)
    ).fetchall()
    return {c: t for c, t in filas}


def cargar_tabla(con: psycopg.Connection, tabla: str, filas: list[dict[str, Any]]) -> list[str]:
    """Inserta las filas; devuelve columnas del respaldo que la tabla restaurada no tiene (un cambio de esquema no migrado)."""
    cols = columnas(con, tabla)
    faltantes: set[str] = set()
    for f in filas:
        usar = {k: v for k, v in f.items() if k in cols}
        faltantes |= set(f) - set(cols)
        valores = [Jsonb(v) if (cols[k] in ("json", "jsonb") and v is not None) else v for k, v in usar.items()]
        nombres = ", ".join(f'"{k}"' for k in usar)
        con.execute(f'insert into public."{tabla}" ({nombres}) values ({", ".join(["%s"] * len(usar))})', valores)
    return sorted(faltantes)


def main() -> int:
    ap = argparse.ArgumentParser(description="Prueba de restauración de un respaldo en un Postgres local descartable")
    ap.add_argument("respaldo", type=Path)
    ap.add_argument("--salida", type=Path, help="escribe el informe JSON acá (sin datos personales)")
    args = ap.parse_args()
    carpeta: Path = args.respaldo
    man = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
    informe: dict[str, Any] = {"respaldo_creado_utc": man["creado_utc"], "comprobaciones": {}, "ok": True}

    def marcar(nombre: str, ok: bool, detalle: Any = None) -> None:
        informe["comprobaciones"][nombre] = {"ok": bool(ok), **({"detalle": detalle} if detalle is not None else {})}
        informe["ok"] = informe["ok"] and bool(ok)
        print(f"  [{'OK ' if ok else 'FALLA'}] {nombre}" + (f" — {detalle}" if detalle is not None and not ok else ""))

    with tempfile.TemporaryDirectory(prefix="kinetiq-restauracion-") as tmp:
        servidor = pgserver.get_server(Path(tmp) / "pg", cleanup_mode="delete")
        try:
            with psycopg.connect(servidor.get_uri(), autocommit=True) as con:
                print("Postgres local:", con.execute("select version()").fetchone()[0].split(",")[0])
                con.execute(PLATAFORMA)
                aplicadas, desviaciones = aplicar_migraciones(con)
                informe['desviaciones_del_arnes'] = desviaciones
                marcar(
                    "las migraciones aplican sobre una base vacía",
                    aplicadas == man["migraciones_esperadas"],
                    {"aplicadas": len(aplicadas), "esperadas": len(man["migraciones_esperadas"])},
                )

                # --- carga (disparadores apagados: es lo que hace un volcado)
                con.execute("set session_replication_role = replica")
                cuentas = leer_jsonl(carpeta / "auth" / "usuarios.jsonl")
                for u in cuentas:
                    con.execute(
                        "insert into auth.users (id, email, raw_user_meta_data, raw_app_meta_data, created_at, email_confirmed_at, last_sign_in_at) "
                        "values (%s, %s, %s, %s, %s, %s, %s)",
                        (u["id"], u["email"], Jsonb(u["user_metadata"]), Jsonb(u["app_metadata"]), u["created_at"], u["email_confirmed_at"], u["last_sign_in_at"]),
                    )
                respaldadas: dict[str, list[dict[str, Any]]] = {}
                sin_columna: dict[str, list[str]] = {}
                for t in TABLAS:
                    filas = leer_jsonl(carpeta / "tablas" / f"{t}.jsonl")
                    respaldadas[t] = filas
                    f = cargar_tabla(con, t, filas)
                    if f:
                        sin_columna[t] = f
                con.execute("set session_replication_role = origin")
                marcar("todas las columnas del respaldo existen en el esquema restaurado", not sin_columna, sin_columna)

                # --- comparación fila por fila
                for t in TABLAS:
                    restauradas = [r[0] for r in con.execute(f'select to_jsonb(x) from public."{t}" x order by id').fetchall()]
                    originales = sorted(respaldadas[t], key=lambda f: str(f["id"]))
                    restauradas = sorted(restauradas, key=lambda f: str(f["id"]))
                    esperado = man["tablas"][t]["filas"]
                    mismas = len(originales) == len(restauradas) == esperado and all(
                        iguales({k: v for k, v in o.items()}, {k: r.get(k) for k in o}) for o, r in zip(originales, restauradas)
                    )
                    marcar(f"tabla {t}: {len(restauradas)} filas iguales al respaldo", mismas)

                n_aut = con.execute("select count(*) from auth.users").fetchone()[0]
                marcar(f"cuentas: {n_aut}", n_aut == man["auth"]["usuarios"])

                # --- archivos de Storage
                for b, d in man["storage"].items():
                    con.execute("insert into storage.buckets (id, name) values (%s, %s) on conflict do nothing", (b, b))
                    mal = []
                    for a in d["lista"]:
                        p = carpeta / "storage" / b / a["ruta"]
                        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != a["sha256"]:
                            mal.append(a["ruta"])
                            continue
                        dueño = a["ruta"].split("/")[0]
                        con.execute(
                            "insert into storage.objects (bucket_id, name, owner, metadata) values (%s, %s, %s, %s)",
                            (b, a["ruta"], dueño if len(dueño) == 36 else None, Jsonb({"size": a["bytes"], "sha256": a["sha256"]})),
                        )
                    marcar(f"archivos de {b}: {d['archivos']} con su huella", not mal, mal[:5])
                (n_video,) = con.execute("select count(*) from public.videos").fetchone()
                (n_sin,) = con.execute(
                    "select count(*) from public.videos v where v.ruta_almacenamiento is not null and not exists "
                    "(select 1 from storage.objects o where o.bucket_id = 'videos' and o.name = v.ruta_almacenamiento)"
                ).fetchone()
                marcar(f"cada uno de los {n_video} videos tiene su archivo en el bucket", n_sin == 0, {"sin_archivo": n_sin})

                # --- aislamiento con las políticas restauradas
                con.execute("grant select on all tables in schema public to authenticated")
                dueños = [r[0] for r in con.execute("select distinct usuario_id::text from public.videos").fetchall()]
                todos = [r[0] for r in con.execute("select id::text from auth.users").fetchall()]
                aislamiento_ok = True
                detalle_aisl: dict[str, Any] = {}
                for u in todos:
                    esperados = con.execute("select count(*) from public.videos where usuario_id = %s", (u,)).fetchone()[0]
                    con.execute("begin")
                    con.execute("set local role authenticated")
                    con.execute("select set_config('request.jwt.claim.sub', %s, true)", (u,))
                    visibles = con.execute("select count(*) from public.videos").fetchone()[0]
                    ajenos = con.execute("select count(*) from public.videos where usuario_id <> %s", (u,)).fetchone()[0]
                    con.execute("rollback")
                    ok_u = visibles == esperados and ajenos == 0
                    aislamiento_ok &= ok_u
                    detalle_aisl[u[:8]] = {"propios": esperados, "visibles": visibles, "ajenos": ajenos}
                marcar(
                    f"aislamiento: cada una de las {len(todos)} cuentas ve solo sus videos ({len(dueños)} con datos)",
                    aislamiento_ok,
                    detalle_aisl if not aislamiento_ok else None,
                )
        finally:
            servidor.cleanup()

    print("\nRESTAURACIÓN " + ("VERIFICADA" if informe["ok"] else "CON FALLAS"))
    if args.salida:
        args.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if informe["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
