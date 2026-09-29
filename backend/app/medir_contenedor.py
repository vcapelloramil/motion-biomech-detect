"""Etapa 4.5, tarea 4.5.3 — mide tiempo y memoria pico del pipeline dentro de un contenedor.

Corre el pipeline completo (ingesta -> pose -> E3 -> secuenciación anclada al torso) sobre UN clip,
igual que hace `medicion_criterio1.medir_clip`, pero como script independiente que no depende del
catálogo ni de `KINETIQ_DATA_DIR`: recibe la ruta del video y el lado dominante por línea de comandos,
para poder correr dentro de un contenedor con un solo archivo montado.

La memoria pico se mide DESDE ADENTRO del proceso con `resource.getrusage` (RSS máximo del proceso;
en Linux, `ru_maxrss` ya viene en kilobytes) — es la magnitud correcta para decidir un plan de
contenedor por memoria, más fina que lo que reporta `docker stats` por muestreo. Si el proceso se queda
sin memoria, el sistema operativo lo mata (OOM) antes de que llegue a imprimir nada: eso se ve afuera,
como código de salida 137, no en la salida de este script.

Uso (dentro del contenedor):
    python -m app.medir_contenedor /datos/clip.mov --lado der [--backend mediapipe|fake]
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

try:
    import resource  # solo Unix/Linux: es lo que corre dentro del contenedor.
except ImportError:
    resource = None  # Windows (desarrollo local): sin medición de RSS, no rompe el import.


def _rss_pico_mb() -> float | None:
    """RSS pico del proceso, en MB. None si no se puede medir (p. ej. en Windows)."""
    if resource is None:
        return None
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: ru_maxrss en KB. macOS: en bytes. El contenedor de destino es Linux.
    return round(pico / 1024, 1) if platform.system() == "Linux" else round(pico / 1_048_576, 1)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Mide tiempo y memoria del pipeline sobre un clip, en contenedor.")
    ap.add_argument("clip", type=Path)
    ap.add_argument("--lado", choices=["der", "izq"], default="der")
    ap.add_argument("--backend", choices=["mediapipe", "fake"], default="mediapipe")
    ap.add_argument("--model-complexity", type=int, choices=[0, 1, 2], default=2,
                    help="0=lite, 1=full, 2=heavy (default, el que usa el motor hoy). Compara velocidad/memoria "
                         "contra cobertura: --model-complexity 1 puede ser la diferencia entre el plan de "
                         "contenedor de 7 o de 25 USD/mes.")
    ap.add_argument("--reducir-resolucion", type=int, default=None, metavar="ANCHO",
                    help="Reescala cada fotograma a este ancho (alto proporcional) antes de la pose. "
                         "Reduce memoria y tiempo a costa de precisión; no implementado sobre 'fake'.")
    ap.add_argument("--salida", type=Path, default=None, help="JSON con los tiempos/memoria por etapa.")
    args = ap.parse_args(argv)

    if not args.clip.is_file():
        print(f"No existe el clip: {args.clip}")
        return 2

    hitos: list[dict] = []

    def marca(etapa: str, t0: float) -> float:
        ahora = time.monotonic()
        pico_mb = _rss_pico_mb()
        hitos.append({"etapa": etapa, "segundos_etapa": round(ahora - t0, 2), "rss_pico_mb": pico_mb})
        pico_txt = f"{pico_mb:.1f} MB" if pico_mb is not None else "no disponible (Windows)"
        print(f"[{etapa}] +{ahora - t0:.2f}s | RSS pico hasta ahora: {pico_txt}", flush=True)
        return ahora

    t_inicio = time.monotonic()
    t = t_inicio

    from app.engine.ingest import probe
    md = probe(args.clip)
    t = marca("ingesta (probe)", t)

    if args.backend == "mediapipe":
        from app.engine.pose.mediapipe_backend import MediaPipeBackend
        backend = MediaPipeBackend(model_complexity=args.model_complexity)
    else:
        from app.engine.pose.fake_backend import FakeBackend
        backend = FakeBackend(dims=3)
    t = marca(f"cargar backend de pose ({args.backend}, model_complexity={args.model_complexity})", t)

    from app.engine.ingest import iterar_fotogramas
    fotogramas = iterar_fotogramas(args.clip)
    if args.reducir_resolucion:
        # Se resamplea el FOTOGRAMA que ve MediaPipe, pero se sigue declarando ancho/alto del video
        # ORIGINAL a procesar() (más abajo): las coordenadas que devuelve MediaPipe son normalizadas
        # [0,1] y no dependen de la resolución de entrada, así que multiplicarlas por el tamaño
        # original sigue dando la posición correcta en píxeles del video real.
        import cv2

        ancho_reducido = args.reducir_resolucion
        alto_reducido = round(md.alto * ancho_reducido / md.ancho)

        def _reescalar(frames):
            for f in frames:
                yield cv2.resize(f, (ancho_reducido, alto_reducido), interpolation=cv2.INTER_AREA)

        fotogramas = _reescalar(fotogramas)
        t = marca(f"(reducción de resolución activa: {ancho_reducido}x{alto_reducido})", t)

    with backend:
        seq = backend.procesar(
            fotogramas, ancho=md.ancho, alto=md.alto,
            fps_efectivos=md.fps_declarados,  # el clip de prueba ya viene a la frecuencia real
        )
    t = marca(f"inferencia de pose ({seq.n_frames} fotogramas)", t)
    cobertura_general = round(seq.cobertura, 4)
    print(f"  cobertura (fracción de fotogramas con persona detectada): {cobertura_general:.1%}")

    from app.engine.pipeline import procesar_e3
    filt = procesar_e3(seq)
    t = marca("E3 (filtrado de fase cero)", t)

    from app.engine.sequencing import secuenciar
    resultados, resumen = secuenciar(
        filt.secuencia, lado_dominante=args.lado, tramos_excluidos=filt.tramos_excluidos,
        brazo_via="codo", ancla="torso",
    )
    t = marca("E4 (secuenciación)", t)

    total_s = time.monotonic() - t_inicio
    pico_final_mb = _rss_pico_mb()
    pico_final_txt = f"{pico_final_mb:.1f} MB" if pico_final_mb is not None else "no disponible (Windows)"
    print(f"\nTOTAL: {total_s:.2f} s | RSS pico del proceso: {pico_final_txt}")
    if resultados and resultados[0].orden_observado:
        print("orden observado:", " > ".join(s.value for s in resultados[0].orden_observado))

    salida = {
        "clip": str(args.clip), "tamano_mb": round(args.clip.stat().st_size / 1_048_576, 1),
        "backend": args.backend, "model_complexity": args.model_complexity,
        "reducir_resolucion": args.reducir_resolucion, "cobertura": cobertura_general,
        "fps_declarados": md.fps_declarados, "n_frames": seq.n_frames,
        "python": platform.python_version(), "plataforma": platform.platform(),
        "total_segundos": round(total_s, 2), "rss_pico_mb": pico_final_mb,
        "hitos": hitos,
    }
    if args.salida:
        args.salida.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Escrito: {args.salida}")
    else:
        print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
