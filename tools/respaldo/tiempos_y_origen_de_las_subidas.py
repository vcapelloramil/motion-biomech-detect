"""Tiempos de cola y de procesamiento por sesión, y ORIGEN de cada archivo subido (SOLO LECTURA).

* Espera en cola = ``inicio_procesamiento_en − encolado_en``; procesamiento = ``fin − inicio`` (el Criterio 4 mide solo el procesamiento).
* Origen: la marca ``com.apple.quicktime.creationdate`` del archivo guardado (``ffprobe`` sobre una URL firmada de 5 min; no se descarga nada) contra la fecha de
  creación de los 16 originales de ``docs/resultados/corpus-real-alineacion.json``. Los recortes hechos con ``ffmpeg -c copy`` (``recortar_evolucion.py``) no conservan esa marca.

No imprime correos ni claves. Uso, desde ``backend/``::

    PYTHONPATH=. .venv/Scripts/python.exe ../tools/respaldo/tiempos_y_origen_de_las_subidas.py
"""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.security import get_admin_client  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]


def _t(x: str | None) -> datetime | None:
    return datetime.fromisoformat(x.replace("Z", "+00:00")) if x else None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = get_admin_client()
    sesiones = {s["id"]: s for s in a.table("sesiones").select("id,fecha,gesto,encuadre").execute().data}
    videos = a.table("videos").select("*").execute().data

    print("TIEMPOS POR SESIÓN (hora UTC de la base):")
    for sid in sorted({v["sesion_id"] for v in videos}):
        vs = [v for v in videos if v["sesion_id"] == sid and v.get("encolado_en") and v.get("inicio_procesamiento_en") and v.get("fin_procesamiento_en")]
        if not vs:
            continue
        procs = [(_t(v["fin_procesamiento_en"]) - _t(v["inicio_procesamiento_en"])).total_seconds() for v in vs]
        esp = [(_t(v["inicio_procesamiento_en"]) - _t(v["encolado_en"])).total_seconds() for v in vs]
        pared = (max(_t(v["fin_procesamiento_en"]) for v in vs) - min(_t(v["encolado_en"]) for v in vs)).total_seconds()
        fr = [v["total_fotogramas"] for v in vs]
        s = sesiones[sid]
        print(
            f"  {sid[:8]} {s['fecha']} {s['gesto']} {s['encuadre']}: golpes={len(vs)} pared={pared:.0f}s procesamiento mediana={statistics.median(procs):.1f}s "
            f"(min {min(procs):.1f}, max {max(procs):.1f}) espera mediana={statistics.median(esp):.1f}s max={max(esp):.1f}s fotogramas {min(fr)}–{max(fr)} "
            f"s/fotograma mediana={statistics.median([p / f for p, f in zip(procs, fr)]):.3f}"
        )

    print("\nORIGEN DE LOS ARCHIVOS (creationdate del archivo guardado → original del corpus):")
    al = json.loads((RAIZ / "docs" / "resultados" / "corpus-real-alineacion.json").read_text(encoding="utf-8"))
    reales = al["reales"].items() if isinstance(al["reales"], dict) else al["reales"]
    por_creado = {r["creado"]: nombre for nombre, r in reales}
    for v in videos:
        s = sesiones[v["sesion_id"]]
        url = a.storage.from_("videos").create_signed_url(v["ruta_almacenamiento"], 300)["signedURL"]
        marca = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format_tags=com.apple.quicktime.creationdate", "-of", "default=nw=1:nk=1", url],
            capture_output=True, text=True,
        ).stdout.strip()
        print(f"  sesión {v['sesion_id'][:8]} ({s['fecha']} {s['gesto']} {s['encuadre']}): {v['ruta_almacenamiento'].split('/')[-1]} · creationdate={marca or '—'} → {por_creado.get(marca, 'sin marca (recorte con ffmpeg -c copy)' if not marca else '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
