"""E5 — Artefactos visuales del reporte: fotogramas clave y video corto con el esqueleto (tabla 4.7 de la tesis, §4.5.3).

Dos productos, ambos opcionales (si fallan, el reporte sale igual con ``artefactos`` vacío = "no generado", nunca "cero"):

* **Tres fotogramas clave** (decisión 024, especificación §6 "Tres momentos del golpe"): el fotograma real del video, con el esqueleto,
  en el pico de velocidad de la cadera, del tronco y del brazo. JPEG de a lo sumo 720 px de alto.
* **Un video corto con el esqueleto** (§4.5.3: se conserva como evidencia visual aunque el original se borre a los 7 días): la ventana
  del golpe más un margen, acercado al jugador, en 720 px de alto, H.264 liviano, **en cámara lenta fija** (``FPS_REPRODUCCION`` cuadros por segundo sobre
  la grilla uniforme del análisis), para que se pueda mirar cuadro a cuadro. El factor se informa: nunca se disfraza.

Qué se dibuja (R3/R4): solo puntos detectados con confianza >= ``UMBRAL_DIBUJO``. Un punto dudoso **no se dibuja** (no se completa ni se
estima), y el fotograma es siempre uno realmente capturado: el más cercano en el tiempo al instante del pico, nunca un fotograma
interpolado. El esqueleto sale de la pose de ESE fotograma, sin filtrar.

El módulo no importa nada web ni de Supabase: recibe rutas y estructuras de datos y deja archivos en un directorio; la subida es de
``procesar_video``.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, SecuenciaPose
from app.engine.segmentos_corporales import ORDEN_ESPERADO, SegmentoCadena

UMBRAL_DIBUJO = 0.5          # confianza mínima para dibujar un punto (visibility de MediaPipe)
ALTO_FOTOGRAMA_CLAVE = 720   # px
ALTO_VIDEO = 720             # px (12/10: a 360 px / CRF 30 el video de 12 s pesaba 160 KB y se veía mal)
FPS_REPRODUCCION = 30        # cuadros por segundo del video de salida
MARGEN_VIDEO_S = 0.5         # antes y después de la ventana del golpe
CRF_VIDEO = 20               # H.264: ~1,5 MB para 12 s a 720 px; ffmpeg de 1 hilo, ~76 MB de memoria
CALIDAD_JPEG = 80

# Colores BGR (OpenCV). Los de segmento son los de la especificación §2: cadera violeta, tronco turquesa, brazo blanco.
_COLOR_HUESO = (184, 163, 148)       # gris azulado
_COLOR_SEGMENTO = {
    SegmentoCadena.PELVIS: (250, 139, 167),   # #a78bfa
    SegmentoCadena.TORSO: (238, 211, 34),     # #22d3ee
    SegmentoCadena.BRAZO: (249, 250, 241),    # #f1f5f9
}

_HUESOS_FIJOS = (
    (A.HOMBRO_IZQ, A.CODO_IZQ), (A.CODO_IZQ, A.MUNECA_IZQ),
    (A.HOMBRO_DER, A.CODO_DER), (A.CODO_DER, A.MUNECA_DER),
    (A.HOMBRO_IZQ, A.CADERA_IZQ), (A.HOMBRO_DER, A.CADERA_DER),
    (A.CADERA_IZQ, A.RODILLA_IZQ), (A.RODILLA_IZQ, A.TOBILLO_IZQ),
    (A.CADERA_DER, A.RODILLA_DER), (A.RODILLA_DER, A.TOBILLO_DER),
)


# --- tiempo -----------------------------------------------------------------------------------------------


def indice_fuente_mas_cercano(t_s: float, pts: np.ndarray | None, fps_grilla: float, n_fuente: int) -> int:
    """Índice del fotograma FUENTE más cercano en el tiempo al instante ``t_s`` de la grilla (segundos desde el primer fotograma).

    ``pts``: marcas de los fotogramas fuente (segundos). ``None`` = el archivo es uniforme a ``fps_grilla`` y el índice de la grilla es
    el del fotograma.
    """
    if pts is None:
        return int(min(max(round(t_s * fps_grilla), 0), n_fuente - 1))
    rel = np.asarray(pts, dtype=float) - float(pts[0])
    return int(np.argmin(np.abs(rel - t_s)))


# --- dibujo -----------------------------------------------------------------------------------------------


def _xy(frame: PoseFrame, art: A, ancho: int, alto: int) -> tuple[int, int] | None:
    p = frame.puntos.get(art)
    if p is None or p.confianza < UMBRAL_DIBUJO:
        return None
    return int(round(p.x * ancho)), int(round(p.y * alto))


def dibujar_esqueleto(img: np.ndarray, frame: PoseFrame, lado_dominante: str, *, resaltar: SegmentoCadena | None = None) -> np.ndarray:
    """Dibuja sobre ``img`` (BGR, modificada en el lugar) la pose de ``frame``; devuelve la misma imagen.

    La cadera, la línea de hombros y el brazo dominante van con el color de su segmento; ``resaltar`` los hace más gruesos.
    """
    import cv2

    alto, ancho = img.shape[:2]
    grosor = max(2, round(alto / 360))
    lado = "DER" if lado_dominante == "der" else "IZQ"
    brazo = (A[f"HOMBRO_{lado}"], A[f"CODO_{lado}"]), (A[f"CODO_{lado}"], A[f"MUNECA_{lado}"])

    def trazo(a: A, b: A, color: tuple[int, int, int], g: int) -> None:
        pa, pb = _xy(frame, a, ancho, alto), _xy(frame, b, ancho, alto)
        if pa is not None and pb is not None:
            cv2.line(img, pa, pb, color, g, cv2.LINE_AA)

    if not frame.detectado:
        return img
    for a, b in _HUESOS_FIJOS:
        trazo(a, b, _COLOR_HUESO, grosor)
    gruesos = {s: grosor + (2 if resaltar == s else 1) for s in _COLOR_SEGMENTO}
    trazo(A.CADERA_IZQ, A.CADERA_DER, _COLOR_SEGMENTO[SegmentoCadena.PELVIS], gruesos[SegmentoCadena.PELVIS])
    trazo(A.HOMBRO_IZQ, A.HOMBRO_DER, _COLOR_SEGMENTO[SegmentoCadena.TORSO], gruesos[SegmentoCadena.TORSO])
    for a, b in brazo:
        trazo(a, b, _COLOR_SEGMENTO[SegmentoCadena.BRAZO], gruesos[SegmentoCadena.BRAZO])
    for art in A:
        if art in (A.NARIZ,):
            continue
        pt = _xy(frame, art, ancho, alto)
        if pt is not None:
            cv2.circle(img, pt, grosor + 1, (255, 255, 255), -1, cv2.LINE_AA)
    return img


MARGEN_CAJA = 0.30           # margen alrededor del jugador, como fracción de su caja
LADO_MIN_CAJA = 0.30         # la caja no baja de esta fracción del alto del cuadro (sin acercar de más a un jugador lejano)


def caja_del_jugador(seq: SecuenciaPose, indices, ancho: int, alto: int) -> tuple[int, int, int, int] | None:
    """Recuadro ``(x0, y0, x1, y1)`` en píxeles, de dimensiones PARES, que contiene al jugador en todos los ``indices`` dados.

    Sale solo de puntos detectados con confianza suficiente (lo mismo que se dibuja). ``None`` si no hay ninguno: se muestra el cuadro
    entero. El recuadro es el mismo para todo el video (el cuadro no "salta"), así que la unión de lo que se movió en la ventana.
    """
    xs: list[float] = []
    ys: list[float] = []
    for i in indices:
        if not 0 <= i < seq.n_frames:
            continue
        f = seq.frames[i]
        if not f.detectado:
            continue
        for p in f.puntos.values():
            if p.confianza >= UMBRAL_DIBUJO:
                xs.append(p.x)
                ys.append(p.y)
    if not xs:
        return None
    x_min, x_max, y_min, y_max = min(xs) * ancho, max(xs) * ancho, min(ys) * alto, max(ys) * alto
    cx, cy = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0
    alto_c = max((y_max - y_min) * (1 + 2 * MARGEN_CAJA), LADO_MIN_CAJA * alto)
    ancho_c = max((x_max - x_min) * (1 + 2 * MARGEN_CAJA), alto_c * 0.75)   # nunca más angosto que 3:4
    ancho_c, alto_c = min(ancho_c, ancho), min(alto_c, alto)
    x0 = int(min(max(cx - ancho_c / 2, 0), ancho - ancho_c))
    y0 = int(min(max(cy - alto_c / 2, 0), alto - alto_c))
    w, h = int(ancho_c) // 2 * 2, int(alto_c) // 2 * 2
    return x0, y0, x0 + w, y0 + h


def _recortar(img: np.ndarray, caja: tuple[int, int, int, int] | None) -> np.ndarray:
    if caja is None:
        return img
    x0, y0, x1, y1 = caja
    return img[y0:y1, x0:x1]


def _redimensionar(img: np.ndarray, alto_destino: int) -> np.ndarray:
    import cv2

    alto, ancho = img.shape[:2]
    if alto <= alto_destino:
        return img
    ancho_d = int(round(ancho * alto_destino / alto / 2.0)) * 2   # par: lo exige yuv420p
    return cv2.resize(img, (ancho_d, alto_destino), interpolation=cv2.INTER_AREA)


# --- plan y resultado -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FotogramaClaveLocal:
    segmento: SegmentoCadena
    instante_s: float            # relativo al inicio de la ventana, como Pico.instante_s
    indice_fuente: int
    archivo: Path


@dataclass(frozen=True)
class VideoEsqueletoLocal:
    archivo: Path
    desde_s: float               # en el eje del clip (segundos desde el primer fotograma)
    hasta_s: float
    fps_reproduccion: int
    factor_lento: float          # cuántas veces más lento que la realidad se reproduce
    fotogramas: int
    bytes: int


@dataclass
class ArtefactosLocales:
    fotogramas_clave: list[FotogramaClaveLocal] = field(default_factory=list)
    video: VideoEsqueletoLocal | None = None


def plan_fotogramas_clave(
    repeticion, pts: np.ndarray | None, fps_grilla: float, n_fuente: int
) -> list[tuple[SegmentoCadena, float, int]]:
    """``(segmento, instante relativo a la ventana, índice del fotograma fuente)`` por cada pico medido de la repetición."""
    import math

    plan: list[tuple[SegmentoCadena, float, int]] = []
    for seg in ORDEN_ESPERADO:
        p = repeticion.picos.get(seg)
        if p is None or not p.auditable or not math.isfinite(p.velocidad):
            continue                                   # un pico no medido no tiene fotograma (R3)
        t_abs = p.frame / fps_grilla
        plan.append((seg, float(max(0.0, p.instante_s)), indice_fuente_mas_cercano(t_abs, pts, fps_grilla, n_fuente)))
    return plan


def generar_artefactos(
    clip: str | Path,
    seq_fuente: SecuenciaPose,
    pts: np.ndarray | None,
    fps_grilla: float,
    repeticion,
    lado_dominante: str,
    salida: str | Path,
    *,
    con_video: bool = True,
) -> ArtefactosLocales:
    """Una sola pasada por el clip: escribe los fotogramas clave y el video con esqueleto en ``salida``.

    ``seq_fuente``: la secuencia de poses ANTES de regularizar (un fotograma por fotograma del archivo). ``pts``: sus marcas de tiempo
    (``None`` si el archivo es uniforme a ``fps_grilla``). ``repeticion``: el ``ResultadoRepeticion`` cuyo golpe se muestra.
    """
    import cv2

    from app.engine.ingest import iterar_fotogramas

    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    n = seq_fuente.n_frames
    resultado = ArtefactosLocales()
    plan = plan_fotogramas_clave(repeticion, pts, fps_grilla, n)
    por_indice: dict[int, list[tuple[SegmentoCadena, float]]] = {}
    for seg, rel, idx in plan:
        por_indice.setdefault(idx, []).append((seg, rel))

    # Video: los puntos de la grilla de la ventana (+ margen) y, de cada uno, el fotograma fuente que le corresponde.
    mapa: list[int] = []
    t_desde = t_hasta = 0.0
    if con_video:
        v = repeticion.ventana
        # Mismo conteo que ``regularizar`` (un punto por período desde la primera marca).
        n_grilla = int(np.floor((float(pts[-1] - pts[0]) if pts is not None else (n - 1) / fps_grilla) * fps_grilla + 1e-9)) + 1
        g0 = max(0, int(round((v.desde_s - MARGEN_VIDEO_S) * fps_grilla)))
        g1 = min(n_grilla - 1, int(round((v.hasta_s + MARGEN_VIDEO_S) * fps_grilla)))
        mapa = [indice_fuente_mas_cercano(g / fps_grilla, pts, fps_grilla, n) for g in range(g0, g1 + 1)]
        t_desde, t_hasta = g0 / fps_grilla, g1 / fps_grilla

    ultimo = max([*por_indice, *(mapa[-1:] if mapa else [])], default=-1)
    if ultimo < 0:
        return resultado
    # Un acercamiento al jugador: en una toma abierta ocupa una fracción chica del cuadro y a 360 px no se ve el gesto.
    caja = caja_del_jugador(seq_fuente, [*por_indice, *mapa], seq_fuente.ancho, seq_fuente.alto)

    escritor = None
    n_escritos = 0
    ruta_video = salida / "esqueleto.mp4"
    por_escribir = list(mapa)               # índices fuente, uno por cuadro de salida, en orden
    video_roto = False
    try:
        for i, bruto in enumerate(iterar_fotogramas(clip)):
            if i > ultimo:
                break
            if i >= n:
                break
            necesita_clave = i in por_indice
            necesita_video = bool(por_escribir) and por_escribir[0] == i
            if not (necesita_clave or necesita_video):
                continue
            pose = seq_fuente.frames[i]
            if necesita_clave:
                for seg, rel in por_indice[i]:
                    # se dibuja sobre el cuadro entero (coordenadas normalizadas) y recién después se recorta y se achica
                    img = dibujar_esqueleto(bruto.copy(), pose, lado_dominante, resaltar=seg)
                    img = _redimensionar(_recortar(img, caja), ALTO_FOTOGRAMA_CLAVE)
                    archivo = salida / f"clave_{seg.value}.jpg"
                    cv2.imwrite(str(archivo), img, [cv2.IMWRITE_JPEG_QUALITY, CALIDAD_JPEG])
                    resultado.fotogramas_clave.append(FotogramaClaveLocal(seg, rel, i, archivo))
            if necesita_video:
                chico = _redimensionar(_recortar(dibujar_esqueleto(bruto.copy(), pose, lado_dominante), caja), ALTO_VIDEO)
                try:
                    if escritor is None:
                        alto_s, ancho_s = chico.shape[:2]
                        escritor = _abrir_ffmpeg(ruta_video, ancho_s, alto_s)
                    cuadro = chico.tobytes()
                    while por_escribir and por_escribir[0] == i:   # un mismo fotograma fuente puede cubrir varios puntos de la grilla
                        escritor.stdin.write(cuadro)
                        por_escribir.pop(0)
                        n_escritos += 1
                except OSError:
                    # Sin ffmpeg, o ffmpeg murió: el video es opcional, los fotogramas clave siguen (el reporte no depende de él).
                    video_roto = True
                    por_escribir = []
    finally:
        if escritor is not None:
            try:
                escritor.stdin.close()
            except OSError:
                pass
            escritor.wait(timeout=120)
    if escritor is not None and not video_roto and escritor.returncode == 0 and ruta_video.exists() and n_escritos > 0:
        resultado.video = VideoEsqueletoLocal(
            archivo=ruta_video, desde_s=t_desde, hasta_s=t_hasta, fps_reproduccion=FPS_REPRODUCCION,
            factor_lento=round(fps_grilla / FPS_REPRODUCCION, 3), fotogramas=n_escritos, bytes=ruta_video.stat().st_size,
        )
    return resultado


def _abrir_ffmpeg(destino: Path, ancho: int, alto: int) -> subprocess.Popen:
    """``ffmpeg`` por tubería: el contenedor ya lo trae (ffprobe lo usa la ingesta) y OpenCV no escribe H.264 reproducible en navegador."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ancho}x{alto}", "-r", str(FPS_REPRODUCCION), "-i", "-",
        "-an", "-threads", "1", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF_VIDEO), "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(destino),
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
