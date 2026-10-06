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

**Corrección del 2/10/2026, en dos pasos (decisión 020):**

1. Primer hallazgo: la versión original tomaba ``fps_declarados`` de ``probe()`` como
   ``fps_efectivos`` directamente, con el comentario "los clips de la Fase B ya vienen a
   la frecuencia real" — **FALSO**: son capturas Apple en cámara lenta, el contenedor
   declara 30 fps y la captura real es 240 fps. Primer arreglo (buscar el factor en
   ``catalogo.csv`` por nombre de archivo) servía para el corpus de prueba, pero NO para
   producción: un usuario sube "IMG_4012.MOV" sin fila de catálogo, y el archivo solo no
   alcanza para saber si es cámara lenta (confirmado por Valentín: el contenedor declara
   30 fps sea cual sea el recorte o el dispositivo donde se recortó).
2. **Diseño final:** el usuario declara el modo de captura al cargar, una vez por sesión
   (``sesiones.modo_captura``: ``normal`` | ``camara_lenta_120`` | ``camara_lenta_240`` —
   especificación de frontend §5). El motor combina esa declaración con el fps real del
   contenedor (normalizado NTSC, ``engine.ingest.normalizar_fps``) — ver
   ``_factor_y_motivo``. ``normal`` nunca falla (significa "sin cámara lenta": los fps
   efectivos son los del contenedor, sean los que sean — hay teléfonos que graban 120+ fps
   en modo normal). ``camara_lenta_120``/``camara_lenta_240`` fallan con
   ``videos.motivo_fallo = 'modo_captura_incompatible'`` (código cerrado, no texto libre —
   el texto en lenguaje llano para el usuario lo resuelve el frontend, R2) si el factor
   resultante no es un entero ≥ 1: nunca se adivina en silencio (R3). La detección
   automática de cámara lenta sin que el usuario la declare sigue sin resolver — no hace
   falta: el usuario siempre la declara.

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


_FPS_OBJETIVO_POR_MODO = {"camara_lenta_240": 240.0, "camara_lenta_120": 120.0}
_TOLERANCIA_FACTOR_ENTERO = 1e-6

# Códigos cerrados de videos.motivo_fallo (migración 20261002000000). El texto en
# lenguaje llano para el jugador lo resuelve el frontend (R2); acá solo el código.
MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE = "modo_captura_incompatible"


def _factor_y_motivo(modo_captura: str, fps_contenedor: float) -> tuple[float, bool, str, str | None]:
    """(factor, escala_conocida, origen_factor, codigo_motivo_fallo) para
    ``ingest.evaluar``. ``codigo_motivo_fallo`` es ``None`` si la combinación cierra; si
    no, es uno de los códigos cerrados de ``videos.motivo_fallo`` — el detalle técnico
    (fps del contenedor, factor calculado) se imprime en el log, no se guarda en la
    columna ni se le muestra al usuario tal cual (R2/R3, decisión 020, ajuste de
    Valentín).

    ``normal`` NUNCA falla acá: significa "sin cámara lenta", así que los fps efectivos
    son los del contenedor tal cual, sean los que sean (hay teléfonos que graban 120+ fps
    en modo normal, y eso es válido). La regla R1, en ``procesar_video``, es la que
    decide si esos fps alcanzan para la secuenciación completa — no esta función.
    """
    from app.engine.ingest import normalizar_fps  # import perezoso: ver nota en procesar_video.

    fps_norm = normalizar_fps(fps_contenedor)

    if modo_captura == "normal":
        return 1.0, True, "declaracion_usuario", None

    objetivo = _FPS_OBJETIVO_POR_MODO[modo_captura]
    factor = objetivo / fps_norm
    if round(factor) < 1 or abs(factor - round(factor)) > _TOLERANCIA_FACTOR_ENTERO:
        print(
            f"[procesar_video] {MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE}: "
            f"modo_captura={modo_captura!r} (objetivo {objetivo:.0f} fps), "
            f"contenedor={fps_norm:.1f} fps, factor calculado={factor:.4f} "
            "(no es un múltiplo entero ≥ 1)."
        )
        return 1.0, False, "declaracion_usuario", MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE
    return float(round(factor)), True, "declaracion_usuario", None


def procesar_video(admin, video_id: str) -> dict[str, Any]:
    """Corre el pipeline completo sobre un video ya registrado y escribe el resultado en
    reportes_biomecanicos/metricas. Devuelve un resumen (también sirve como salida de log
    del contenedor). Si algo falla, deja videos.estado = 'fallido' antes de relanzar la
    excepción — regla de CLAUDE.md §6: un dato faltante es mejor que uno equivocado
    presentado como bueno; "el análisis quedó procesando para siempre" sería peor que
    "fallido" y visible."""
    video = (
        admin.table("videos")
        .select(
            "id, ruta_almacenamiento, "
            "sesiones(encuadre, modo_captura, atletas(mano_dominante))"
        )
        .eq("id", video_id)
        .single()
        .execute()
        .data
    )
    mano_dominante = video["sesiones"]["atletas"]["mano_dominante"]
    lado_dominante = _MANO_A_LADO[mano_dominante]
    modo_captura = video["sesiones"]["modo_captura"]

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
            factor, escala_conocida, origen_factor, codigo_motivo_fallo = _factor_y_motivo(
                modo_captura, md.fps_declarados
            )

            if codigo_motivo_fallo is not None:
                # No se adivina en silencio (R3): modo_captura declarado no cierra con el
                # fps del contenedor. fps_real y apto_fase_rapida quedan null — no se
                # guarda un valor que ya se demostró no confiable.
                admin.table("videos").update(
                    {
                        "estado": "fallido",
                        "motivo_fallo": codigo_motivo_fallo,
                        "total_fotogramas": md.nb_frames,
                        "duracion_s": md.duracion_s,
                        "resolucion": f"{md.ancho}x{md.alto}",
                    }
                ).eq("id", video_id).execute()
                segundos_totales = round(time.monotonic() - t_inicio, 2)
                return {
                    "video_id": video_id,
                    "reporte_id": None,
                    "estado": "fallido",
                    "orden_observado": None,
                    "metricas_insertadas": 0,
                    "segundos_totales": segundos_totales,
                    "rss_pico_mb": _rss_pico_mb(),
                    "motivo_fallo": codigo_motivo_fallo,
                }

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
                    # Trazabilidad (R4) de la escala temporal, congelada en el reporte: lo que
                    # declaró el usuario (sesiones.modo_captura es editable después), el factor
                    # que resultó de combinarlo con el contenedor, y su origen.
                    "modo_captura": modo_captura,
                    "factor_ralentizacion": factor,
                    "escala_temporal_conocida": ingesta.escala_temporal_conocida,
                    "origen_factor": origen_factor,
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
