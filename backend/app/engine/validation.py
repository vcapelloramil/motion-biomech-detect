"""E2b — Validación de los puntos de pose (plan, tarea 2.4).

Dos controles independientes sobre una ``SecuenciaPose``:

1. **Confianza baja.** Puntos por debajo de un umbral de confianza. No se descartan
   acá: se listan para que E3 los interpole o excluya antes de filtrar (tesis
   §3.4.2.6). Un dato de baja confianza que se hace pasar por bueno es peor que un
   dato faltante (regla R3, tesis §3.3.2.1).

2. **Saltos imposibles.** Un punto que se desplaza demasiado entre dos fotogramas
   consecutivos: eso no es movimiento, es un error de detección (un punto
   confiadamente equivocado, que la confianza sola no atrapa). El umbral se expresa
   en **fracciones de la longitud del torso** (distancia cadera-hombro), que es la
   regla interna: es de las magnitudes más estables (tesis §3.3.3.2) y evita
   depender de una escala métrica que el material descargado no tiene.

3. **Inversiones de profundidad.** Sub-caso del anterior que el umbral de saltos no
   atrapa: MediaPipe no siempre distingue si una articulación está delante o detrás
   del plano del cuerpo, y en el instante rápido puede "dar vuelta" la coordenada
   ``z`` de golpe (§3.3.2.1). Firma: la articulación venía con confianza alta, ``z``
   cambia de signo con ``|Δz|`` grande y dominado por ``z`` (``x``,``y`` casi no se
   mueven), y ``z`` **vuelve** al signo original en pocos fotogramas. Calibrado con
   ``zverev_saque_lateral_02`` frame 566, que ni el umbral de confianza (0,65 > 0,5)
   ni el de saltos (0,31 < 0,5 torsos) marcan. **En toma lateral la ``z`` del brazo
   rápido es poco fiable y esto dispara seguido**: ver decisión 009 (§ hallazgo).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose

UMBRAL_CONFIANZA = 0.5
MAX_SALTO_TORSOS = 0.5
# Inversión de profundidad = MediaPipe venía siguiendo bien una articulación y de
# golpe elige el lado equivocado del plano del cuerpo, y después corrige. Firma:
#   (1) el fotograma anterior tiene confianza alta (venía bien seguida);
#   (2) el fotograma de entrada cambia el signo de z, con |Δz| grande y dominado por z;
#   (3) z **vuelve** al signo original dentro de unos pocos fotogramas.
# Si la articulación ya venía con confianza baja, su z es ruido crónico, no una
# inversión puntual (lo maneja el marcado por baja confianza). Si z no vuelve, es un
# cambio de posición genuino.
CONF_MIN_PRE_INVERSION = 0.80
UMBRAL_INVERSION_Z_TORSOS = 0.20
FACTOR_DOMINANCIA_Z = 1.8
MAX_SPAN_INVERSION_Z = 15  # fotogramas: si z no vuelve en esta ventana, no es glitch


@dataclass(frozen=True)
class SaltoImposible:
    articulacion: ArticulacionCanonica
    frame_desde: int
    frame_hasta: int
    desplazamiento_torsos: float


@dataclass(frozen=True)
class InversionZ:
    articulacion: ArticulacionCanonica
    frame_desde: int
    frame_hasta: int
    dz_torsos: float
    z_antes: float
    z_despues: float


@dataclass
class ResultadoValidacion:
    umbral_confianza: float
    max_salto_torsos: float
    puntos_baja_confianza: list[tuple[int, ArticulacionCanonica]] = field(default_factory=list)
    saltos_imposibles: list[SaltoImposible] = field(default_factory=list)
    inversiones_z: list[InversionZ] = field(default_factory=list)
    # Fracción de fotogramas en que cada articulación está presente y por encima
    # del umbral de confianza. Se reporta por articulación, no como número único
    # (tesis §3.3.2.8).
    cobertura_auditable: dict[ArticulacionCanonica, float] = field(default_factory=dict)

    @property
    def n_baja_confianza(self) -> int:
        return len(self.puntos_baja_confianza)

    @property
    def n_saltos(self) -> int:
        return len(self.saltos_imposibles)

    @property
    def n_inversiones_z(self) -> int:
        return len(self.inversiones_z)


# Espacio de coordenadas sobre el que trabaja la validación. E3 usa "mundo"
# (métrico, centrado en caderas): quita la traslación por paneo de cámara, así un
# salto real se distingue mejor. Los backends 2D puros solo tienen "imagen".
_ESPACIOS = ("imagen", "mundo")


def _puntos(frame: PoseFrame, espacio: str) -> dict[ArticulacionCanonica, Punto]:
    return frame.puntos if espacio == "imagen" else frame.puntos_mundo


def _dist(a: Punto, b: Punto) -> float:
    dz = 0.0 if (a.z is None or b.z is None) else (a.z - b.z)
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + dz**2)


def largo_torso(frame: PoseFrame, *, espacio: str = "imagen") -> float | None:
    """Distancia media hombro-cadera (mismo lado). None si falta un lado completo."""
    puntos = _puntos(frame, espacio)
    lados = (
        (ArticulacionCanonica.HOMBRO_IZQ, ArticulacionCanonica.CADERA_IZQ),
        (ArticulacionCanonica.HOMBRO_DER, ArticulacionCanonica.CADERA_DER),
    )
    largos = [
        _dist(puntos[h], puntos[c])
        for h, c in lados
        if h in puntos and c in puntos
    ]
    return sum(largos) / len(largos) if largos else None


def marcar_baja_confianza(
    seq: SecuenciaPose, *, umbral: float = UMBRAL_CONFIANZA, espacio: str = "imagen"
) -> list[tuple[int, ArticulacionCanonica]]:
    marcados: list[tuple[int, ArticulacionCanonica]] = []
    for frame in seq.frames:
        for art, punto in _puntos(frame, espacio).items():
            if punto.confianza < umbral:
                marcados.append((frame.indice, art))
    return marcados


def detectar_saltos_imposibles(
    seq: SecuenciaPose, *, max_torsos: float = MAX_SALTO_TORSOS, espacio: str = "imagen"
) -> list[SaltoImposible]:
    saltos: list[SaltoImposible] = []
    for anterior, actual in zip(seq.frames, seq.frames[1:]):
        if not (anterior.detectado and actual.detectado):
            continue
        escala = largo_torso(actual, espacio=espacio) or largo_torso(
            anterior, espacio=espacio
        )
        if not escala or escala <= 0:
            continue  # sin escala interna no se puede juzgar
        p_ant = _puntos(anterior, espacio)
        for art, p_actual in _puntos(actual, espacio).items():
            if art not in p_ant:
                continue
            desplazamiento = _dist(p_ant[art], p_actual) / escala
            if desplazamiento > max_torsos:
                saltos.append(
                    SaltoImposible(
                        articulacion=art,
                        frame_desde=anterior.indice,
                        frame_hasta=actual.indice,
                        desplazamiento_torsos=desplazamiento,
                    )
                )
    return saltos


def _z_por_articulacion(
    seq: SecuenciaPose, art: ArticulacionCanonica, espacio: str
) -> dict[int, float]:
    salida: dict[int, float] = {}
    for i, frame in enumerate(seq.frames):
        p = _puntos(frame, espacio).get(art)
        if frame.detectado and p is not None and p.z is not None:
            salida[i] = p.z
    return salida


def detectar_inversiones_z(
    seq: SecuenciaPose,
    *,
    espacio: str = "imagen",
    umbral_torsos: float = UMBRAL_INVERSION_Z_TORSOS,
    factor_dominancia_z: float = FACTOR_DOMINANCIA_Z,
    max_span: int = MAX_SPAN_INVERSION_Z,
    conf_min_pre: float = CONF_MIN_PRE_INVERSION,
) -> list[InversionZ]:
    """Franjas donde ``z`` se dio vuelta de golpe (cambio de signo dominado por z).

    Devuelve una entrada por franja, con ``frame_hasta`` = último fotograma con el
    signo invertido (o el tope de ``max_span``). No hace nada si el backend no da
    ``z`` (2D puro) o si falta la escala del torso.
    """
    inversiones: list[InversionZ] = []
    articulaciones = {a for f in seq.frames for a in _puntos(f, espacio)}

    for art in articulaciones:
        zpos = _z_por_articulacion(seq, art, espacio)
        i = 0
        n = len(seq.frames)
        while i < n - 1:
            if i not in zpos or (i + 1) not in zpos:
                i += 1
                continue
            z0, z1 = zpos[i], zpos[i + 1]
            escala = largo_torso(seq.frames[i + 1], espacio=espacio) or largo_torso(
                seq.frames[i], espacio=espacio
            )
            if not escala or escala <= 0 or z0 * z1 >= 0:
                i += 1
                continue
            dz = abs(z1 - z0)
            p0, p1 = _puntos(seq.frames[i], espacio)[art], _puntos(seq.frames[i + 1], espacio)[art]
            dxy = math.hypot(p1.x - p0.x, p1.y - p0.y)
            if (
                p0.confianza < conf_min_pre  # la articulación no venía bien seguida
                or dz / escala <= umbral_torsos
                or dz <= factor_dominancia_z * dxy
            ):
                i += 1
                continue
            # entrada a la inversión en i -> i+1 (signo de z1). Buscar el retorno al
            # signo original (el de z0) dentro de max_span.
            signo_invertido = 1.0 if z1 > 0 else -1.0
            fin = i + 1
            retorno = None
            for j in range(i + 2, min(n, i + 1 + max_span)):
                if j not in zpos:
                    break
                if zpos[j] * signo_invertido > 0:  # sigue invertido
                    fin = j
                else:  # volvió al signo original
                    retorno = j
                    break
            if retorno is None:
                # no volvió: cambio de posición genuino o tracking malo sostenido
                i += 1
                continue
            inversiones.append(
                InversionZ(
                    articulacion=art,
                    frame_desde=seq.frames[i].indice,
                    frame_hasta=seq.frames[fin].indice,
                    dz_torsos=dz / escala,
                    z_antes=z0,
                    z_despues=z1,
                )
            )
            i = retorno
    return inversiones


def _cobertura_auditable(
    seq: SecuenciaPose, umbral: float, espacio: str
) -> dict[ArticulacionCanonica, float]:
    if not seq.frames:
        return {}
    n = len(seq.frames)
    cobertura: dict[ArticulacionCanonica, float] = {}
    for art in seq.articulaciones:
        ok = sum(
            1
            for f in seq.frames
            if (p := _puntos(f, espacio).get(art)) is not None and p.confianza >= umbral
        )
        cobertura[art] = ok / n
    return cobertura


def validar(
    seq: SecuenciaPose,
    *,
    umbral_confianza: float = UMBRAL_CONFIANZA,
    max_salto_torsos: float = MAX_SALTO_TORSOS,
    espacio: str = "imagen",
) -> ResultadoValidacion:
    if espacio not in _ESPACIOS:
        raise ValueError(f"espacio debe ser uno de {_ESPACIOS}")
    return ResultadoValidacion(
        umbral_confianza=umbral_confianza,
        max_salto_torsos=max_salto_torsos,
        puntos_baja_confianza=marcar_baja_confianza(
            seq, umbral=umbral_confianza, espacio=espacio
        ),
        saltos_imposibles=detectar_saltos_imposibles(
            seq, max_torsos=max_salto_torsos, espacio=espacio
        ),
        inversiones_z=detectar_inversiones_z(seq, espacio=espacio),
        cobertura_auditable=_cobertura_auditable(seq, umbral_confianza, espacio),
    )
