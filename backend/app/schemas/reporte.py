"""Contrato del reporte — estructura JSON de salida del sistema.

CONGELADO. Nació en la Etapa 0 (Anexo A de ``docs/plan-desarrollo.md``) y se actualizó UNA vez
antes de generar cualquier JSON real: contrato v1.0, decisión 024. El Anexo A ya no es la
fuente; lo es este archivo junto con ``docs/contrato-reporte.ejemplo.json``. Todo lo demás
(motor, API, interfaz) se construye contra esta estructura, así que cambiarla es una decisión de
arquitectura: debe quedar registrada en ``docs/decisiones/``, subir ``version_contrato`` y
comunicarse a las dos puntas (motor e interfaz). Un reporte guardado declara con qué versión
se escribió (RNF-02).

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

# v1.1 (decisión 029, aditiva): la tasa puede salir de las marcas de tiempo del archivo y se informa qué regularización temporal se hizo.
# v1.2 (decisión 031, aditiva): una observación puede ser "sin_evaluar" (se documenta un dato sin emitir juicio).
# Un reporte guardado como "1.0" o "1.1" sigue siendo válido: lo nuevo es opcional o un valor más de un vocabulario.
VERSION_CONTRATO = "1.2"

Gesto = Literal["saque", "drive", "reves"]
Segmento = Literal["pelvis", "torso", "brazo"]
# Los CUATRO estados de R3 (CLAUDE.md), los mismos que alertas.severidad en la base (decisión 018).
# Antes eran tres ("atencion"): "atencion" se reemplazó por "desvio_leve" y se sumó "alerta_de_carga".
Severidad = Literal["correcto", "desvio_leve", "alerta_de_carga", "no_auditable"]
# Lo que puede llevar una OBSERVACIÓN. "sin_evaluar" NO es un quinto estado del semáforo (R3 sigue teniendo cuatro y `Severidad` es
# la que coincide con alertas.severidad): es la etiqueta de un dato que se documenta sin juicio, la misma que el brazo en la decisión
# 011. No significa "no se pudo medir" (eso es `no_auditable`): se midió y no hay respaldo para evaluarlo (decisión 031).
SeveridadObservacion = Literal["correcto", "desvio_leve", "alerta_de_carga", "no_auditable", "sin_evaluar"]
# Mismos vocabularios cerrados que sesiones.modo_captura y reportes_biomecanicos.origen_factor.
ModoCaptura = Literal["normal", "camara_lenta_120", "camara_lenta_240"]
OrigenFactor = Literal["declaracion_usuario", "marcas_de_tiempo"]


class _Base(BaseModel):
    """Base común: prohíbe campos no declarados en todos los modelos del contrato."""

    model_config = ConfigDict(extra="forbid")


# --- Trazabilidad (regla R4: de dónde salió cada número) -----------------------

class Filtro(_Base):
    tipo: str
    orden: int = Field(ge=1)
    corte_hz: float = Field(gt=0.0)
    fase_cero: bool


class Regularizacion(_Base):
    """Interpolación a grilla uniforme antes de filtrar (R4: cuántos puntos no son una medición sino una interpolación)."""

    fotogramas_fuente: int = Field(ge=0)
    puntos_de_la_grilla: int = Field(ge=0)
    puntos_copiados: int = Field(ge=0)
    puntos_interpolados: int = Field(ge=0)
    puntos_interpolados_pct: float = Field(ge=0.0, le=100.0)
    puntos_sin_dato: int = Field(ge=0)
    fps_grilla: float = Field(gt=0.0)
    fps_real_medio: float = Field(gt=0.0)
    hueco_maximo_ms: float = Field(ge=0.0)


class Trazabilidad(_Base):
    version_motor: str
    backend_pose: str
    filtro: Filtro
    fps_real: float = Field(gt=0.0)
    apto_fase_rapida: bool
    # False cuando fps_real es una estimación (material descargado, cámara lenta con
    # factor cronometrado a ojo): sirve para el ORDEN de los picos, no para
    # velocidades absolutas. Ver docs/decisiones/001 y 004. Regla R3 aplicada al dato.
    escala_temporal_conocida: bool
    # Cómo se obtuvo la escala temporal (decisión 020, R4): lo que declaró el usuario, el factor
    # de ralentización resultante (1 en modo normal) y su origen. Con esto la cuenta se rehace:
    # fps_real = fps del contenedor (normalizado NTSC) x factor_ralentizacion.
    modo_captura: ModoCaptura
    factor_ralentizacion: float = Field(ge=1.0)
    origen_factor: OrigenFactor
    # --- v1.1 (decisión 029): la tasa real se LEE del archivo -------------------------------------------------------------------
    # fps_real (arriba) es la tasa real MEDIA medida; fps_nominal es la de las marcas (240 en un iPhone, con ~17 % de fotogramas
    # perdidos). Ninguna de las dos se supone: salen de las marcas de tiempo de los fotogramas visibles. None en un horneado.
    fps_nominal: float | None = Field(default=None, gt=0.0)
    fotogramas_perdidos_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    regularizacion: "Regularizacion | None" = None


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
    # `orden_observado` es el de la cadena completa (se documenta siempre que se midió). `correcto` es el veredicto del par
    # cadera -> tronco, el único con referencia en la literatura (decisión 011), y solo existe donde el gesto y el encuadre
    # tienen referencia del orden esperado y el Criterio 1 cumplido (decisión 031); None = "sin evaluar" o no ordenable.
    orden_observado: list[Segmento] | None = None
    correcto: bool | None = None
    motivo_no_auditable: str | None = None
    picos: list[Pico] = Field(default_factory=list)


class ResumenSecuenciacion(_Base):
    repeticiones_correctas: int = Field(ge=0)
    repeticiones_evaluadas: int = Field(ge=0)
    orden_predominante: list[Segmento]
    # None con menos de dos repeticiones evaluadas: una dispersión no se define con un solo valor, y
    # un 0 sería un dato inventado (R3). Con un video = un golpe (MVP) es lo habitual.
    dispersion_instante_pico_torso_ms: float | None = Field(default=None, ge=0.0)


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
    severidad: SeveridadObservacion
    texto: str
    # Presentes solo cuando la observación se apoya en un número y una fuente
    # (regla R4: toda alerta responde "qué magnitud" y "qué fuente").
    fundamento: str | None = None
    referencia: str | None = None


# --- Artefactos generados --------------------------------------------------

class FotogramaClave(_Base):
    """Uno de los "tres momentos del golpe" de la vista simple (especificación de frontend §6):
    el fotograma, con el esqueleto superpuesto, en el pico de ese segmento."""

    segmento: Segmento
    # Relativo al inicio de la ventana, igual que Pico.instante_s.
    instante_s: float = Field(ge=0.0)
    # Ruta del objeto en Storage, NO una URL: una URL firmada vence, y el reporte se guarda. El
    # cliente firma la URL al leerlo (decisión 025).
    ruta: str = Field(min_length=1)


class Artefactos(_Base):
    # Rutas en Storage (no URLs, ver FotogramaClave.ruta). Opcionales: el video con esqueleto y el
    # PDF no existen en la primera entrega (decisión 024); None = no generado, no "vacío".
    overlay_ruta: str | None = None
    pdf_ruta: str | None = None
    fotogramas_clave: list[FotogramaClave] = Field(default_factory=list)


# --- Reporte (raíz del contrato) -----------------------------------------

class Reporte(_Base):
    version_contrato: Literal["1.0", "1.1", "1.2"]
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
