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
