"""Backend de pose por defecto: MediaPipe Pose (tesis §4.4.3).

Elegido como opción por defecto del MVP: tridimensionalidad de extremo a extremo
con una sola dependencia, 33 puntos (incluye mano y pie), y el mejor de los
modelos 3D directos en la evaluación de Rode et al. (2025).

``static_image_mode=True`` por defecto (decisión de esta etapa): cada fotograma se
estima por separado, sin el suavizado temporal interno de MediaPipe. La señal sale
lo más cruda posible y el filtrado de fase cero lo hace E3, que es quien debe
hacerlo (tesis §3.4.2.6). El modo con tracking queda disponible por configuración.
"""

from __future__ import annotations

import numpy as np

from app.engine.pose.articulaciones import (
    MEDIAPIPE_A_CANONICO,
    ArticulacionCanonica,
    articulaciones_de,
)
from app.engine.pose.base import PoseBackend, PoseFrame, Punto


class MediaPipeBackend(PoseBackend):
    dims = 3

    def __init__(
        self,
        *,
        static_image_mode: bool = True,
        model_complexity: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._cfg = {
            "static_image_mode": static_image_mode,
            "model_complexity": model_complexity,
            "min_detection_confidence": min_detection_confidence,
            "min_tracking_confidence": min_tracking_confidence,
        }
        self._pose = None  # se crea perezosamente en el primer frame

    def _asegurar_pose(self):
        if self._pose is None:
            from mediapipe.python.solutions import pose as mp_pose

            self._pose = mp_pose.Pose(**self._cfg)
        return self._pose

    @property
    def id(self) -> str:
        return "mediapipe"

    @property
    def version(self) -> str:
        import mediapipe

        return f"mediapipe-{mediapipe.__version__}"

    @property
    def articulaciones_disponibles(self) -> tuple[ArticulacionCanonica, ...]:
        return articulaciones_de(MEDIAPIPE_A_CANONICO)

    def _config(self) -> dict:
        return dict(self._cfg)

    def estimar_frame(self, frame_bgr: np.ndarray, indice: int) -> PoseFrame:
        import cv2

        pose = self._asegurar_pose()
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        resultado = pose.process(rgb)

        landmarks = getattr(resultado, "pose_landmarks", None)
        if landmarks is None:
            return PoseFrame(indice=indice, detectado=False, puntos={}, puntos_mundo={})

        mundo = getattr(resultado, "pose_world_landmarks", None)
        puntos: dict[ArticulacionCanonica, Punto] = {}
        puntos_mundo: dict[ArticulacionCanonica, Punto] = {}
        for idx, art in MEDIAPIPE_A_CANONICO.items():
            lm = landmarks.landmark[idx]
            puntos[art] = Punto(
                x=float(lm.x), y=float(lm.y), z=float(lm.z),
                confianza=float(lm.visibility),
            )
            if mundo is not None:
                wm = mundo.landmark[idx]
                puntos_mundo[art] = Punto(
                    x=float(wm.x), y=float(wm.y), z=float(wm.z),
                    confianza=float(wm.visibility),
                )
        return PoseFrame(
            indice=indice, detectado=True, puntos=puntos, puntos_mundo=puntos_mundo
        )

    def cerrar(self) -> None:
        if self._pose is not None:
            self._pose.close()
            self._pose = None
