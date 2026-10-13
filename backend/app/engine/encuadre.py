"""Contraste entre el encuadre que declaró el usuario y el que se ve en el video (decisión 035, parte D).

El encuadre (perfil / tres cuartos) lo declara el usuario y de él depende qué grupo de la tabla de respaldo se aplica. En la prueba de producción
del 12/10 un saque de tres cuartos (``IMG_6391``) se subió como "perfil" y el reporte le aplicó el veredicto del grupo equivocado. Esta función pura
compara lo declarado con lo que muestra la pose: **el giro de la línea de hombros en la preparación**, de 0,8 a 0,3 s antes del pico del tronco, en
coordenadas métricas (0° = línea paralela al plano de la imagen, 90° = apuntando a la cámara).

Calibración (``docs/resultados/paso-b-saque.md``): en 22 saques de un jugador, el perfil dio **26–42°** (mediana 35°) y tres cuartos **50–83°**
(mediana 56°), sin solaparse. Detecta una discrepancia **gruesa**; no mide el ángulo de la cámara. **Solo está calibrado con el saque**: para drive y
revés (otra postura de preparación) no se aplica hasta tener datos propios (Paso B).
"""

from __future__ import annotations

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A

PERFIL_MAX_GRADOS = 42.0           # el perfil del corpus llegó hasta 42°
TRES_CUARTOS_MIN_GRADOS = 50.0     # y tres cuartos desde 50°: entre los dos no se afirma nada
PREPARACION_DESDE_S = 0.8          # antes del pico del tronco
PREPARACION_HASTA_S = 0.3
MIN_FOTOGRAMAS_VALIDOS = 30
GESTOS_CALIBRADOS = ("saque",)

ENCUADRES = ("perfil", "tres_cuartos")


def giro_hombros_grados(frames_mundo: list[dict], desde: int, hasta: int) -> float | None:
    """Mediana del giro de la línea de hombros (0–90°) en [desde, hasta]; ``None`` si hay menos de ``MIN_FOTOGRAMAS_VALIDOS``."""
    valores = []
    for i in range(max(0, desde), min(len(frames_mundo) - 1, hasta) + 1):
        p = frames_mundo[i]
        izq, der = p.get(A.HOMBRO_IZQ), p.get(A.HOMBRO_DER)
        if izq is None or der is None or izq.z is None or der.z is None:
            continue
        angulo = abs(float(np.degrees(np.arctan2(der.z - izq.z, der.x - izq.x))))
        if np.isfinite(angulo):
            valores.append(180.0 - angulo if angulo > 90.0 else angulo)
    if len(valores) < MIN_FOTOGRAMAS_VALIDOS:
        return None
    return float(np.median(valores))


def clasificar(giro: float | None) -> str | None:
    """``"perfil"``, ``"tres_cuartos"`` o ``None`` (sin dato o en la franja en que no se afirma nada)."""
    if giro is None:
        return None
    if giro <= PERFIL_MAX_GRADOS:
        return "perfil"
    if giro >= TRES_CUARTOS_MIN_GRADOS:
        return "tres_cuartos"
    return None


def encuadre_visto(frames_mundo: list[dict], frame_pico_torso: int, fps: float) -> dict:
    """``{"giro_grados", "visto"}`` en la preparación del golpe (``visto`` puede ser ``None``)."""
    desde = frame_pico_torso - int(round(PREPARACION_DESDE_S * fps))
    hasta = frame_pico_torso - int(round(PREPARACION_HASTA_S * fps))
    giro = giro_hombros_grados(frames_mundo, desde, hasta)
    return {"giro_grados": giro, "visto": clasificar(giro)}


def discrepa(gesto: str, declarado: str, visto: str | None) -> bool:
    """¿El encuadre visto contradice claramente al declarado? Solo para los gestos calibrados y para encuadres conocidos."""
    return gesto in GESTOS_CALIBRADOS and declarado in ENCUADRES and visto in ENCUADRES and visto != declarado


def aviso(declarado: str, visto: str) -> str:
    """El aviso para el jugador: sin tecnicismos, sin bloquear (la carga ya terminó), solo avisa y no se emite veredicto."""
    nombre = {"perfil": "perfil", "tres_cuartos": "tres cuartos"}
    return (
        f"El video parece grabado de {nombre[visto]}, pero elegiste {nombre[declarado]}. "
        "Revisá el encuadre antes de comparar tus resultados."
    )
