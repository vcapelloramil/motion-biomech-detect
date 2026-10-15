"""Respaldo lógico (paso 7): la carpeta de salida no puede estar en el repositorio y `verificar` detecta una copia dañada."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app import respaldo


def test_la_salida_dentro_del_repositorio_se_rechaza(tmp_path):
    assert respaldo.fuera_del_repo(tmp_path) is True
    assert respaldo.fuera_del_repo(respaldo.RAIZ_REPO) is False
    assert respaldo.fuera_del_repo(respaldo.RAIZ_REPO / "docs" / "respaldos") is False


def _copia_minima(raiz: Path) -> Path:
    c = raiz / "respaldo-prueba"
    (c / "tablas").mkdir(parents=True)
    (c / "auth").mkdir()
    (c / "storage" / "videos" / "u1" / "v1").mkdir(parents=True)
    (c / "storage" / "artefactos").mkdir(parents=True)
    archivo = c / "storage" / "videos" / "u1" / "v1" / "original.mov"
    archivo.write_bytes(b"contenido del video")
    fila_video = {"id": "v1", "ruta_almacenamiento": "u1/v1/original.mov", "ruta_fotograma_pelvis": None}
    tablas = {}
    for t in respaldo.TABLAS:
        p = c / "tablas" / f"{t}.jsonl"
        texto = (json.dumps(fila_video) + "\n") if t == "videos" else ""
        p.write_bytes(texto.encode("utf-8"))
        tablas[t] = {"filas": 1 if t == "videos" else 0, "sha256": hashlib.sha256(texto.encode()).hexdigest()}
    pa = c / "auth" / "usuarios.jsonl"
    pa.write_text("", encoding="utf-8")
    man = {
        "tablas": tablas,
        "auth": {"usuarios": 0, "sha256": hashlib.sha256(b"").hexdigest()},
        "storage": {
            "videos": {
                "archivos": 1,
                "bytes": 19,
                "lista": [{"ruta": "u1/v1/original.mov", "bytes": 19, "bytes_listados": 19, "sha256": hashlib.sha256(b"contenido del video").hexdigest()}],
            },
            "artefactos": {"archivos": 0, "bytes": 0, "lista": []},
        },
    }
    (c / "manifiesto.json").write_text(json.dumps(man), encoding="utf-8")
    return c


def test_una_copia_integra_verifica(tmp_path):
    assert respaldo.verificar(_copia_minima(tmp_path)) == []


def test_un_archivo_alterado_o_faltante_se_detecta(tmp_path):
    c = _copia_minima(tmp_path)
    (c / "storage" / "videos" / "u1" / "v1" / "original.mov").write_bytes(b"otro contenido!!!!!!")
    assert any("no coincide con su huella" in p for p in respaldo.verificar(c))
    (c / "storage" / "videos" / "u1" / "v1" / "original.mov").unlink()
    assert any("falta videos/u1/v1/original.mov" in p for p in respaldo.verificar(c))


def test_una_fila_que_apunta_a_un_archivo_inexistente_se_detecta(tmp_path):
    c = _copia_minima(tmp_path)
    p = c / "tablas" / "videos.jsonl"
    texto = json.dumps({"id": "v2", "ruta_almacenamiento": "u1/v2/original.mov"}) + "\n"
    p.write_bytes(texto.encode("utf-8"))
    man = json.loads((c / "manifiesto.json").read_text(encoding="utf-8"))
    man["tablas"]["videos"] = {"filas": 1, "sha256": hashlib.sha256(texto.encode()).hexdigest()}
    (c / "manifiesto.json").write_text(json.dumps(man), encoding="utf-8")
    assert any("v2" in p and "no está en videos/" in p for p in respaldo.verificar(c))
