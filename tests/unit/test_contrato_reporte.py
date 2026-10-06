"""El contrato del reporte (Anexo A) valida el ejemplo y rechaza datos mal formados.

Criterio de aceptación de la Etapa 0: "El contrato del reporte valida un ejemplo
de datos ficticios sin errores".
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.reporte import Reporte

_EJEMPLO = Path(__file__).resolve().parents[2] / "docs" / "contrato-reporte.ejemplo.json"


def _ejemplo_dict() -> dict:
    return json.loads(_EJEMPLO.read_text(encoding="utf-8"))


def test_el_ejemplo_valida():
    datos = _ejemplo_dict()
    reporte = Reporte.model_validate(datos)
    assert reporte.gesto == "saque"
    assert reporte.secuenciacion.orden_esperado == ["pelvis", "torso", "brazo"]


def test_roundtrip_json():
    # Serializar y volver a validar no debe perder ni cambiar nada.
    reporte = Reporte.model_validate(_ejemplo_dict())
    otra_vez = Reporte.model_validate(json.loads(reporte.model_dump_json()))
    assert otra_vez == reporte


def test_metrica_no_auditable_admite_valor_null():
    # Regla R3: si no es auditable, valor = None (no un número estimado).
    reporte = Reporte.model_validate(_ejemplo_dict())
    no_auditables = [m for m in reporte.metricas if not m.auditable]
    assert no_auditables and all(m.valor is None for m in no_auditables)


def test_rechaza_campo_desconocido():
    datos = _ejemplo_dict()
    datos["campo_que_no_existe"] = 123
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_rechaza_confianza_fuera_de_rango():
    datos = _ejemplo_dict()
    datos["metricas"][0]["confianza"] = 1.5  # fuera de [0, 1]
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_rechaza_gesto_fuera_del_alcance():
    datos = _ejemplo_dict()
    datos["gesto"] = "volea"  # fuera del alcance declarado (R5)
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_trazabilidad_exige_escala_temporal_conocida():
    # Agregado en la Etapa 1 (ver docs/decisiones/004): distingue una frecuencia
    # medida de una estimada. Es obligatorio, no tiene default.
    datos = _ejemplo_dict()
    del datos["trazabilidad"]["escala_temporal_conocida"]
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


# --- Contrato v1.0 (decisión 024) ---------------------------------------------------------------


def test_severidad_tiene_los_cuatro_estados_de_R3():
    from typing import get_args

    from app.schemas.reporte import Severidad

    assert set(get_args(Severidad)) == {"correcto", "desvio_leve", "alerta_de_carga", "no_auditable"}


def test_rechaza_el_estado_viejo_atencion():
    datos = _ejemplo_dict()
    datos["observaciones"][0]["severidad"] = "atencion"  # renombrado a desvio_leve en la v1.0
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_severidad_del_contrato_coincide_con_la_de_la_base():
    """alertas.severidad (decisión 018) y el contrato dicen lo mismo: si uno cambia y el otro no,
    esto avisa antes de que un reporte válido se rechace al guardarlo."""
    import re
    from typing import get_args

    from app.schemas.reporte import Severidad

    sql = (Path(__file__).resolve().parents[2] / "supabase/migrations/20261001090000_esquema_inicial.sql").read_text(
        encoding="utf-8"
    )
    en_la_base = set(re.search(r"check \(severidad in \(([^)]*)\)\)", sql).group(1).replace("'", "").replace(" ", "").split(","))
    assert en_la_base == set(get_args(Severidad))


def test_modo_captura_y_factor_son_obligatorios_y_cerrados():
    for campo in ("modo_captura", "factor_ralentizacion", "origen_factor"):
        datos = _ejemplo_dict()
        del datos["trazabilidad"][campo]
        with pytest.raises(ValidationError):
            Reporte.model_validate(datos)
    for campo, valor in (("modo_captura", "turbo"), ("factor_ralentizacion", 0.5), ("origen_factor", "catalogo")):
        datos = _ejemplo_dict()
        datos["trazabilidad"][campo] = valor
        with pytest.raises(ValidationError):
            Reporte.model_validate(datos)


def test_modo_normal_con_factor_uno_es_valido():
    datos = _ejemplo_dict()
    datos["trazabilidad"].update(modo_captura="normal", factor_ralentizacion=1.0, fps_real=60.0)
    assert Reporte.model_validate(datos).trazabilidad.factor_ralentizacion == 1.0


def test_la_version_del_contrato_es_obligatoria_y_conocida():
    from app.schemas.reporte import VERSION_CONTRATO

    assert Reporte.model_validate(_ejemplo_dict()).version_contrato == VERSION_CONTRATO == "1.0"
    datos = _ejemplo_dict()
    del datos["version_contrato"]
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)
    datos = _ejemplo_dict()
    datos["version_contrato"] = "0.9"
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_artefactos_son_opcionales_en_la_primera_entrega():
    """Sin video con esqueleto ni PDF: None = no generado. Los fotogramas clave sí pueden venir."""
    datos = _ejemplo_dict()
    datos["artefactos"] = {}
    r = Reporte.model_validate(datos)
    assert r.artefactos.overlay_ruta is None and r.artefactos.pdf_ruta is None
    assert r.artefactos.fotogramas_clave == []


def test_fotograma_clave_guarda_una_ruta_y_no_una_url_ni_una_ruta_vacia():
    datos = _ejemplo_dict()
    datos["artefactos"]["fotogramas_clave"][0]["ruta"] = ""
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)
    datos = _ejemplo_dict()
    datos["artefactos"]["fotogramas_clave"][0]["segmento"] = "rodilla"  # fuera de pelvis/torso/brazo
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_las_urls_viejas_ya_no_existen_en_artefactos():
    datos = _ejemplo_dict()
    datos["artefactos"]["overlay_url"] = "https://ejemplo.invalido/x.mp4"
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_dispersion_es_none_con_un_solo_golpe():
    """Un video = un golpe: no hay dispersión que calcular, y un 0 sería un dato inventado (R3)."""
    datos = _ejemplo_dict()
    datos["secuenciacion"]["resumen"]["dispersion_instante_pico_torso_ms"] = None
    assert Reporte.model_validate(datos).secuenciacion.resumen.dispersion_instante_pico_torso_ms is None
    datos["secuenciacion"]["resumen"]["dispersion_instante_pico_torso_ms"] = -1
    with pytest.raises(ValidationError):
        Reporte.model_validate(datos)


def test_el_vocabulario_de_modo_captura_coincide_con_la_base():
    import re
    from typing import get_args

    from app.schemas.reporte import ModoCaptura

    sql = (Path(__file__).resolve().parents[2] / "supabase/migrations/20261002000000_modo_captura_y_trazabilidad_escala.sql").read_text(
        encoding="utf-8"
    )
    en_la_base = set(re.search(r"modo_captura in \(([^)]*)\)", sql).group(1).replace("'", "").replace(" ", "").split(","))
    assert en_la_base == set(get_args(ModoCaptura))
