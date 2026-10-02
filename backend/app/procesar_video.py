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

**Simplificación deliberada frente al flujo real de la Etapa 8.** Toma ``fps_declarados``
de ``probe()`` como ``fps_efectivos`` directamente, igual que ``medir_contenedor.py``: los
clips de la Fase B ya vienen a la frecuencia real. La clasificación completa de aptitud
(factor de cámara lenta, origen del factor, regla R1) es del catalogador
(``app/catalogador.py``) y de la futura pantalla de carga (Etapa 8); no se reimplementa acá.

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
import sys
import tempfile
from pathlib import Path
from typing import Any

from app.config import get_supabase_service_role_key, get_supabase_url
from app.engine.version import __version__ as VERSION_MOTOR

BACKEND_POSE = "mediapipe"
# decisión 017: model_complexity queda en 2 ("heavy") hasta nuevo aviso explícito de
# Valentín. El hallazgo de que 1 corta tiempo/memoria a la mitad sigue sin aplicarse.
MODEL_COMPLEXITY = 2
BUCKET = "videos"

_MANO_A_LADO = {"derecha": "der", "izquierda": "izq"}


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

    try:
        contenido = admin.storage.from_(BUCKET).download(video["ruta_almacenamiento"])

        with tempfile.TemporaryDirectory() as directorio_tmp:
            clip = Path(directorio_tmp) / Path(video["ruta_almacenamiento"]).name
            clip.write_bytes(contenido)

            from app.engine.ingest import iterar_fotogramas, probe

            md = probe(clip)

            from app.engine.pose.mediapipe_backend import MediaPipeBackend

            with MediaPipeBackend(model_complexity=MODEL_COMPLEXITY) as backend:
                seq = backend.procesar(
                    iterar_fotogramas(clip),
                    ancho=md.ancho,
                    alto=md.alto,
                    fps_efectivos=md.fps_declarados,
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
                "fps_real": md.fps_declarados,
                "total_fotogramas": md.nb_frames,
                "duracion_s": md.duracion_s,
                "resolucion": f"{md.ancho}x{md.alto}",
                "apto_fase_rapida": md.fps_declarados >= 120,
            }
        ).eq("id", video_id).execute()

        return {
            "video_id": video_id,
            "reporte_id": reporte["id"],
            "estado": estado_final,
            "orden_observado": orden_observado,
            "metricas_insertadas": metricas_insertadas,
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
