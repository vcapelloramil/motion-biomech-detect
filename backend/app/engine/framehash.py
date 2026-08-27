"""Verificación 2 de la decisión 001: unicidad de fotogramas por huella exacta.

El problema (decisión 001): un archivo puede declarar 25 fps y contener información
temporal real (cámara lenta), o declarar 25 fps y estar "estirado" duplicando
fotogramas, sin aportar nada. Los dos casos son indistinguibles por metadatos.

No se usa ``mpdecimate`` de ffmpeg: compara si dos fotogramas son *parecidos* según
un umbral, y en cámara lenta buena el movimiento entre cuadros cae por debajo de ese
umbral y los descarta como falsos duplicados ("cuanto mejor la cámara lenta, más
falsos duplicados reporta mpdecimate"). En cambio, la huella (hash) exacta solo
marca iguales dos fotogramas idénticos bit a bit.

Esta es la contraparte en código del comando manual de la decisión 001
(``ffmpeg ... -f framehash``).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

# Fracción central del clip que se analiza por defecto, para no incluir títulos ni
# transiciones (decisión 001: la prueba va sobre un tramo representativo, no sobre
# el archivo entero).
_FRACCION_CENTRAL = 0.6

# Cortes heurísticos sobre el ratio de fotogramas únicos (decisión 001, tabla
# "Cómo se lee"). Ajustables.
_UMBRAL_CAPTURA_REAL = 0.97          # ~100% -> captura real, sin duplicación
_UMBRAL_REPETICION_AISLADA = 0.60   # ~70-95% -> alguna repetición aislada
# por debajo -> ~33% o ~50% -> duplicación sistemática


@dataclass(frozen=True)
class ResultadoUnicidad:
    total: int
    unicos: int
    desde_s: float
    hasta_s: float

    @property
    def ratio(self) -> float:
        return self.unicos / self.total if self.total else 0.0

    @property
    def categoria(self) -> str:
        return interpretar_ratio(self.ratio)

    def __str__(self) -> str:
        return f"{self.unicos}/{self.total} ({self.ratio * 100:.1f}%) — {self.categoria}"


def interpretar_ratio(ratio: float) -> str:
    """Traduce el ratio de únicos a una de las tres categorías de la decisión 001."""
    if ratio >= _UMBRAL_CAPTURA_REAL:
        return "captura_real"
    if ratio >= _UMBRAL_REPETICION_AISLADA:
        return "repeticion_aislada"
    return "duplicacion_sistematica"


def ratio_fotogramas_unicos(
    ruta: str | Path,
    *,
    desde_s: float | None = None,
    hasta_s: float | None = None,
) -> ResultadoUnicidad:
    """Decodifica la ventana pedida y cuenta cuántos fotogramas son únicos.

    Si no se pasan ``desde_s``/``hasta_s``, se usa el 60% central del clip. Si no
    se puede determinar la duración, se recorre el archivo entero.

    Costo: decodifica y hashea cada fotograma de la ventana (md5 sobre los bytes
    crudos). Para un clip de decenas de segundos es cuestión de segundos; es una
    herramienta offline de admisión al corpus, no parte del pipeline en caliente.
    """
    import cv2

    from app.engine.ingest import IngestaError

    ruta = Path(ruta)
    cap = cv2.VideoCapture(str(ruta))
    if not cap.isOpened():
        cap.release()
        raise IngestaError(f"OpenCV no pudo abrir el archivo: {ruta}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        nb = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        dur = nb / fps if fps and fps > 0 and nb and nb > 0 else None

        if desde_s is None and hasta_s is None and dur:
            margen = dur * (1.0 - _FRACCION_CENTRAL) / 2.0
            desde_s, hasta_s = margen, dur - margen
        inicio = desde_s if desde_s is not None else 0.0
        fin = hasta_s if hasta_s is not None else float("inf")

        if inicio > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, inicio * 1000.0)

        vistos: set[str] = set()
        total = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            pos_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            if pos_s > fin:
                break
            total += 1
            vistos.add(hashlib.md5(frame.tobytes()).hexdigest())
    finally:
        cap.release()

    if total == 0:
        raise IngestaError(
            f"No se pudo leer ningún fotograma en la ventana pedida: {ruta}"
        )

    return ResultadoUnicidad(
        total=total,
        unicos=len(vistos),
        desde_s=inicio,
        hasta_s=fin if fin != float("inf") else (dur or inicio),
    )
