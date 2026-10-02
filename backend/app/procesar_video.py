"""Etapa 4.5, tarea 4.5.3 — procesa un video real: lo baja de Supabase Storage, corre el
pipeline existente y escribe el resultado mínimo en la base.

Es el primer entrypoint que cierra el círculo completo de la arquitectura del apartado 4.5
de la tesis (Storage -> motor -> base) con datos reales, a diferencia de
``medir_contenedor.py`` (que sigue siendo el script de medición de tiempo/memoria de la
decisión 017, sobre un archivo montado a mano — no se toca acá).

**Alcance deliberadamente mínimo, no la Etapa 5.** Escribe ``reportes_biomecanicos`` y
``metricas`` con lo que el pipeline (ingesta -> pose -> E3 -> secuenciación) ya produce
hoy. NO calcula alertas (``engine/audit.py`` todavía no existe, es la tarea 5.1) ni el
puntaje de rendimiento (``reportes_sesion``, fórmula a congelar en la Etapa 5): dejarlos
vacíos en esta etapa es correcto, no una omisión.

**Corrección del 2/10/2026 (encontrada al investigar el tarea 4.5.4, pedido de Valentín):**
la versión anterior de este módulo tomaba ``fps_declarados`` de ``probe()`` como
``fps_efectivos`` directamente, con el comentario "los clips de la Fase B ya vienen a la
frecuencia real" — **FALSO**: son capturas Apple en cámara lenta, el contenedor declara
30 fps y la captura real es 240 fps (factor 8, confirmado por formato y huella en el
catálogo). Con el valor sin corregir, toda velocidad angular y el tamaño de la ventana de
secuenciación salían mal por un factor de 8 — no un caso límite, un resultado inválido en
cualquier clip de este corpus. Corregido: si el nombre de archivo tiene una fila en
``catalogo.csv`` (``KINETIQ_DATA_DIR``), se usa su ``factor_estimado``/``escala_temporal``
reales (ver ``_factor_de_catalogo``); si no (un upload real sin catálogo, el caso de la
Etapa 8), se usa ``factor=1.0`` sin inventar un valor, y la regla R1 decide si corresponde
análisis completo según la aptitud resultante — nunca se corre la secuenciación completa
por debajo de 120 fps efectivos. La detección automática de cámara lenta para uploads
sin catálogo sigue sin resolver (depende de la pantalla de carga real, Etapa 8); no se
inventa acá.

Uso:
    python -m app.procesar_video <video_id>

Requiere que el video ya exista como fila en la tabla ``videos`` (con ``sesion_id`` ->
``sesiones`` -> ``atletas.mano_dominante`` resueltos) y que ``ruta_almacenamiento`` apunte
a un objeto real del bucket "videos".
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    import resource  # solo Unix/Linux: es lo que corre en el contenedor y en Render.
except ImportError:
    resource = None  # Windows (desarrollo local): sin medición de RSS, no rompe el import.

from app.config import get_supabase_service_role_key, get_supabase_url
from app.engine.version import __version__ as VERSION_MOTOR

BACKEND_POSE = "mediapipe"
# fps efectivos mínimos para la secuenciación completa (R3/R1 vía AptitudFaseRapida):
# por debajo de esto ("solo_preparacion" o "rechazado" en engine/ingest.py) no se corre
# la secuenciación — mejor un video "parcial" sin resultado que un resultado calculado
# sobre una base temporal que la propia regla R1 considera insuficiente.
_UMBRAL_SECUENCIACION_FPS = 120.0
# decisión 017: model_complexity queda en 2 ("heavy") hasta nuevo aviso explícito de
# Valentín. El hallazgo de que 1 corta tiempo/memoria a la mitad sigue sin aplicarse.
MODEL_COMPLEXITY = 2
BUCKET = "videos"

_MANO_A_LADO = {"derecha": "der", "izquierda": "izq"}


def _rss_pico_mb() -> float | None:
    """RSS pico del proceso en MB — mismo método que ``medir_contenedor.py`` (decisión
    017), reutilizado acá para que la medición real de la tarea 4.5.4 (tiempo y memoria
    contra el plan gratuito de Render) salga del log del servicio, no de una lectura
    aparte del panel."""
    if resource is None:
        return None
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(pico / 1024, 1) if platform.system() == "Linux" else round(pico / 1_048_576, 1)


def _version_motor_id(admin, parametros_dsp: dict[str, Any]) -> str:
    """Reutiliza la fila de versiones_motor si ya existe una igual (version_motor +
    backend_pose): es una fila por VERSIÓN del motor, no una fila por análisis
    (apartado 4.4.6 de la tesis, "la materialización directa del requisito RNF-02").
    Crearla si no existe todavía."""
    existente = (
        admin.table("versiones_motor")
        .select("id")
        .eq("version_motor", VERSION_MOTOR)
        .eq("backend_pose", BACKEND_POSE)
        .limit(1)
        .execute()
        .data
    )
    if existente:
        return existente[0]["id"]
    creada = (
        admin.table("versiones_motor")
        .insert(
            {
                "version_motor": VERSION_MOTOR,
                "backend_pose": BACKEND_POSE,
                "version_modelo": f"model_complexity={MODEL_COMPLEXITY}",
                "parametros_dsp": parametros_dsp,
            }
        )
        .execute()
        .data[0]
    )
    return creada["id"]


def _factor_de_catalogo(nombre_archivo: str) -> tuple[float, bool, str]:
    """(factor, escala_conocida, origen_factor) para ``ingest.evaluar`` — ver
    ``app/engine/ingest.py::evaluar``: el factor de ralentización "casi nunca puede
    inferirse automáticamente (decisión 001): se pasa a mano o se toma del catálogo".

    Acá se toma del catálogo (``catalogo.csv`` en ``KINETIQ_DATA_DIR``) cuando el
    archivo tiene una fila — es el caso de todo clip de prueba de la Fase B, incluidos
    los que usan las pruebas de integración de este proyecto. Si no hay catálogo o el
    archivo no tiene fila (un upload real sin antecedente, el caso futuro de la Etapa 8),
    se devuelve factor=1.0 sin inventar nada: R1, más abajo en ``procesar_video``, se
    encarga de que un fps efectivo insuficiente no corra la secuenciación completa en
    vez de correrla con un factor adivinado.
    """
    try:
        from app.config import get_data_dir

        ruta_catalogo = get_data_dir() / "catalogo.csv"
    except Exception:
        return 1.0, False, "declarado"
    if not ruta_catalogo.is_file():
        return 1.0, False, "declarado"

    import csv

    with ruta_catalogo.open(encoding="utf-8", newline="") as f:
        fila = next((r for r in csv.DictReader(f) if r.get("archivo") == nombre_archivo), None)
    if fila is None or not fila.get("factor_estimado"):
        return 1.0, False, "declarado"

    try:
        factor = float(fila["factor_estimado"])
    except ValueError:
        return 1.0, False, "declarado"
    escala_conocida = fila.get("escala_temporal") == "conocida"
    return factor, escala_conocida, "catalogo"


def procesar_video(admin, video_id: str) -> dict[str, Any]:
    """Corre el pipeline completo sobre un video ya registrado y escribe el resultado en
    reportes_biomecanicos/metricas. Devuelve un resumen (también sirve como salida de log
    del contenedor). Si algo falla, deja videos.estado = 'fallido' antes de relanzar la
    excepción — regla de CLAUDE.md §6: un dato faltante es mejor que uno equivocado
    presentado como bueno; "el análisis quedó procesando para siempre" sería peor que
    "fallido" y visible."""
    video = (
        admin.table("videos")
        .select("id, ruta_almacenamiento, sesiones(encuadre, atletas(mano_dominante))")
        .eq("id", video_id)
        .single()
        .execute()
        .data
    )
    mano_dominante = video["sesiones"]["atletas"]["mano_dominante"]
    lado_dominante = _MANO_A_LADO[mano_dominante]

    admin.table("videos").update({"estado": "procesando"}).eq("id", video_id).execute()

    t_inicio = time.monotonic()
    try:
        contenido = admin.storage.from_(BUCKET).download(video["ruta_almacenamiento"])

        with tempfile.TemporaryDirectory() as directorio_tmp:
            clip = Path(directorio_tmp) / Path(video["ruta_almacenamiento"]).name
            clip.write_bytes(contenido)
            # Soltar los bytes del clip ANTES de la inferencia: si no, quedan vivos en
            # memoria (referenciados por esta variable) durante toda la inferencia de
            # MediaPipe, superpuestos con sus propios buffers — el pico de RSS mide el
            # máximo del proceso completo, así que esta superposición es pura cuenta
            # doble (tarea 4.5.4: investigación del salto de RSS de 426 a 480 MB en
            # Render, decisión 017).
            del contenido

            from app.engine import ingest
            from app.engine.ingest import iterar_fotogramas, probe

            md = probe(clip)
            factor, escala_conocida, origen_factor = _factor_de_catalogo(clip.name)
            ingesta = ingest.evaluar(
                md, factor=factor, escala_conocida=escala_conocida, origen_factor=origen_factor
            )

            if ingesta.fps_efectivos < _UMBRAL_SECUENCIACION_FPS:
                # R1: por debajo de 120 fps efectivos solo se habilita la fase de
                # preparación, que este script todavía no implementa (Etapa 5). No se
                # corre la secuenciación completa sobre una base temporal que la propia
                # regla considera insuficiente (R3: un dato faltante es mejor que uno
                # equivocado presentado como bueno).
                admin.table("videos").update(
                    {
                        "estado": "parcial",
                        "fps_real": ingesta.fps_efectivos,
                        "total_fotogramas": md.nb_frames,
                        "duracion_s": md.duracion_s,
                        "resolucion": f"{md.ancho}x{md.alto}",
                        "apto_fase_rapida": False,
                    }
                ).eq("id", video_id).execute()
                segundos_totales = round(time.monotonic() - t_inicio, 2)
                print(
                    f"[procesar_video] {video_id}: fps efectivos {ingesta.fps_efectivos:.1f} "
                    f"(aptitud {ingesta.aptitud.value}) < {_UMBRAL_SECUENCIACION_FPS:.0f} — "
                    "no se corre la secuenciación completa (R1)."
                )
                return {
                    "video_id": video_id,
                    "reporte_id": None,
                    "estado": "parcial",
                    "orden_observado": None,
                    "metricas_insertadas": 0,
                    "segundos_totales": segundos_totales,
                    "rss_pico_mb": _rss_pico_mb(),
                    "motivo": f"fps efectivos insuficientes para R1 ({ingesta.aptitud.value})",
                }

            from app.engine.pose.mediapipe_backend import MediaPipeBackend

            with MediaPipeBackend(model_complexity=MODEL_COMPLEXITY) as backend:
                seq = backend.procesar(
                    iterar_fotogramas(clip),
                    ancho=md.ancho,
                    alto=md.alto,
                    fps_efectivos=ingesta.fps_efectivos,
                )

        from app.engine.pipeline import procesar_e3

        filt = procesar_e3(seq)

        from app.engine.sequencing import secuenciar

        resultados, _resumen = secuenciar(
            filt.secuencia,
            lado_dominante=lado_dominante,
            tramos_excluidos=filt.tramos_excluidos,
            brazo_via="codo",
            ancla="torso",
        )
        repeticion = resultados[0] if resultados else None

        version_motor_id = _version_motor_id(
            admin,
            {"filtro": "butterworth_fase_cero", "orden": 4, "corte_hz": filt.corte_hz},
        )

        orden_observado = (
            [s.value for s in repeticion.orden_observado]
            if repeticion and repeticion.orden_observado
            else None
        )

        reporte = (
            admin.table("reportes_biomecanicos")
            .insert(
                {
                    "video_id": video_id,
                    "version_motor_id": version_motor_id,
                    "orden_picos_observado": orden_observado,
                    "secuencia_correcta": repeticion.correcto if repeticion else None,
                    "corte_filtro_hz": filt.corte_hz,
                    "cobertura_auditable_pct": round(seq.cobertura * 100, 2),
                }
            )
            .execute()
            .data[0]
        )

        metricas_insertadas = 0
        if repeticion:
            for segmento, pico in repeticion.picos.items():
                # Un pico ausente (None) no se estima ni se rellena (R3): sin fila, no con un
                # valor inventado ni con auditable=False y valor=null. Lo mismo para un pico
                # presente pero no finito (NaN/infinito): no es un dato, es un artefacto
                # numérico (p. ej. un tramo con duración casi cero en el cálculo de ω) — ni
                # json ni la columna numeric de Postgres lo aceptan, y presentarlo igual
                # violaría R3 ("un dato equivocado es peor que uno faltante").
                if pico is None:
                    continue
                if not math.isfinite(pico.velocidad):
                    print(
                        f"  [aviso] pico de {segmento.value} no finito ({pico.velocidad!r}), "
                        "se omite la métrica (no es un bug de este script, revisar el pipeline)"
                    )
                    continue
                admin.table("metricas").insert(
                    {
                        "reporte_id": reporte["id"],
                        "segmento": segmento.value,
                        "tipo": "velocidad_pico",
                        "valor": pico.velocidad,
                        "unidad": "grados/s",
                        "auditable": True,
                    }
                ).execute()
                metricas_insertadas += 1

        estado_final = "completado" if (repeticion and repeticion.auditable) else "parcial"
        admin.table("videos").update(
            {
                "estado": estado_final,
                "fps_real": ingesta.fps_efectivos,
                "total_fotogramas": md.nb_frames,
                "duracion_s": md.duracion_s,
                "resolucion": f"{md.ancho}x{md.alto}",
                "apto_fase_rapida": ingesta.aptitud.value in ("completo", "reducido"),
            }
        ).eq("id", video_id).execute()

        segundos_totales = round(time.monotonic() - t_inicio, 2)
        rss_pico_mb = _rss_pico_mb()
        print(
            f"[procesar_video] {video_id}: {segundos_totales} s, "
            f"RSS pico {rss_pico_mb if rss_pico_mb is not None else 'no disponible'} MB "
            f"(tarea 4.5.4: esto es lo que hay que leer del log de Render para decidir "
            f"Free vs Starter)"
        )

        return {
            "video_id": video_id,
            "reporte_id": reporte["id"],
            "estado": estado_final,
            "orden_observado": orden_observado,
            "metricas_insertadas": metricas_insertadas,
            "segundos_totales": segundos_totales,
            "rss_pico_mb": rss_pico_mb,
        }
    except Exception:
        admin.table("videos").update({"estado": "fallido"}).eq("id", video_id).execute()
        raise


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        description="Baja un video de Supabase Storage, corre el pipeline y escribe el "
        "resultado (reportes_biomecanicos + metricas) en la base."
    )
    ap.add_argument("video_id", help="uuid de una fila ya existente en la tabla videos")
    args = ap.parse_args(argv)

    from supabase import create_client

    admin = create_client(get_supabase_url(), get_supabase_service_role_key())
    resultado = procesar_video(admin, args.video_id)
    print(json.dumps(resultado, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
