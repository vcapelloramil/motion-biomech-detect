"""``engine/render``: fotogramas clave y video con esqueleto (ajuste del 12/10, tabla 4.7 de la tesis y §4.5.3).

Clip sintético (ffmpeg) y poses fabricadas: sin MediaPipe ni Supabase.
"""

from __future__ import annotations

import subprocess

import numpy as np
import pytest

from app.engine import render
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import PicoSegmento, ResultadoRepeticion, Ventana
from video_fixtures import FFPROBE, generar_clip, requiere_ffmpeg

_ARTS = (
    A.HOMBRO_IZQ, A.HOMBRO_DER, A.CODO_IZQ, A.CODO_DER, A.MUNECA_IZQ, A.MUNECA_DER,
    A.CADERA_IZQ, A.CADERA_DER, A.RODILLA_IZQ, A.RODILLA_DER, A.TOBILLO_IZQ, A.TOBILLO_DER,
)
_POS = {
    A.HOMBRO_IZQ: (0.40, 0.30), A.HOMBRO_DER: (0.60, 0.30), A.CODO_IZQ: (0.35, 0.45), A.CODO_DER: (0.65, 0.45),
    A.MUNECA_IZQ: (0.33, 0.60), A.MUNECA_DER: (0.68, 0.60), A.CADERA_IZQ: (0.43, 0.55), A.CADERA_DER: (0.57, 0.55),
    A.RODILLA_IZQ: (0.42, 0.72), A.RODILLA_DER: (0.58, 0.72), A.TOBILLO_IZQ: (0.41, 0.90), A.TOBILLO_DER: (0.59, 0.90),
}


def _pose(i: int, confianza: float = 0.9, detectado: bool = True) -> PoseFrame:
    if not detectado:
        return PoseFrame(i, False)
    return PoseFrame(i, True, puntos={a: Punto(x, y, None, confianza) for a, (x, y) in _POS.items()})


def _seq(n: int, fps: float, confianza: float = 0.9) -> SecuenciaPose:
    return SecuenciaPose(
        backend_id="t", backend_version="t-0", articulaciones=_ARTS, dims=2, ancho=320, alto=240,
        fps_efectivos=fps, config_hash="x", frames=[_pose(i, confianza) for i in range(n)],
    )


def _repeticion(fps: float, frame_pelvis: int, frame_torso: int, frame_brazo: int, desde: int = 20, hasta: int = 80):
    def pico(seg, frame, ok=True):
        return PicoSegmento(seg, frame, (frame - desde) / fps, 500.0 if ok else float("nan"), auditable=ok)

    picos = {S.PELVIS: pico(S.PELVIS, frame_pelvis), S.TORSO: pico(S.TORSO, frame_torso), S.BRAZO: pico(S.BRAZO, frame_brazo)}
    return ResultadoRepeticion(1, Ventana(desde, hasta, fps), picos, (S.PELVIS, S.TORSO, S.BRAZO), None, True)


# --- tiempo ------------------------------------------------------------------------------------------------


def test_el_fotograma_fuente_es_el_mas_cercano_en_el_tiempo_y_nunca_uno_interpolado():
    pts = np.array([10.0, 10.004, 10.008, 10.020, 10.025])      # un hueco de 12 ms entre el tercero y el cuarto
    assert render.indice_fuente_mas_cercano(0.0, pts, 240.0, 5) == 0
    assert render.indice_fuente_mas_cercano(0.011, pts, 240.0, 5) == 2   # 11 ms: más cerca de 8 ms que de 20 ms
    assert render.indice_fuente_mas_cercano(0.015, pts, 240.0, 5) == 3
    assert render.indice_fuente_mas_cercano(9.0, pts, 240.0, 5) == 4     # fuera de rango: el último, no un índice inexistente


def test_sin_marcas_el_indice_de_la_grilla_es_el_del_fotograma():
    assert render.indice_fuente_mas_cercano(0.5, None, 120.0, 100) == 60
    assert render.indice_fuente_mas_cercano(5.0, None, 120.0, 100) == 99


def test_el_plan_no_incluye_los_picos_no_medidos():
    rep = _repeticion(120.0, 40, 45, 60)
    rep.picos[S.BRAZO] = PicoSegmento(S.BRAZO, 60, 0.33, float("nan"), auditable=False, motivo="sin dato")
    plan = render.plan_fotogramas_clave(rep, None, 120.0, 120)
    assert [p[0] for p in plan] == [S.PELVIS, S.TORSO]
    assert plan[0][2] == 40 and plan[1][2] == 45


# --- dibujo: R3, nada que no se haya medido -----------------------------------------------------------------


def test_un_punto_con_poca_confianza_no_se_dibuja():
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    out = render.dibujar_esqueleto(img.copy(), _pose(0, confianza=render.UMBRAL_DIBUJO - 0.1), "der")
    assert not out.any()


def test_un_fotograma_sin_persona_queda_intacto():
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    assert not render.dibujar_esqueleto(img.copy(), _pose(0, detectado=False), "der").any()


def test_con_confianza_suficiente_se_dibuja_el_esqueleto_con_los_colores_de_segmento():
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    out = render.dibujar_esqueleto(img, _pose(0), "der")
    assert out.any()
    # la línea de caderas (violeta) pasa por el punto medio entre las dos caderas
    x = int(round((0.43 + 0.57) / 2 * 320)); y = int(round(0.55 * 240))
    assert tuple(out[y, x]) == render._COLOR_SEGMENTO[S.PELVIS]


def test_la_caja_del_jugador_es_par_acota_al_cuadro_y_sale_solo_de_puntos_confiables():
    seq = _seq(10, 120.0)
    x0, y0, x1, y1 = render.caja_del_jugador(seq, range(10), 1920, 1080)
    assert (x1 - x0) % 2 == 0 and (y1 - y0) % 2 == 0
    assert 0 <= x0 < x1 <= 1920 and 0 <= y0 < y1 <= 1080
    # contiene a las caderas y a los tobillos del jugador sintético
    assert x0 <= 0.43 * 1920 and x1 >= 0.57 * 1920 and y0 <= 0.30 * 1080 and y1 >= 0.90 * 1080
    assert render.caja_del_jugador(_seq(10, 120.0, confianza=0.1), range(10), 1920, 1080) is None


# --- archivos -----------------------------------------------------------------------------------------------


@requiere_ffmpeg
def test_genera_tres_fotogramas_clave_y_un_video_con_el_factor_lento_declarado(tmp_path):
    import cv2

    fps = 120.0
    clip = generar_clip(tmp_path / "clip.mp4", fps=fps, segundos=1.0, tamano="640x480")
    rep = _repeticion(fps, frame_pelvis=40, frame_torso=48, frame_brazo=60, desde=30, hasta=75)
    res = render.generar_artefactos(clip, _seq(120, fps), None, fps, rep, "der", tmp_path / "out")

    assert sorted(f.segmento.value for f in res.fotogramas_clave) == ["brazo", "pelvis", "torso"]
    for f in res.fotogramas_clave:
        img = cv2.imread(str(f.archivo))
        assert img is not None and img.shape[0] <= render.ALTO_FOTOGRAMA_CLAVE
        assert f.instante_s == pytest.approx((f.indice_fuente - 30) / fps)

    v = res.video
    assert v is not None and v.archivo.exists() and v.bytes > 0
    assert v.fps_reproduccion == render.FPS_REPRODUCCION and v.factor_lento == pytest.approx(fps / render.FPS_REPRODUCCION)
    # ventana (30..75) + margen de 0,5 s a cada lado, recortada al clip: 0..119
    assert v.desde_s == pytest.approx(0.0) and v.hasta_s == pytest.approx(119 / fps)
    # un cuadro de salida por punto de la grilla
    assert v.fotogramas == 120
    cuadros = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames,height",
         "-of", "csv=p=0", str(v.archivo)],
        capture_output=True, text=True, check=True,
    ).stdout.strip().split(",")
    assert int(cuadros[0]) <= 720 and int(cuadros[0]) % 2 == 0 and int(cuadros[1]) == 120


@requiere_ffmpeg
def test_si_ffmpeg_falla_los_fotogramas_clave_salen_igual(tmp_path, monkeypatch):
    """El video es opcional: sin ffmpeg el reporte conserva los tres momentos."""
    fps = 120.0
    clip = generar_clip(tmp_path / "clip.mp4", fps=fps, segundos=1.0)

    def sin_ffmpeg(*a, **k):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(render, "_abrir_ffmpeg", sin_ffmpeg)
    rep = _repeticion(fps, 40, 48, 60)
    res = render.generar_artefactos(clip, _seq(120, fps), None, fps, rep, "der", tmp_path / "out")
    assert len(res.fotogramas_clave) == 3 and res.video is None


@requiere_ffmpeg
def test_sin_picos_medidos_no_hay_fotogramas_pero_el_video_igual(tmp_path):
    fps = 120.0
    clip = generar_clip(tmp_path / "clip.mp4", fps=fps, segundos=1.0)
    rep = _repeticion(fps, 40, 48, 60)
    for seg in list(rep.picos):
        rep.picos[seg] = PicoSegmento(seg, 0, 0.0, float("nan"), auditable=False)
    res = render.generar_artefactos(clip, _seq(120, fps), None, fps, rep, "der", tmp_path / "out")
    assert res.fotogramas_clave == [] and res.video is not None


# --- subida a Storage desde procesar_video ---------------------------------------------------------------------


class _Almacen:
    def __init__(self):
        self.subidos: dict[str, tuple[bytes, dict]] = {}

    def upload(self, ruta, datos, file_options=None):
        self.subidos[ruta] = (datos, file_options or {})


class _Storage:
    def __init__(self, almacen):
        self.almacen, self.bucket = almacen, None

    def from_(self, bucket):
        self.bucket = bucket
        return self.almacen


class _Admin:
    def __init__(self, almacen):
        self.storage = _Storage(almacen)


@requiere_ffmpeg
def test_sube_los_artefactos_al_bucket_propio_con_rutas_por_usuario_y_video(tmp_path):
    from app.procesar_video import BUCKET_ARTEFACTOS, _generar_y_subir_artefactos

    fps = 120.0
    clip = generar_clip(tmp_path / "clip.mp4", fps=fps, segundos=1.0, tamano="640x480")
    almacen = _Almacen()
    admin = _Admin(almacen)
    rep = _repeticion(fps, 40, 48, 60, desde=30, hasta=75)
    out = _generar_y_subir_artefactos(admin, clip, "usr-1", "vid-1", _seq(120, fps), None, fps, rep, "der", str(tmp_path))

    assert admin.storage.bucket == BUCKET_ARTEFACTOS == "artefactos"
    assert sorted(almacen.subidos) == [
        "usr-1/vid-1/clave_brazo.jpg", "usr-1/vid-1/clave_pelvis.jpg", "usr-1/vid-1/clave_torso.jpg", "usr-1/vid-1/esqueleto.mp4",
    ]
    assert almacen.subidos["usr-1/vid-1/clave_torso.jpg"][1]["content-type"] == "image/jpeg"
    assert almacen.subidos["usr-1/vid-1/esqueleto.mp4"][1]["content-type"] == "video/mp4"
    # lo que va al reporte son RUTAS (no URLs) y valida contra el contrato
    from app.schemas.reporte import Artefactos

    modelo = Artefactos.model_validate(out)
    assert modelo.overlay_ruta == "usr-1/vid-1/esqueleto.mp4" and modelo.overlay_info.factor_lento == pytest.approx(4.0)
    assert {f.segmento for f in modelo.fotogramas_clave} == {"pelvis", "torso", "brazo"}
    assert all(not f.ruta.startswith("http") for f in modelo.fotogramas_clave)


@requiere_ffmpeg
def test_un_fallo_al_generar_o_subir_deja_artefactos_vacios_y_no_levanta(tmp_path):
    from app.procesar_video import _generar_y_subir_artefactos

    class _Roto:
        class storage:  # noqa: N801
            @staticmethod
            def from_(_):
                raise RuntimeError("Storage caído")

    fps = 120.0
    clip = generar_clip(tmp_path / "clip.mp4", fps=fps, segundos=1.0)
    rep = _repeticion(fps, 40, 48, 60)
    assert _generar_y_subir_artefactos(_Roto(), clip, "u", "v", _seq(120, fps), None, fps, rep, "der", str(tmp_path)) == {}
    # sin usuario o sin repetición: nada que generar
    assert _generar_y_subir_artefactos(_Roto(), clip, None, "v", _seq(120, fps), None, fps, rep, "der", str(tmp_path)) == {}
    assert _generar_y_subir_artefactos(_Roto(), clip, "u", "v", _seq(120, fps), None, fps, None, "der", str(tmp_path)) == {}
