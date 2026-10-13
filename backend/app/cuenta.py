"""Eliminar la cuenta y todos sus datos — paso 5 del plan §8 (derecho de supresión, Ley 25.326).

La base borra en cascada (``auth.users`` → ``usuarios`` → ``atletas`` → ``sesiones`` → ``videos`` → ``reportes_*``), pero **los archivos de
Storage no**: el original y los artefactos de cada golpe (fotogramas y video con esqueleto) están en dos buckets privados. Por eso el borrado
es del servidor, con ``service_role``: primero los archivos, **después** la cuenta.

El orden importa: si los archivos fallan, la cuenta **no** se borra y el usuario puede reintentar. Al revés, quedarían archivos con una persona
identificable en un bucket sin ninguna fila que los referencie y sin forma de pedir su borrado.

Función aparte del router para probarla sin red.
"""

from __future__ import annotations

from typing import Any

BUCKETS_DEL_USUARIO = ("videos", "artefactos")
_PAGINA = 100
# Storage rechaza listas muy largas en `remove`; de a lotes.
_LOTE_BORRADO = 100
_PROFUNDIDAD_MAXIMA = 6


def rutas_del_usuario(storage: Any, bucket: str, usuario_id: str) -> list[str]:
    """Todos los objetos del usuario en un bucket: la carpeta ``<usuario_id>/`` recorrida a fondo y paginada (``<usuario>/<video>/<archivo>``)."""
    rutas: list[str] = []
    pendientes: list[tuple[str, int]] = [(usuario_id, 0)]
    while pendientes:
        carpeta, nivel = pendientes.pop()
        offset = 0
        while True:
            items = storage.from_(bucket).list(carpeta, {"limit": _PAGINA, "offset": offset}) or []
            for it in items:
                ruta = f"{carpeta}/{it['name']}"
                if it.get("id") is None:          # una carpeta (Storage no tiene carpetas reales: un prefijo sin id)
                    if nivel < _PROFUNDIDAD_MAXIMA:
                        pendientes.append((ruta, nivel + 1))
                else:
                    rutas.append(ruta)
            if len(items) < _PAGINA:
                break
            offset += _PAGINA
    return rutas


def eliminar_cuenta(admin: Any, usuario_id: str) -> dict[str, int]:
    """Borra los archivos del usuario y, si todo salió bien, su cuenta (y por cascada, sus datos). Devuelve cuántos archivos borró.

    Si un borrado de archivos falla, relanza: la cuenta queda como estaba."""
    borrados = 0
    for bucket in BUCKETS_DEL_USUARIO:
        rutas = rutas_del_usuario(admin.storage, bucket, usuario_id)
        for i in range(0, len(rutas), _LOTE_BORRADO):
            admin.storage.from_(bucket).remove(rutas[i : i + _LOTE_BORRADO])
        borrados += len(rutas)
    admin.auth.admin.delete_user(usuario_id)
    return {"archivos_eliminados": borrados}
