"""E0 — Cómo llegó el archivo: marcas de tiempo, tipo de cámara lenta y velocidad no uniforme.

Un golpe grabado a 240 fps en un iPhone puede llegar al servidor de **tres formas** (decisión 028):

* **(a) 240 fps en tiempo real:** las marcas de tiempo (``pts``) están separadas 1/240 s. Pasa cuando el golpe se
  recorta del medio de una cámara lenta en Fotos: el archivo conserva la frecuencia de captura y pierde la indicación
  de reproducción lenta. Válido.
* **(b) cámara lenta horneada a 30 fps:** el archivo conserva **todos** los fotogramas de la captura pero con las
  marcas separadas 1/30 s (reproducido, el golpe dura 8 veces más). Es el formato del corpus propio. Válido.
* **(c) 30 fps en tiempo real, con fotogramas descartados:** las marcas también están separadas 1/30 s, pero faltan 7
  de cada 8 fotogramas. **Es el único inválido**, y declarar "cámara lenta" sobre él multiplicaría por 8 todas las
  velocidades sin ningún aviso.

**Lo que las marcas de tiempo pueden y no pueden decir.** Distinguen (a) de (b)/(c) (1/240 contra 1/30). **No distinguen
(b) de (c)**: las dos son 1/30 constante. Hace falta saber cuánto duró el gesto en la vida real (cuántos fotogramas
tendría que haber: duración real x 240 en (b), x 30 en (c)). Esa duración la sabe el usuario, no el archivo.

**Velocidad no uniforme (EXPERIMENTAL, no validada contra una rampa real).** Una cámara lenta de iPhone con el tramo lento
editado en Fotos tiene tramos a velocidad normal en los extremos (rampas), horneados descartando fotogramas. Con marcas de
tiempo constantes (1/30), las rampas no se ven en los tiempos: se verían en el **contenido**, donde el movimiento entre
fotogramas consecutivos sería ~8 veces mayor. ``detectar_tramos_acelerados`` busca eso con la energía de movimiento
(diferencia media entre fotogramas consecutivos).

**Límite medido el 7/10/2026 (decisión 028):** esta energía **no distingue una rampa de cualquier movimiento brusco**: en el
corpus propio marca los extremos de **los 18 originales** (también los dos de velocidad normal, que no tienen rampas), porque
ahí se ve a la persona caminando hacia el teléfono y manipulándolo, y con el umbral por defecto marca el 5 % de los recortes
de golpe válidos (0 % con 8×, donde una rampa real quedaría en el borde). El corpus no contiene ninguna rampa real con la cual calibrarla. Por eso **solo informa**: no se usa
para rechazar nada en producción.

La lógica de decisión es pura (se prueba sin video). Solo ``marcas_de_tiempo``, ``energia_de_movimiento`` y
``analizar_archivo`` tocan archivos.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np

# Una frecuencia de marcas de tiempo a partir de la cual se considera captura en tiempo real de alta frecuencia
# (120 o 240 fps). Un archivo normal (24-60 fps) queda por debajo.
FPS_MARCAS_TIEMPO_REAL = 100.0
# Tolerancia al comparar la cantidad de fotogramas contra la esperada para una duración real conocida.
TOLERANCIA_FOTOGRAMAS = 0.35
# Una separación entre marcas es "regular" si difiere de la mediana en menos de esto (relativo).
TOLERANCIA_SEPARACION_REGULAR = 0.02
# Las marcas son "constantes" si al menos esta fracción de las separaciones es regular. Un único intervalo atípico (por ejemplo, el último
# fotograma de un recorte) no vuelve variable a un archivo: se midió en el corpus propio (decisión 028).
FRACCION_MINIMA_REGULAR = 0.97


class CasoArchivo(str, Enum):
    TIEMPO_REAL = "a"          # 240 (o 120) fps en tiempo real
    HORNEADO = "b"             # cámara lenta horneada: todos los fotogramas, marcas a ~30
    DESCARTADO = "c"           # 30 fps reales con fotogramas descartados: INVÁLIDO
    INDETERMINADO = "indeterminado"  # marcas a ~30: puede ser (b) o (c); falta la duración real


@dataclass(frozen=True)
class MarcasDeTiempo:
    n_paquetes: int
    separacion_mediana_s: float
    separacion_min_s: float
    separacion_max_s: float
    fraccion_regular: float = 1.0  # fracción de separaciones a menos del 2 % de la mediana

    @property
    def fps_por_marcas(self) -> float:
        return 1.0 / self.separacion_mediana_s if self.separacion_mediana_s > 0 else 0.0

    @property
    def es_constante(self) -> bool:
        return self.separacion_mediana_s > 0 and self.fraccion_regular >= FRACCION_MINIMA_REGULAR


@dataclass(frozen=True)
class ClasificacionCaso:
    caso: CasoArchivo
    explicacion: str
    # Cuántos fotogramas había que esperar a la frecuencia de captura, y qué fracción del esperado trae el archivo.
    fotogramas_esperados: int | None = None
    fraccion_del_esperado: float | None = None

    @property
    def es_valido(self) -> bool | None:
        """True (a, b), False (c), None si no se puede decidir sin la duración real."""
        if self.caso is CasoArchivo.DESCARTADO:
            return False
        if self.caso is CasoArchivo.INDETERMINADO:
            return None
        return True


def clasificar_caso(
    marcas: MarcasDeTiempo,
    n_fotogramas: int,
    duracion_real_s: float | None,
    *,
    fps_captura: float = 240.0,
) -> ClasificacionCaso:
    """Decide si el archivo es (a), (b) o (c). Pura: no toca el archivo.

    ``duracion_real_s`` es la duración del gesto en la vida real (no la reproducida). Sin ella, un archivo con marcas a
    ~30 fps queda ``INDETERMINADO``: las marcas no distinguen (b) de (c).
    """
    if marcas.fps_por_marcas >= FPS_MARCAS_TIEMPO_REAL:
        return ClasificacionCaso(
            CasoArchivo.TIEMPO_REAL,
            f"las marcas de tiempo están a {marcas.fps_por_marcas:.0f} fps: frecuencia de captura en tiempo real",
        )

    if duracion_real_s is None or duracion_real_s <= 0:
        return ClasificacionCaso(
            CasoArchivo.INDETERMINADO,
            f"las marcas de tiempo están a {marcas.fps_por_marcas:.0f} fps: puede ser cámara lenta horneada (b) o 30 fps "
            "reales con fotogramas descartados (c); falta la duración real del gesto para decidir",
        )

    esperados = round(duracion_real_s * fps_captura)
    fraccion = n_fotogramas / esperados if esperados else 0.0
    if abs(fraccion - 1.0) <= TOLERANCIA_FOTOGRAMAS:
        return ClasificacionCaso(
            CasoArchivo.HORNEADO,
            f"trae {n_fotogramas} fotogramas y a {fps_captura:.0f} fps un gesto de {duracion_real_s:g} s tiene {esperados}: "
            "conserva todos los de la captura, con las marcas estiradas a ~30 fps",
            esperados,
            fraccion,
        )
    fraccion_30 = marcas.fps_por_marcas / fps_captura
    if abs(fraccion - fraccion_30) <= TOLERANCIA_FOTOGRAMAS * fraccion_30:
        return ClasificacionCaso(
            CasoArchivo.DESCARTADO,
            f"trae {n_fotogramas} fotogramas, el {fraccion * 100:.0f} % de los {esperados} esperados a {fps_captura:.0f} fps: "
            f"es tiempo real a ~{marcas.fps_por_marcas:.0f} fps con fotogramas descartados",
            esperados,
            fraccion,
        )
    return ClasificacionCaso(
        CasoArchivo.INDETERMINADO,
        f"trae {n_fotogramas} fotogramas, el {fraccion * 100:.0f} % de los {esperados} esperados a {fps_captura:.0f} fps: "
        "no coincide ni con (b) ni con (c); revisar la duración real informada",
        esperados,
        fraccion,
    )


@dataclass(frozen=True)
class TramoAcelerado:
    desde_s: float   # en tiempo de reproducción del archivo
    hasta_s: float
    razon_maxima: float  # energía de movimiento máxima del tramo / energía base del archivo


def detectar_tramos_acelerados(
    energia: np.ndarray,
    fps_reproduccion: float,
    *,
    razon_minima: float = 5.0,
    duracion_minima_s: float = 0.5,
    ventana_mediana: int = 15,
    percentil_base: float = 25.0,
) -> list[TramoAcelerado]:
    """Tramos del archivo donde el movimiento entre fotogramas es mucho mayor que el habitual. EXPERIMENTAL.

    **No distingue una rampa de velocidad de movimiento brusco** (manejo de la cámara, la persona acercándose al teléfono): ver
    el docstring del módulo. Devuelve "tramos de mucho movimiento", y quien lo use no debe llamarlos rampas sin otra evidencia.

    ``energia[i]`` es la diferencia media entre el fotograma i e i+1. La **base** es un percentil bajo de la serie
    suavizada (el tramo lento domina un archivo de cámara lenta, y un percentil bajo no se corre si hay un tramo largo
    acelerado). Un tramo es una racha de al menos ``duracion_minima_s`` con energía suavizada > ``razon_minima`` x base.

    Heurística de contenido, no una lectura de metadatos. Una serie sin movimiento (todo el archivo quieto) no produce tramos.
    """
    energia = np.asarray(energia, dtype=float)
    if energia.size < ventana_mediana or fps_reproduccion <= 0:
        return []
    from scipy.signal import medfilt

    k = ventana_mediana if ventana_mediana % 2 == 1 else ventana_mediana + 1
    suave = medfilt(energia, kernel_size=k)
    base = float(np.percentile(suave, percentil_base))
    if base <= 0:
        return []
    marcado = suave > razon_minima * base
    tramos: list[TramoAcelerado] = []
    i, n = 0, marcado.size
    min_cuadros = max(int(round(duracion_minima_s * fps_reproduccion)), 1)
    while i < n:
        if not marcado[i]:
            i += 1
            continue
        j = i
        while j < n and marcado[j]:
            j += 1
        if j - i >= min_cuadros:
            tramos.append(TramoAcelerado(i / fps_reproduccion, j / fps_reproduccion, float(suave[i:j].max() / base)))
        i = j
    return tramos


# --------------------------------------------------------------------------------
# Entrada/salida: lectura de archivos reales.
# --------------------------------------------------------------------------------

def marcas_de_tiempo(ruta: str | Path) -> MarcasDeTiempo:
    """Marcas de tiempo (``pts``) de los paquetes de video, leídas con ffprobe. Lanza RuntimeError si ffprobe falla."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "packet=pts_time", "-of", "json", str(ruta),
    ]
    try:
        salida = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True).stdout
        paquetes = json.loads(salida)["packets"]
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError(f"no se pudieron leer las marcas de tiempo de {ruta}: {exc}") from exc
    pts = np.array(sorted(float(p["pts_time"]) for p in paquetes if p.get("pts_time") not in (None, "N/A")))
    if pts.size < 2:
        raise RuntimeError(f"{ruta} tiene menos de dos fotogramas con marca de tiempo")
    dt = np.diff(pts)
    mediana = float(np.median(dt))
    regular = float(np.mean(np.abs(dt - mediana) <= TOLERANCIA_SEPARACION_REGULAR * mediana)) if mediana > 0 else 0.0
    return MarcasDeTiempo(int(pts.size), mediana, float(dt.min()), float(dt.max()), regular)


def energia_de_movimiento(ruta: str | Path, ancho: int = 160) -> np.ndarray:
    """Diferencia media absoluta entre fotogramas consecutivos, en gris y reducidos a ``ancho`` px de ancho."""
    import cv2

    cap = cv2.VideoCapture(str(ruta))
    previo = None
    serie: list[float] = []
    try:
        while True:
            ok, cuadro = cap.read()
            if not ok:
                break
            chico = cv2.resize(cuadro, (ancho, max(int(cuadro.shape[0] * ancho / cuadro.shape[1]), 1)))
            gris = cv2.cvtColor(chico, cv2.COLOR_BGR2GRAY).astype(np.float32)
            if previo is not None:
                serie.append(float(np.abs(gris - previo).mean()))
            previo = gris
    finally:
        cap.release()
    return np.array(serie)
