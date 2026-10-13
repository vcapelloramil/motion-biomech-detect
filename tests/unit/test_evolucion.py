"""``serie_de_evolucion`` y ``GET /evolucion`` — un jugador frente a sí mismo (paso 6). Puras / cliente de Supabase falso, sin red.

Lo que importa: usa la MISMA definición de "medido" y de "mismo orden" que la vista de sesión; no emite veredicto; no inventa una variación
habitual con pocos golpes; y declara lo que hace dudosa la comparación (otro lado de la cámara, otra versión del motor)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.consistencia import serie_de_evolucion
from app.main import app
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado


def _reporte(sep, t_pelvis=0.30, t_torso=0.40, version="0.5.3"):
    return {
        "trazabilidad": {"version_motor": version, "tolerancia_orden_ms": 8.33},
        "secuenciacion": {
            "repeticiones": [
                {
                    "auditable": True,
                    "picos": [
                        {"segmento": "pelvis", "instante_s": t_pelvis, "confianza": 0.9},
                        {"segmento": "torso", "instante_s": t_torso, "confianza": 0.9},
                    ],
                }
            ]
        },
        "metricas": [{"nombre": "separacion_cadera_hombro_max", "valor": sep, "auditable": True}],
    }


def _sesion(sid, fecha, valores, lado="derecha", version="0.5.3"):
    golpes = [{"video_id": f"{sid}-{i}", "estado": "completado", "reporte": _reporte(v, version=version)} for i, v in enumerate(valores)]
    return {"sesion_id": sid, "fecha": fecha, "lado_camara": lado, "golpes": golpes}


def test_sin_sesiones_no_inventa_nada():
    r = serie_de_evolucion([])
    assert r["sesiones"] == [] and r["cambio_separacion"] is None and r["variacion_habitual"] is None


def test_una_sola_sesion_no_tiene_cambio():
    r = serie_de_evolucion([_sesion("s1", "2026-09-24", [28, 30, 31, 33, 29, 30])])
    assert len(r["sesiones"]) == 1 and r["cambio_separacion"] is None
    assert r["variacion_habitual"] is not None            # la dispersión de esa sesión
    assert r["centro_habitual"] is None                    # con menos de 3 sesiones no hay "centro" propio


def test_dos_sesiones_dentro_de_la_variacion_habitual_se_mantienen():
    r = serie_de_evolucion([
        _sesion("s1", "2026-09-24", [28, 30, 31, 33, 29, 30]),
        _sesion("s2", "2026-09-25", [29, 31, 32, 34, 30, 31]),
    ])
    c = r["cambio_separacion"]
    assert c["delta"] == pytest.approx(1.0, abs=0.01) and c["dentro_de_lo_habitual"] is True


def test_un_cambio_mayor_que_la_variacion_habitual_se_dice_sin_juzgarlo():
    r = serie_de_evolucion([
        _sesion("s1", "2026-09-24", [29, 30, 30.5, 31, 31.5, 30]),
        _sesion("s2", "2026-09-30", [36, 37, 37.5, 38, 38.5, 37]),
    ])
    c = r["cambio_separacion"]
    assert c["delta"] > 5 and c["dentro_de_lo_habitual"] is False
    texto = str(r)
    for prohibido in ("mejor", "peor", "mejoró", "empeoró", "correcto"):
        assert prohibido not in texto


def test_con_tres_sesiones_aparece_el_centro_habitual():
    r = serie_de_evolucion([
        _sesion("s1", "2026-09-20", [30, 31, 29, 30, 31, 30]),
        _sesion("s2", "2026-09-24", [31, 32, 30, 31, 32, 31]),
        _sesion("s3", "2026-09-25", [29, 30, 28, 29, 30, 29]),
    ])
    assert r["centro_habitual"] == pytest.approx(30.5, abs=1.0)


def test_una_sesion_sin_dato_es_un_hueco_y_no_se_interpola():
    sin_dato = {"sesion_id": "s2", "fecha": "2026-09-25", "lado_camara": "derecha", "golpes": [{"video_id": "x", "estado": "fallido", "reporte": None}]}
    r = serie_de_evolucion([
        _sesion("s1", "2026-09-24", [28, 30, 31, 33]),
        sin_dato,
        _sesion("s3", "2026-09-26", [29, 31, 32, 34]),
    ])
    assert [f["separacion_cadera_hombro"]["mediana"] is None for f in r["sesiones"]] == [False, True, False]
    # el cambio compara las dos últimas sesiones CON dato: la 1 y la 3
    assert r["cambio_separacion"]["anterior"] == pytest.approx(30.5, abs=0.1)


def test_declara_otro_lado_de_camara_y_otra_version_del_motor():
    r = serie_de_evolucion([
        _sesion("s1", "2026-09-24", [30, 31, 29, 30], lado="derecha", version="0.5.0"),
        _sesion("s2", "2026-09-25", [30, 31, 29, 30], lado="izquierda", version="0.5.3"),
    ])
    assert r["lados_de_camara"] == ["derecha", "izquierda"]
    assert r["mezcla_de_versiones"] is True and r["versiones_motor"] == ["0.5.0", "0.5.3"]


def test_los_empates_cuentan_como_medidos_en_la_serie():
    s = _sesion("s1", "2026-09-24", [30, 31, 29, 30])
    for g in s["golpes"]:
        g["reporte"]["secuenciacion"]["repeticiones"][0]["picos"][1]["instante_s"] = 0.304   # 4 ms: empate
        g["reporte"]["secuenciacion"]["repeticiones"][0]["auditable"] = False
    f = serie_de_evolucion([s])["sesiones"][0]
    assert f["golpes"]["medidos"] == 4 and f["golpes"]["con_orden_distinguible"] == 0
    assert f["orden"]["ordenables"] == 0 and f["orden"]["suficiente"] is False


# --- el endpoint -----------------------------------------------------------------------------------------------------------------------------

_USUARIO = "11111111-1111-4111-8111-111111111111"


class _Q:
    def __init__(self, data):
        self.data, self.filtros = data, {}

    def select(self, *_a, **_k):
        return self

    def eq(self, c, v):
        self.filtros[c] = v
        return self

    def order(self, *_a, **_k):
        return self

    def execute(self):
        return SimpleNamespace(data=self.data)


class _Admin:
    def __init__(self, filas):
        self.q = _Q(filas)

    def table(self, nombre):
        assert nombre == "sesiones"
        return self.q


@pytest.fixture
def cliente():
    def _armar(admin):
        app.dependency_overrides[get_admin_client] = lambda: admin
        app.dependency_overrides[usuario_autenticado] = lambda: UsuarioAutenticado(id=_USUARIO)
        return TestClient(app)

    yield _armar
    app.dependency_overrides.clear()


def _fila(sid, fecha, valores):
    return {
        "id": sid, "fecha": fecha, "creado_en": fecha + "T12:00:00Z", "lado_camara": "derecha",
        "videos": [{"id": f"{sid}-{i}", "estado": "completado", "reportes_biomecanicos": [{"reporte": _reporte(v)}]} for i, v in enumerate(valores)],
    }


def test_el_endpoint_devuelve_la_serie_y_filtra_por_el_usuario_del_token(cliente):
    admin = _Admin([_fila("s1", "2026-09-24", [28, 30, 31, 33]), _fila("s2", "2026-09-25", [29, 31, 32, 34])])
    r = cliente(admin).get("/evolucion", params={"atleta_id": "a1", "gesto": "saque", "encuadre": "tres_cuartos"})
    assert r.status_code == 200
    d = r.json()
    assert [s["sesion_id"] for s in d["sesiones"]] == ["s1", "s2"] and d["cambio_separacion"]["dentro_de_lo_habitual"] is True
    assert admin.q.filtros["usuario_id"] == _USUARIO and admin.q.filtros["atleta_id"] == "a1"
    assert admin.q.filtros["gesto"] == "saque" and admin.q.filtros["encuadre"] == "tres_cuartos"


def test_un_gesto_desconocido_es_422(cliente):
    r = cliente(_Admin([])).get("/evolucion", params={"atleta_id": "a1", "gesto": "volea", "encuadre": "perfil"})
    assert r.status_code == 422


def test_sin_sesion_iniciada_es_401():
    app.dependency_overrides.clear()
    r = TestClient(app).get("/evolucion", params={"atleta_id": "a1", "gesto": "saque", "encuadre": "perfil"})
    assert r.status_code == 401
