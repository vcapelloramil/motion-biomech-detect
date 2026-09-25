"""E3 — Orden del pipeline de procesamiento de señales (plan, tarea 3.4; tesis §3.4.2.6).

Orden fijo, no negociable:

    detección de pose (E2)
      → validación (baja confianza + saltos imposibles)
      → preparación (excluir no confiables, interpolar huecos cortos)
      → elección del corte (Winter)
      → filtrado Butterworth de fase cero
      → [E4: recién acá se segmentan las repeticiones y se calculan velocidades]

Se filtra la **secuencia completa**, antes de cualquier recorte: `filtfilt` necesita
margen de borde y las ventanas de repetición de E4 son demasiado cortas.

Se filtra el espacio **métrico** (`puntos_mundo`) cuando existe; los backends 2D
puros caen a `puntos` (imagen). El overlay de E5 usa siempre `puntos` sin filtrar.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from app.engine.dsp import ORDEN_POR_DEFECTO, butterworth_fase_cero_por_segmentos
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.preparacion import (
    GAP_MAX_INTERPOLABLE,
    TramoExcluido,
    preparar_series,
)
from app.engine.validation import (
    MAX_SALTO_TORSOS,
    UMBRAL_CONFIANZA,
    ResultadoValidacion,
    validar,
)
from app.engine.winter import ResultadoWinter, elegir_corte


@dataclass(frozen=True)
class SecuenciaFiltrada:
    secuencia: SecuenciaPose  # nueva, con las coordenadas filtradas
    espacio: str
    corte_hz: float
    orden: int
    fps: float
    metodo_corte: str  # "winter" | "manual"
    validacion: ResultadoValidacion
    tramos_excluidos: list[TramoExcluido] = field(default_factory=list)
    winter: ResultadoWinter | None = None

    def trazabilidad_filtro(self) -> dict:
        """Bloque para ``trazabilidad.filtro`` del contrato del reporte."""
        return {
            "tipo": "butterworth",
            "orden": self.orden,
            "corte_hz": round(self.corte_hz, 3),
            "fase_cero": True,
        }


def _reconstruir_secuencia(
    original: SecuenciaPose,
    series: dict,
    *,
    espacio: str,
) -> SecuenciaPose:
    """Arma una SecuenciaPose nueva con las series filtradas en el espacio dado."""
    n = original.n_frames
    frames: list[PoseFrame] = []
    for i, viejo in enumerate(original.frames):
        nuevos: dict = {}
        for art in original.articulaciones:
            sx = series.get((art, "x"))
            sy = series.get((art, "y"))
            if sx is None or sy is None or np.isnan(sx[i]) or np.isnan(sy[i]):
                continue
            sz = series.get((art, "z"))
            z = None if sz is None or np.isnan(sz[i]) else float(sz[i])
            base = (viejo.puntos_mundo if espacio == "mundo" else viejo.puntos).get(art)
            conf = base.confianza if base is not None else 0.0
            nuevos[art] = Punto(x=float(sx[i]), y=float(sy[i]), z=z, confianza=conf)
        if espacio == "mundo":
            frames.append(
                PoseFrame(viejo.indice, viejo.detectado, puntos=viejo.puntos, puntos_mundo=nuevos)
            )
        else:
            frames.append(PoseFrame(viejo.indice, viejo.detectado, puntos=nuevos, puntos_mundo={}))
    return SecuenciaPose(
        backend_id=original.backend_id,
        backend_version=original.backend_version,
        articulaciones=original.articulaciones,
        dims=original.dims,
        ancho=original.ancho,
        alto=original.alto,
        fps_efectivos=original.fps_efectivos,
        config_hash=original.config_hash,
        frames=frames,
    )


def procesar_e3(
    seq: SecuenciaPose,
    *,
    corte_hz: float | None = None,
    orden: int = ORDEN_POR_DEFECTO,
    gap_max: int = GAP_MAX_INTERPOLABLE,
    umbral_confianza: float = UMBRAL_CONFIANZA,
    max_salto_torsos: float = MAX_SALTO_TORSOS,
) -> SecuenciaFiltrada:
    """Corre validación → preparación → Winter → filtrado, en ese orden.

    Si ``corte_hz`` se pasa, se usa ese (método "manual"); si no, lo elige Winter.
    """
    espacio = "mundo" if seq.tiene_mundo else "imagen"
    fps = seq.fps_efectivos

    val = validar(
        seq,
        umbral_confianza=umbral_confianza,
        max_salto_torsos=max_salto_torsos,
        espacio=espacio,
    )
    series, tramos = preparar_series(seq, val, espacio=espacio, gap_max=gap_max)

    winter = None
    if corte_hz is None:
        winter = elegir_corte(series, fps=fps, orden=orden)
        corte_hz = winter.corte_elegido_hz
        metodo = "winter"
    else:
        metodo = "manual"

    # Cada serie se filtra POR SEGMENTOS continuos (v0.4.1): los huecos largos siguen en
    # NaN y no se rellenan; un segmento demasiado corto para filtfilt pasa a NaN y se
    # registra como tramo excluido, nunca se deja crudo (regla R3). Antes de 0.4.1 toda
    # serie con algún NaN se dejaba ENTERA sin filtrar (ver decisión 010).
    indices = [f.indice for f in seq.frames]
    filtradas: dict = {}
    for (art, coord), serie in series.items():
        filtradas[(art, coord)], cortos = butterworth_fase_cero_por_segmentos(
            serie, fps=fps, corte_hz=corte_hz, orden=orden
        )
        for desde, hasta in cortos:
            tramos.append(TramoExcluido(art, coord, indices[desde], indices[hasta]))

    seq_filtrada = _reconstruir_secuencia(seq, filtradas, espacio=espacio)
    return SecuenciaFiltrada(
        secuencia=seq_filtrada,
        espacio=espacio,
        corte_hz=corte_hz,
        orden=orden,
        fps=fps,
        metodo_corte=metodo,
        validacion=val,
        tramos_excluidos=tramos,
        winter=winter,
    )
