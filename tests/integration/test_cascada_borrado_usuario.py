"""Prueba de borrado en cascada — Etapa 4.5, tarea 4.5.1, decisión 018 (ajuste 2).

Confirma que borrar un usuario de auth.users se lleva en cascada todos sus datos
relacionales: atleta, sesión, video, reporte por golpe, métrica, alerta y reporte de
sesión. Es el requisito de "eliminar mi cuenta y mis datos"
(docs/ux/maquetas/capturas/Perfil.png, Ley 25.326).

NO verifica el borrado de archivos en Storage: la cascada de Postgres no puede tocarlos,
no son filas de estas tablas (ver el comentario sobre ruta_pdf en
supabase/migrations/20261001090000_esquema_inicial.sql). Queda como pendiente conocido
para cuando la Etapa 7 implemente de verdad "eliminar mi cuenta".

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas.
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

pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_supabase,
    pytest.mark.skipif(
        not (_SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
]


def test_borrar_usuario_arrastra_todos_sus_datos():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-cascada-{uuid.uuid4().hex[:12]}@example.invalid"
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": secrets.token_urlsafe(18), "email_confirm": True}
    ).user.id
    # El trigger de alta (ajuste 3) ya creó la fila en usuarios; no hace falta insertarla.

    # Todo lo que sigue puede fallar (inserts, asserts) y tiene que dejar igual el usuario de
    # prueba borrado: si algo revienta a mitad de camino sin este try/finally, queda una cuenta
    # huérfana en el proyecto — exactamente lo que pasó en la corrida real contra este esquema
    # antes de que service_role tuviera sus GRANT (decisión 018). usuario_borrado rastrea si la
    # prueba ya lo borró como parte de lo que está probando, para no borrarlo dos veces.
    usuario_borrado = False
    version_motor_id = None
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": "Atleta de prueba cascada",
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
                    "encuadre": "tres_cuartos",
                    "lado_camara": "derecha",
                    "modo_captura": "normal",
                }
            )
            .execute()
            .data[0]
        )
        video = (
            admin.table("videos")
            .insert(
                {
                    "sesion_id": sesion["id"],
                    "usuario_id": usuario_id,
                    "ruta_almacenamiento": "privado/cascada-no-existe.mp4",
                }
            )
            .execute()
            .data[0]
        )
        version_motor = (
            admin.table("versiones_motor")
            .insert({"version_motor": "test-cascada", "backend_pose": "fake"})
            .execute()
            .data[0]
        )
        version_motor_id = version_motor["id"]
        reporte = (
            admin.table("reportes_biomecanicos")
            .insert(
                {
                    "video_id": video["id"],
                    "version_motor_id": version_motor_id,
                    # NOT NULL sin default (migración 20261006): un reporte sin esto no es auditable (R4).
                    "modo_captura": "normal",
                    "factor_ralentizacion": 1,
                }
            )
            .execute()
            .data[0]
        )
        metrica = (
            admin.table("metricas")
            .insert(
                {
                    "reporte_id": reporte["id"],
                    "segmento": "torso",
                    "tipo": "angulo_max",
                    "valor": 45.0,
                    "unidad": "grados",
                    "auditable": True,
                }
            )
            .execute()
            .data[0]
        )
        alerta = (
            admin.table("alertas")
            .insert(
                {
                    "reporte_id": reporte["id"],
                    "codigo": "TEST-CASCADA",
                    "severidad": "correcto",
                    "mensaje_usuario": "Alerta de prueba, no real.",
                }
            )
            .execute()
            .data[0]
        )
        reporte_sesion = (
            admin.table("reportes_sesion")
            .insert({"sesion_id": sesion["id"], "estado_puntaje": "sin_referencia"})
            .execute()
            .data[0]
        )

        filas_de_prueba = {
            "atletas": atleta["id"],
            "sesiones": sesion["id"],
            "videos": video["id"],
            "reportes_biomecanicos": reporte["id"],
            "metricas": metrica["id"],
            "alertas": alerta["id"],
            "reportes_sesion": reporte_sesion["id"],
        }

        for tabla, id_fila in filas_de_prueba.items():
            assert len(admin.table(tabla).select("id").eq("id", id_fila).execute().data) == 1, (
                f"setup inválido: {tabla} no tiene la fila de prueba antes de borrar"
            )

        admin.auth.admin.delete_user(usuario_id)
        usuario_borrado = True

        for tabla, id_fila in filas_de_prueba.items():
            restante = admin.table(tabla).select("id").eq("id", id_fila).execute().data
            assert restante == [], f"{tabla}: la fila sobrevivió al borrado del usuario (no cascadeó)"

        assert admin.table("usuarios").select("id").eq("id", usuario_id).execute().data == [], (
            "la fila de usuarios sobrevivió al borrado de auth.users"
        )
    finally:
        if not usuario_borrado:
            admin.auth.admin.delete_user(usuario_id)
        if version_motor_id:
            admin.table("versiones_motor").delete().eq("id", version_motor_id).execute()
