"""Diagnóstico de solo lectura: por qué el pico de BRAZO no sale auditable, separado por
gesto, encuadre y lado de cámara respecto de la mano dominante — pedido de Valentín al
cerrar la tarea 4.5.4 (el aviso "pico de brazo no finito (nan)" de
``app/procesar_video.py`` ya apareció dos veces sobre clips reales de la Fase B).

**Hallazgo de lectura de código, antes de medir nada** (``engine/sequencing.py``,
``evaluar_repeticion``): ``PicoSegmento.velocidad = NaN`` es el valor CENTINELA que el
motor ya usa para TODO pico con ``auditable=False``, sea cual sea la causa — no es, por sí
solo, evidencia de un problema de cálculo. La causa real vive en ``PicoSegmento.motivo``,
que viene de ``detectar_pico`` y tiene cuatro valores posibles (ver ``_clasificar_motivo``
abajo). Este script no "descubre" el NaN: lo explica, clasificando el motivo real detrás
de cada caso.

NO modifica nada del motor ni el catálogo: misma invocación que ``medicion_criterio1.py``
(ventana anclada al torso, una repetición por clip — coherente con que cada fila del
catálogo con "_rep" en el nombre ya es un solo golpe —, brazo vía codo) sobre la pose ya
cacheada.

Uso (desde backend/):
    python -m app.diagnostico_brazo_corpus [--sesion {1,2}] [--salida ruta.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from app.config import get_cache_dir, get_data_dir
from app.diagnosticos_e3 import _buscar_video, _catalogo, fechas_propias, lado_cercano, sesion_de
from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import MARGEN_ANCLA_S, secuenciar

GRUPOS = ("perfil", "trescuartos")

# Las cuatro salidas reales de detectar_pico (sequencing.py:138-160), transcriptas tal
# cual están en el código — no se inventa ninguna categoría nueva, solo se agrupan.
_MOTIVO_SERIE_CORTA = "serie demasiado corta o incompleta"
_MOTIVO_SIN_PROMINENCIA = "sin picos marcados por encima de la prominencia mínima"
_MOTIVO_TRAMO_EXCLUIDO = "el pico cae en un tramo no auditable"
_PREFIJO_IMPLAUSIBLE = "velocidad implausible"


def _clasificar_motivo(motivo: str | None) -> str:
    """Mapea el motivo real de detectar_pico a la categoría que pidió Valentín
    (oclusión / problema de cálculo), sin forzar los casos ambiguos a ninguna de las dos."""
    if motivo is None:
        return "auditable"
    if motivo == _MOTIVO_TRAMO_EXCLUIDO:
        # El pico cae en un tramo que E3/validation ya marcó no auditable (baja
        # confianza, salto imposible, inversión de z): oclusión, documentada en
        # la decisión 013.
        return "oclusion"
    if motivo == _MOTIVO_SERIE_CORTA:
        # Menos de 5 fotogramas válidos (no-NaN) en la ventana: mismo origen que la
        # oclusión (cobertura insuficiente), solo que tan extremo que ni siquiera hay
        # serie para buscar un pico.
        return "oclusion"
    if motivo.startswith(_PREFIJO_IMPLAUSIBLE):
        # El propio motor lo etiqueta "probable error de detección": una velocidad
        # finita mayor al techo de plausibilidad de Fleisig x3, no un problema de
        # confianza de los puntos. Es la categoría más cercana a lo que Valentín
        # describe como "problema de cálculo".
        return "problema_de_calculo"
    if motivo == _MOTIVO_SIN_PROMINENCIA:
        # Hay serie suficiente y ningún valor supera el techo, pero ningún máximo local
        # se destaca lo suficiente (señal plana/ruidosa): no es oclusión (no viene de
        # tramos excluidos) ni un NaN/infinito de cálculo. Se reporta aparte a
        # propósito, sin forzarlo a ninguna de las dos categorías pedidas.
        return "senal_plana_sin_pico_claro"
    return "otro_no_catalogado"  # no debería pasar nunca; si aparece, es la señal real de un motivo nuevo


def diagnosticar(sesion: int | None) -> dict:
    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    backend = MediaPipeBackend()

    clips = sorted(
        n
        for n, r in cat.items()
        if r.get("fuente") == "propio"
        and "_rep" in n
        and str(r.get("fps_efectivos")).strip() in ("240", "240.0")  # solo el conjunto a 240 fps
        and r.get("angulo") in GRUPOS
        and (sesion is None or sesion_de(n, fechas) == sesion)
    )

    filas: list[dict] = []
    sin_pose: list[str] = []

    for nombre in clips:
        fila_cat = cat[nombre]
        video = _buscar_video(base, nombre)
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), video, backend.id, backend.config_hash)
        if seq is None:
            sin_pose.append(nombre)
            continue

        lado_dominante = fila_cat["lado_dominante"]
        # Lado de cámara sobre TODO el clip, no solo la ventana del gesto: la posición
        # de la cámara es fija durante toda la toma (mismo método que
        # diagnosticos_e3.lado_cercano, z relativa de hombros).
        lado_cam = lado_cercano(seq, np.ones(seq.n_frames, dtype=bool))
        if lado_cam is None:
            lado_cam_vs_dominante = "indeterminado"
        elif lado_cam == lado_dominante:
            lado_cam_vs_dominante = "mismo_lado_que_dominante"
        else:
            lado_cam_vs_dominante = "lado_opuesto_al_dominante"

        base_fila = {
            "clip": nombre,
            "sesion": sesion_de(nombre, fechas),
            "gesto": fila_cat["gesto"],
            "encuadre": fila_cat["angulo"],
            "lado_camara_vs_dominante": lado_cam_vs_dominante,
        }

        try:
            filt = procesar_e3(seq)
        except ValueError as e:
            filas.append({**base_fila, "categoria": "sin_pose_utilizable_e3", "motivo": f"E3: {e}"})
            continue

        resultados, _ = secuenciar(
            filt.secuencia,
            lado_dominante=lado_dominante,
            tramos_excluidos=filt.tramos_excluidos,
            brazo_via="codo",
            ancla="torso",
            margen_ancla_s=MARGEN_ANCLA_S,
        )
        rep = resultados[0]

        if not rep.picos:
            # El ancla (torso) no fue auditable: la repetición entera queda sin evaluar.
            # Es un problema del TORSO, no del brazo — se cuenta aparte para no mezclar
            # dos causas distintas en la misma estadística.
            filas.append({**base_fila, "categoria": "sin_ancla_torso", "motivo": rep.motivo_no_auditable})
            continue

        pico_brazo = rep.picos.get(S.BRAZO)
        auditable = pico_brazo is not None and pico_brazo.auditable
        motivo = None if auditable else (pico_brazo.motivo if pico_brazo is not None else rep.motivo_no_auditable)
        filas.append({**base_fila, "categoria": _clasificar_motivo(motivo), "motivo": motivo})

    return {"filas": filas, "sin_pose": sin_pose}


def resumir(filas: list[dict]) -> list[dict]:
    """Una fila por (gesto, encuadre, lado_camara_vs_dominante), con el conteo de cada
    categoría. 'auditable' + 'oclusion' + 'problema_de_calculo' + 'senal_plana_sin_pico_claro'
    + 'otro_no_catalogado' sobre el total EVALUADO (excluye sin_ancla_torso y
    sin_pose_utilizable_e3, que no llegan a evaluar el brazo en absoluto — se informan
    aparte, no se mezclan en el denominador)."""
    claves = sorted({(f["gesto"], f["encuadre"], f["lado_camara_vs_dominante"]) for f in filas})
    filas_resumen = []
    for gesto, encuadre, lado in claves:
        del_grupo = [f for f in filas if (f["gesto"], f["encuadre"], f["lado_camara_vs_dominante"]) == (gesto, encuadre, lado)]
        evaluadas = [f for f in del_grupo if f["categoria"] not in ("sin_ancla_torso", "sin_pose_utilizable_e3")]
        cnt = Counter(f["categoria"] for f in evaluadas)
        n = len(evaluadas)
        no_evaluadas = len(del_grupo) - n
        filas_resumen.append(
            {
                "gesto": gesto,
                "encuadre": encuadre,
                "lado_camara_vs_dominante": lado,
                "n_evaluadas": n,
                "no_evaluadas_sin_ancla_o_e3": no_evaluadas,
                "auditable": cnt.get("auditable", 0),
                "oclusion": cnt.get("oclusion", 0),
                "problema_de_calculo": cnt.get("problema_de_calculo", 0),
                "senal_plana": cnt.get("senal_plana_sin_pico_claro", 0),
                "otro_no_catalogado": cnt.get("otro_no_catalogado", 0),
                "pct_no_auditable": round(100 * (n - cnt.get("auditable", 0)) / n, 1) if n else None,
            }
        )
    return filas_resumen


def _imprimir_tabla(resumen: list[dict]) -> None:
    encabezado = (
        f"{'gesto':<8} {'encuadre':<12} {'lado cámara':<26} {'n':>3}  {'no audit.':>9}  "
        f"{'oclus.':>6}  {'cálculo':>7}  {'plana':>6}  {'sin ancla/E3':>12}"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for f in resumen:
        pct = f"{f['pct_no_auditable']}%" if f["pct_no_auditable"] is not None else "—"
        print(
            f"{f['gesto']:<8} {f['encuadre']:<12} {f['lado_camara_vs_dominante']:<26} "
            f"{f['n_evaluadas']:>3}  {pct:>9}  {f['oclusion']:>6}  {f['problema_de_calculo']:>7}  "
            f"{f['senal_plana']:>6}  {f['no_evaluadas_sin_ancla_o_e3']:>12}"
        )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sesion", type=int, choices=(1, 2), default=None)
    ap.add_argument("--salida", type=Path, default=None)
    args = ap.parse_args(argv)

    datos = diagnosticar(args.sesion)
    resumen = resumir(datos["filas"])

    if datos["sin_pose"]:
        print(f"[aviso] {len(datos['sin_pose'])} clip(s) sin pose cacheada, excluidos: {datos['sin_pose']}")
        print()

    _imprimir_tabla(resumen)

    otros = [f for f in datos["filas"] if f["categoria"] == "otro_no_catalogado"]
    if otros:
        print(f"\n[alerta] {len(otros)} fila(s) con un motivo no catalogado por este script — revisar a mano:")
        for f in otros:
            print(f"  {f['clip']}: {f['motivo']!r}")

    salida = {"resumen": resumen, "filas": datos["filas"], "sin_pose": datos["sin_pose"]}
    if args.salida:
        args.salida.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
