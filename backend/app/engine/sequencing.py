"""E4 — Secuenciación: picos de velocidad y orden de la cadena (plan, tareas 4.4–4.6b).

El núcleo del sistema (§3.3.4.2, fila 6): el **orden** en que pelvis, torso y brazo
alcanzan su velocidad angular máxima. Inmune al desvío fijo y a la escala; solo lo
afectan el temblor (ya filtrado en E3) y un FPS mal leído (resuelto en E1).

Un tramo no auditable dentro de la ventana de una repetición → el pico de ese
segmento **no se reporta ni se estima** (regla R3); la repetición queda `auditable
= False`.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks

from app.engine.kinematics import velocidad_angular_segmento
from app.engine.pose.base import SecuenciaPose
from app.engine.preparacion import TramoExcluido
from app.engine.segmentos_corporales import (
    ORDEN_ESPERADO,
    SegmentoCadena,
    articulaciones_de_segmento,
)

# Heurísticas de detección de picos (constantes nombradas, a calibrar con más material).
PROMINENCIA_MIN_ABS = 40.0          # °/s
PROMINENCIA_MIN_REL = 0.15          # fracción del pico máximo de la ventana
SEPARACION_MIN_S = 0.05            # s entre picos
# Segmentación automática: "quietud" = velocidad total por debajo de esta fracción
# del máximo del clip, sostenida.
QUIETUD_REL = 0.10
DUR_MIN_REPETICION_S = 0.20

# --- Techo de plausibilidad física, POR SEGMENTO, anclado a la literatura --------
# Velocidades angulares máximas medidas por Fleisig et al. (2003) en tenistas de
# nivel mundial (tesis §3.4.2.2). Son un tope: un jugador amateur no debería
# acercarse.
_FLEISIG_MAX = {
    SegmentoCadena.PELVIS: 440.0,
    SegmentoCadena.TORSO: 870.0,
    SegmentoCadena.BRAZO: 2368.0,   # rotación interna del hombro, el pico más rápido
}
# Margen sobre el valor de Fleisig. Criterio: cubre (1) que el factor de
# ralentización de los clips descargados es una estimación
# (`escala_temporal_conocida = False`), así que el fps efectivo —y por lo tanto ω—
# tiene incertidumbre de un factor cercano a 2; y (2) el ruido de MediaPipe (146 mm
# de error 3D, §3.3.2.5), que infla las tasas instantáneas. Un pico por encima de
# Fleisig × este margen es un error de detección, no un movimiento (regla R3).
MARGEN_PLAUSIBILIDAD = 3.0

_CAVEAT_PUBLICO = (
    "Corpus público (sin repeticiones controladas del mismo jugador): estos "
    "agregados son una validación cualitativa temprana, NO la medición del "
    "Criterio 1 ni del Criterio 3, que requieren el conjunto propio de la Fase B."
)


def techo_velocidad(seg: SegmentoCadena) -> float:
    return _FLEISIG_MAX[seg] * MARGEN_PLAUSIBILIDAD


@dataclass(frozen=True)
class PicoSegmento:
    segmento: SegmentoCadena
    frame: int
    instante_s: float          # relativo al inicio de la ventana
    velocidad: float           # °/s
    auditable: bool = True
    motivo: str | None = None


@dataclass(frozen=True)
class Ventana:
    desde_frame: int
    hasta_frame: int           # inclusive
    fps: float

    @property
    def desde_s(self) -> float:
        return self.desde_frame / self.fps

    @property
    def hasta_s(self) -> float:
        return self.hasta_frame / self.fps


@dataclass(frozen=True)
class ResultadoRepeticion:
    indice: int
    ventana: Ventana
    picos: dict[SegmentoCadena, PicoSegmento | None]
    orden_observado: tuple[SegmentoCadena, ...] | None
    correcto: bool | None
    auditable: bool
    motivo_no_auditable: str | None = None


@dataclass(frozen=True)
class ResumenSecuenciacion:
    repeticiones_evaluadas: int
    repeticiones_auditables: int
    repeticiones_correctas: int
    orden_predominante: tuple[SegmentoCadena, ...] | None
    dispersion_instante_pico_torso_ms: float | None
    nota: str = ""


# --- frames no auditables por segmento --------------------------------------

def _frames_excluidos_por_segmento(
    tramos: list[TramoExcluido], seg: SegmentoCadena, lado_dominante: str, brazo_via: str
) -> set[int]:
    arts = set(articulaciones_de_segmento(seg, lado_dominante, brazo_via=brazo_via))
    fuera: set[int] = set()
    for t in tramos:
        if t.articulacion in arts:
            fuera.update(range(t.desde_frame, t.hasta_frame + 1))
    return fuera


# --- detección de un pico --------------------------------------------------

def detectar_pico(
    omega: np.ndarray,
    *,
    fps: float,
    offset_frame: int,
    frames_excluidos: set[int],
    techo: float,
) -> tuple[int, float] | tuple[None, str]:
    """Devuelve (frame_absoluto, velocidad) del pico dominante, o (None, motivo)."""
    valido = omega[~np.isnan(omega)]
    if valido.size < 5:
        return None, "serie demasiado corta o incompleta"
    tope = float(np.nanmax(omega))
    prominencia = max(PROMINENCIA_MIN_ABS, PROMINENCIA_MIN_REL * tope)
    distancia = max(1, int(SEPARACION_MIN_S * fps))
    omega_sin_nan = np.nan_to_num(omega, nan=-np.inf)
    idxs, _ = find_peaks(omega_sin_nan, prominence=prominencia, distance=distancia)
    if len(idxs) == 0:
        return None, "sin picos marcados por encima de la prominencia mínima"
    k = int(idxs[np.argmax(omega_sin_nan[idxs])])  # pico dominante = el más alto
    frame_abs = offset_frame + k
    if frame_abs in frames_excluidos:
        return None, "el pico cae en un tramo no auditable"
    velocidad = float(omega[k])
    if velocidad > techo:
        return None, (
            f"velocidad implausible ({velocidad:.0f} °/s > techo {techo:.0f}): "
            f"probable error de detección"
        )
    return frame_abs, velocidad


# --- orden observado -----------------------------------------------------

def orden_observado(
    picos: dict[SegmentoCadena, PicoSegmento | None],
) -> tuple[tuple[SegmentoCadena, ...] | None, bool | None, str | None]:
    faltan = [s.value for s, p in picos.items() if p is None]
    if faltan:
        return None, None, f"sin pico auditable para: {', '.join(faltan)}"
    orden = tuple(s for s, _ in sorted(picos.items(), key=lambda kv: kv[1].instante_s))
    return orden, (orden == ORDEN_ESPERADO), None


# --- segmentación ------------------------------------------------------

def _velocidad_total(seq: SecuenciaPose, lado_dominante: str, brazo_via: str) -> np.ndarray:
    partes = [
        velocidad_angular_segmento(seq, s, lado_dominante, brazo_via=brazo_via)
        for s in ORDEN_ESPERADO
    ]
    return np.nansum(np.vstack(partes), axis=0)


def sugerir_repeticiones(
    seq: SecuenciaPose, lado_dominante: str, brazo_via: str = "codo"
) -> list[tuple[int, int]]:
    """Ventanas activas entre pausas de quietud. Fallback: todo el clip."""
    total = _velocidad_total(seq, lado_dominante, brazo_via)
    n = seq.n_frames
    if n < 10 or np.all(np.isnan(total)):
        return [(0, n - 1)]
    tope = float(np.nanmax(total))
    activo = total > QUIETUD_REL * tope
    ventanas: list[tuple[int, int]] = []
    inicio = None
    dur_min = max(1, int(DUR_MIN_REPETICION_S * seq.fps_efectivos))
    for i in range(n):
        if activo[i] and inicio is None:
            inicio = i
        elif not activo[i] and inicio is not None:
            if i - inicio >= dur_min:
                ventanas.append((inicio, i - 1))
            inicio = None
    if inicio is not None and n - inicio >= dur_min:
        ventanas.append((inicio, n - 1))
    return ventanas or [(0, n - 1)]


def segmentar(
    seq: SecuenciaPose,
    lado_dominante: str,
    *,
    brazo_via: str = "codo",
    manual: list[tuple[float, float]] | None = None,
) -> list[Ventana]:
    fps = seq.fps_efectivos
    if manual:
        return [
            Ventana(int(round(d * fps)), int(round(h * fps)), fps) for d, h in manual
        ]
    return [
        Ventana(d, h, fps)
        for d, h in sugerir_repeticiones(seq, lado_dominante, brazo_via)
    ]


# --- evaluación por repetición y agregación --------------------------------

def evaluar_repeticion(
    seq: SecuenciaPose,
    ventana: Ventana,
    indice: int,
    *,
    lado_dominante: str,
    tramos_excluidos: list[TramoExcluido],
    brazo_via: str = "codo",
) -> ResultadoRepeticion:
    fps = seq.fps_efectivos
    d, h = ventana.desde_frame, ventana.hasta_frame
    picos: dict[SegmentoCadena, PicoSegmento | None] = {}
    for seg in ORDEN_ESPERADO:
        omega = velocidad_angular_segmento(
            seq, seg, lado_dominante, brazo_via=brazo_via
        )[d : h + 1]
        excluidos = _frames_excluidos_por_segmento(
            tramos_excluidos, seg, lado_dominante, brazo_via
        )
        resultado = detectar_pico(
            omega, fps=fps, offset_frame=d, frames_excluidos=excluidos,
            techo=techo_velocidad(seg),
        )
        if resultado[0] is None:
            picos[seg] = PicoSegmento(
                seg, -1, float("nan"), float("nan"), auditable=False, motivo=resultado[1]
            )
        else:
            frame_abs, vel = resultado
            picos[seg] = PicoSegmento(seg, frame_abs, (frame_abs - d) / fps, vel)

    orden, correcto, motivo = orden_observado(
        {s: (p if p and p.auditable else None) for s, p in picos.items()}
    )
    return ResultadoRepeticion(
        indice=indice,
        ventana=ventana,
        picos=picos,
        orden_observado=orden,
        correcto=correcto,
        auditable=orden is not None,
        motivo_no_auditable=motivo,
    )


def agregar(
    resultados: list[ResultadoRepeticion], *, corpus_publico: bool = False
) -> ResumenSecuenciacion:
    auditables = [r for r in resultados if r.auditable]
    correctas = [r for r in auditables if r.correcto]

    predominante = None
    if auditables:
        predominante = Counter(r.orden_observado for r in auditables).most_common(1)[0][0]

    dispersion = None
    instantes_torso = [
        r.picos[SegmentoCadena.TORSO].instante_s
        for r in auditables
        if r.picos.get(SegmentoCadena.TORSO) and r.picos[SegmentoCadena.TORSO].auditable
    ]
    if len(instantes_torso) >= 2:
        dispersion = float(np.std(instantes_torso, ddof=1) * 1000.0)

    return ResumenSecuenciacion(
        repeticiones_evaluadas=len(resultados),
        repeticiones_auditables=len(auditables),
        repeticiones_correctas=len(correctas),
        orden_predominante=predominante,
        dispersion_instante_pico_torso_ms=dispersion,
        nota=_CAVEAT_PUBLICO if corpus_publico else "",
    )


def secuenciar(
    seq: SecuenciaPose,
    *,
    lado_dominante: str,
    tramos_excluidos: list[TramoExcluido] | None = None,
    brazo_via: str = "codo",
    manual: list[tuple[float, float]] | None = None,
    corpus_publico: bool = False,
) -> tuple[list[ResultadoRepeticion], ResumenSecuenciacion]:
    tramos_excluidos = tramos_excluidos or []
    ventanas = segmentar(seq, lado_dominante, brazo_via=brazo_via, manual=manual)
    resultados = [
        evaluar_repeticion(
            seq, v, i + 1, lado_dominante=lado_dominante,
            tramos_excluidos=tramos_excluidos, brazo_via=brazo_via,
        )
        for i, v in enumerate(ventanas)
    ]
    return resultados, agregar(resultados, corpus_publico=corpus_publico)
