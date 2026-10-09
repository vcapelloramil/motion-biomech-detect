"""E0/E1 — Ingesta y validación de FPS.

Convierte un archivo de video en fotogramas con metadatos temporales confiables, y
clasifica el material según si su frecuencia de captura efectiva alcanza para medir
la fase rápida del gesto.

Por qué esta etapa es crítica (tesis, apartados 3.3.1.1 y 3.4.2.2): un FPS mal
leído no produce ruido, produce un reporte "internamente coherente y completamente
falso" —todas las velocidades quedan multiplicadas o divididas por el mismo factor
y ningún filtro posterior lo detecta—. Y el orden de los picos de velocidad, que es
el núcleo del sistema, es inmune al desvío fijo y a la escala pero NO a un FPS mal
leído (apartado 3.3.4.2). Esta ingesta es la única defensa contra ese error.

Diseño: el núcleo de decisión (contrastar metadatos, clasificar, calcular la
frecuencia efectiva) es lógica pura sobre números y se prueba sin ningún video.
Solo ``probe()`` y ``iterar_fotogramas()`` tocan archivos.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from pathlib import Path

# Tolerancia relativa al contrastar la tasa declarada contra la que se deduce de
# (cantidad de fotogramas / duración). Por encima de esto se marca inconsistencia.
TOLERANCIA_COHERENCIA = 0.05


class IngestaError(RuntimeError):
    """El archivo no se pudo abrir o leer como video (corrupto, formato no soportado)."""


class AptitudFaseRapida(str, Enum):
    """Clasificación por frecuencia de captura efectiva (plan, tarea 1.3).

    Se apoya SIEMPRE en la frecuencia de captura efectiva, nunca en la declarada.
    """

    COMPLETO = "completo"                # >= 240 fps: incluye el impacto
    REDUCIDO = "reducido"               # 120-239 fps: impacto con confianza reducida
    SOLO_PREPARACION = "solo_preparacion"  # 60-119 fps: solo fase de preparación
    RECHAZADO = "rechazado"             # < 60 fps: no se analiza


# Umbrales de la tabla 1.3, en fps efectivos.
_UMBRAL_COMPLETO = 240.0
_UMBRAL_REDUCIDO = 120.0
_UMBRAL_PREPARACION = 60.0

# Tasas de captura estándar. Las tasas NTSC (24000/1001 = 23.976, 30000/1001 =
# 29.97, 60000/1001 = 59.94, ...) son artefactos de la aritmética de video, no
# decisiones: un archivo a 59.94 fps es material "60p".
_FPS_ESTANDAR = (24.0, 25.0, 30.0, 48.0, 50.0, 60.0, 96.0, 100.0, 120.0, 240.0)
_TOL_NORMALIZACION = 0.005  # 0.5%


def normalizar_fps(fps: float) -> float:
    """Ajusta una tasa NTSC a su valor nominal si cae a menos de 0.5% de él.

    Sin esto, un clip a 59.94 fps quedaría por debajo del umbral de 60 y se
    rechazaría por un redondeo, no por una limitación real de muestreo.
    """
    if fps <= 0:
        return fps
    for estandar in _FPS_ESTANDAR:
        if abs(fps - estandar) / estandar <= _TOL_NORMALIZACION:
            return estandar
    return fps


def clasificar_fps(fps_efectivos: float) -> AptitudFaseRapida:
    """Aplica la tabla de aptitud del plan (tarea 1.3) a una frecuencia efectiva."""
    if fps_efectivos >= _UMBRAL_COMPLETO:
        return AptitudFaseRapida.COMPLETO
    if fps_efectivos >= _UMBRAL_REDUCIDO:
        return AptitudFaseRapida.REDUCIDO
    if fps_efectivos >= _UMBRAL_PREPARACION:
        return AptitudFaseRapida.SOLO_PREPARACION
    return AptitudFaseRapida.RECHAZADO


@dataclass(frozen=True)
class MetadatosVideo:
    """Lo que se lee del archivo, sin interpretar todavía.

    ``fps_declarados`` es la tasa de REPRODUCCIÓN que declara el contenedor. No es
    necesariamente la tasa a la que se capturó (ver el caso de cámara lenta).
    Los campos ``*_ffprobe`` son None si ffprobe no está disponible.
    """

    ruta: Path
    fps_declarados: float
    nb_frames: int
    duracion_s: float
    ancho: int
    alto: int
    # Enriquecimiento opcional vía ffprobe (más fiable para el contraste).
    r_frame_rate: float | None = None
    avg_frame_rate: float | None = None
    nb_frames_ffprobe: int | None = None
    duracion_ffprobe_s: float | None = None
    # Marcas de tiempo de los fotogramas VISIBLES (decisión 029). El contenedor puede declarar ``nb_frames`` y ``avg_frame_rate``
    # contando fotogramas de pre-roll que la lista de edición oculta (479 declarados contra 398 visibles en un recorte real de
    # iPhone): ``nb_frames`` y ``duracion_s`` de esta clase ya están corregidos con los visibles cuando hay marcas.
    fps_nominal_marcas: float | None = None   # inversa de la separación mediana entre fotogramas visibles
    fps_real_medio: float | None = None       # (visibles - 1) / (última marca - primera marca): la tasa REAL
    n_preroll: int = 0                        # fotogramas con marca negativa, no visibles
    marcas_constantes: bool | None = None
    # Marcas de los fotogramas visibles, en orden de presentación. Sirve para regularizar el tiempo (engine/regularizacion.py).
    pts_visibles: object | None = field(default=None, repr=False, compare=False)
    rotacion_grados: int = 0                  # etiqueta de rotación del archivo (0/90/180/270); ya aplicada al decodificar

    @property
    def es_tiempo_real(self) -> bool:
        """Las marcas de tiempo son de captura en tiempo real (>= 45 fps): la tasa sale del archivo y no de una declaración.

        Un archivo horneado de cámara lenta tiene marcas a ~30 fps constantes y queda fuera. Que sea tiempo real NO significa que
        alcance para la fase rápida: eso lo decide R1 sobre ``fps_real_medio``."""
        from app.engine.uniformidad_temporal import FPS_MARCAS_TIEMPO_REAL

        return bool(self.fps_nominal_marcas and self.fps_nominal_marcas >= FPS_MARCAS_TIEMPO_REAL and self.fps_real_medio)

    @property
    def fps_por_conteo(self) -> float | None:
        """Tasa deducida de cantidad de fotogramas / duración. None si falta el dato."""
        nb = self.nb_frames_ffprobe or self.nb_frames
        dur = self.duracion_ffprobe_s or self.duracion_s
        if nb and dur and dur > 0:
            return nb / dur
        return None


@dataclass(frozen=True)
class ResultadoIngesta:
    """Veredicto de la ingesta para un clip."""

    metadatos: MetadatosVideo
    factor: float
    origen_factor: str  # "declarado" | "manual" | "catalogo"
    fps_declarados_normalizado: float
    fps_efectivos: float
    escala_temporal_conocida: bool
    aptitud: AptitudFaseRapida
    inconsistencias: list[str] = field(default_factory=list)
    motivo_rechazo: str | None = None

    @property
    def habilita_fase_rapida(self) -> bool:
        return self.aptitud in (AptitudFaseRapida.COMPLETO, AptitudFaseRapida.REDUCIDO)

    @property
    def habilita_preparacion(self) -> bool:
        return self.aptitud != AptitudFaseRapida.RECHAZADO

    @property
    def duracion_real_s(self) -> float | None:
        """Duración del movimiento en tiempo real (no la de reproducción).

        nb_frames / fps_efectivos. Para un clip de cámara lenta esto "des-estira"
        el eje temporal. Es la magnitud que debe coincidir entre un clip a 240 fps
        y su versión ralentizada (prueba de coherencia temporal del plan).
        """
        nb = self.metadatos.nb_frames_ffprobe or self.metadatos.nb_frames
        if nb and self.fps_efectivos > 0:
            return nb / self.fps_efectivos
        return None


def detectar_inconsistencias(md: MetadatosVideo) -> list[str]:
    """Contrasta los valores de metadatos entre sí (decisión 001, verificación 1).

    No lanza: devuelve una lista de descripciones (vacía si todo es coherente).
    Detectar una inconsistencia no descalifica el clip por sí solo; es una señal
    para revisar, que el catalogador reporta.
    """
    avisos: list[str] = []

    if md.fps_declarados <= 0:
        avisos.append("La tasa de fotogramas declarada es 0 o negativa.")
    if md.nb_frames <= 0:
        avisos.append("No se pudo determinar la cantidad de fotogramas.")
    if md.duracion_s <= 0:
        avisos.append("No se pudo determinar la duración.")

    fps_conteo = md.fps_por_conteo
    if fps_conteo is not None and md.fps_declarados > 0:
        dif = abs(fps_conteo - md.fps_declarados) / md.fps_declarados
        if dif > TOLERANCIA_COHERENCIA:
            avisos.append(
                f"La tasa declarada ({md.fps_declarados:.3f} fps) no coincide con "
                f"fotogramas/duración ({fps_conteo:.3f} fps): "
                f"{dif * 100:.1f}% de diferencia. Puede haber tasa variable, "
                f"metadatos incorrectos o ralentización incorporada al archivo."
            )

    if (
        md.r_frame_rate is not None
        and md.avg_frame_rate is not None
        and md.r_frame_rate > 0
    ):
        dif = abs(md.avg_frame_rate - md.r_frame_rate) / md.r_frame_rate
        if dif > TOLERANCIA_COHERENCIA:
            avisos.append(
                f"r_frame_rate ({md.r_frame_rate:.3f}) y avg_frame_rate "
                f"({md.avg_frame_rate:.3f}) difieren en {dif * 100:.1f}%."
            )

    return avisos


def evaluar(
    md: MetadatosVideo,
    *,
    factor: float = 1.0,
    escala_conocida: bool = False,
    origen_factor: str = "declarado",
) -> ResultadoIngesta:
    """Produce el veredicto de ingesta a partir de los metadatos y el factor.

    ``factor`` es el factor de ralentización: ``fps_efectivos = fps_declarados *
    factor``. Para material descargado casi nunca puede inferirse automáticamente
    (decisión 001): se pasa a mano o se toma del catálogo, y en ese caso
    ``escala_conocida`` normalmente es False (la escala temporal no es confiable,
    solo sirve para el ORDEN de los picos, no para velocidades absolutas).

    ``factor <= 0`` es un error de programación, no un dato: se lanza ValueError.
    Un clip con frecuencia efectiva insuficiente NO lanza: devuelve un
    ResultadoIngesta con ``aptitud == RECHAZADO`` y ``motivo_rechazo``, para que el
    rechazo quede registrado y sea trazable (regla R4).
    """
    if factor <= 0:
        raise ValueError(f"El factor de ralentización debe ser > 0 (se recibió {factor}).")

    # Archivo en tiempo real (decisión 029, RNF-01): la tasa es la MEDIDA de las marcas de tiempo, no la que declara el contenedor
    # (que con pre-roll o tasa variable es otra cosa: 169,28 contra 198,9 reales en un recorte de iPhone). Se normaliza solo si
    # cae a menos de 0,5 % de un estándar (59,94 -> 60), como siempre.
    fps_base = normalizar_fps(md.fps_real_medio if md.es_tiempo_real else md.fps_declarados)
    fps_efectivos = fps_base * factor
    aptitud = clasificar_fps(fps_efectivos)
    inconsistencias = detectar_inconsistencias(md)

    motivo = None
    if aptitud is AptitudFaseRapida.RECHAZADO:
        # Texto sin tildes: es una cadena generada que puede terminar en un CSV
        # o en el reporte; se mantiene ASCII.
        motivo = (
            f"Frecuencia de captura efectiva {fps_efectivos:.1f} fps < "
            f"{_UMBRAL_PREPARACION:.0f} fps: insuficiente incluso para la fase de "
            f"preparacion."
        )

    return ResultadoIngesta(
        metadatos=md,
        factor=factor,
        origen_factor=origen_factor,
        fps_declarados_normalizado=fps_base,
        fps_efectivos=fps_efectivos,
        escala_temporal_conocida=escala_conocida,
        aptitud=aptitud,
        inconsistencias=inconsistencias,
        motivo_rechazo=motivo,
    )


# --------------------------------------------------------------------------------
# Entrada/salida: lectura de archivos reales. Todo lo de abajo toca el disco.
# --------------------------------------------------------------------------------

def _parse_fraction(valor: str | None) -> float | None:
    """Convierte '25/1' o '30000/1001' a float. None si no se puede."""
    if not valor or valor in ("0/0", "N/A"):
        return None
    try:
        return float(Fraction(valor))
    except (ValueError, ZeroDivisionError):
        try:
            return float(valor)
        except ValueError:
            return None


def _leer_ffprobe(ruta: Path) -> dict:
    """Lee metadatos del contenedor con ffprobe. dict vacío si ffprobe no está o falla.

    ffprobe es una dependencia del catalogador (no del núcleo del motor); si no
    está instalado, la ingesta sigue funcionando solo con lo que da OpenCV.
    """
    import json

    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,avg_frame_rate,nb_frames,duration",
        "-show_entries", "format=duration",
        "-of", "json", str(ruta),
    ]
    try:
        salida = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=True
        ).stdout
    except (FileNotFoundError, subprocess.SubprocessError):
        return {}

    try:
        datos = json.loads(salida)
    except json.JSONDecodeError:
        return {}

    stream = (datos.get("streams") or [{}])[0]
    fmt = datos.get("format") or {}

    def _int(v: str | None) -> int | None:
        try:
            return int(v) if v not in (None, "N/A") else None
        except ValueError:
            return None

    def _float(v: str | None) -> float | None:
        try:
            return float(v) if v not in (None, "N/A") else None
        except ValueError:
            return None

    return {
        "r_frame_rate": _parse_fraction(stream.get("r_frame_rate")),
        "avg_frame_rate": _parse_fraction(stream.get("avg_frame_rate")),
        "nb_frames_ffprobe": _int(stream.get("nb_frames")),
        "duracion_ffprobe_s": _float(stream.get("duration")) or _float(fmt.get("duration")),
    }


def probe(ruta: str | Path, *, usar_ffprobe: bool = True) -> MetadatosVideo:
    """Abre el video y lee sus metadatos.

    OpenCV da la tasa declarada, el conteo (a veces estimado), la resolución. Si
    ``usar_ffprobe`` y ffprobe está disponible, se enriquece con datos del
    contenedor más fiables para el contraste de coherencia.

    Lanza IngestaError si el archivo no abre o no tiene un stream de video legible.
    """
    import cv2

    ruta = Path(ruta)
    if not ruta.is_file():
        raise IngestaError(f"No existe el archivo: {ruta}")

    cap = cv2.VideoCapture(str(ruta))
    try:
        if not cap.isOpened():
            raise IngestaError(f"OpenCV no pudo abrir el archivo: {ruta}")

        # Videos verticales de celular: la rotación viene como etiqueta y OpenCV NO la aplica por defecto (el fotograma sale
        # acostado y la pose fallaría). Se activa la orientación automática ANTES de leer.
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
        rotacion = int(cap.get(cv2.CAP_PROP_ORIENTATION_META) or 0) % 360

        fps = cap.get(cv2.CAP_PROP_FPS)
        nb = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Un archivo que abre pero no entrega ni un fotograma se trata como corrupto.
        ok, primero = cap.read()
        if not ok:
            raise IngestaError(
                f"El archivo abre pero no se pudo leer ningún fotograma: {ruta}"
            )
        # Resolución del fotograma YA orientado (la que ve la pose), no la de las propiedades del contenedor.
        alto, ancho = int(primero.shape[0]), int(primero.shape[1])
    finally:
        cap.release()

    fps = float(fps) if fps and fps > 0 else 0.0
    duracion = nb / fps if fps > 0 and nb > 0 else 0.0

    extra = _leer_ffprobe(ruta) if usar_ffprobe else {}

    # Marcas de tiempo de los fotogramas visibles. Si se leen, corrigen la cantidad de fotogramas y la duración.
    marcas = None
    if usar_ffprobe:
        from app.engine.uniformidad_temporal import marcas_de_tiempo_visibles

        marcas = marcas_de_tiempo_visibles(ruta)
    if marcas is not None:
        nb = marcas.n_paquetes
        duracion = marcas.n_paquetes / marcas.fps_real if marcas.fps_real > 0 else duracion

    return MetadatosVideo(
        ruta=ruta,
        fps_declarados=fps or (extra.get("r_frame_rate") or 0.0),
        nb_frames=nb,
        duracion_s=duracion,
        ancho=ancho,
        alto=alto,
        r_frame_rate=extra.get("r_frame_rate"),
        avg_frame_rate=extra.get("avg_frame_rate"),
        nb_frames_ffprobe=extra.get("nb_frames_ffprobe"),
        duracion_ffprobe_s=extra.get("duracion_ffprobe_s"),
        fps_nominal_marcas=marcas.fps_por_marcas if marcas is not None else None,
        fps_real_medio=marcas.fps_real if marcas is not None else None,
        n_preroll=marcas.n_preroll if marcas is not None else 0,
        marcas_constantes=marcas.es_constante if marcas is not None else None,
        pts_visibles=marcas.pts if marcas is not None else None,
        rotacion_grados=rotacion,
    )


def iterar_fotogramas(ruta: str | Path) -> Iterator["object"]:
    """Genera los fotogramas del video uno por uno, sin cargar el archivo entero.

    Cada elemento es un ndarray BGR de OpenCV. Pensado para recorrer videos largos
    a alta frecuencia con un consumo de memoria constante (plan, tarea 1.4).
    """
    import cv2

    ruta = Path(ruta)
    cap = cv2.VideoCapture(str(ruta))
    if not cap.isOpened():
        cap.release()
        raise IngestaError(f"OpenCV no pudo abrir el archivo: {ruta}")
    # Misma orientación automática que probe(): los fotogramas salen derechos aunque el archivo sea vertical.
    cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            yield frame
    finally:
        cap.release()
