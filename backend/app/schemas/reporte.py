"""Contrato del reporte — estructura JSON de salida del sistema.

CONGELADO EN LA ETAPA 0. Transcribe el Anexo A de ``docs/plan-desarrollo.md``.
Todo lo demás (motor, API, interfaz) se construye contra esta estructura, así que
cambiarla es una decisión de arquitectura: debe quedar registrada en
``docs/decisiones/`` y comunicada a las dos puntas (motor e interfaz).

Notas de diseño (ver ``docs/decisiones/003-estructura-monorepo.md``):

* ``extra="forbid"``: si llega un campo que el contrato no declara, la validación
  falla en vez de ignorarlo en silencio. Un contrato congelado tiene que ser
  estricto para servir de algo.
* Los campos que el motor puede no poder medir son ``... | None`` y su valor es
  ``None``, nunca un número estimado (regla R3 del CLAUDE.md: "cuando una métrica
  no es auditable, su valor es null; nunca se estima ni se rellena").
* Las confianzas van en el rango [0, 1]; los porcentajes en [0, 100]. Son
  restricciones de dominio, no del Anexo A, pero hacen que el contrato detecte
  datos imposibles.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# --- Vocabularios cerrados -------------------------------------------------------

Gesto = Literal["saque", "drive", "reves"]
Segmento = Literal["pelvis", "torso", "brazo"]
Severidad = Literal["correcto", "atencion", "no_auditable"]


class _Base(BaseModel):
    """Base común: prohíbe campos no declarados en todos los modelos del contrato."""

    model_config = ConfigDict(extra="forbid")


# --- Trazabilidad (regla R4: de dónde salió cada número) -----------------------

class Filtro(_Base):
    tipo: str
    orden: int = Field(ge=1)
    corte_hz: float = Field(gt=0.0)
    fase_cero: bool


class Trazabilidad(_Base):
    version_motor: str
    backend_pose: str
    filtro: Filtro
    fps_real: float = Field(gt=0.0)
    apto_fase_rapida: bool


# --- Cobertura auditable -------------------------------------------------------

class TramoNoAuditable(_Base):
    desde_s: float = Field(ge=0.0)
    hasta_s: float = Field(ge=0.0)
    motivo: str


class Cobertura(_Base):
    auditable_pct: float = Field(ge=0.0, le=100.0)
    tramos_no_auditables: list[TramoNoAuditable] = Field(default_factory=list)


# --- Segmentación en repeticiones --------------------------------------------

class Segmentacion(_Base):
    metodo: str
    repeticiones_marcadas: int = Field(ge=0)
    repeticiones_auditables: int = Field(ge=0)


# --- Secuenciación (el corazón del sistema) ----------------------------------

class Pico(_Base):
    segmento: Segmento
    instante_s: float = Field(ge=0.0)
    velocidad: float
    unidad: str
    confianza: float = Field(ge=0.0, le=1.0)


class RepeticionSecuenciacion(_Base):
    indice: int = Field(ge=1)
    desde_s: float = Field(ge=0.0)
    hasta_s: float = Field(ge=0.0)
    auditable: bool
    # Cuando la repetición no es auditable, estos tres quedan en None.
    orden_observado: list[Segmento] | None = None
    correcto: bool | None = None
    motivo_no_auditable: str | None = None
    picos: list[Pico] = Field(default_factory=list)


class ResumenSecuenciacion(_Base):
    repeticiones_correctas: int = Field(ge=0)
    repeticiones_evaluadas: int = Field(ge=0)
    orden_predominante: list[Segmento]
    dispersion_instante_pico_torso_ms: float = Field(ge=0.0)


class Secuenciacion(_Base):
    orden_esperado: list[Segmento]
    repeticiones: list[RepeticionSecuenciacion]
    resumen: ResumenSecuenciacion


# --- Métricas articulares ----------------------------------------------------

class Metrica(_Base):
    nombre: str
    # None cuando auditable=False. Nunca se estima.
    valor: float | None
    unidad: str
    confianza: float = Field(ge=0.0, le=1.0)
    auditable: bool


# --- Comparación del jugador consigo mismo ----------------------------------

class ComparacionPropia(_Base):
    sesion_anterior_id: UUID
    desfase_torso_ms: int
    direccion: str


# --- Observaciones de nivel 1 (veredicto) ----------------------------------

class Observacion(_Base):
    severidad: Severidad
    texto: str
    # Presentes solo cuando la observación se apoya en un número y una fuente
    # (regla R4: toda alerta responde "qué magnitud" y "qué fuente").
    fundamento: str | None = None
    referencia: str | None = None


# --- Artefactos generados --------------------------------------------------

class Artefactos(_Base):
    overlay_url: str
    pdf_url: str


# --- Reporte (raíz del contrato) -----------------------------------------

class Reporte(_Base):
    reporte_id: UUID
    video_id: UUID
    gesto: Gesto
    creado_en: datetime

    trazabilidad: Trazabilidad
    cobertura: Cobertura
    segmentacion: Segmentacion
    secuenciacion: Secuenciacion
    metricas: list[Metrica]
    # None cuando no hay sesión previa con la cual comparar.
    comparacion_propia: ComparacionPropia | None = None
    observaciones: list[Observacion]
    artefactos: Artefactos
