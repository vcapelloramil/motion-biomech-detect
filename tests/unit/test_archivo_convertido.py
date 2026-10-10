"""Motivo de fallo ``archivo_convertido`` (decisiones 029 y 030, migración 20261009120000).

El teléfono convirtió el video al subirlo y llegó con menos de 120 fps reales aunque el usuario declaró cámara lenta. Sin Supabase:
un cliente falso registra lo que ``procesar_video`` escribiría.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from app import procesar_video as pv
from app.engine.ingest import MetadatosVideo
from app.reintento import MOTIVO_ARCHIVO_CONVERTIDO, MOTIVO_ERROR_INESPERADO, MOTIVO_MODO_CAPTURA_INCOMPATIBLE, decidir_reintento

_MIGRACION = Path(__file__).resolve().parents[2] / "supabase/migrations/20261009120000_reporte_json_y_motivo_archivo_convertido.sql"


def _md(nominal: float | None, real: float | None, declarado: float | None = None, n: int = 200) -> MetadatosVideo:
    declarado = declarado or real or 30.0
    return MetadatosVideo(
        ruta=Path("x.mov"), fps_declarados=declarado, nb_frames=n, duracion_s=n / (real or declarado), ancho=1920, alto=1080,
        fps_nominal_marcas=nominal, fps_real_medio=real,
        pts_visibles=None if nominal is None else np.arange(n) / (real or 30.0),
    )


# --- la regla -----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("modo", ["camara_lenta_120", "camara_lenta_240"])
def test_cualquier_camara_lenta_declarada_con_un_archivo_en_tiempo_real_bajo_r1_es_convertido(modo):
    """El caso medido el 7/10: un recorte a 240 que llegó a 100 fps (H.264)."""
    assert pv._motivo_archivo_convertido(_md(100.0, 100.0), modo, 100.0) == MOTIVO_ARCHIVO_CONVERTIDO


def test_la_cuenta_de_43_fps_de_la_camara_lenta_sin_recortar_tambien_lo_es():
    """Fotos por defecto sobre 9,5 s de cámara lenta: 60 nominales y 43 reales."""
    assert pv._motivo_archivo_convertido(_md(60.0, 43.0), "camara_lenta_240", 43.0) == MOTIVO_ARCHIVO_CONVERTIDO


def test_un_video_normal_a_60_fps_no_culpa_al_telefono():
    """Declaró 'normal': es un video genuino de 60 fps y R1 lo deja en `parcial`, sin motivo de fallo."""
    assert pv._motivo_archivo_convertido(_md(60.0, 60.0), "normal", 60.0) is None


def test_una_captura_de_120_con_fotogramas_perdidos_no_es_un_archivo_convertido():
    """Nominal 120 y real media 118,6: la grilla del archivo es la de la captura, el teléfono no convirtió nada. R1 decide (`parcial`)."""
    assert pv._motivo_archivo_convertido(_md(119.88, 118.6), "camara_lenta_120", 118.6) is None


def test_un_archivo_que_llega_con_los_fps_pedidos_no_es_convertido():
    assert pv._motivo_archivo_convertido(_md(239.98, 198.87), "camara_lenta_240", 198.87) is None


def test_un_horneado_no_es_convertido_porque_su_tasa_sale_de_la_declaracion():
    """Marcas a 30 fps constantes (corpus propio): no es tiempo real, rige la decisión 020."""
    assert pv._motivo_archivo_convertido(_md(30.0, 30.0), "camara_lenta_240", 240.0) is None


# --- el vocabulario cerrado coincide con la base -----------------------------------------------------------------


def test_los_codigos_de_motivo_fallo_coinciden_con_la_migracion():
    sql = _MIGRACION.read_text(encoding="utf-8")
    en_la_base = set(re.search(r"motivo_fallo in \(([^)]*)\)", sql).group(1).replace("'", "").replace(" ", "").split(","))
    assert en_la_base == {pv.MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE, pv.MOTIVO_FALLO_ERROR_INESPERADO, pv.MOTIVO_FALLO_ARCHIVO_CONVERTIDO}
    # y el módulo del reintento usa los mismos valores
    assert {MOTIVO_MODO_CAPTURA_INCOMPATIBLE, MOTIVO_ERROR_INESPERADO, MOTIVO_ARCHIVO_CONVERTIDO} == en_la_base


def test_la_migracion_agrega_la_columna_del_reporte_como_jsonb_objeto():
    sql = _MIGRACION.read_text(encoding="utf-8")
    assert re.search(r"add column reporte jsonb", sql)
    assert "jsonb_typeof(reporte) = 'object'" in sql


# --- el reintento ------------------------------------------------------------------------------------------------


def test_un_archivo_convertido_no_se_reintenta_con_la_misma_declaracion():
    d = decidir_reintento("fallido", MOTIVO_ARCHIVO_CONVERTIDO, "camara_lenta_240", "camara_lenta_240", 1, 3)
    assert not d.permitido and d.codigo == "declaracion_sin_cambios"


def test_un_archivo_convertido_se_reintenta_si_el_usuario_corrigio_la_declaracion():
    assert decidir_reintento("fallido", MOTIVO_ARCHIVO_CONVERTIDO, "camara_lenta_240", "normal", 1, 3).permitido


# --- procesar_video con un cliente falso -----------------------------------------------------------------------------


class _Consulta:
    def __init__(self, admin, tabla):
        self.admin, self.tabla, self._data = admin, tabla, []

    def select(self, *_):
        self._data = self.admin.video if self.tabla == "videos" else []
        return self

    def eq(self, *_):
        return self

    def single(self):
        return self

    def update(self, patch):
        self.admin.updates.append((self.tabla, dict(patch)))
        return self

    def insert(self, fila):
        self.admin.inserts.append((self.tabla, dict(fila)))
        self._data = [{"id": "nuevo", **fila}]
        return self

    def delete(self):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data)


class _AdminFalso:
    def __init__(self, modo):
        self.video = {
            "id": "v1",
            "ruta_almacenamiento": "u/v1.mov",
            "sesiones": {"gesto": "saque", "encuadre": "perfil", "modo_captura": modo, "atletas": {"mano_dominante": "derecha"}},
        }
        self.updates: list[tuple[str, dict]] = []
        self.inserts: list[tuple[str, dict]] = []
        self.storage = SimpleNamespace(from_=lambda _bucket: SimpleNamespace(download=lambda _ruta: b"no-es-un-video"))

    def table(self, nombre):
        return _Consulta(self, nombre)


def _procesar(monkeypatch, modo, md):
    import app.engine.ingest as ingest

    monkeypatch.setattr(ingest, "probe", lambda _ruta: md)
    admin = _AdminFalso(modo)
    return pv.procesar_video(admin, "v1"), admin


def test_procesar_video_deja_fallido_con_el_motivo_propio_y_guarda_la_tasa_medida(monkeypatch):
    resultado, admin = _procesar(monkeypatch, "camara_lenta_240", _md(100.0, 100.0))
    assert resultado["estado"] == "fallido" and resultado["motivo_fallo"] == "archivo_convertido"
    assert resultado["reporte_id"] is None and resultado["metricas_insertadas"] == 0
    final = [patch for tabla, patch in admin.updates if tabla == "videos"][-1]
    assert final["estado"] == "fallido" and final["motivo_fallo"] == "archivo_convertido"
    assert final["fps_real"] == pytest.approx(100.0) and final["apto_fase_rapida"] is False
    assert admin.inserts == []  # ni reporte ni métricas
    # Criterio 4: el inicio queda al arrancar y el fin en la misma salida del fallo
    inicio = [p for t, p in admin.updates if t == "videos"][0]
    assert inicio["estado"] == "procesando" and inicio["inicio_procesamiento_en"] and inicio["fin_procesamiento_en"] is None
    assert final["fin_procesamiento_en"] >= inicio["inicio_procesamiento_en"]


def test_procesar_video_con_la_declaracion_normal_deja_parcial_sin_motivo(monkeypatch):
    resultado, admin = _procesar(monkeypatch, "normal", _md(100.0, 100.0))
    assert resultado["estado"] == "parcial"
    final = [patch for tabla, patch in admin.updates if tabla == "videos"][-1]
    assert final["estado"] == "parcial" and "motivo_fallo" not in final
    assert final["fin_procesamiento_en"]  # también el parcial por R1 cierra el tiempo
