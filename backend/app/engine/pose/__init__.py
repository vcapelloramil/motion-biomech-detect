"""Estimación de pose: contrato intercambiable + backends (Etapa 2)."""

from app.engine.pose.articulaciones import (
    ARTICULACIONES_CORE,
    COCO_A_CANONICO,
    MEDIAPIPE_A_CANONICO,
    ArticulacionCanonica,
)
from app.engine.pose.base import (
    PoseBackend,
    PoseFrame,
    Punto,
    SecuenciaPose,
    hash_config,
)
from app.engine.pose.fake_backend import FakeBackend

__all__ = [
    "ArticulacionCanonica",
    "ARTICULACIONES_CORE",
    "MEDIAPIPE_A_CANONICO",
    "COCO_A_CANONICO",
    "Punto",
    "PoseFrame",
    "SecuenciaPose",
    "PoseBackend",
    "hash_config",
    "FakeBackend",
]
