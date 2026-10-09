"""Reintento fallido -> encolado contra Supabase real — decisión 022, pasos (b) y (c).

Cubre lo que las pruebas unitarias (tests/unit/test_reintento.py, test_api_analisis.py) no pueden:
el trigger de la base que bloquea cambiar lo que invalida un análisis, las columnas nuevas
protegidas, y el flujo completo por la API (con el cliente de prueba de FastAPI, que corre la tarea
de fondo antes de responder).

El flujo completo NO corre inferencia de MediaPipe a propósito: usa el clip público de 25 fps
(``fase-a/segmentos/zverev_saque_lateral_01.mp4``), que falla por modo incompatible antes de la
inferencia y, ya corregido a "normal", queda ``parcial`` por R1 (< 120 fps), también sin inferencia.
Así recorre fallido -> corregir -> reintento -> parcial en segundos. El análisis completo con
inferencia lo prueba test_procesar_video_e2e.py.

Requiere supabase/migrations/20261007000000_reintento_fallido.sql aplicada. Se salta sin
credenciales configuradas.
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import (
        get_supabase_anon_key,
        get_supabase_service_role_key,
        get_supabase_url,
    )

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_ANON_KEY = get_supabase_anon_key()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_ANON_KEY = _SUPABASE_SERVICE_ROLE_KEY = None

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
        not (_SUPABASE_URL and _SUPABASE_ANON_KEY and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_ANON_KEY / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
]

_MENSAJE_BLOQUEO = "sesion_con_golpes_analizados"


@pytest.fixture(scope="module")
def entorno():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-reintento-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    ).user.id
    rutas_storage: list[str] = []
    # Todo lo que puede fallar va dentro del try: el finally borra igual el usuario (se lleva en
    # cascada atletas, sesiones, videos y reportes) y los objetos de Storage subidos.
    try:
        atletas = [
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": f"Atleta de prueba reintento {n}",
                    "mano_dominante": "derecha",
                    "nivel": "intermedio",
                }
            )
            .execute()
            .data[0]["id"]
            for n in (1, 2)
        ]
        cliente = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente.auth.sign_in_with_password({"email": email, "password": password})
        yield {
            "admin": admin,
            "cliente": cliente,
            "usuario_id": usuario_id,
            "atleta_id": atletas[0],
            "otro_atleta_id": atletas[1],
            "rutas_storage": rutas_storage,
        }
    finally:
        if rutas_storage:
            admin.storage.from_("videos").remove(rutas_storage)
        admin.auth.admin.delete_user(usuario_id)


def _sesion_y_video(entorno, *, estado=None, modo="camara_lenta_240", ruta="privado/no-existe.mp4"):
    """Una sesión con un video, creados con el cliente admin (que sí puede fijar estado)."""
    admin = entorno["admin"]
    sesion = (
        admin.table("sesiones")
        .insert(
            {
                "usuario_id": entorno["usuario_id"],
                "atleta_id": entorno["atleta_id"],
                "gesto": "saque",
                "encuadre": "perfil",
                "lado_camara": "izquierda",
                "modo_captura": modo,
            }
        )
        .execute()
        .data[0]
    )
    fila = {"sesion_id": sesion["id"], "usuario_id": entorno["usuario_id"], "ruta_almacenamiento": ruta}
    if estado is not None:
        fila["estado"] = estado
    video = admin.table("videos").insert(fila).execute().data[0]
    return sesion["id"], video["id"]


def _editar_sesion(entorno, sesion_id: str, patch: dict):
    return entorno["cliente"].table("sesiones").update(patch).eq("id", sesion_id).execute()


def _exigir_bloqueo(entorno, sesion_id: str, patch: dict) -> None:
    from postgrest.exceptions import APIError

    with pytest.raises(APIError) as info:
        _editar_sesion(entorno, sesion_id, patch)
    assert info.value.message == _MENSAJE_BLOQUEO, (
        f"se esperaba el bloqueo del trigger y fue {info.value.code}: {info.value.message}"
    )


# --- Trigger: no se cambia lo que invalida un análisis con golpes ya analizados ----------------


@pytest.mark.parametrize("estado", ["encolado", "procesando", "completado", "parcial"])
def test_el_modo_no_se_cambia_con_un_golpe_en_proceso_o_analizado(entorno, estado):
    sesion_id, _ = _sesion_y_video(entorno, estado=estado)
    _exigir_bloqueo(entorno, sesion_id, {"modo_captura": "normal"})
    fila = entorno["admin"].table("sesiones").select("modo_captura").eq("id", sesion_id).single().execute().data
    assert fila["modo_captura"] == "camara_lenta_240"


def test_gesto_encuadre_lado_y_atleta_tampoco_con_un_golpe_analizado(entorno):
    sesion_id, _ = _sesion_y_video(entorno, estado="completado")
    for patch in (
        {"gesto": "drive"},
        {"encuadre": "tres_cuartos"},
        {"lado_camara": "derecha"},
        {"atleta_id": entorno["otro_atleta_id"]},
    ):
        _exigir_bloqueo(entorno, sesion_id, patch)


def test_la_fecha_si_se_corrige_con_un_golpe_analizado(entorno):
    """La fecha de grabación no cambia ningún cálculo: corregirla no invalida nada."""
    sesion_id, _ = _sesion_y_video(entorno, estado="completado")
    resp = _editar_sesion(entorno, sesion_id, {"fecha": "2026-01-02"})
    assert len(resp.data) == 1 and resp.data[0]["fecha"] == "2026-01-02"


@pytest.mark.parametrize("estado", [None, "fallido"], ids=["pendiente", "fallido"])
def test_con_todos_los_golpes_pendientes_o_fallidos_la_declaracion_se_corrige(entorno, estado):
    """Es justo el caso del reintento: nada analizado que contradecir."""
    sesion_id, _ = _sesion_y_video(entorno, estado=estado)
    resp = _editar_sesion(
        entorno, sesion_id, {"modo_captura": "normal", "gesto": "drive", "encuadre": "tres_cuartos"}
    )
    assert len(resp.data) == 1 and resp.data[0]["modo_captura"] == "normal"


def test_un_solo_golpe_analizado_alcanza_para_bloquear(entorno):
    """Con un golpe fallido y otro completado en la misma sesión: se bloquea."""
    sesion_id, _ = _sesion_y_video(entorno, estado="fallido")
    entorno["admin"].table("videos").insert(
        {
            "sesion_id": sesion_id,
            "usuario_id": entorno["usuario_id"],
            "ruta_almacenamiento": "privado/otro.mp4",
            "estado": "completado",
        }
    ).execute()
    _exigir_bloqueo(entorno, sesion_id, {"modo_captura": "normal"})


# --- Las columnas nuevas las escribe el motor, no el usuario -----------------------------------


@pytest.mark.parametrize("patch", [{"intentos": 0}, {"modo_captura_intentado": "normal"}], ids=lambda p: next(iter(p)))
def test_el_usuario_no_escribe_las_columnas_nuevas_del_motor(entorno, patch):
    from postgrest.exceptions import APIError

    _, video_id = _sesion_y_video(entorno, estado="fallido")
    with pytest.raises(APIError) as info:
        entorno["cliente"].table("videos").update(patch).eq("id", video_id).execute()
    assert info.value.code == "42501"


def test_el_motor_puede_registrar_error_inesperado(entorno):
    """El CHECK ampliado acepta el código nuevo (y sigue rechazando uno inventado)."""
    from postgrest.exceptions import APIError

    _, video_id = _sesion_y_video(entorno, estado="fallido")
    tabla = entorno["admin"].table("videos")
    ok = tabla.update({"motivo_fallo": "error_inesperado"}).eq("id", video_id).execute()
    assert ok.data[0]["motivo_fallo"] == "error_inesperado"
    with pytest.raises(APIError):
        tabla.update({"motivo_fallo": "inventado"}).eq("id", video_id).execute()


# --- Flujo completo por la API ------------------------------------------------------------------


@pytest.fixture
def api(monkeypatch, entorno):
    from fastapi.testclient import TestClient

    monkeypatch.setenv("KINETIQ_MAX_INTENTOS", "3")
    from app.main import app

    # Tarea 7.4: la API autentica con el JWT del usuario (el de la sesión que ya inició la fixture `entorno`).
    token = entorno["cliente"].auth.get_session().access_token
    cliente = TestClient(app)

    def _procesar(video_id: str):
        return cliente.post(f"/analisis/{video_id}/procesar", headers={"Authorization": f"Bearer {token}"})

    return _procesar


def _fila_video(entorno, video_id: str) -> dict:
    return (
        entorno["admin"]
        .table("videos")
        .select("estado, motivo_fallo, modo_captura_intentado, intentos, fps_real, apto_fase_rapida")
        .eq("id", video_id)
        .single()
        .execute()
        .data
    )


@pytest.mark.skipif(_CLIP is None, reason="No está fase-a/segmentos/zverev_saque_lateral_01.mp4 en KINETIQ_DATA_DIR")
def test_falla_por_modo_se_corrige_la_declaracion_y_se_reintenta(entorno, api):
    ruta = f"{entorno['usuario_id']}/{uuid.uuid4().hex}/{_CLIP.name}"
    entorno["admin"].storage.from_("videos").upload(
        ruta, _CLIP.read_bytes(), file_options={"content-type": "video/mp4"}
    )
    entorno["rutas_storage"].append(ruta)
    # 25 fps reales declarados cámara lenta a 240: 240/25 = 9,6, no cierra.
    sesion_id, video_id = _sesion_y_video(entorno, modo="camara_lenta_240", ruta=ruta)

    # 1. Primer intento: falla por la declaración, y queda registrado con qué modo se intentó.
    assert api(video_id).status_code == 202
    fila = _fila_video(entorno, video_id)
    assert (fila["estado"], fila["motivo_fallo"]) == ("fallido", "modo_captura_incompatible")
    assert (fila["modo_captura_intentado"], fila["intentos"]) == ("camara_lenta_240", 1)

    # 2. Reintentar sin corregir nada: 409 y no gasta cómputo.
    resp = api(video_id)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "declaracion_sin_cambios", "estado_actual": "fallido"}
    assert _fila_video(entorno, video_id)["intentos"] == 1

    # 3. El usuario corrige la declaración (permitido: el único golpe de la sesión falló) y reintenta.
    assert _editar_sesion(entorno, sesion_id, {"modo_captura": "normal"}).data[0]["modo_captura"] == "normal"
    assert api(video_id).status_code == 202
    fila = _fila_video(entorno, video_id)
    # 25 fps en modo normal: no es un fallo, es R1 (< 120 fps efectivos) -> 'parcial', sin motivo.
    assert fila["estado"] == "parcial"
    assert fila["motivo_fallo"] is None, "el motivo de la corrida anterior no se arrastra"
    assert (fila["modo_captura_intentado"], fila["intentos"]) == ("normal", 2)
    assert float(fila["fps_real"]) == 25.0 and fila["apto_fase_rapida"] is False

    # 4. Un video 'parcial' no se reanaliza, y la sesión ya no deja cambiar el modo.
    resp = api(video_id)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "estado_no_reintentable", "estado_actual": "parcial"}
    _exigir_bloqueo(entorno, sesion_id, {"modo_captura": "camara_lenta_240"})


def test_error_inesperado_deja_codigo_y_se_reintenta_hasta_el_tope(entorno, api):
    # Sin objeto en Storage: la descarga revienta, algo que el usuario no puede corregir.
    _, video_id = _sesion_y_video(entorno, ruta=f"{entorno['usuario_id']}/no-existe/{uuid.uuid4().hex}.mp4")

    for intento in (1, 2, 3):
        assert api(video_id).status_code == 202
        fila = _fila_video(entorno, video_id)
        assert (fila["estado"], fila["motivo_fallo"], fila["intentos"]) == ("fallido", "error_inesperado", intento)

    resp = api(video_id)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "intentos_agotados", "estado_actual": "fallido"}
    assert _fila_video(entorno, video_id)["intentos"] == 3


def test_el_doble_pedido_encola_una_sola_vez(entorno, api):
    """Un video ya encolado (el primer pedido ganó la carrera) responde 409 al segundo."""
    _, video_id = _sesion_y_video(entorno, estado="encolado")
    resp = api(video_id)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "estado_no_reintentable", "estado_actual": "encolado"}
    assert _fila_video(entorno, video_id)["estado"] == "encolado"
