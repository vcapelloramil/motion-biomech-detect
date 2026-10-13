"""``app.consistencia.resumen_de_sesion``: cuánto se parecen entre sí los golpes de una sesión. Pura, sin red.

Lo que importa de esta función no es la estadística (que es simple) sino lo que NO hace: no emite veredicto, no inventa dispersión con
pocos golpes y no mezcla en silencio reportes de motores distintos."""

from __future__ import annotations

from app.consistencia import (
    MIN_GOLPES_APARTA,
    MIN_GOLPES_DISPERSION,
    MIN_ORDENABLES_REPETIBILIDAD,
    resumen_de_sesion,
)


def _reporte(sep: float | None = 30.0, t_pelvis: float = 0.30, t_torso: float = 0.40, version: str = "0.5.3", auditable: bool = True,
             tolerancia_ms: float = 8.33) -> dict:
    return {
        "trazabilidad": {"version_motor": version, "tolerancia_orden_ms": tolerancia_ms},
        "secuenciacion": {
            "repeticiones": [
                {
                    "auditable": auditable,
                    "picos": [
                        {"segmento": "pelvis", "instante_s": t_pelvis},
                        {"segmento": "torso", "instante_s": t_torso},
                    ],
                }
            ]
        },
        "metricas": (
            [{"nombre": "separacion_cadera_hombro_max", "valor": sep, "auditable": True, "unidad": "grados", "confianza": 0.9}]
            if sep is not None
            else []
        ),
    }


def _golpes(reportes: list[dict | None], estado: str = "completado") -> list[dict]:
    return [{"video_id": f"v{i}", "estado": estado if r is not None else "fallido", "reporte": r} for i, r in enumerate(reportes)]


def test_sin_golpes_no_inventa_nada():
    r = resumen_de_sesion([])
    assert r["golpes"] == {"total": 0, "medidos": 0, "no_medibles": 0, "en_analisis": 0}
    assert r["separacion_cadera_hombro"]["mediana"] is None and r["separacion_cadera_hombro"]["dispersion"] is None
    assert r["golpe_tipico"] is None and r["golpes_que_se_apartan"] == []


def test_cuenta_medidos_no_medibles_y_en_analisis():
    golpes = _golpes([_reporte(), _reporte(auditable=False), None]) + [{"video_id": "vq", "estado": "encolado", "reporte": None}]
    assert resumen_de_sesion(golpes)["golpes"] == {"total": 4, "medidos": 1, "no_medibles": 2, "en_analisis": 1}


def test_la_dispersion_solo_aparece_con_suficientes_golpes():
    pocos = resumen_de_sesion(_golpes([_reporte(sep=s) for s in (28, 30, 32)]))["separacion_cadera_hombro"]
    assert pocos["n"] == 3 and pocos["mediana"] == 30.0 and pocos["dispersion"] is None
    assert MIN_GOLPES_DISPERSION == 4
    suf = resumen_de_sesion(_golpes([_reporte(sep=s) for s in (28, 29, 31, 32)]))["separacion_cadera_hombro"]
    assert suf["n"] == 4 and suf["dispersion"] is not None and suf["dispersion"] > 0


def test_una_separacion_no_auditable_no_cuenta():
    r = _reporte(sep=33.0)
    r["metricas"][0]["auditable"] = False
    assert resumen_de_sesion(_golpes([r, _reporte(sep=30.0)]))["separacion_cadera_hombro"]["n"] == 1


def test_repetibilidad_del_orden_cuenta_el_mismo_orden_sin_juzgarlo():
    # 5 golpes ordenables: 4 con la cadera primero y 1 con el tronco primero
    reps = [_reporte(t_pelvis=0.30, t_torso=0.40)] * 4 + [_reporte(t_pelvis=0.40, t_torso=0.30)]
    o = resumen_de_sesion(_golpes(reps))["orden"]
    assert o["ordenables"] == 5 and o["mismo_orden"] == 4 and o["orden_modal"] == ["pelvis", "torso"]
    assert o["suficiente"] is True and MIN_ORDENABLES_REPETIBILIDAD == 5


def test_el_orden_dentro_de_la_tolerancia_no_es_ordenable():
    reps = [_reporte(t_pelvis=0.300, t_torso=0.305)] * 3 + [_reporte(t_pelvis=0.30, t_torso=0.40)]
    o = resumen_de_sesion(_golpes(reps))["orden"]
    assert o["medidos"] == 4 and o["ordenables"] == 1 and o["suficiente"] is False


def test_el_golpe_tipico_es_el_mas_cercano_a_la_mediana_no_el_mejor():
    reps = [_reporte(sep=s) for s in (20.0, 30.0, 31.0, 45.0)]
    r = resumen_de_sesion(_golpes(reps))
    # mediana = 30,5; los más cercanos son v1 (30) y v2 (31): a igual distancia, el de menor id
    assert r["golpe_tipico"] == "v1"


def test_el_golpe_que_se_aparta_se_informa_solo_con_suficientes_golpes_y_lejos_de_los_demas():
    cercanos = [29.0, 30.0, 30.5, 31.0, 31.5]
    r = resumen_de_sesion(_golpes([_reporte(sep=s) for s in cercanos + [50.0]]))
    assert r["golpes_que_se_apartan"] == ["v5"]
    # con menos golpes que el mínimo no se marca ninguno, aunque uno esté lejos
    pocos = resumen_de_sesion(_golpes([_reporte(sep=s) for s in (29.0, 30.0, 31.0, 50.0)]))
    assert pocos["golpes_que_se_apartan"] == [] and MIN_GOLPES_APARTA == 5


def test_un_golpe_apenas_distinto_no_se_marca_por_el_piso_de_dispersion():
    r = resumen_de_sesion(_golpes([_reporte(sep=s) for s in (30.0, 30.0, 30.0, 30.0, 30.0, 31.5)]))
    assert r["golpes_que_se_apartan"] == []      # 1,5° con dispersión ~0: el piso de 1° exige > 3°


def test_declara_la_mezcla_de_versiones_del_motor():
    r = resumen_de_sesion(_golpes([_reporte(version="0.5.0"), _reporte(version="0.5.3")]))
    assert r["versiones_motor"] == ["0.5.0", "0.5.3"] and r["mezcla_de_versiones"] is True
    assert resumen_de_sesion(_golpes([_reporte(), _reporte()]))["mezcla_de_versiones"] is False


def test_no_emite_ningun_veredicto():
    texto = str(resumen_de_sesion(_golpes([_reporte(sep=s) for s in (28, 29, 31, 32, 30)])))
    for prohibido in ("correcto", "desvio", "alerta", "mejor", "peor"):
        assert prohibido not in texto
