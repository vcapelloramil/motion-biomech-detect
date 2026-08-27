"""Catalogador del corpus (plan, tarea 1.5).

Recorre un directorio de clips, y para cada uno:
  1. lee los metadatos (OpenCV + ffprobe),
  2. toma del catálogo manual los datos que no puede inferir (factor de
     ralentización, si la escala temporal es conocida),
  3. calcula la frecuencia de captura efectiva y la aptitud para fase rápida
     (tabla 1.3),
  4. mide el ratio de fotogramas únicos (decisión 001, verificación 2),
  5. combina ambas verificaciones en un "uso" final.

Escribe un CSV derivado (``catalogo-verificado.csv``) y NO toca ``catalogo.csv``
(que tiene campos curados a mano). Avisa de toda discrepancia entre lo que calcula
y lo que dice el catálogo manual.

Uso:
    python -m app.catalogador                       # usa KINETIQ_DATA_DIR
    python -m app.catalogador --dir RUTA --sin-hash
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from app.engine.framehash import ratio_fotogramas_unicos
from app.engine.ingest import AptitudFaseRapida, IngestaError, evaluar, probe

EXTENSIONES_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}

# Subcarpetas que se saltan por defecto: contienen material de origen (videos
# largos de los que se recortan los segmentos), no unidades de análisis.
CARPETAS_EXCLUIDAS = {"compilaciones"}


@dataclass
class FilaCatalogo:
    archivo: str
    ruta_relativa: str
    fps_declarados: float = 0.0          # normalizado (59.94 -> 60)
    fps_declarados_crudo: float = 0.0    # lo que devolvió el archivo, sin normalizar
    factor: float = 1.0
    origen_factor: str = "declarado"
    fps_efectivos: float = 0.0
    escala_temporal_conocida: bool = False
    aptitud_fps: str = ""
    unicos: int | None = None
    total: int | None = None
    ratio_unicidad: float | None = None
    categoria_unicidad: str | None = None
    uso_final: str = ""
    inconsistencias: str = ""
    avisos: str = ""


def _combinar_uso(
    aptitud: AptitudFaseRapida, categoria_unicidad: str | None
) -> str:
    """Regla de combinación: ninguna verificación alcanza por sí sola.

    El uso final es la intersección de la aptitud por fps efectivos y la categoría
    de unicidad de fotogramas.
    """
    if aptitud is AptitudFaseRapida.RECHAZADO:
        return "rechazado"

    if aptitud in (AptitudFaseRapida.COMPLETO, AptitudFaseRapida.REDUCIDO):
        base = "E1-E4"
    else:  # SOLO_PREPARACION: la fase rápida no es auditable, solo la preparación
        base = "E1-E2 (solo preparación)"

    if categoria_unicidad == "duplicacion_sistematica":
        # Fotogramas duplicados: no sirve para velocidades ni orden de picos.
        return "E1-E2"
    if categoria_unicidad == "repeticion_aislada":
        return f"{base} (con reservas)"
    return base


def _leer_catalogo(ruta: Path) -> tuple[dict[str, dict], set[str], list[str]]:
    """Lee catalogo.csv de forma tolerante.

    Devuelve (filas_por_archivo, nombres_mal_formados, avisos). Sobre una fila con
    cantidad de columnas incorrecta se usa lo que se pudo leer, pero no se hacen
    cruces semánticos contra ella (los campos están corridos).
    """
    avisos: list[str] = []
    filas: dict[str, dict] = {}
    mal_formados: set[str] = set()
    if not ruta.is_file():
        avisos.append(f"No se encontró {ruta.name}; se asume factor 1.0 para todos.")
        return filas, mal_formados, avisos

    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f, restkey="_sobrantes", restval=None)
        n_columnas = len(lector.fieldnames or [])
        for i, fila in enumerate(lector, start=2):
            nombre = (fila.get("archivo") or "").strip()
            if not nombre:
                continue
            if "_sobrantes" in fila or any(v is None for v in fila.values()):
                mal_formados.add(nombre)
                avisos.append(
                    f"{ruta.name} línea {i}: la fila no tiene {n_columnas} columnas; "
                    f"se usa lo que se pudo leer y no se cruza contra ella."
                )
            filas[nombre] = fila
    return filas, mal_formados, avisos


def _a_float(valor, defecto=None):
    try:
        return float(str(valor).strip())
    except (TypeError, ValueError):
        return defecto


def catalogar_directorio(
    directorio: Path,
    *,
    catalogo: Path | None = None,
    con_hash: bool = True,
    ventana: tuple[float, float] | None = None,
    incluir_todo: bool = False,
) -> tuple[list[FilaCatalogo], list[str]]:
    """Cataloga los videos bajo ``directorio``. No escribe nada.

    Salta las subcarpetas de ``CARPETAS_EXCLUIDAS`` (material de origen) salvo que
    ``incluir_todo`` sea True. Devuelve (filas, avisos_globales).
    """
    directorio = Path(directorio)
    if catalogo:
        manual, mal_formados, avisos = _leer_catalogo(catalogo)
    else:
        manual, mal_formados, avisos = {}, set(), []

    videos = sorted(
        p for p in directorio.rglob("*")
        if p.suffix.lower() in EXTENSIONES_VIDEO
        and (incluir_todo or not (CARPETAS_EXCLUIDAS & set(p.relative_to(directorio).parts)))
    )
    if not videos:
        avisos.append(f"No se encontraron videos bajo {directorio}.")

    filas: list[FilaCatalogo] = []
    for ruta in videos:
        rel = ruta.relative_to(directorio).as_posix()
        fila = FilaCatalogo(archivo=ruta.name, ruta_relativa=rel)
        avisos_fila: list[str] = []

        m = manual.get(ruta.name)
        factor = _a_float(m.get("factor_estimado")) if m else None
        if factor is None:
            factor, origen = 1.0, "declarado"
            if m is None:
                avisos_fila.append("sin fila en catalogo.csv: se asume factor 1.0")
        else:
            origen = "catalogo"
        escala_conocida = bool(
            m and (m.get("escala_temporal") or "").strip().lower() == "conocida"
        )

        try:
            md = probe(ruta)
        except IngestaError as e:
            fila.aptitud_fps = "ERROR"
            fila.avisos = str(e)
            filas.append(fila)
            continue

        if factor <= 0:
            avisos_fila.append(f"factor inválido en catálogo ({factor}); se usa 1.0")
            factor, origen = 1.0, "declarado"

        res = evaluar(
            md, factor=factor, escala_conocida=escala_conocida, origen_factor=origen
        )

        fila.fps_declarados = round(res.fps_declarados_normalizado, 3)
        fila.fps_declarados_crudo = round(md.fps_declarados, 3)
        if abs(res.fps_declarados_normalizado - md.fps_declarados) > 0.01:
            avisos_fila.append(
                f"tasa NTSC {md.fps_declarados:.3f} normalizada a "
                f"{res.fps_declarados_normalizado:.0f}"
            )
        fila.factor = factor
        fila.origen_factor = res.origen_factor
        fila.fps_efectivos = round(res.fps_efectivos, 2)
        fila.escala_temporal_conocida = res.escala_temporal_conocida
        fila.aptitud_fps = res.aptitud.value
        fila.inconsistencias = " | ".join(res.inconsistencias)

        categoria = None
        if con_hash and res.aptitud is not AptitudFaseRapida.RECHAZADO:
            try:
                desde, hasta = ventana if ventana else (None, None)
                uni = ratio_fotogramas_unicos(ruta, desde_s=desde, hasta_s=hasta)
                fila.unicos, fila.total = uni.unicos, uni.total
                fila.ratio_unicidad = round(uni.ratio, 4)
                fila.categoria_unicidad = categoria = uni.categoria
            except IngestaError as e:
                avisos_fila.append(f"no se pudo medir unicidad: {e}")

        fila.uso_final = _combinar_uso(res.aptitud, categoria)

        # Cruces contra el catálogo manual (solo si la fila está bien formada).
        if m and ruta.name not in mal_formados:
            uso_manual = (m.get("uso") or "").strip()
            if uso_manual and uso_manual not in fila.uso_final:
                avisos_fila.append(
                    f"'uso' del catálogo ('{uso_manual}') no coincide con el "
                    f"calculado ('{fila.uso_final}')"
                )
            fps_ef_manual = _a_float(m.get("fps_efectivos"))
            if fps_ef_manual and fila.fps_efectivos and abs(
                fps_ef_manual - fila.fps_efectivos
            ) / fps_ef_manual > 0.05:
                avisos_fila.append(
                    f"fps_efectivos del catálogo ({fps_ef_manual}) difiere del "
                    f"calculado ({fila.fps_efectivos})"
                )

        if avisos_fila:
            fila.avisos = " | ".join(avisos_fila)
        filas.append(fila)

    # Filas del catálogo manual que no tienen un archivo correspondiente.
    escaneados = {f.archivo for f in filas}
    huerfanas = sorted(set(manual) - escaneados)
    for nombre in huerfanas:
        avisos.append(
            f"catalogo.csv tiene una fila para '{nombre}' pero no se encontró ese "
            f"archivo bajo {directorio}."
        )

    return filas, avisos


def escribir_csv(filas: list[FilaCatalogo], salida: Path) -> None:
    campos = list(FilaCatalogo.__dataclass_fields__.keys())
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for fila in filas:
            w.writerow(asdict(fila))


def _imprimir_tabla(filas: list[FilaCatalogo]) -> None:
    cols = ("archivo", "fps_declarados", "factor", "fps_efectivos", "aptitud_fps",
            "ratio_unicidad", "uso_final")
    anchos = {c: len(c) for c in cols}
    for fila in filas:
        d = asdict(fila)
        for c in cols:
            anchos[c] = max(anchos[c], len(str(d[c] if d[c] is not None else "")))
    linea = "  ".join(c.ljust(anchos[c]) for c in cols)
    print(linea)
    print("-" * len(linea))
    for fila in filas:
        d = asdict(fila)
        print("  ".join(str(d[c] if d[c] is not None else "").ljust(anchos[c]) for c in cols))
        if fila.avisos:
            print(f"    [aviso] {fila.avisos}")
        if fila.inconsistencias:
            print(f"    [aviso] metadatos: {fila.inconsistencias}")


def main(argv: list[str] | None = None) -> int:
    # La consola de Windows suele ser cp1252 y no puede imprimir algunos caracteres.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Catalogador del corpus de video (KinetiQ).")
    parser.add_argument("--dir", type=Path, default=None,
                        help="Directorio de clips (default: KINETIQ_DATA_DIR/fase-a).")
    parser.add_argument("--catalogo", type=Path, default=None,
                        help="catalogo.csv manual (default: KINETIQ_DATA_DIR/catalogo.csv).")
    parser.add_argument("--salida", type=Path, default=None,
                        help="CSV de salida (default: KINETIQ_DATA_DIR/catalogo-verificado.csv).")
    parser.add_argument("--ventana", type=str, default=None,
                        help="Ventana para el hash, en segundos 'desde:hasta'.")
    parser.add_argument("--sin-hash", action="store_true",
                        help="Omite la verificación de unicidad de fotogramas (más rápido).")
    parser.add_argument("--incluir-todo", action="store_true",
                        help=f"No saltear las subcarpetas de origen ({', '.join(sorted(CARPETAS_EXCLUIDAS))}).")
    args = parser.parse_args(argv)

    if args.dir is None or args.catalogo is None or args.salida is None:
        from app.config import get_data_dir

        base = get_data_dir()
        args.dir = args.dir or base / "fase-a"
        args.catalogo = args.catalogo or base / "catalogo.csv"
        args.salida = args.salida or base / "catalogo-verificado.csv"

    ventana = None
    if args.ventana:
        desde, hasta = args.ventana.split(":")
        ventana = (float(desde), float(hasta))

    filas, avisos = catalogar_directorio(
        args.dir, catalogo=args.catalogo, con_hash=not args.sin_hash,
        ventana=ventana, incluir_todo=args.incluir_todo,
    )

    _imprimir_tabla(filas)
    for a in avisos:
        print(f"[aviso] {a}")

    escribir_csv(filas, args.salida)
    print(f"\nEscrito: {args.salida}  ({len(filas)} clips)")

    errores = [f for f in filas if f.aptitud_fps == "ERROR"]
    rechazados = [f for f in filas if f.uso_final == "rechazado"]
    con_avisos = [f for f in filas if f.avisos or f.inconsistencias]
    print(f"Aptos fase rápida: {sum(1 for f in filas if f.uso_final.startswith('E1-E4'))}  "
          f"| solo preparación: {sum(1 for f in filas if 'preparación' in f.uso_final)}  "
          f"| solo E1-E2: {sum(1 for f in filas if f.uso_final == 'E1-E2')}  "
          f"| rechazados: {len(rechazados)}  | con error: {len(errores)}")
    if con_avisos or avisos:
        print(f"Con avisos: {len(con_avisos)} clip(s) + {len(avisos)} aviso(s) global(es).")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
