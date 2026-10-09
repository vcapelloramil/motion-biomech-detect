"""Inspecciona los archivos que la página de prueba del iPhone subió a Storage.

Prueba de riesgo del plan de punta a punta (``docs/plan-mvp-punta-a-punta.md``): ¿el archivo que entrega Safari
del iPhone conserva los fotogramas y la duración del original? La página (``tools/prueba-iphone/``) sube el mismo
video elegido con cuatro selectores distintos; este script baja cada objeto y mide lo que el motor mide
(``engine.ingest.probe``) más lo que ``ffprobe`` sabe del contenedor (códec, rotación, etiquetas).

Por cada archivo informa (decisión 028): fps del contenedor, cantidad de fotogramas, duración, si las marcas de
tiempo son de **tiempo real a 240** o de **cámara lenta horneada a 30**, y en cuál de los tres casos cae:

* **(a)** 240 fps en tiempo real (válido),
* **(b)** 30 fps con la cámara lenta horneada, todos los fotogramas (válido, como el corpus),
* **(c)** 30 fps en tiempo real con fotogramas descartados (**inválido**).

Las marcas de tiempo distinguen (a) de (b)/(c) pero **no (b) de (c)**: para eso hace falta ``--duracion-real``. Además
informa **tramos con mucho más movimiento por fotograma** que el resto del archivo (heurística experimental, decisión 028: puede ser una
rampa de velocidad de la cámara lenta o simplemente manejo de la cámara; **no las distingue**).

Es de solo lectura sobre Storage salvo ``--borrar``. Usa ``service_role``, así que corre en la máquina de Valentín,
no en Render.

Uso (desde ``backend/`` o con ``PYTHONPATH=backend``):
    python -m app.inspeccionar_subidas --email tu-correo@... [--duracion-real 2.0]

``--duracion-real`` es la duración **en tiempo real** del gesto grabado (segundos, lo que dura en la vida real, no lo
que dura reproducido en cámara lenta). Sin ella, un archivo con marcas a ~30 fps queda "indeterminado" (b o c).
``--captura`` es la frecuencia de captura declarada (240 por defecto).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.config import get_supabase_service_role_key, get_supabase_url
from app.engine.uniformidad_temporal import (
    clasificar_caso,
    detectar_tramos_acelerados,
    energia_de_movimiento,
    marcas_de_tiempo,
)

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


def _que_haria_el_sistema(fps_contenedor: float, nb_frames: int) -> dict[str, str]:
    """Qué haría ``procesar_video`` HOY con este archivo según el modo que declare el usuario (decisión 020), sin correrlo.

    Usa las mismas funciones que producción: ``_factor_y_motivo`` (declaración x fps del contenedor) y, si cierra, ``ingest.evaluar`` más
    el umbral de R1 (< 120 fps efectivos: no se corre la secuenciación, el video queda 'parcial')."""
    from pathlib import Path

    from app.engine import ingest
    from app.procesar_video import _UMBRAL_SECUENCIACION_FPS, _factor_y_motivo

    md = ingest.MetadatosVideo(
        ruta=Path("x"), fps_declarados=fps_contenedor, nb_frames=nb_frames, duracion_s=nb_frames / fps_contenedor if fps_contenedor else 0.0, ancho=0, alto=0
    )
    salida = {}
    for modo in ("camara_lenta_240", "camara_lenta_120", "normal"):
        factor, escala, origen, motivo = _factor_y_motivo(modo, fps_contenedor)
        if motivo is not None:
            salida[modo] = f"FALLA ({motivo}): el factor no es un entero >= 1"
            continue
        r = ingest.evaluar(md, factor=factor, escala_conocida=escala, origen_factor=origen)
        if r.fps_efectivos < _UMBRAL_SECUENCIACION_FPS:
            salida[modo] = f"queda PARCIAL por R1: {r.fps_efectivos:g} fps efectivos (< {_UMBRAL_SECUENCIACION_FPS:g}), sin análisis de la fase rápida"
        else:
            salida[modo] = f"SE ANALIZA con {r.fps_efectivos:g} fps efectivos (factor {factor:g})"
    return salida


def _resumir(nombre: str, tamano: int, ruta: Path, duracion_real: float | None, fps_captura: float) -> dict:
    from app.engine.ingest import probe

    md = probe(ruta)
    raw = _ffprobe_completo(ruta)
    stream = (raw.get("streams") or [{}])[0]
    fmt = raw.get("format") or {}
    marcas = marcas_de_tiempo(ruta)
    # Los fotogramas son los VISIBLES (los que decodifica el reproductor). nb_frames del contenedor puede incluir pre-roll oculto.
    fotogramas = marcas.n_paquetes
    caso = clasificar_caso(marcas, fotogramas, duracion_real, fps_captura=fps_captura)
    tramos = detectar_tramos_acelerados(energia_de_movimiento(ruta), fps_reproduccion=marcas.fps_por_marcas)

    resumen = {
        "objeto": nombre,
        "selector": nombre.split("-")[0],
        "tamano_mb": round(tamano / 1_048_576, 2),
        "contenedor": fmt.get("format_name"),
        "codec": stream.get("codec_name"),
        "perfil": stream.get("profile"),
        "resolucion": f"{md.ancho}x{md.alto}",
        # Lo que E0 lee HOY (OpenCV). Para archivos con marcas variables o con pre-roll NO coincide con la tasa real: ver "tasa_real".
        "fps_contenedor": md.fps_declarados,
        "fotogramas": fotogramas,
        "fotogramas_segun_el_contenedor": md.nb_frames_ffprobe or md.nb_frames,
        "fotogramas_de_preroll_ocultos": marcas.n_preroll,
        "tasa_real": {
            "nominal_fps": round(marcas.fps_por_marcas, 2),
            "real_media_fps": round(marcas.fps_real, 2),
            "fotogramas_perdidos_pct": round(marcas.fraccion_perdida * 100, 1),
            "intervalos_en_periodos": {str(k): v for k, v in sorted(__import__("collections").Counter(marcas.intervalos_en_periodos).items())},
        },
        "duracion_reproducida_s": round(md.duracion_ffprobe_s or md.duracion_s, 3),
        "marcas_de_tiempo": {
            "fps_por_marcas": round(marcas.fps_por_marcas, 2),
            "separacion_mediana_ms": round(marcas.separacion_mediana_s * 1000, 3),
            "constantes": marcas.es_constante,
            "tipo": "tiempo real (>= 100 fps)" if marcas.fps_por_marcas >= 100 else "estiradas a ~30 fps (cámara lenta horneada o tiempo real a 30)",
        },
        "que_haria_el_sistema": _que_haria_el_sistema(md.fps_declarados, fotogramas),
        "caso": caso.caso.value,
        "caso_valido": caso.es_valido,
        "caso_explicacion": caso.explicacion,
        "fraccion_de_fotogramas_esperados": round(caso.fraccion_del_esperado, 3) if caso.fraccion_del_esperado is not None else None,
        "sin_tramos_de_mucho_movimiento": not tramos,
        "tramos_de_mucho_movimiento": [
            {"desde_s": round(t.desde_s, 2), "hasta_s": round(t.hasta_s, 2), "razon_maxima": round(t.razon_maxima, 1)} for t in tramos
        ],
        "rotacion": next((d.get("rotation") for d in stream.get("side_data_list", []) if "rotation" in d), None),
        "etiquetas_stream": stream.get("tags"),
    }
    return resumen


def _veredicto(r: dict) -> str:
    if "error" in r:
        return f"{r['objeto']}: ERROR {r['error']}"
    caso = {"a": "(a) tiempo real (sin cámara lenta horneada)", "b": "(b) cámara lenta horneada", "c": "(c) INVÁLIDO: fotogramas descartados",
            "indeterminado": "(b o c) falta --duracion-real"}[r["caso"]]
    vel = (
        "movimiento parejo"
        if r["sin_tramos_de_mucho_movimiento"]
        else f"TRAMOS CON MUCHO MÁS MOVIMIENTO POR FOTOGRAMA (¿rampa de velocidad o manejo de la cámara?): {r['tramos_de_mucho_movimiento']}"
    )
    prod = " | ".join(f"{m}: {t}" for m, t in r["que_haria_el_sistema"].items())
    t = r["tasa_real"]
    return (f"{r['selector']}: {r['codec']} · E0 lee {r['fps_contenedor']:g} fps · {r['fotogramas']} fotogramas visibles "
            f"(el contenedor dice {r['fotogramas_segun_el_contenedor']}) · {r['duracion_reproducida_s']} s\n"
            f"      marcas de tiempo: nominal {t['nominal_fps']:g} fps, REAL MEDIA {t['real_media_fps']:g} fps "
            f"({t['fotogramas_perdidos_pct']:g} % perdidos) → {caso} · {vel}\n"
            f"      El sistema (con la lectura actual de E0), según lo que declares → {prod}")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Mide los archivos subidos por la página de prueba del iPhone.")
    ap.add_argument("--email", required=True, help="correo del usuario de prueba con el que se subió")
    ap.add_argument("--duracion-real", type=float, default=None, help="duración real del gesto, en segundos")
    ap.add_argument("--captura", type=float, default=240.0, help="frecuencia de captura declarada (fps), 240 por defecto")
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
                resultados.append(_resumir(o["name"], len(contenido), destino, args.duracion_real, args.captura))
            except Exception as exc:  # noqa: BLE001 - un archivo ilegible es un resultado, no un error del script
                resultados.append({"objeto": o["name"], "tamano_mb": round(len(contenido) / 1_048_576, 2), "error": repr(exc)})

    print(json.dumps(resultados, ensure_ascii=False, indent=1))
    print("\n== Resumen por selector ==")
    for r in resultados:
        print(" ", _veredicto(r))
    if args.borrar:
        admin.storage.from_(BUCKET).remove([f"{carpeta}/{o['name']}" for o in objetos])
        print(f"\nBorrados {len(objetos)} objetos de {BUCKET}/{carpeta}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
