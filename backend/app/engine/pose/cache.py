"""Persistencia de las coordenadas de pose extraídas (plan, tarea 2.5).

La inferencia es la operación más lenta del pipeline. Cachearla en disco evita
re-inferir en cada iteración de E3/E4. Formato: un ``.pose.npz`` con los arrays y
un ``.pose.json`` con los metadatos de trazabilidad.

La clave de caché incluye el hash de la configuración del backend, así que dos
configuraciones distintas no se pisan. Al cargar se compara una firma rápida del
video de origen: si el archivo cambió, la caché se considera vencida.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose

# Versión del formato en disco. Se sube cuando cambia la estructura guardada, para
# invalidar cachés viejas aunque la config del backend no haya cambiado.
#   1 — solo puntos de imagen (Etapa 2)
#   2 — + puntos_mundo métricos (Etapa 3)
_ESQUEMA = 2


def firma_video(ruta: Path) -> str:
    """Identidad rápida del archivo: tamaño + mtime + sha1 de los primeros 64 KB."""
    st = ruta.stat()
    h = hashlib.sha1()
    h.update(str(st.st_size).encode())
    h.update(str(int(st.st_mtime)).encode())
    with ruta.open("rb") as f:
        h.update(f.read(65536))
    return h.hexdigest()


def clave_cache(video: Path, backend_id: str, config_hash: str) -> str:
    return f"{Path(video).stem}__{backend_id}__{config_hash[:12]}"


def ruta_base(cache_dir: Path, video: Path, backend_id: str, config_hash: str) -> Path:
    return Path(cache_dir) / "pose" / clave_cache(video, backend_id, config_hash)


def _p_npz(base: Path) -> Path:
    return Path(f"{base}.pose.npz")


def _p_json(base: Path) -> Path:
    return Path(f"{base}.pose.json")


def guardar(seq: SecuenciaPose, base: Path, *, video: Path | None = None) -> tuple[Path, Path]:
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    arts = list(seq.articulaciones)
    n = seq.n_frames

    detectado = np.zeros(n, dtype=bool)
    indices = np.zeros(n, dtype=np.int64)
    img = {a.value: np.full((n, 4), np.nan, dtype=np.float64) for a in arts}
    mundo = {a.value: np.full((n, 4), np.nan, dtype=np.float64) for a in arts}

    for i, frame in enumerate(seq.frames):
        indices[i] = frame.indice
        detectado[i] = frame.detectado
        for art, p in frame.puntos.items():
            img[art.value][i] = (p.x, p.y, np.nan if p.z is None else p.z, p.confianza)
        for art, p in frame.puntos_mundo.items():
            mundo[art.value][i] = (p.x, p.y, np.nan if p.z is None else p.z, p.confianza)

    np.savez_compressed(
        str(base) + ".pose",
        detectado=detectado,
        indices=indices,
        **{f"kp__{k}": v for k, v in img.items()},
        **{f"kpw__{k}": v for k, v in mundo.items()},
    )
    meta = {
        "esquema": _ESQUEMA,
        "backend_id": seq.backend_id,
        "backend_version": seq.backend_version,
        "articulaciones": [a.value for a in arts],
        "dims": seq.dims,
        "ancho": seq.ancho,
        "alto": seq.alto,
        "fps_efectivos": seq.fps_efectivos,
        "config_hash": seq.config_hash,
        "n_frames": n,
        "firma_video": firma_video(Path(video)) if video else None,
    }
    _p_json(base).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return _p_npz(base), _p_json(base)


def cargar(base: Path) -> SecuenciaPose:
    base = Path(base)
    meta = json.loads(_p_json(base).read_text(encoding="utf-8"))
    datos = np.load(_p_npz(base))

    arts = [ArticulacionCanonica(v) for v in meta["articulaciones"]]
    detectado = datos["detectado"]
    indices = datos["indices"]

    def _leer(prefijo: str, i: int) -> dict[ArticulacionCanonica, Punto]:
        salida: dict[ArticulacionCanonica, Punto] = {}
        for art in arts:
            clave = f"{prefijo}{art.value}"
            if clave not in datos:
                continue
            x, y, z, conf = datos[clave][i]
            if np.isnan(x):
                continue
            salida[art] = Punto(
                x=float(x), y=float(y),
                z=None if np.isnan(z) else float(z), confianza=float(conf),
            )
        return salida

    frames: list[PoseFrame] = []
    for i in range(meta["n_frames"]):
        frames.append(
            PoseFrame(
                indice=int(indices[i]),
                detectado=bool(detectado[i]),
                puntos=_leer("kp__", i),
                puntos_mundo=_leer("kpw__", i),
            )
        )

    return SecuenciaPose(
        backend_id=meta["backend_id"],
        backend_version=meta["backend_version"],
        articulaciones=tuple(arts),
        dims=meta["dims"],
        ancho=meta["ancho"],
        alto=meta["alto"],
        fps_efectivos=meta["fps_efectivos"],
        config_hash=meta["config_hash"],
        frames=frames,
    )


def cargar_si_vigente(
    cache_dir: Path, video: Path, backend_id: str, config_hash: str
) -> SecuenciaPose | None:
    """Devuelve la SecuenciaPose cacheada si existe y el video no cambió; si no, None."""
    base = ruta_base(cache_dir, video, backend_id, config_hash)
    if not (_p_npz(base).is_file() and _p_json(base).is_file()):
        return None
    meta = json.loads(_p_json(base).read_text(encoding="utf-8"))
    if meta.get("esquema") != _ESQUEMA:
        return None  # formato viejo: re-extraer
    if meta.get("firma_video") and meta["firma_video"] != firma_video(Path(video)):
        return None
    return cargar(base)
