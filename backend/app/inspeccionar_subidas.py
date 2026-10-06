"""Inspecciona los archivos que la página de prueba del iPhone subió a Storage.

Prueba de riesgo del plan de punta a punta (``docs/plan-mvp-punta-a-punta.md``): ¿el archivo que entrega Safari
del iPhone conserva los fotogramas y la duración del original? La página (``tools/prueba-iphone/``) sube el mismo
video elegido con cuatro selectores distintos; este script baja cada objeto y mide lo que el motor mide
(``engine.ingest.probe``) más lo que ``ffprobe`` sabe del contenedor (códec, rotación, etiquetas).

Es de solo lectura sobre Storage salvo ``--borrar``. Usa ``service_role``, así que corre en la máquina de Valentín,
no en Render.

Uso (desde ``backend/`` o con ``PYTHONPATH=backend``):
    python -m app.inspeccionar_subidas --email tu-correo@... [--duracion-real 2.0]

``--duracion-real`` es la duración **en tiempo real** del gesto grabado (segundos, lo que dura en la vida real, no lo
que dura reproducido en cámara lenta). Con ella se calcula cuántos fotogramas tendría que tener el archivo si se
conservaron todos los de 240 fps.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.config import get_supabase_service_role_key, get_supabase_url

BUCKET = "videos"
PREFIJO = "prueba-iphone"


def _ffprobe_completo(ruta: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries",
        "stream=codec_name,profile,width,height,r_frame_rate,avg_frame_rate,nb_frames,duration,bit_rate:"
        "stream_tags:stream_side_data=rotation:format=format_name,duration,bit_rate:format_tags",
        "-of", "json", str(ruta),
    ]
    try:
        salida = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True).stdout
        return json.loads(salida)
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"error": f"ffprobe no disponible o falló: {exc}"}


def _resumir(nombre: str, tamano: int, ruta: Path, duracion_real: float | None) -> dict:
    from app.engine.ingest import probe

    md = probe(ruta)
    raw = _ffprobe_completo(ruta)
    stream = (raw.get("streams") or [{}])[0]
    fmt = raw.get("format") or {}
    resumen = {
        "objeto": nombre,
        "tamano_mb": round(tamano / 1_048_576, 2),
        "contenedor": fmt.get("format_name"),
        "codec": stream.get("codec_name"),
        "perfil": stream.get("profile"),
        "resolucion": f"{md.ancho}x{md.alto}",
        "fps_declarados": md.fps_declarados,
        "r_frame_rate": md.r_frame_rate,
        "avg_frame_rate": md.avg_frame_rate,
        "fotogramas_opencv": md.nb_frames,
        "fotogramas_ffprobe": md.nb_frames_ffprobe,
        "duracion_reproducida_s": round(md.duracion_ffprobe_s or md.duracion_s, 3),
        "rotacion": next(
            (d.get("rotation") for d in stream.get("side_data_list", []) if "rotation" in d), None
        ),
        "etiquetas_stream": stream.get("tags"),
        "etiquetas_formato": fmt.get("tags"),
    }
    fotogramas = md.nb_frames_ffprobe or md.nb_frames
    if duracion_real:
        esperados_240 = round(duracion_real * 240)
        resumen["fotogramas_esperados_a_240fps"] = esperados_240
        resumen["fotogramas_vs_esperados"] = round(fotogramas / esperados_240, 3) if esperados_240 else None
        resumen["fps_efectivos_si_duracion_real"] = round(fotogramas / duracion_real, 1)
    return resumen


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Mide los archivos subidos por la página de prueba del iPhone.")
    ap.add_argument("--email", required=True, help="correo del usuario de prueba con el que se subió")
    ap.add_argument("--duracion-real", type=float, default=None, help="duración real del gesto, en segundos")
    ap.add_argument("--borrar", action="store_true", help="borra de Storage lo inspeccionado, al terminar")
    args = ap.parse_args(argv)

    from supabase import create_client

    admin = create_client(get_supabase_url(), get_supabase_service_role_key())
    usuarios = [u for u in admin.auth.admin.list_users() if (u.email or "").lower() == args.email.lower()]
    if not usuarios:
        print(f"No existe un usuario con el correo {args.email}.")
        return 1
    carpeta = f"{usuarios[0].id}/{PREFIJO}"
    objetos = [o for o in admin.storage.from_(BUCKET).list(carpeta) if o.get("name") and o.get("id")]
    if not objetos:
        print(f"No hay archivos en {BUCKET}/{carpeta}/ todavía.")
        return 1

    resultados = []
    with tempfile.TemporaryDirectory() as tmp:
        for o in sorted(objetos, key=lambda x: x["name"]):
            contenido = admin.storage.from_(BUCKET).download(f"{carpeta}/{o['name']}")
            destino = Path(tmp) / o["name"]
            destino.write_bytes(contenido)
            try:
                resultados.append(_resumir(o["name"], len(contenido), destino, args.duracion_real))
            except Exception as exc:  # noqa: BLE001 - un archivo ilegible es un resultado, no un error del script
                resultados.append({"objeto": o["name"], "tamano_mb": round(len(contenido) / 1_048_576, 2), "error": repr(exc)})

    print(json.dumps(resultados, ensure_ascii=False, indent=1))
    if args.borrar:
        admin.storage.from_(BUCKET).remove([f"{carpeta}/{o['name']}" for o in objetos])
        print(f"\nBorrados {len(objetos)} objetos de {BUCKET}/{carpeta}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
