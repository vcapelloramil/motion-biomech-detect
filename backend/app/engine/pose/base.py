"""Contrato de percepción intercambiable (plan, tarea 2.1; tesis §4.4.3).

El motor no sabe qué estimador de pose se usó. Habla con este contrato:

- ``Punto`` — un punto articular (x, y normalizados a la imagen; z relativo o None; confianza).
- ``PoseFrame`` — la pose de un fotograma: qué articulaciones se vieron y con qué confianza.
- ``SecuenciaPose`` — la secuencia completa + metadatos de trazabilidad.
- ``PoseBackend`` — la clase base que cada estimador implementa. Solo hay que
  escribir ``estimar_frame``; el recorrido y el ensamblado los da ``procesar``.

Sobre este contrato se implementa MediaPipe (por defecto, §4.4.3) y, más adelante,
la Vía A (YOLOv8-Pose 2D + elevación). ``dims=2`` en un backend puramente
bidimensional: ``z`` es siempre None y el motor lo sabe por ``SecuenciaPose.dims``.
"""

from __future__ import annotations

import abc
import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica


@dataclass(frozen=True, slots=True)
class Punto:
    """Un punto articular en un fotograma.

    x, y: coordenadas en la imagen, normalizadas a [0, 1] (0,0 = esquina superior
    izquierda). z: profundidad relativa estimada (MediaPipe) o None si el backend
    es bidimensional. confianza: [0, 1] (para MediaPipe, la 'visibility').
    """

    x: float
    y: float
    z: float | None
    confianza: float


@dataclass(frozen=True, slots=True)
class PoseFrame:
    indice: int
    detectado: bool
    puntos: dict[ArticulacionCanonica, Punto] = field(default_factory=dict)

    def get(self, art: ArticulacionCanonica) -> Punto | None:
        return self.puntos.get(art)


@dataclass(frozen=True)
class SecuenciaPose:
    backend_id: str
    backend_version: str
    articulaciones: tuple[ArticulacionCanonica, ...]
    dims: int  # 2 (z siempre None) o 3
    ancho: int
    alto: int
    fps_efectivos: float
    config_hash: str
    frames: list[PoseFrame]

    @property
    def n_frames(self) -> int:
        return len(self.frames)

    @property
    def cobertura(self) -> float:
        """Fracción de fotogramas con una persona detectada."""
        if not self.frames:
            return 0.0
        return sum(1 for f in self.frames if f.detectado) / len(self.frames)

    def cobertura_articulacion(
        self, art: ArticulacionCanonica, *, umbral_confianza: float = 0.0
    ) -> float:
        """Fracción de fotogramas donde ``art`` está presente por encima del umbral."""
        if not self.frames:
            return 0.0
        n = sum(
            1
            for f in self.frames
            if (p := f.puntos.get(art)) is not None and p.confianza >= umbral_confianza
        )
        return n / len(self.frames)


def hash_config(config: dict) -> str:
    """Huella estable de la configuración de un backend (para la clave de caché)."""
    payload = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


class PoseBackend(abc.ABC):
    """Contrato que cumple cualquier estimador de pose usable por el motor."""

    dims: int = 3  # los backends 2D lo ponen en 2

    @property
    @abc.abstractmethod
    def id(self) -> str:
        """Identificador corto del backend, p. ej. 'mediapipe'."""

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Versión legible, p. ej. 'mediapipe-0.10.18'. Va al reporte (R4)."""

    @property
    @abc.abstractmethod
    def articulaciones_disponibles(self) -> tuple[ArticulacionCanonica, ...]:
        """Articulaciones canónicas que este backend puede entregar."""

    @abc.abstractmethod
    def _config(self) -> dict:
        """Parámetros que afectan la salida (entran en la clave de caché)."""

    @abc.abstractmethod
    def estimar_frame(self, frame_bgr: np.ndarray, indice: int) -> PoseFrame:
        """Estima la pose de UN fotograma (imagen BGR de OpenCV)."""

    def cerrar(self) -> None:
        """Libera recursos. Sin efecto por defecto."""

    def __enter__(self) -> PoseBackend:
        return self

    def __exit__(self, *exc: object) -> bool:
        self.cerrar()
        return False

    @property
    def config(self) -> dict:
        """Parámetros que afectan la salida (copia legible, para logs/reportes)."""
        return dict(self._config())

    @property
    def config_hash(self) -> str:
        return hash_config(
            {"backend": self.id, "version": self.version, **self._config()}
        )

    def procesar(
        self,
        fotogramas: Iterable[np.ndarray],
        *,
        ancho: int,
        alto: int,
        fps_efectivos: float,
        max_frames: int | None = None,
    ) -> SecuenciaPose:
        """Recorre los fotogramas y arma la SecuenciaPose. No hace falta redefinirlo."""
        frames: list[PoseFrame] = []
        for i, frame in enumerate(fotogramas):
            if max_frames is not None and i >= max_frames:
                break
            frames.append(self.estimar_frame(frame, i))
        return SecuenciaPose(
            backend_id=self.id,
            backend_version=self.version,
            articulaciones=tuple(self.articulaciones_disponibles),
            dims=self.dims,
            ancho=ancho,
            alto=alto,
            fps_efectivos=fps_efectivos,
            config_hash=self.config_hash,
            frames=frames,
        )
