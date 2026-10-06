"""Prueba de extremo a extremo del contenedor — Etapa 4.5, tarea 4.5.3.

Sube un clip real de la Fase B a Storage, registra la sesión/video que le correspondería
en la base, corre `app.procesar_video.procesar_video` (el mismo código que usaría el
contenedor desplegado en la tarea 4.5.4) y confirma que produce una fila de
reportes_biomecanicos con datos reales, no simulados — es el criterio de aceptación de la
Etapa 4.5 completa ("un clip de la Fase B... produce una fila en la base de datos a través
del contenedor", `docs/plan-desarrollo.md`), corrido localmente antes del despliegue real.

Es la prueba más lenta de las de Supabase: corre la inferencia de MediaPipe de verdad
sobre un clip completo (las mismas decenas de segundos que midió la decisión 017, acá sin
las restricciones de memoria/CPU de un contenedor).

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas o sin
ningún clip de la Fase B disponible en KINETIQ_DATA_DIR.
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import (
        get_supabase_service_role_key,
        get_supabase_url,
    )

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_SERVICE_ROLE_KEY = None

try:
    from app.config import get_data_dir

    # Cualquier recorte de una repetición de la Fase B alcanza para probar el circuito
    # completo; no hace falta que sea el mismo que usó la decisión 017.
    # Solo recortes a 240 fps (cámara lenta real): estas pruebas declaran `camara_lenta_240`, y desde que
    # existe el recorte de 60 fps en modo normal ("el primer .mov") ya no garantiza un clip de cámara lenta.
    _CLIP = next(get_data_dir().glob("fase-b/*/*/recortes/*_240_*.mov"), None)
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


def test_procesar_video_produce_reporte_real():
    from supabase import create_client

    from app.procesar_video import procesar_video

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-e2e-{uuid.uuid4().hex[:12]}@example.invalid"
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": secrets.token_urlsafe(18), "email_confirm": True}
    ).user.id
    # El trigger de alta (decisión 018, ajuste 3) ya creó la fila en usuarios.

    ruta_storage = None
    version_previa_id = None
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": "Atleta de prueba E2E",
                    "mano_dominante": "derecha",
                    "nivel": "intermedio",
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
                    "gesto": "drive",
                    "encuadre": "perfil",
                    "lado_camara": "izquierda",
                    # Los clips de la Fase B son capturas Apple en cámara lenta (el
                    # contenedor declara 30 fps, la captura real es 240 — decisión 020):
                    # declarar el modo real es justo lo que prueba esta corrida de
                    # punta a punta.
                    "modo_captura": "camara_lenta_240",
                }
            )
            .execute()
            .data[0]
        )

        # El nombre real del archivo (no solo la carpeta) se conserva a propósito: es
        # la clave con la que procesar_video busca el factor de cámara lenta en
        # catalogo.csv (ver app/procesar_video._factor_de_catalogo). Perderlo acá
        # haría que la prueba corriera con factor=1.0 en vez del real.
        ruta_storage = f"{usuario_id}/{uuid.uuid4().hex}/{_CLIP.name}"
        admin.storage.from_("videos").upload(
            ruta_storage, _CLIP.read_bytes(), file_options={"content-type": "video/quicktime"}
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

        # Reporte previo (resto de un intento anterior que falló después de insertarlo): la restricción
        # única de video_id haría fallar el insert y dejar 'fallido' un video que sí se analizó. La
        # decisión 022 hace que procesar_video lo reemplace en vez de chocar con él.
        version_previa = (
            admin.table("versiones_motor")
            .insert({"version_motor": "test-reporte-previo", "backend_pose": "fake"})
            .execute()
            .data[0]
        )
        version_previa_id = version_previa["id"]
        reporte_previo = (
            admin.table("reportes_biomecanicos")
            .insert(
                {
                    "video_id": video["id"],
                    "version_motor_id": version_previa_id,
                    "modo_captura": "normal",
                    "factor_ralentizacion": 1,
                }
            )
            .execute()
            .data[0]
        )

        resultado = procesar_video(admin, video["id"])

        assert resultado["estado"] in ("completado", "parcial")
        assert resultado["reporte_id"]
        assert resultado["reporte_id"] != reporte_previo["id"], "el reporte previo no se reemplazó"
        reportes_del_video = (
            admin.table("reportes_biomecanicos").select("id").eq("video_id", video["id"]).execute().data
        )
        assert [r["id"] for r in reportes_del_video] == [resultado["reporte_id"]]

        fila_video = (
            admin.table("videos")
            .select("estado, fps_real, total_fotogramas, duracion_s, resolucion")
            .eq("id", video["id"])
            .single()
            .execute()
            .data
        )
        assert fila_video["estado"] == resultado["estado"]
        assert fila_video["fps_real"] is not None
        assert fila_video["total_fotogramas"] is not None
        assert fila_video["duracion_s"] is not None
        assert fila_video["resolucion"] is not None

        fila_reporte = (
            admin.table("reportes_biomecanicos")
            .select(
                "video_id, cobertura_auditable_pct, corte_filtro_hz, orden_picos_observado, version_motor_id, "
                "modo_captura, factor_ralentizacion, origen_factor, escala_temporal_conocida"
            )
            .eq("id", resultado["reporte_id"])
            .single()
            .execute()
            .data
        )
        assert fila_reporte["video_id"] == video["id"]
        assert fila_reporte["cobertura_auditable_pct"] is not None
        assert fila_reporte["corte_filtro_hz"] is not None
        assert fila_reporte["version_motor_id"]
        # Trazabilidad (R4) de la escala temporal, congelada en el reporte: lo declarado, el factor
        # (240 declarado / 30 del contenedor = 8) y su origen — visibles sin leer la sesión.
        assert fila_reporte["modo_captura"] == "camara_lenta_240"
        assert float(fila_reporte["factor_ralentizacion"]) == 8.0
        assert fila_reporte["origen_factor"] == "declaracion_usuario"
        assert fila_reporte["escala_temporal_conocida"] is True

        metricas = (
            admin.table("metricas")
            .select("segmento, tipo, valor, auditable")
            .eq("reporte_id", resultado["reporte_id"])
            .execute()
            .data
        )
        assert len(metricas) == resultado["metricas_insertadas"]
        for fila_metrica in metricas:
            # R3: una métrica auditable siempre trae valor; nunca se estima.
            assert fila_metrica["auditable"] is True
            assert fila_metrica["valor"] is not None
    finally:
        if ruta_storage:
            admin.storage.from_("videos").remove([ruta_storage])
        admin.auth.admin.delete_user(usuario_id)
        if version_previa_id:
            # Después de borrar al usuario: esa FK no tiene cascada y un reporte aún la apuntaría.
            admin.table("versiones_motor").delete().eq("id", version_previa_id).execute()
        # La fila de versiones_motor real NO se borra: a diferencia del resto de los datos de
        # este test, es una fila legítima de referencia (qué versión del motor existe), no
        # un dato sintético — la reutilizan corridas futuras, de prueba o reales, por
        # version_motor + backend_pose (ver app/procesar_video._version_motor_id).
