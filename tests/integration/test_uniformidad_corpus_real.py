"""Un recorte real del corpus propio llega como caso (b): cámara lenta horneada a 30 fps — decisión 028.

Sin Supabase. Se salta si el clip no está en KINETIQ_DATA_DIR. Mide con ffprobe (marcas de tiempo) y no decodifica el video.
"""

from __future__ import annotations

import pytest

try:
    from app.config import get_data_dir

    _CLIP = next(get_data_dir().glob("fase-b/sesion-01/drive/recortes/*_drive_perfil_240_01_rep01.mov"), None)
except Exception:  # sin KINETIQ_DATA_DIR
    _CLIP = None

pytestmark = pytest.mark.skipif(_CLIP is None, reason="No está el recorte de la Fase B en KINETIQ_DATA_DIR")


def test_el_recorte_del_corpus_es_camara_lenta_horneada():
    from app.engine.ingest import probe
    from app.engine.uniformidad_temporal import CasoArchivo, clasificar_caso, marcas_de_tiempo

    marcas = marcas_de_tiempo(_CLIP)
    assert marcas.es_constante
    assert marcas.fps_por_marcas == pytest.approx(30.0, abs=0.01)  # marcas estiradas: NO es tiempo real a 240

    fotogramas = probe(_CLIP).nb_frames
    assert fotogramas == 360  # 1,5 s reales x 240 fps

    # Sin la duración real, las marcas solas no distinguen (b) de (c): no se adivina.
    assert clasificar_caso(marcas, fotogramas, None).caso is CasoArchivo.INDETERMINADO
    # Con la duración real del golpe, cae en (b).
    assert clasificar_caso(marcas, fotogramas, 1.5).caso is CasoArchivo.HORNEADO
    # Y si el golpe hubiera durado 12 s reales a 30 fps (los 360 fotogramas serían tiempo real), no es cámara lenta.
    assert clasificar_caso(marcas, fotogramas, 12.0).caso is not CasoArchivo.HORNEADO
