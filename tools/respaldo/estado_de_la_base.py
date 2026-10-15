"""Estado de la base de producción, SOLO LECTURA (cuentas, sesiones, versiones del motor, análisis en curso y archivos huérfanos).

Sirve para verificar una limpieza antes de la demo (`docs/demo-guion.md`, §C) y para mirar que no haya análisis en curso antes de publicar
(`docs/publicacion-y-vuelta-atras.md`). No imprime correos ni claves. Uso, desde ``backend/``::

    PYTHONPATH=. .venv/Scripts/python.exe ../tools/respaldo/estado_de_la_base.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.respaldo import listar_bucket  # noqa: E402
from app.security import get_admin_client  # noqa: E402


def _version_de(v: dict) -> str:
    r = v.get("reportes_biomecanicos")
    r = r[0] if isinstance(r, list) and r else r
    rep = (r or {}).get("reporte") if isinstance(r, dict) else None
    return ((rep or {}).get("trazabilidad") or {}).get("version_motor", "—")


def main() -> int:
    a = get_admin_client()
    usuarios = a.table("usuarios").select("id, nombre, rol, creado_en").order("creado_en").execute().data
    letra = {u["id"]: chr(65 + i) for i, u in enumerate(usuarios)}
    print("CUENTAS (A, B, C… por antigüedad):")
    for u in usuarios:
        n = a.table("sesiones").select("id", count="exact").eq("usuario_id", u["id"]).execute().count
        print(f"  {letra[u['id']]}  creada={u['creado_en'][:10]}  nombre={u['nombre']!r}  rol={u['rol']}  sesiones={n}")

    print("\nSESIONES:")
    ses = a.table("sesiones").select("id, usuario_id, fecha, gesto, encuadre, lado_camara, atletas(nombre)").order("fecha").order("creado_en").execute().data
    versiones: Counter[str] = Counter()
    for s in ses:
        vids = a.table("videos").select("id, estado, reportes_biomecanicos(reporte)").eq("sesion_id", s["id"]).execute().data
        est = Counter(v["estado"] for v in vids)
        ver = Counter(_version_de(v) for v in vids)
        versiones.update(ver)
        print(f"  {s['id'][:8]} cuenta={letra.get(s['usuario_id'], '?')} {s['fecha']} {s['gesto']:6s} {s['encuadre']:12s} lado={s['lado_camara']:9s} "
              f"golpes={len(vids)} estados={dict(est)} motor={dict(ver)}")
    print("\nVERSIONES DEL MOTOR (todos los golpes):", dict(versiones) or "—")

    en_curso = a.table("videos").select("id, estado").in_("estado", ["encolado", "procesando", "pendiente"]).execute().data
    print("EN CURSO (encolado / procesando / pendiente):", dict(Counter(v["estado"] for v in en_curso)) or "ninguno")
    fallidos = a.table("videos").select("id", count="exact").eq("estado", "fallido").execute().count
    print("FALLIDOS:", fallidos)

    # archivos huérfanos: en Storage pero sin fila que los referencie
    videos = a.table("videos").select("ruta_almacenamiento, ruta_fotograma_pelvis, ruta_fotograma_torso, ruta_fotograma_brazo").execute().data
    refs = {(c, v[c]) for v in videos for c in ("ruta_almacenamiento", "ruta_fotograma_pelvis", "ruta_fotograma_torso", "ruta_fotograma_brazo") if v.get(c)}
    huerfanos: list[tuple[str, str, int]] = []
    ids = {r[1].rsplit("/", 1)[0] for r in refs}
    rutas = {r[1] for r in refs}
    for b in ("videos", "artefactos"):
        for o in listar_bucket(a, b):
            ruta = o["ruta"]
            # los artefactos (video con esqueleto, etc.) viven bajo <usuario>/<video>/…: se considera referido si su carpeta es de un video existente
            carpeta = "/".join(ruta.split("/")[:2])
            if ruta not in rutas and carpeta not in ids:
                huerfanos.append((b, ruta, o["tamano"]))
    total = sum(t for _, _, t in huerfanos)
    print(f"ARCHIVOS HUÉRFANOS (sin video que los referencie): {len(huerfanos)}  ({total / 1e6:.0f} MB)")
    por_dueño = Counter((letra.get(r.split("/")[0], "?"), r.split("/")[1] if "/" in r else "") for _, r, _ in huerfanos)
    for (dueño, carpeta), n in por_dueño.items():
        print(f"    cuenta {dueño}, carpeta '{carpeta}': {n} archivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
