"""E5.4 mínimo — ensambla el reporte del contrato v1.1 (``app.schemas.reporte``) a partir de lo que ya
calculó el motor (decisiones 024 y 030, pieza 2 del plan de punta a punta).

Función **pura**: no toca Supabase, archivos ni el reloj. Recibe los resultados del pipeline y devuelve un
``dict`` listo para guardar en ``reportes_biomecanicos.reporte`` (jsonb) **después de validarlo** contra el
contrato: un reporte que no cumple el contrato no se guarda (``pydantic.ValidationError``), en vez de llegar
roto al frontend.

Qué agrega este módulo sobre lo que el motor ya devolvía:

* **Confianza por pico** (R4): el contrato la exige y el motor no la calcula. Es la media de la ``confianza`` de
  las articulaciones que definen el segmento (las del vector director) en el fotograma del pico; sobre el
  espacio que filtró E3 (métrico si existe, imagen si no). Un pico interpolado por la regularización lleva la
  confianza interpolada de sus vecinos.
* **Veredicto del par cadera -> tronco, solo donde hay respaldo** (decisión 031, ver ``RESPALDO_POR_GRUPO``): referencia del
  orden esperado **y** Criterio 1 cumplido para ese gesto y encuadre. Donde falta alguna, el orden se documenta como
  ``sin_evaluar`` (la misma etiqueta del brazo, decisión 011), que no es ``no_auditable`` ("no se pudo medir").
* **Observaciones** en el vocabulario de R2 (se observa / se documenta / no se pudo medir); no hay verbos ni
  términos prohibidos, y una prueba lo verifica.
* **Tramos no auditables** en segundos, unidos por superposición, solo de las articulaciones de la cadena.

Lo que **no** hay todavía y por lo tanto no se inventa: alertas con umbral (E5.1: sin referencia bibliográfica
no hay alerta), puntaje de rendimiento, comparación con la sesión anterior y el PDF: ``comparacion_propia = None`` y
``artefactos`` vacío son "no generado", no "cero". Los fotogramas clave y el video con esqueleto (``engine/render.py``)
entran por el parámetro ``artefactos``, ya subidos a Storage: este módulo sigue sin tocar archivos.
"""

from __future__ import annotations

import math
from collections import Counter
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.engine import encuadre as encuadre_mod
from app.engine import magnitudes
from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import SecuenciaPose
from app.engine.preparacion import TramoExcluido
from app.engine.render import indice_fuente_mas_cercano
from app.engine.segmentos_corporales import ORDEN_ESPERADO, SegmentoCadena, articulaciones_de_segmento
from app.engine.sequencing import ResultadoRepeticion, ResumenSecuenciacion
from app.engine.tolerancia_orden import TOLERANCIA_ORDEN_MS, es_ordenable
from app.schemas.reporte import VERSION_CONTRATO, Reporte

# Los metadatos y los resultados llegan como objetos del motor; se anotan como Any para que este módulo no
# arrastre imports de ingesta ni de pipeline (la función solo lee atributos).

UNIDAD_VELOCIDAD = "grados/s"
PREFIJO_METRICA_VELOCIDAD = "velocidad_pico_"

# Decisión 031: el veredicto (correcto / desvío leve) del par cadera -> tronco solo se emite en un gesto y encuadre donde se cumplen
# las DOS condiciones. (a) hay referencia bibliográfica del orden esperado; (b) el Criterio 1 se cumplió para ese grupo (decisión 014,
# par pelvis-torso, tolerancia de 1 fotograma, sesión 2: ``docs/resultados/criterio1-resumen.md``). La tabla se revisó con el
# Paso A del recálculo con la tasa real (``docs/resultados/paso-a-resumen.md``): ahí cambiaron las cifras de (b).
#
# (a) La tesis (apartado 4.3.3, tabla 4.8) sustenta el saque con Kovacs y Ellenbecker (2011) y Fleisig et al. (2003); para drive y
# revés declara "un conjunto reducido de reglas", sin citar una referencia del orden esperado. Si aparece una, se agrega acá y el
# grupo pasa a tener veredicto si además cumple (b). Martin et al. (2014) (el tronco gira más tarde en los lesionados) no sustenta el
# sentido de "tronco antes que cadera": se reserva para la alerta de carga por tiempo tardío del tronco (E5.1, sin umbral todavía).
REFERENCIA_ORDEN_SAQUE = "Kovacs y Ellenbecker (2011); Fleisig et al. (2003)"


@dataclass(frozen=True)
class Suspension:
    """(c) Decisiones 035 y 036: el orden medido de este gesto no es confiable con una sola cámara y NO se emite veredicto, aunque haya
    referencia (a) y el Criterio 1 (b) se cumpla: los grupos que lo cumplen son justamente los sospechosos (Paso B)."""

    por_encuadre: bool   # True: el orden cambia con el encuadre (saque y drive); False: no sigue ese patrón y es sensible al método (revés)
    detalle: str         # la razón técnica con las cifras del Paso B, para el detalle del reporte (nivel 3); no va al texto del jugador


@dataclass(frozen=True)
class RespaldoGrupo:
    referencia_orden: str | None   # (a) cita del orden esperado; None = sin referencia
    criterio1_cumplido: bool       # (b) Criterio 1 del par pelvis-torso, tolerancia de 1 fotograma, sesión 2 (decisión 014)
    # (c) Mientras haya una suspensión, no se emite veredicto, sean cuales sean (a) y (b). Solo se levanta con una medición independiente
    # de la pelvis (cintas de color o dos cámaras); ver la decisión 036.
    suspension: Suspension | None = None

    @property
    def depende_del_encuadre(self) -> bool:
        return self.suspension is not None and self.suspension.por_encuadre

    @property
    def con_veredicto(self) -> bool:
        return self.suspension is None and self.referencia_orden is not None and self.criterio1_cumplido


_CIERRE_SUSPENSION = "Mientras no haya una medición independiente de la pelvis no se emite veredicto."
_SUSPENSION_SAQUE = Suspension(
    True,
    "En este gesto el orden medido depende del encuadre: con los originales a tasa real, el saque da la cadera primero en tres cuartos "
    f"(7 de 7 ordenables) y el tronco primero en perfil (8 de 8). {_CIERRE_SUSPENSION}",
)
_SUSPENSION_DRIVE = Suspension(
    True,
    "En este gesto el orden medido depende del encuadre: con los originales a tasa real, el drive da la cadera primero en tres cuartos "
    f"(3 de 3 ordenables) y el tronco primero en perfil (7 de 8). {_CIERRE_SUSPENSION}",
)
_SUSPENSION_REVES = Suspension(
    False,
    "En este gesto el orden medido no es confiable con una sola cámara: con los originales a tasa real, el revés da el tronco primero en "
    "tres cuartos (5 de 5 ordenables) y queda 3 contra 3 en perfil, y el orden de perfil cambia con el método de medición (giro axial). "
    f"Con estos datos no se puede separar el gesto del sesgo de la medición. {_CIERRE_SUSPENSION}",
)

# Las cifras de (b) son las del PASO A del recálculo (12/10/2026, ``docs/resultados/paso-a-resumen.md``): tiempo real a 120,2 fps y
# tolerancia de 8,33 ms (la misma constante de ``engine/tolerancia_orden.py``), sesión 2. Reemplazan a las de la medición original
# (decisión 014), que usaba el reloj y la ventana equivocados. Ver la decisión 031 (revisión) y las 035 y 036.
#
# Decisión 036 (extiende la 035): NINGÚN grupo emite veredicto. Se suspendieron los seis, y la suspensión es lo que decide, no (a) ni (b):
# aunque aparezca una referencia del orden para el drive o el revés, o el Criterio 1 de un grupo de perfil se cumpla (el drive de perfil
# lo cumple en el Paso B, 1a 0,83, con el tronco primero), no se emite veredicto hasta levantar la suspensión con una medición independiente.
RESPALDO_POR_GRUPO: dict[tuple[str, str], RespaldoGrupo] = {
    # Decisión 035: perfil cumple el Criterio 1 (1a 0,83 · 1b 1,00, tronco primero 8 de 8 con los originales) pero tres cuartos da cadera
    # primero 7 de 7: el orden depende del encuadre.
    ("saque", "perfil"): RespaldoGrupo(REFERENCIA_ORDEN_SAQUE, True, _SUSPENSION_SAQUE),
    ("saque", "tres_cuartos"): RespaldoGrupo(REFERENCIA_ORDEN_SAQUE, False, _SUSPENSION_SAQUE),   # 1a 0,17 y 0,50
    # La columna (b) de drive y revés sigue con las cifras del Paso A: su revisión con el Paso B (`docs/resultados/paso-b-resumen.md`: el drive
    # de perfil pasaría a cumplir, 1a 0,83 · 1b 1,00, con el tronco primero) es un pendiente posterior a la demo. No cambia ningún veredicto.
    ("drive", "perfil"): RespaldoGrupo(None, False, _SUSPENSION_DRIVE),
    ("drive", "tres_cuartos"): RespaldoGrupo(None, False, _SUSPENSION_DRIVE),
    ("reves", "perfil"): RespaldoGrupo(None, False, _SUSPENSION_REVES),
    ("reves", "tres_cuartos"): RespaldoGrupo(None, False, _SUSPENSION_REVES),
}
_SIN_RESPALDO = RespaldoGrupo(None, False)

# Decisiones 014, 015 y 032: dos picos son "ordenables" si su diferencia supera la tolerancia de ``engine.tolerancia_orden`` (1/120 s,
# 8,3 ms, la misma constante del recálculo del corpus). Dentro de ella el orden no se puede establecer (decisión 015, corrección del
# 29/9: es un motivo de "no auditable", no un estado nuevo).

_NOMBRE_SEGMENTO = {
    SegmentoCadena.PELVIS: "la cadera",
    SegmentoCadena.TORSO: "el tronco",
    SegmentoCadena.BRAZO: "el brazo",
}
_NOMBRE_CORTO = {SegmentoCadena.PELVIS: "cadera", SegmentoCadena.TORSO: "tronco", SegmentoCadena.BRAZO: "brazo"}


def nombre_metrica_velocidad(segmento: SegmentoCadena | str) -> str:
    valor = segmento.value if isinstance(segmento, SegmentoCadena) else segmento
    return f"{PREFIJO_METRICA_VELOCIDAD}{valor}"


def segmento_de_metrica_velocidad(nombre: str) -> str | None:
    """Inversa de ``nombre_metrica_velocidad``; ``None`` si no es una métrica de velocidad pico."""
    return nombre.removeprefix(PREFIJO_METRICA_VELOCIDAD) if nombre.startswith(PREFIJO_METRICA_VELOCIDAD) else None


# --- confianza -------------------------------------------------------------------------------------------


def _puntos(seq: SecuenciaPose, frame: int) -> dict:
    f = seq.frames[frame]
    return f.puntos_mundo if seq.tiene_mundo else f.puntos


def _confianza_en_frame(seq: SecuenciaPose, frame: int, arts: tuple[ArticulacionCanonica, ...]) -> float:
    if not 0 <= frame < seq.n_frames:
        return 0.0
    puntos = _puntos(seq, frame)
    valores = [puntos[a].confianza for a in arts if a in puntos]
    return _acotar(sum(valores) / len(valores)) if valores else 0.0


def _confianza_en_ventana(seq: SecuenciaPose, desde: int, hasta: int, arts: tuple[ArticulacionCanonica, ...]) -> float:
    valores: list[float] = []
    for i in range(max(0, desde), min(seq.n_frames - 1, hasta) + 1):
        puntos = _puntos(seq, i)
        valores.extend(puntos[a].confianza for a in arts if a in puntos)
    return _acotar(sum(valores) / len(valores)) if valores else 0.0


def _acotar(x: float) -> float:
    return round(min(1.0, max(0.0, float(x))), 3)


# --- cobertura -------------------------------------------------------------------------------------------


def _tramos_no_auditables(
    tramos: list[TramoExcluido], articulaciones_cadena: set[ArticulacionCanonica], fps: float
) -> list[dict[str, Any]]:
    """Tramos excluidos de las articulaciones de la cadena, en segundos y unidos donde se superponen o se tocan."""
    relevantes = sorted((t for t in tramos if t.articulacion in articulaciones_cadena), key=lambda t: t.desde_frame)
    unidos: list[list] = []  # [desde_frame, hasta_frame, {articulaciones}]
    for t in relevantes:
        if unidos and t.desde_frame <= unidos[-1][1] + 1:
            unidos[-1][1] = max(unidos[-1][1], t.hasta_frame)
            unidos[-1][2].add(t.articulacion)
        else:
            unidos.append([t.desde_frame, t.hasta_frame, {t.articulacion}])
    return [
        {
            "desde_s": round(desde / fps, 3),
            # +1: el último fotograma excluido ocupa un período de muestreo completo.
            "hasta_s": round((hasta + 1) / fps, 3),
            "motivo": "sin_datos_confiables: " + ", ".join(sorted(a.value for a in arts)),
        }
        for desde, hasta, arts in unidos
    ]


def _cobertura_auditable_pct(
    tramos: list[TramoExcluido], articulaciones_cadena: set[ArticulacionCanonica], n_frames: int
) -> float:
    """Porcentaje de fotogramas en los que TODA la cadena (pelvis, torso y brazo) se pudo medir: la unión de los tramos excluidos
    de sus articulaciones, la misma que se lista en ``tramos_no_auditables``. Antes de la decisión 030 la columna guardaba la
    fracción de fotogramas con una persona detectada, que da 100 % al lado de tramos no auditables (R3)."""
    if n_frames <= 0:
        return 0.0
    excluidos: set[int] = set()
    for t in tramos:
        if t.articulacion in articulaciones_cadena:
            excluidos.update(range(max(0, t.desde_frame), min(n_frames - 1, t.hasta_frame) + 1))
    return round(100.0 * (n_frames - len(excluidos)) / n_frames, 2)


# --- veredicto y observaciones ----------------------------------------------------------------------------


def respaldo_del_grupo(gesto: str, encuadre: str) -> RespaldoGrupo:
    return RESPALDO_POR_GRUPO.get((gesto, encuadre), _SIN_RESPALDO)


def _pico_medido(rep: ResultadoRepeticion, seg: SegmentoCadena):
    p = rep.picos.get(seg)
    return p if p is not None and p.auditable and math.isfinite(p.velocidad) else None


@dataclass(frozen=True)
class _Par:
    """Cómo salió el par cadera -> tronco en una repetición."""

    estado: str            # "cadera_primero" | "tronco_primero" | "no_ordenable" | "sin_dato"
    delta_ms: float | None  # tronco - cadera; > 0 = la cadera llegó primero. Depende de la escala temporal.


def _evaluar_par(rep: ResultadoRepeticion) -> _Par:
    pelvis, torso = _pico_medido(rep, SegmentoCadena.PELVIS), _pico_medido(rep, SegmentoCadena.TORSO)
    if pelvis is None or torso is None:
        return _Par("sin_dato", None)
    delta_s = torso.instante_s - pelvis.instante_s
    if not es_ordenable(delta_s):
        return _Par("no_ordenable", delta_s * 1000.0)
    return _Par("cadera_primero" if delta_s > 0 else "tronco_primero", delta_s * 1000.0)


def _veredicto(gesto: str, encuadre: str, rep: ResultadoRepeticion, discrepa: bool = False) -> bool | None:
    """``correcto`` que se publica para una repetición: del par cadera -> tronco, y solo con respaldo (decisión 031). ``None`` =
    sin evaluar, no ordenable o no medido. Nunca fuerza un ``True``/``False`` sin fundamento (R4)."""
    if discrepa or not respaldo_del_grupo(gesto, encuadre).con_veredicto:
        return None
    par = _evaluar_par(rep)
    if par.estado == "cadera_primero":
        return True
    if par.estado == "tronco_primero":
        return False
    return None


def _fundamento_instantes(rep: ResultadoRepeticion) -> str:
    partes = [
        f"{_NOMBRE_CORTO[s]} {_pico_medido(rep, s).instante_s:.3f}".replace(".", ",") + " s"
        for s in ORDEN_ESPERADO
        if _pico_medido(rep, s) is not None
    ]
    return "Instantes de la velocidad máxima, desde el inicio de la ventana analizada: " + ", ".join(partes) + "."


def _ms(x: float) -> str:
    return f"{abs(x):.0f} ms"


def _ms_coma(x: float) -> str:
    """Milisegundos con una decimal y coma, sin el ',0' (5 ms, 8,3 ms)."""
    return f"{x:.1f}".removesuffix(".0").replace(".", ",")


def _resolucion_texto(fps: float | None) -> str:
    """'1 fotograma ≈ 5 ms a 200 fps reales': la resolución del archivo real, no la de la grilla de 240 Hz (ajuste del 12/10)."""
    if not fps or fps <= 0:
        return ""
    return f"1 fotograma ≈ {_ms_coma(1000.0 / fps)} ms a {fps:.0f} fps reales"


# Texto para el jugador cuando el orden se midió pero no hay con qué evaluarlo (decisión 031). Sin citas en el texto principal: la
# literatura y la razón técnica van en `fundamento` y `referencia`, que la interfaz muestra en el detalle (especificación §6).
_SIN_PATRON = (
    "Todavía no tenemos un patrón de referencia para este golpe; lo registramos para que puedas compararte en tus próximas sesiones."
)
_SIN_VALIDACION = (
    "Todavía no podemos evaluar este orden con suficiente confianza en este encuadre; lo registramos para que puedas compararte "
    "en tus próximas sesiones."
)


_SIN_ENCUADRE = (
    "El orden entre tu cadera y tu tronco cambia según desde dónde se grabó el golpe, y todavía no podemos asegurar cuál es el correcto. "
    "Por eso lo registramos sin evaluarlo."
)


_SIN_METODO = (
    "El orden entre tu cadera y tu tronco en este golpe todavía no se puede medir con suficiente confianza con una sola cámara, "
    "y no podemos asegurar cuál es el correcto. Por eso lo registramos sin evaluarlo."
)


def _cierre_sin_evaluar(respaldo: RespaldoGrupo) -> str:
    if respaldo.suspension is not None:
        return _SIN_ENCUADRE if respaldo.suspension.por_encuadre else _SIN_METODO
    return _SIN_PATRON if respaldo.referencia_orden is None else _SIN_VALIDACION


def _porque_sin_evaluar(respaldo: RespaldoGrupo) -> str:
    """La razón técnica, para el detalle (nivel 3): ahí sí van la literatura y la validación propia."""
    if respaldo.suspension is not None:
        return respaldo.suspension.detalle
    if respaldo.referencia_orden is None and not respaldo.criterio1_cumplido:
        return "Para este gesto y encuadre todavía no hay una referencia del orden esperado ni una validación propia suficiente."
    if respaldo.referencia_orden is None:
        return "Para este gesto todavía no hay una referencia del orden esperado en la literatura que usa el sistema."
    return "La validación propia del orden en este encuadre todavía no alcanzó el criterio de repetibilidad."


def _obs_par(
    gesto: str, encuadre: str, resultados: list[ResultadoRepeticion], escala: bool, fps_real: float | None = None,
    discrepa: bool = False,
) -> dict[str, Any]:
    respaldo = respaldo_del_grupo(gesto, encuadre)
    if discrepa:  # el video no parece del encuadre declarado: el veredicto de ese grupo no corresponde (decisión 035, D)
        respaldo = dataclasses.replace(respaldo, referencia_orden=None)
    pares = [(r, _evaluar_par(r)) for r in resultados]
    ordenables = [(r, p) for r, p in pares if p.estado in ("cadera_primero", "tronco_primero")]

    if not ordenables:
        sin_dato = [r for r, p in pares if p.estado == "sin_dato"]
        if sin_dato:
            motivos = sorted({r.motivo_no_auditable for r in sin_dato if r.motivo_no_auditable})
            return {
                "severidad": "no_auditable",
                "texto": "No se pudo medir el orden entre la cadera y el tronco en este golpe.",
                "fundamento": "; ".join(motivos) if motivos else "el motor no encontró un pico medible en la cadera o en el tronco",
                "referencia": None,
            }
        r0, p0 = pares[0]
        resolucion = _resolucion_texto(fps_real or r0.ventana.fps)
        ms = (
            f" Diferencia: {_ms(p0.delta_ms)}; la tolerancia es de {_ms_coma(TOLERANCIA_ORDEN_MS)} ms"
            + (f" y {resolucion}." if resolucion else ".")
            if escala
            else ""
        )
        return {
            "severidad": "no_auditable",
            "texto": (
                "La cadera y el tronco alcanzaron su velocidad máxima casi al mismo tiempo: "
                "a esta resolución del video no se puede saber cuál fue primero."
            ),
            "fundamento": "Simultaneidad al límite de resolución." + ms,
            "referencia": None,
        }

    if len(resultados) == 1:
        r, p = ordenables[0]
        primero, segundo = ("la cadera", "el tronco") if p.estado == "cadera_primero" else ("el tronco", "la cadera")
        cuanto = f" {_ms(p.delta_ms)}" if escala and p.delta_ms is not None else ""
        hecho = f"Se observa que {primero} alcanzó su velocidad máxima{cuanto} antes que {segundo}"
        instantes = _fundamento_instantes(r)
        if not respaldo.con_veredicto:
            return {
                "severidad": "sin_evaluar",
                "texto": f"{hecho}. {_cierre_sin_evaluar(respaldo)}",
                "fundamento": f"{instantes} {_porque_sin_evaluar(respaldo)}",
                "referencia": None,
            }
        if p.estado == "cadera_primero":
            return {
                "severidad": "correcto",
                "texto": f"{hecho}: es el orden esperado para este golpe.",
                "fundamento": instantes,
                "referencia": respaldo.referencia_orden,
            }
        return {
            "severidad": "desvio_leve",
            "texto": f"{hecho}: es distinto del orden esperado para este golpe (la cadera primero).",
            "fundamento": instantes,
            "referencia": respaldo.referencia_orden,
        }

    # Varias repeticiones: un resumen; el detalle de cada una está en la secuenciación.
    n, k = len(resultados), sum(1 for _, p in ordenables if p.estado == "cadera_primero")
    hecho = (
        f"Se observa que la cadera alcanzó su velocidad máxima antes que el tronco en {k} de {len(ordenables)} repeticiones "
        f"ordenables (de {n} analizadas)"
    )
    if not respaldo.con_veredicto:
        return {
            "severidad": "sin_evaluar",
            "texto": f"{hecho}. {_cierre_sin_evaluar(respaldo)}",
            "fundamento": _porque_sin_evaluar(respaldo),
            "referencia": None,
        }
    return {
        "severidad": "correcto" if k == len(ordenables) else "desvio_leve",
        "texto": f"{hecho}: el orden esperado para este golpe es la cadera primero.",
        "fundamento": None,
        "referencia": respaldo.referencia_orden,
    }


_SIN_PATRON_BRAZO = "Es un dato de tu golpe: todavía no tenemos un patrón de referencia para el brazo."
_POR_QUE_BRAZO = "El balanceo del brazo no tiene una referencia equivalente en la literatura: se informa como dato, sin evaluarlo."


def _obs_brazo(resultados: list[ResultadoRepeticion], escala: bool) -> dict[str, Any]:
    """El brazo (balanceo del vector hombro-codo) se informa como dato, nunca como correcto o incorrecto (decisión 011)."""
    medidos = [r for r in resultados if _pico_medido(r, SegmentoCadena.TORSO) and _pico_medido(r, SegmentoCadena.BRAZO)]
    if not medidos:
        return {
            "severidad": "no_auditable",
            "texto": "No se pudo medir el instante en que el brazo alcanzó su velocidad máxima en este golpe.",
            "fundamento": None,
            "referencia": None,
        }
    if len(resultados) == 1:
        r = medidos[0]
        delta = _pico_medido(r, SegmentoCadena.BRAZO).instante_s - _pico_medido(r, SegmentoCadena.TORSO).instante_s
        cuando = "después" if delta >= 0 else "antes"
        cuanto = f"{abs(delta) * 1000:.0f} ms " if escala else ""
        return {
            "severidad": "sin_evaluar",
            "texto": f"El brazo alcanzó su velocidad máxima {cuanto}{cuando} del tronco. {_SIN_PATRON_BRAZO}",
            "fundamento": f"{_fundamento_instantes(r)} {_POR_QUE_BRAZO}",
            "referencia": None,
        }
    return {
        "severidad": "sin_evaluar",
        "texto": (
            f"Se midió el instante del brazo respecto del tronco en {len(medidos)} de {len(resultados)} repeticiones. "
            f"{_SIN_PATRON_BRAZO}"
        ),
        "fundamento": _POR_QUE_BRAZO,
        "referencia": None,
    }


def _observaciones(
    gesto: str,
    encuadre: str,
    resultados: list[ResultadoRepeticion],
    escala_temporal_conocida: bool,
    fps_real: float | None = None,
    aviso_encuadre: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not resultados:
        return [
            {
                "severidad": "no_auditable",
                "texto": "No se pudo medir el orden en que la cadera, el tronco y el brazo alcanzan su velocidad máxima en este golpe.",
                "fundamento": "el motor no devolvió ninguna repetición",
                "referencia": None,
            }
        ]
    obs = [
        _obs_par(gesto, encuadre, resultados, escala_temporal_conocida, fps_real, discrepa=aviso_encuadre is not None),
        _obs_brazo(resultados, escala_temporal_conocida),
    ]
    if aviso_encuadre is not None:
        obs.insert(0, aviso_encuadre)
    if not escala_temporal_conocida:
        obs.append(
            {
                "severidad": "no_auditable",
                "texto": (
                    "No se pudo confirmar la escala temporal de este video: el orden de los picos se documenta, "
                    "pero las velocidades y los tiempos en milisegundos no son auditables."
                ),
                "fundamento": "escala_temporal_conocida = false",
                "referencia": None,
            }
        )
    return obs


# --- magnitudes articulares ------------------------------------------------------------------------------


def _magnitudes_articulares(
    primera: ResultadoRepeticion,
    conf_seq: SecuenciaPose,
    secuencia: SecuenciaPose,
    seq_fuente: SecuenciaPose | None,
    pts_fuente: Any,
    fps_grilla: float,
    tramos_excluidos: list[TramoExcluido],
) -> list[dict[str, Any]]:
    """Separación cadera-hombro máxima y los ángulos de rodilla y codo en el pico del tronco, con la definición con que se validaron
    (``engine/magnitudes``). Un valor que no cumple su regla (cobertura de la ventana, confianza >= 0,6 en los tres puntos) sale con
    ``valor = None`` y ``auditable = False``: nunca se estima (R3)."""
    v = primera.ventana
    salida: list[dict[str, Any]] = []

    # Los fotogramas con alguna de las cuatro articulaciones en un tramo no auditable no cuentan (como en la velocidad).
    excluidos = {
        i
        for t in tramos_excluidos
        if t.articulacion in magnitudes.ARTICULACIONES_SEPARACION
        for i in range(max(0, t.desde_frame), t.hasta_frame + 1)
    }
    mundo = [({} if i in excluidos else f.puntos_mundo) for i, f in enumerate(conf_seq.frames)]
    sep = magnitudes.separacion_cadera_hombro_max(mundo, v.desde_frame, v.hasta_frame)
    if sep["auditable"]:
        conf = _confianza_en_frame(conf_seq, sep["frame"], magnitudes.ARTICULACIONES_SEPARACION)
    else:
        conf = _confianza_en_ventana(conf_seq, v.desde_frame, v.hasta_frame, magnitudes.ARTICULACIONES_SEPARACION)
    salida.append(
        {
            "nombre": "separacion_cadera_hombro_max",
            "valor": round(sep["valor"], 1) if sep["auditable"] else None,
            "unidad": "grados",
            "confianza": conf,
            "auditable": bool(sep["auditable"]),
        }
    )

    # Rodilla y codo en el instante del pico del tronco, sobre el fotograma REAL más cercano (no uno interpolado).
    pico = primera.picos.get(SegmentoCadena.TORSO)
    if pico is None or not pico.auditable:
        return salida
    if seq_fuente is not None:
        idx = indice_fuente_mas_cercano(pico.frame / fps_grilla, pts_fuente, fps_grilla, seq_fuente.n_frames)
        origen = seq_fuente
    else:
        idx, origen = pico.frame, secuencia
    if not 0 <= idx < origen.n_frames:
        return salida
    puntos = origen.frames[idx].puntos
    for angulo in ("rodilla", "codo"):
        r = magnitudes.angulo_en_el_frame(puntos, angulo, origen.ancho, origen.alto)
        nombre = f"angulo_{angulo}_{r['lado']}_en_pico_tronco" if r["lado"] else f"angulo_{angulo}_en_pico_tronco"
        salida.append(
            {
                "nombre": nombre,
                "valor": round(r["valor"], 1) if r["auditable"] else None,
                "unidad": "grados",
                "confianza": _acotar(r["confianza"]),
                "auditable": bool(r["auditable"]),
            }
        )
    return salida


# --- ensamblado ------------------------------------------------------------------------------------------


def ensamblar_reporte(
    *,
    reporte_id: UUID | str,
    video_id: UUID | str,
    gesto: str,
    encuadre: str,
    creado_en: datetime,
    version_motor: str,
    backend_pose: str,
    modo_captura: str,
    factor_ralentizacion: float,
    origen_factor: str,
    escala_temporal_conocida: bool,
    apto_fase_rapida: bool,
    metadatos: Any,
    fps_real: float,
    secuencia: SecuenciaPose,
    filtrada: Any,
    resultados: list[ResultadoRepeticion],
    resumen: ResumenSecuenciacion,
    lado_dominante: str,
    brazo_via: str = "codo",
    metodo_segmentacion: str = "ancla_torso",
    regularizacion: dict | None = None,
    artefactos: dict[str, Any] | None = None,
    seq_fuente: SecuenciaPose | None = None,
    pts_fuente: Any = None,
) -> dict[str, Any]:
    """Devuelve el reporte como ``dict`` JSON-compatible, ya validado contra el contrato.

    ``metadatos``: ``MetadatosVideo`` (lee ``fps_nominal_marcas``, ``fps_real_medio``, ``es_tiempo_real``).
    ``secuencia``: la que entró a E3 (da la cobertura). ``filtrada``: ``SecuenciaFiltrada`` de E3 (da el filtro,
    los tramos excluidos y la secuencia sobre la que se leyó la confianza). ``fps_real`` es la tasa efectiva con
    la que se calculó (la real media medida en un archivo con marcas; la declarada x factor en un horneado).
    """
    arts_por_segmento = {
        s: articulaciones_de_segmento(s, lado_dominante, brazo_via=brazo_via) for s in ORDEN_ESPERADO
    }
    arts_cadena = {a for arts in arts_por_segmento.values() for a in arts}
    fps_grilla = float(secuencia.fps_efectivos)
    conf_seq = filtrada.secuencia

    # --- trazabilidad
    en_tiempo_real = bool(metadatos.es_tiempo_real)
    fps_nominal = float(metadatos.fps_nominal_marcas) if en_tiempo_real and metadatos.fps_nominal_marcas else None
    perdidos = None
    if fps_nominal and metadatos.fps_real_medio:
        perdidos = round(min(100.0, max(0.0, 100.0 * (1.0 - float(metadatos.fps_real_medio) / fps_nominal))), 2)
    trazabilidad = {
        "version_motor": version_motor,
        "backend_pose": backend_pose,
        "filtro": filtrada.trazabilidad_filtro(),
        "fps_real": float(fps_real),
        "apto_fase_rapida": bool(apto_fase_rapida),
        "escala_temporal_conocida": bool(escala_temporal_conocida),
        "modo_captura": modo_captura,
        "factor_ralentizacion": float(factor_ralentizacion),
        "origen_factor": origen_factor,
        "fps_nominal": round(fps_nominal, 3) if fps_nominal else None,
        "fotogramas_perdidos_pct": perdidos,
        "regularizacion": regularizacion,
        # v1.3 (decisión 032): la tolerancia con que se decidió "ordenable", para que un reporte se pueda releer con su regla.
        "tolerancia_orden_ms": round(TOLERANCIA_ORDEN_MS, 3),
    }

    # --- encuadre declarado contra encuadre visto (decisión 035, D): no bloquea nada, solo quita el veredicto y avisa
    aviso_encuadre: dict[str, Any] | None = None
    primero = resultados[0] if resultados else None
    pico_torso = primero.picos.get(SegmentoCadena.TORSO) if primero is not None else None
    if pico_torso is not None and pico_torso.auditable and gesto in encuadre_mod.GESTOS_CALIBRADOS:
        visto = encuadre_mod.encuadre_visto([f.puntos_mundo for f in secuencia.frames], pico_torso.frame, fps_grilla)
        if encuadre_mod.discrepa(gesto, encuadre, visto["visto"]):
            aviso_encuadre = {
                "severidad": "no_auditable",
                "texto": encuadre_mod.aviso(encuadre, visto["visto"]),
                "fundamento": (
                    f"Giro de la línea de hombros en la preparación: {str(round(visto['giro_grados']))}° "
                    f"(en el corpus propio: perfil 26–42°, tres cuartos 50–83°). Detecta una diferencia gruesa; no mide el ángulo de la cámara. "
                    "Con esta discrepancia no se emite veredicto."
                ),
                "referencia": None,
            }

    # --- secuenciación
    repeticiones: list[dict[str, Any]] = []
    for r in resultados:
        # Decisión 014/015 (corrección del 29/9): con cadera y tronco a un fotograma o menos el orden no se puede establecer, y la
        # repetición se muestra como no auditable con ese motivo; el motor solo ordena por instantes y no conoce la tolerancia.
        par = _evaluar_par(r)
        no_ordenable = par.estado == "no_ordenable"
        # Cadera y tronco ordenables aunque el brazo no se haya podido medir (p. ej. codo dominante sin datos en media ventana, 12/10):
        # la repetición es auditable en lo que se midió, con el orden de los segmentos medidos (2 en lugar de 3). El brazo queda
        # como "no se pudo medir" en las observaciones. Con los tres medidos nada cambia: es el orden del motor.
        solo_el_par = par.estado in ("cadera_primero", "tronco_primero") and not r.auditable
        picos = []
        for seg in ORDEN_ESPERADO:
            p = r.picos.get(seg)
            if p is None or not p.auditable or not math.isfinite(p.velocidad):
                continue  # un pico ausente o no finito no se estima ni se rellena (R3)
            picos.append(
                {
                    "segmento": seg.value,
                    "instante_s": round(max(0.0, p.instante_s), 4),
                    "velocidad": round(float(p.velocidad), 3),
                    "unidad": UNIDAD_VELOCIDAD,
                    "confianza": _confianza_en_frame(conf_seq, p.frame, arts_por_segmento[seg]),
                }
            )
        repeticiones.append(
            {
                "indice": r.indice,
                "desde_s": round(r.ventana.desde_s, 4),
                "hasta_s": round(r.ventana.hasta_s, 4),
                "auditable": (bool(r.auditable) and not no_ordenable) or solo_el_par,
                "orden_observado": (
                    [s.value for s in r.orden_observado] if r.orden_observado and not no_ordenable
                    else [d["segmento"] for d in sorted(picos, key=lambda d: d["instante_s"])] if solo_el_par
                    else None
                ),
                "correcto": _veredicto(gesto, encuadre, r, aviso_encuadre is not None),
                "motivo_no_auditable": (
                    None if solo_el_par
                    else "simultaneidad al límite de resolución: la cadera y el tronco quedaron a un fotograma o menos"
                    if no_ordenable and not r.motivo_no_auditable
                    else r.motivo_no_auditable
                ),
                # Los picos medidos se informan aunque la repetición no sea ordenable: son datos reales
                # (y están en `metricas`); lo que queda en None es el orden y el veredicto.
                "picos": picos,
            }
        )

    correctas = sum(1 for r in resultados if _veredicto(gesto, encuadre, r, aviso_encuadre is not None))
    # Las repeticiones auditables son las del JSON (ya sin las que no se pueden ordenar): el resumen se calcula de ahí.
    ordenes = [tuple(rp["orden_observado"]) for rp in repeticiones if rp["auditable"] and rp["orden_observado"]]
    predominante = Counter(ordenes).most_common(1)[0][0] if ordenes else ()
    n_auditables = sum(1 for rp in repeticiones if rp["auditable"])
    resumen_json = {
        "repeticiones_correctas": correctas,
        "repeticiones_evaluadas": len(resultados),
        "orden_predominante": list(predominante),
        "dispersion_instante_pico_torso_ms": (
            round(resumen.dispersion_instante_pico_torso_ms, 2)
            if resumen.dispersion_instante_pico_torso_ms is not None
            else None
        ),
    }

    # --- métricas: velocidad pico por segmento de la primera repetición (un video = un golpe)
    metricas: list[dict[str, Any]] = []
    primera = resultados[0] if resultados else None
    if primera is not None:
        v = primera.ventana
        for seg in ORDEN_ESPERADO:
            p = primera.picos.get(seg)
            medible = p is not None and p.auditable and math.isfinite(p.velocidad) and escala_temporal_conocida
            if p is not None and p.auditable and math.isfinite(p.velocidad):
                confianza = _confianza_en_frame(conf_seq, p.frame, arts_por_segmento[seg])
            else:
                confianza = _confianza_en_ventana(conf_seq, v.desde_frame, v.hasta_frame, arts_por_segmento[seg])
            metricas.append(
                {
                    "nombre": nombre_metrica_velocidad(seg),
                    "valor": round(float(p.velocidad), 3) if medible else None,
                    "unidad": UNIDAD_VELOCIDAD,
                    "confianza": confianza,
                    "auditable": bool(medible),
                }
            )

    if primera is not None:
        metricas.extend(
            _magnitudes_articulares(primera, conf_seq, secuencia, seq_fuente, pts_fuente, fps_grilla, filtrada.tramos_excluidos)
        )

    datos = {
        "version_contrato": VERSION_CONTRATO,
        "reporte_id": str(reporte_id),
        "video_id": str(video_id),
        "gesto": gesto,
        "creado_en": creado_en,
        "trazabilidad": trazabilidad,
        "cobertura": {
            "auditable_pct": _cobertura_auditable_pct(filtrada.tramos_excluidos, arts_cadena, secuencia.n_frames),
            "tramos_no_auditables": _tramos_no_auditables(filtrada.tramos_excluidos, arts_cadena, fps_grilla),
        },
        "segmentacion": {
            "metodo": metodo_segmentacion,
            "repeticiones_marcadas": len(resultados),
            "repeticiones_auditables": n_auditables,
        },
        "secuenciacion": {
            "orden_esperado": [s.value for s in ORDEN_ESPERADO],
            "repeticiones": repeticiones,
            "resumen": resumen_json,
        },
        "metricas": metricas,
        "comparacion_propia": None,
        "observaciones": _observaciones(gesto, encuadre, resultados, escala_temporal_conocida, fps_real, aviso_encuadre),
        # Rutas en Storage (no URLs) de lo que generó engine/render.py; {} = no generado (nunca "cero").
        "artefactos": artefactos or {},
    }
    # Valida contra el contrato (extra="forbid", rangos). model_dump(mode="json") deja UUID y fecha como texto.
    return Reporte.model_validate(datos).model_dump(mode="json")
