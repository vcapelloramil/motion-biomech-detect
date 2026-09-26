"""Resumen legible (Markdown) de la medición del Criterio 1, generado desde los JSON de resultados.

Solo formatea: no vuelve a medir ni cambia ninguna regla (decisión 014). Incluye, aparte y rotulado como
DESCRIPTIVO (no pre-registrado), la separación pelvis-torso y torso-brazo por grupo.

Uso (desde backend/):
    python -m app.resumen_criterio1 ../docs/resultados/criterio1-sesion-2.json \\
        ../docs/resultados/criterio1-sesion-1-replica-exploratoria.json --salida ../docs/resultados/criterio1-resumen.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def _f(x, nd=2) -> str:
    return "-" if x is None else f"{x:.{nd}f}"


def _ic(x) -> str:
    return "-" if not x else f"[{x[0]:.2f}–{x[1]:.2f}]"


def tabla_tau(resultado_tau: dict) -> list[str]:
    filas = ["| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |",
             "| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |"]
    for g, e in resultado_tau.items():
        for conj, x in e.items():
            filas.append(
                f"| {g.replace('|', ' · ')} | {'par pelvis-torso' if conj.startswith('par') else 'cadena'} | {x['n']} | {x['validas']} | {x['ordenables']} | "
                f"{_f(x['1a_sobre_todas'])} {_ic(x['1a_sobre_todas_ic95'])} | {_f(x['1a_sobre_validas'])} | "
                f"{_f(x['1b_repetibilidad'])} (`{x['1b_orden_modal'] or '-'}`) | {_f(x['1c_coincidencia'])} | "
                f"{'**cumple**' if x['criterio_1_cumplido'] else 'no cumple'} |")
    return filas


def descriptivo(repeticiones: list[dict]) -> list[str]:
    g = defaultdict(list)
    for r in repeticiones:
        g[(r["encuadre"], r["gesto"])].append(r["frames"])
    filas = ["| grupo | n | mediana \\|pelvis−torso\\| (fot.) | \\|Δ\\| ≤ 1 fot. | mediana torso→brazo (fot.) | brazo después | \\|Δ\\| > 1 fot. |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for k, L in sorted(g.items()):
        pt = [abs(x["t"] - x["p"]) for x in L if x["p"] is not None and x["t"] is not None]
        tb = [x["b"] - x["t"] for x in L if x["b"] is not None and x["t"] is not None]
        filas.append(
            f"| {k[0]} · {k[1]} | {len(L)} | {np.median(pt) if pt else float('nan'):.1f} | {sum(v <= 1 for v in pt)}/{len(pt)} | "
            f"{np.median(tb) if tb else float('nan'):.1f} | {sum(v > 0 for v in tb)}/{len(tb)} | {sum(abs(v) > 1 for v in tb)}/{len(tb)} |")
    return filas


def generar(jsons: list[dict]) -> str:
    out = ["# Criterio 1 — resumen de la medición (decisión 014)", "",
           "Generado por `python -m app.resumen_criterio1` desde los JSON de `docs/resultados/`. 1 fotograma = 4,17 ms.",
           "**1a/1b** son la regla del criterio original (≥ 0,8 cada una); **1c** (coincidencia con el orden esperado) se",
           "informa **aparte**, sin umbral, y no cuenta como éxito ni fallo. Para el brazo, 1c no es comparable con la",
           "literatura (decisión 011).", ""]
    for J in jsons:
        out += [f"## Sesión {J['sesion']} — {J['rol']}", "",
                f"Motor `{J['version_motor']}`, commit `{J['commit'][:10]}`, árbol sucio: {J['arbol_sucio']}.", ""]
        for tau in J["taus"]:
            etq = "PRIMARIA" if tau == J["tau_primaria"] else "sensibilidad"
            out += [f"### τ = {tau} fotograma(s) ({etq})", ""] + tabla_tau(J["resultado_por_tau"][str(tau)]) + [""]
        out += ["### Complemento DESCRIPTIVO (no pre-registrado)", ""] + descriptivo(J["repeticiones"]) + [""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Resumen Markdown del Criterio 1.")
    ap.add_argument("jsons", nargs="+", type=Path)
    ap.add_argument("--salida", type=Path, required=True)
    args = ap.parse_args(argv)
    datos = [json.loads(p.read_text(encoding="utf-8")) for p in args.jsons]
    args.salida.write_text(generar(datos), encoding="utf-8")
    print(f"Escrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
