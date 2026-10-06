"""`procesar_video` con una combinación de modo_captura inconsistente — decisión 020
(ajuste del 2/10/2026), requisito 6 de Valentín: "una combinación inconsistente tiene
que fallar con motivo".

Usa un clip real de 25 fps del corpus público (`fase-a/segmentos/zverev_saque_lateral_01.mp4`,
no es cámara lenta real) declarado `camara_lenta_240`: 240/25 = 9,6, no es un múltiplo
entero — tiene que fallar.

**Por qué no hay acá un clip real para "normal con ≥ 120 fps → análisis completo":** el
iPhone con el que se grabó el corpus solo graba a 120 fps o más en modo cámara lenta; en
modo normal el máximo es 60 fps, así que ese archivo no existe ni se puede producir con
este equipo (decisión 020). Ese caso queda cubierto por
`tests/unit/test_procesar_video_factor.py::test_normal_nunca_falla_sea_cual_sea_el_fps`
(prueba pura, sin archivo) — no se inventa un archivo para esto. El caso real de modo
normal que sí existe (60 fps, un recorte propio) se prueba de punta a punta en
`tests/integration/test_procesar_video_modo_normal_60fps.py`.

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas o sin el
clip del corpus público en KINETIQ_DATA_DIR.
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import get_supabase_service_role_key, get_supabase_url

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_SERVICE_ROLE_KEY = None

try:
    from app.config import get_data_dir

    _CLIP = get_data_dir() / "fase-a" / "segmentos" / "zverev_saque_lateral_01.mp4"
    if not _CLIP.is_file():
        _CLIP = None
except Exception:
    _CLIP = None

pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_supabase,
    pytest.mark.skipif(
        not (_SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
    pytest.mark.skipif(
        _CLIP is None, reason="No está fase-a/segmentos/zverev_saque_lateral_01.mp4 en KINETIQ_DATA_DIR"
    ),
]


def test_modo_captura_incompatible_deja_el_video_fallido():
    from supabase import create_client

    from app.procesar_video import MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE, procesar_video

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-modocaptura-{uuid.uuid4().hex[:12]}@example.invalid"
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": secrets.token_urlsafe(18), "email_confirm": True}
    ).user.id

    ruta_storage = None
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": "Atleta de prueba modo_captura",
                    "mano_dominante": "derecha",
                    "nivel": "avanzado",
                }
            )
            .execute()
            .data[0]
        )
        sesion = (
            admin.table("sesiones")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "atleta_id": atleta["id"],
                    "gesto": "saque",
                    "encuadre": "perfil",
                    "lado_camara": "izquierda",
                    # 25 fps reales, declarado como si fuera cámara lenta a 240: 240/25 =
                    # 9,6, no cierra — justo el caso que tiene que fallar.
                    "modo_captura": "camara_lenta_240",
                }
            )
            .execute()
            .data[0]
        )

        ruta_storage = f"{usuario_id}/{uuid.uuid4().hex}/{_CLIP.name}"
        admin.storage.from_("videos").upload(
            ruta_storage, _CLIP.read_bytes(), file_options={"content-type": "video/mp4"}
        )

        video = (
            admin.table("videos")
            .insert(
                {
                    "sesion_id": sesion["id"],
                    "usuario_id": usuario_id,
                    "ruta_almacenamiento": ruta_storage,
                }
            )
            .execute()
            .data[0]
        )

        resultado = procesar_video(admin, video["id"])

        assert resultado["estado"] == "fallido"
        assert resultado["motivo_fallo"] == MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE
        assert resultado["reporte_id"] is None

        fila_video = (
            admin.table("videos")
            .select("estado, motivo_fallo, fps_real, apto_fase_rapida")
            .eq("id", video["id"])
            .single()
            .execute()
            .data
        )
        assert fila_video["estado"] == "fallido"
        assert fila_video["motivo_fallo"] == MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE
        # No se guesea un fps que ya se demostró no confiable (R3): queda null, no el
        # valor crudo del contenedor presentado como si fuera válido.
        assert fila_video["fps_real"] is None
        assert fila_video["apto_fase_rapida"] is None

        # No se creó ningún reporte: un análisis que no corrió no puede tener resultado.
        reportes = (
            admin.table("reportes_biomecanicos")
            .select("id")
            .eq("video_id", video["id"])
            .execute()
            .data
        )
        assert reportes == []
    finally:
        if ruta_storage:
            admin.storage.from_("videos").remove([ruta_storage])
        admin.auth.admin.delete_user(usuario_id)
