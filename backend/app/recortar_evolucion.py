"""Recorta cada golpe de los originales del iPhone SIN recodificar y verifica, con aritmética entera, que no se perdió nada.

Para qué: armar la pantalla Evolución de la demo con golpes REALES (sesiones del 24/9 y del 25/9, saque en tres cuartos) sin depender de
volver a grabar. ``ffmpeg -c copy`` no toca los fotogramas: conserva las marcas de tiempo reales del archivo (la tasa real, ~200 fps) y
no pierde fotogramas. Se quita el audio (la voz del jugador no es parte del análisis).

Qué hace:
  1. Por cada repetición de la tabla de alineación (``docs/resultados/corpus-real-alineacion.json``, las mismas ventanas del Paso B)
     corta el original con un margen de 0,3 s; ffmpeg arranca en el fotograma clave anterior (~1 s).
  2. Verifica CADA recorte: todos sus fotogramas existen en el original con la misma marca de tiempo (salvo una constante), ninguno
     de la ventana falta, el archivo decodifica sin errores y pesa menos del tope de Cargar (50 MiB).
  3. Escribe ``recortes.json`` con lo anterior.

Los videos NO van al repositorio: la carpeta de salida debe estar fuera de él (o ignorada). Uso, desde ``backend/``::

    PYTHONPATH=. .venv/Scripts/python.exe -m app.recortar_evolucion --originales <carpeta> --salida <carpeta>
    PYTHONPATH=. .venv/Scripts/python.exe -m app.recortar_evolucion --originales <carpeta> --salida <carpeta> --solo-verificar
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ALINEACION = Path(__file__).resolve().parents[2] / "docs" / "resultados" / "corpus-real-alineacion.json"
MARGEN_S = 0.3
TOPE_BYTES = 50 * 1024 * 1024

# (original, prefijo de la repetición en la tabla de alineación, sesión, fecha, toma)
GRUPOS = [
    ("IMG_6376.MOV", "20260924_VCR_saque_trescuartos_240_01", 1, "2026-09-24", "01"),
    ("IMG_6392.MOV", "20260925_VCR_saque_trescuartos_240_02b", 2, "2026-09-25", "02b"),
    ("IMG_6393.MOV", "20260925_VCR_saque_trescuartos_240_02c", 2, "2026-09-25", "02c"),
]


_CACHE_PAQUETES: dict[Path, tuple[Fraction, list[int]]] = {}


def _paquetes(ruta: Path) -> tuple[Fraction, list[int]]:
    """Base de tiempo y marcas (enteras, ordenadas) de los paquetes de video (se lee una vez por archivo)."""
    if ruta not in _CACHE_PAQUETES:
        _CACHE_PAQUETES[ruta] = _paquetes_ffprobe(ruta)
    return _CACHE_PAQUETES[ruta]


def _paquetes_ffprobe(ruta: Path) -> tuple[Fraction, list[int]]:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=time_base:packet=pts", "-of", "json", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    d = json.loads(r.stdout)
    return Fraction(d["streams"][0]["time_base"]), sorted(int(p["pts"]) for p in d["packets"] if "pts" in p)


def _cortar(original: Path, destino: Path, desde_s: float, hasta_s: float) -> None:
    desde = max(desde_s, 0.0)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{desde:.4f}", "-i", str(original), "-t", f"{hasta_s - desde:.4f}",
         "-map", "0:v:0", "-c", "copy", "-map_metadata", "0", "-an", "-sn", "-dn", "-avoid_negative_ts", "make_zero",
         "-movflags", "+faststart", str(destino)],
        check=True,
    )


def _verificar(original: Path, recorte: Path, ventana: tuple[int, int]) -> dict:
    tb_o, pts_o = _paquetes(original)
    tb_c, pts_c = _paquetes(recorte)
    s_o = [Fraction(p) * tb_o for p in pts_o]
    s_c = [Fraction(p) * tb_c for p in pts_c]
    indice = {s: i for i, s in enumerate(s_o)}
    desfase = next((x - s_c[0] for x in s_o if all((s + (x - s_c[0])) in indice for s in s_c)), None)
    decod = subprocess.run(["ffmpeg", "-v", "error", "-i", str(recorte), "-f", "null", "-"], capture_output=True, text=True)
    resultado = {
        "fotogramas": len(pts_c),
        "duracion_s": round(float(s_c[-1] - s_c[0]), 3),
        "fps_real_medio": round((len(pts_c) - 1) / float(s_c[-1] - s_c[0]), 2),
        "bytes": recorte.stat().st_size,
        "mb": round(recorte.stat().st_size / 1e6, 1),
        "decodifica_sin_errores": decod.returncode == 0 and not decod.stderr.strip(),
        "marcas_identicas_al_original": desfase is not None,
    }
    if desfase is None:
        resultado.update(sin_fotogramas_faltantes_en_la_ventana=False, incluye_la_ventana_completa=False)
    else:
        idx = sorted(indice[s + desfase] for s in s_c)
        presentes = set(idx)
        a, b = ventana
        resultado.update(
            sin_fotogramas_faltantes_en_la_ventana=all(i in presentes for i in range(a, b + 1)),
            incluye_la_ventana_completa=idx[0] <= a and idx[-1] >= b,
            primer_fotograma_en_el_original=idx[0],
            ultimo_fotograma_en_el_original=idx[-1],
            fotogramas_antes_de_la_ventana=a - idx[0],
            fotogramas_despues_de_la_ventana=idx[-1] - b,
        )
    resultado["ok"] = bool(
        resultado["marcas_identicas_al_original"] and resultado["sin_fotogramas_faltantes_en_la_ventana"]
        and resultado["incluye_la_ventana_completa"] and resultado["decodifica_sin_errores"] and resultado["bytes"] < TOPE_BYTES
    )
    return resultado


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--originales", type=Path, required=True)
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--solo-verificar", action="store_true", help="no corta: verifica los recortes ya hechos")
    args = ap.parse_args(argv)
    args.salida.mkdir(parents=True, exist_ok=True)
    tabla = json.loads(ALINEACION.read_text(encoding="utf-8"))["repeticiones"]
    filas: list[dict] = []
    for original, prefijo, sesion, fecha, toma in GRUPOS:
        ruta = args.originales / original
        reps = sorted((r for r in tabla if r["repeticion"].startswith(prefijo) and r["real"] == original), key=lambda r: r["repeticion"])
        if len(reps) != 6:
            raise SystemExit(f"{original}: se esperaban 6 repeticiones y la tabla trae {len(reps)}")
        tb, pts = _paquetes(ruta)
        seg = [float(Fraction(p) * tb) for p in pts]
        for n, r in enumerate(reps, start=1):
            a, b = (int(x) for x in r["ventana_real"])
            nombre = f"{fecha.replace('-', '')}_saque_trescuartos_toma{toma}_golpe{n}.mov"
            destino = args.salida / nombre
            if not args.solo_verificar:
                _cortar(ruta, destino, seg[a] - MARGEN_S, seg[b] + MARGEN_S)
            v = _verificar(ruta, destino, (a, b))
            fila = {"archivo": nombre, "sesion": sesion, "fecha": fecha, "original": original, "toma": toma, "golpe": n,
                    "ventana_original": [a, b], **v}
            filas.append(fila)
            print(f"{nombre}: {v['fotogramas']} fot., {v['duracion_s']} s, {v['fps_real_medio']} fps, {v['mb']} MB -> "
                  f"{'OK' if v['ok'] else 'REVISAR'}", flush=True)
    (args.salida / "recortes.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    malos = [f["archivo"] for f in filas if not f["ok"]]
    print(f"\n{len(filas)} recortes; problemas: {malos or 'ninguno'}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
