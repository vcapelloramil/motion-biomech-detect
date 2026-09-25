"""E4 — Analiza un clip de punta a punta: pose (caché) → E3 → E4 (plan, tareas 4.1–4.6b).

Validación cualitativa temprana sobre el corpus público. Uso (desde backend/):
    python -m app.analizar --clip zverev_saque_lateral_01.mp4
    python -m app.analizar --clip reves_lateral_01.mp4 --lado izq
    python -m app.analizar --clip X --manual 0.0:1.2,1.5:2.8
    python -m app.analizar --clip X_rep01.mov --clip-completo   # clip pre-cortado = 1 repetición
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from app.catalogador import CARPETAS_EXCLUIDAS, FASES_POR_DEFECTO
from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.sequencing import secuenciar
from app.engine.segmentos_corporales import ORDEN_ESPERADO, validar_lado


def _campo_de(catalogo: Path, nombre: str, campo: str) -> str | None:
    if not catalogo.is_file():
        return None
    with catalogo.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            if fila.get("archivo") == nombre:
                v = (fila.get(campo) or "").strip().lower()
                return v or None
    return None


def lado_dominante_de(catalogo: Path, nombre: str) -> str | None:
    return _campo_de(catalogo, nombre, "lado_dominante")


def es_corpus_publico(catalogo: Path, nombre: str) -> bool:
    """True salvo que el catálogo marque el clip como material propio.

    Si no se sabe la fuente se asume público: el caveat de más es el error seguro.
    """
    return _campo_de(catalogo, nombre, "fuente") != "propio"


def _parse_manual(txt: str | None) -> list[tuple[float, float]] | None:
    if not txt:
        return None
    ventanas = []
    for par in txt.split(","):
        d, h = par.split(":")
        ventanas.append((float(d), float(h)))
    return ventanas


def _fmt_orden(orden) -> str:
    return " → ".join(s.value for s in orden) if orden else "—"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Analiza un clip (E3 + E4).")
    parser.add_argument("--clip", required=True, help="Nombre del archivo de video.")
    parser.add_argument("--lado", choices=["der", "izq"], default=None,
                        help="Lado dominante; si se omite, se lee de catalogo.csv.")
    parser.add_argument("--manual", default=None,
                        help="Ventanas de repetición 'desde:hasta' en segundos, separadas por coma.")
    parser.add_argument("--clip-completo", action="store_true",
                        help="Todo el clip es UNA repetición (material pre-cortado, p. ej. Fase B); "
                             "no se intenta segmentar. Excluye --manual.")
    parser.add_argument("--brazo-via", default="codo", choices=["codo", "muneca"],
                        help="Articulación distal del segmento 'brazo' (default: codo).")
    parser.add_argument("--backend", default="mediapipe", choices=["mediapipe"])
    args = parser.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir

    base = get_data_dir()
    catalogo = base / "catalogo.csv"
    video = next(
        (p for fase in FASES_POR_DEFECTO for p in (base / fase).rglob(args.clip)
         if p.is_file() and not (CARPETAS_EXCLUIDAS & set(p.relative_to(base / fase).parts))),
        None,
    )
    if video is None:
        print(f"No se encontró {args.clip} bajo {', '.join(FASES_POR_DEFECTO)} de {base}.")
        return 1

    lado = args.lado or lado_dominante_de(catalogo, args.clip)
    if not lado:
        print(
            f"No hay lado dominante para {args.clip}: completá la columna "
            f"'lado_dominante' en catalogo.csv o pasá --lado der|izq. "
            f"(No hay valor por defecto a propósito: un zurdo con el default 'der' "
            f"mediría el brazo equivocado sin ningún error.)"
        )
        return 2
    validar_lado(lado)

    backend = MediaPipeBackend()
    seq = pose_cache.cargar_si_vigente(get_cache_dir(), video, backend.id, backend.config_hash)
    if seq is None:
        print(f"No hay pose cacheada para {args.clip}. Corré primero:  python -m app.extraer_pose --clip {args.clip}")
        return 3

    filt = procesar_e3(seq)
    resultados, resumen = secuenciar(
        filt.secuencia,
        lado_dominante=lado,
        tramos_excluidos=filt.tramos_excluidos,
        brazo_via=args.brazo_via,
        manual=_parse_manual(args.manual),
        clip_completo=args.clip_completo,
        corpus_publico=es_corpus_publico(catalogo, args.clip),
    )

    print(f"clip: {args.clip}   lado dominante: {lado}   brazo vía: {args.brazo_via}")
    print(f"fps efectivos: {seq.fps_efectivos:.1f}   corte del filtro: {filt.corte_hz:.1f} Hz "
          f"({filt.metodo_corte})   orden esperado: {_fmt_orden(ORDEN_ESPERADO)}")
    print("-" * 78)
    for r in resultados:
        v = r.ventana
        print(f"repetición {r.indice}  [{v.desde_s:.2f}–{v.hasta_s:.2f} s]")
        for seg, p in r.picos.items():
            if p and p.auditable:
                print(f"    {seg.value:7} pico @ {p.instante_s:.3f} s   {p.velocidad:8.1f} °/s")
            else:
                print(f"    {seg.value:7} sin pico auditable ({p.motivo if p else '—'})")
        estado = "correcto" if r.correcto else ("incorrecto" if r.correcto is False else "no auditable")
        print(f"    orden observado: {_fmt_orden(r.orden_observado)}   → {estado}")
    print("-" * 78)
    print(f"repeticiones: {resumen.repeticiones_evaluadas} evaluadas, "
          f"{resumen.repeticiones_auditables} auditables, "
          f"{resumen.repeticiones_correctas} correctas")
    print(f"orden predominante: {_fmt_orden(resumen.orden_predominante)}")
    if resumen.dispersion_instante_pico_torso_ms is not None:
        print(f"dispersión del instante del pico de torso: "
              f"{resumen.dispersion_instante_pico_torso_ms:.1f} ms")
    if resumen.nota:
        print(f"\n[nota] {resumen.nota}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
