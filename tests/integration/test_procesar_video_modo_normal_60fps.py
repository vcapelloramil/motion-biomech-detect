"""`procesar_video` con un clip REAL grabado en modo normal a 60 fps — decisión 020.

El recorte `20260924_VCR_saque_perfil_060_01_rep01.mov` (un saque, 5 s, cortado con
`ffmpeg -c copy` del original de ~1 minuto grabado a propósito en modo normal a 60 fps) es
el caso inverso al del resto del corpus: el contenedor dice la verdad. Declarado `normal`:
- `fps_efectivos` = la tasa REAL MEDIA de las marcas de tiempo (decisión 029): ~59,3, porque el
  clip trae un hueco de 3 fotogramas (66,7 ms) en 4,3 s. Antes de la 029 era el 60 del contenedor
  (59,94 normalizado).
- aptitud "solo_preparacion": 59,3 cae 1,2 % bajo 60, dentro de la tolerancia del 5 % sobre los
  pisos de R1 (decisión 029, actualización del 9/10: 57 y 114 fps). Sin esa tolerancia daba "rechazado".
- NO se corre la secuenciación completa: el video queda `parcial`, `apto_fase_rapida = False` y
  sin `reportes_biomecanicos`.
- No es un fallo: `normal` nunca falla, por fps alto o bajo (corrección de Valentín).

No corre inferencia de pose (R1 corta antes), así que es rápida. Corre contra un proyecto
Supabase real; se salta sin credenciales o sin el recorte en KINETIQ_DATA_DIR.
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

    _CLIP = (
        get_data_dir()
        / "fase-b" / "sesion-01" / "saque" / "recortes" / "20260924_VCR_saque_perfil_060_01_rep01.mov"
    )
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
    pytest.mark.skipif(_CLIP is None, reason="No está el recorte 060_01_rep01 en KINETIQ_DATA_DIR"),
]


def test_normal_60fps_queda_parcial_solo_preparacion():
    from supabase import create_client

    from app.procesar_video import procesar_video

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-normal60-{uuid.uuid4().hex[:12]}@example.invalid"
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
                    "nombre": "Atleta de prueba normal 60 fps",
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
                    "modo_captura": "normal",
                }
            )
            .execute()
            .data[0]
        )
        ruta_storage = f"{usuario_id}/{uuid.uuid4().hex}/{_CLIP.name}"
        admin.storage.from_("videos").upload(
            ruta_storage, _CLIP.read_bytes(), file_options={"content-type": "video/quicktime"}
        )
        video = (
            admin.table("videos")
            .insert({"sesion_id": sesion["id"], "usuario_id": usuario_id, "ruta_almacenamiento": ruta_storage})
            .execute()
            .data[0]
        )

        resultado = procesar_video(admin, video["id"])

        assert resultado["estado"] == "parcial"  # no es un fallo: "normal" nunca falla
        assert resultado["reporte_id"] is None
        assert "solo_preparacion" in resultado["motivo"]

        fila = (
            admin.table("videos")
            .select("estado, motivo_fallo, fps_real, apto_fase_rapida")
            .eq("id", video["id"])
            .single()
            .execute()
            .data
        )
        assert fila["estado"] == "parcial"
        assert fila["motivo_fallo"] is None
        assert 59.0 <= float(fila["fps_real"]) <= 60.1  # la tasa medida, no la declarada (decisión 029)
        assert fila["apto_fase_rapida"] is False
        assert (
            admin.table("reportes_biomecanicos").select("id").eq("video_id", video["id"]).execute().data == []
        )
    finally:
        if ruta_storage:
            admin.storage.from_("videos").remove([ruta_storage])
        admin.auth.admin.delete_user(usuario_id)
