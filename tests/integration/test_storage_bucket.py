"""Prueba del bucket de Storage — Etapa 4.5, tarea 4.5.2.

Sube un clip corto real de la Fase B al bucket privado "videos"
(supabase/migrations/20261001090300_bucket_videos.sql) y confirma que se puede
descargar por URL firmada — sin la clave service_role, igual que lo haría el frontend —
antes de borrar el objeto de prueba.

Corre contra un proyecto Supabase real; se salta sin credenciales de Supabase
configuradas o sin ningún clip de la Fase B disponible en KINETIQ_DATA_DIR.
"""

from __future__ import annotations

import uuid

import httpx
import pytest

try:
    from app.config import get_supabase_service_role_key, get_supabase_url

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_SERVICE_ROLE_KEY = None

try:
    from app.config import get_data_dir

    # Cualquier recorte de una repetición de la Fase B alcanza; no importa cuál en particular.
    _CLIP = next(get_data_dir().glob("fase-b/*/*/recortes/*.mov"), None)
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
        _CLIP is None, reason="No hay ningún clip de la Fase B en KINETIQ_DATA_DIR para subir"
    ),
]


def test_subir_y_descargar_por_url_firmada():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    bucket = admin.storage.from_("videos")

    contenido_original = _CLIP.read_bytes()
    # El límite del bucket (file_size_limit, 50 MB) es el de la decisión 016; si el corpus local
    # tiene un clip más grande, es una señal de que esa decisión necesita revisarse, no un bug de
    # esta prueba — se informa claro en vez de dejar que Storage lo rechace con un 413 genérico.
    assert len(contenido_original) < 50 * 1024 * 1024, (
        f"{_CLIP.name} ({len(contenido_original) / 1024 / 1024:.1f} MB) supera el límite de 50 MB "
        "del bucket (decisión 016) — no sirve para esta prueba tal como está"
    )

    ruta = f"test-storage/{uuid.uuid4().hex}{_CLIP.suffix}"
    content_type = "video/quicktime" if _CLIP.suffix.lower() == ".mov" else "video/mp4"
    try:
        bucket.upload(ruta, contenido_original, file_options={"content-type": content_type})

        # Lo que haría el contenedor del motor con service_role: confirma que el objeto quedó
        # bien subido, bit a bit.
        assert bucket.download(ruta) == contenido_original

        # Lo que haría el frontend: una URL firmada, sin ninguna credencial de Supabase, solo la
        # URL en sí. 60 s alcanza de sobra para esta prueba.
        firmada = bucket.create_signed_url(ruta, expires_in=60)
        url = firmada.get("signedURL") or firmada.get("signedUrl")
        assert url, f"create_signed_url no devolvió una URL: {firmada}"

        respuesta = httpx.get(url, timeout=30.0)
        respuesta.raise_for_status()
        assert respuesta.content == contenido_original
    finally:
        bucket.remove([ruta])


def _intentar_subir_y_confirmar_que_no_quedo(bucket, ruta: str, contenido: bytes, content_type: str) -> None:
    """Sube con un upload que debería fallar; si por algún motivo "tuviera éxito" del lado del
    cliente, confirma con un download aparte que el objeto no quedó igual, y lo limpia si
    quedó. No se asume que un upload() sin excepción signifique que el servidor lo aceptó."""
    with pytest.raises(Exception):
        bucket.upload(ruta, contenido, file_options={"content-type": content_type})

    try:
        bucket.download(ruta)
        quedo = True
    except Exception:
        quedo = False
    if quedo:
        bucket.remove([ruta])
    assert not quedo, f"{ruta}: el objeto quedó subido pese a que el upload debía rechazarse"


def test_bucket_rechaza_archivo_de_mas_de_50mb():
    """El límite es del BUCKET (file_size_limit, decisión 016), no de la validación del
    navegador — confirma que el servidor lo aplica aunque se suba con service_role."""
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    bucket = admin.storage.from_("videos")

    # Un byte más que el límite (52428800) alcanza; no hace falta un archivo mucho más grande.
    contenido_demasiado_grande = b"\0" * (52_428_800 + 1)
    ruta = f"test-storage/demasiado-grande-{uuid.uuid4().hex}.mp4"
    _intentar_subir_y_confirmar_que_no_quedo(bucket, ruta, contenido_demasiado_grande, "video/mp4")


def test_bucket_rechaza_tipo_de_archivo_no_permitido():
    """allowed_mime_types del bucket solo admite video/mp4 y video/quicktime (decisión 018,
    tarea 4.5.2) — un .txt disfrazado de lo que sea tiene que rechazarse."""
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    bucket = admin.storage.from_("videos")

    ruta = f"test-storage/tipo-no-permitido-{uuid.uuid4().hex}.txt"
    _intentar_subir_y_confirmar_que_no_quedo(bucket, ruta, b"esto no es un video", "text/plain")
