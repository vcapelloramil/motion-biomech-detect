"""¿Los techos de plausibilidad detectan un clip NORMAL declarado como cámara lenta? — decisión 020.

El error inverso al que originó la decisión: el usuario declara `camara_lenta_240` sobre un
video grabado en modo normal. El factor resultante es un entero (240/60 = 4, 240/30 = 8), así
que la combinación declaración + contenedor NO falla (`_factor_y_motivo` la acepta, es lo
esperado); lo único que queda para frenar un reporte limpio-pero-falso son los techos de
plausibilidad de `engine/sequencing.py` (Fleisig x 3, por segmento).

Esta prueba **caracteriza lo observado** el 2/10/2026 sobre tres clips reales de modo normal:
- el recorte propio de 60 fps (`20260924_VCR_saque_perfil_060_01_rep01.mov`, factor 4),
- `control_drive_30fps_01` (corpus público, 30 fps, factor 8),
- `saque_perfil_030` (original propio, 30 fps, factor 8).

Con la declaración correcta (fps del contenedor) ningún techo se dispara. Declarados
`camara_lenta_240`, los tres quedan con la repetición NO auditable por "velocidad implausible"
(no sale un reporte limpio). **Ojo, la detección es condicional**, no una garantía: salta
solo porque el segmento más rápido de ESTOS jugadores supera techo/factor — pelvis > 330 °/s
reales con factor 4, o torso > 326 °/s con factor 8 —; un golpe más lento pasaría los techos
con un orden "correcto" y números inflados (ver la propuesta de control adicional en la
decisión 020 / bitácora). Si algún día se cambian los techos o el pipeline y esta prueba
falla, es una señal real de que cambió esa red de seguridad, no un detalle.

La pose se extrae una vez por clip y se cachea (`KINETIQ_CACHE_DIR`): los puntos no dependen
de los fps, solo la interpretación temporal, así que se reevalúa E3+E4 con `dataclasses.replace`
sin repetir la inferencia. **Sin caché la primera corrida tarda ~6 minutos** (el original de
30 fps tiene 1385 fotogramas).

No toca Supabase ni Render. Se salta si faltan los clips en KINETIQ_DATA_DIR.
"""

from __future__ import annotations

import dataclasses

import pytest

try:
    from app.config import get_cache_dir, get_data_dir

    _BASE = get_data_dir()
except Exception:  # ConfigError u otra: no hay corpus configurado
    _BASE = None

_CLIPS = (
    ("recorte_060", "fase-b/sesion-01/saque/recortes/20260924_VCR_saque_perfil_060_01_rep01.mov", 60.0),
    ("control_drive_30", "fase-a/control/control_drive_30fps_01.mp4", 30.0),
    ("saque_perfil_030", "fase-b/sesion-01/saque/originales/20260924_VCR_saque_perfil_030_01.mov", 30.0),
)
_FALTAN = [rel for _, rel, _ in _CLIPS if not (_BASE and (_BASE / rel).is_file())]

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(bool(_FALTAN), reason=f"Faltan clips en KINETIQ_DATA_DIR: {_FALTAN}"),
]


def _pose_de(video):
    """Pose del clip desde la caché; si no está, se extrae UNA vez y se guarda."""
    from app.engine.ingest import iterar_fotogramas, normalizar_fps, probe
    from app.engine.pose import cache as pose_cache
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    backend = MediaPipeBackend()
    seq = pose_cache.cargar_si_vigente(get_cache_dir(), video, backend.id, backend.config_hash)
    if seq is not None:
        return seq
    md = probe(video)
    with MediaPipeBackend(model_complexity=2) as be:
        seq = be.procesar(
            iterar_fotogramas(video), ancho=md.ancho, alto=md.alto, fps_efectivos=normalizar_fps(md.fps_declarados)
        )
    pose_cache.guardar(seq, pose_cache.ruta_base(get_cache_dir(), video, backend.id, backend.config_hash), video=video)
    return seq


def _repeticion(seq, fps_efectivos: float):
    """La misma invocación que `procesar_video`: E3 + secuenciación anclada al torso."""
    from app.engine.pipeline import procesar_e3
    from app.engine.sequencing import secuenciar

    filt = procesar_e3(dataclasses.replace(seq, fps_efectivos=float(fps_efectivos)))
    resultados, _ = secuenciar(
        filt.secuencia,
        lado_dominante="der",
        tramos_excluidos=filt.tramos_excluidos,
        brazo_via="codo",
        ancla="torso",
    )
    return resultados[0]


def _motivos(rep) -> list[str]:
    motivos = [p.motivo for p in rep.picos.values() if p.motivo]
    if rep.motivo_no_auditable:
        motivos.append(rep.motivo_no_auditable)
    return motivos


def _hay_techo_disparado(rep) -> bool:
    return any("velocidad implausible" in m for m in _motivos(rep))


@pytest.fixture(scope="module")
def poses():
    return {nombre: _pose_de(_BASE / rel) for nombre, rel, _ in _CLIPS}


@pytest.mark.parametrize("nombre,rel,fps_contenedor", _CLIPS)
def test_declaracion_correcta_no_dispara_ningun_techo(poses, nombre, rel, fps_contenedor):
    """Control: con los fps reales del contenedor (modo normal) los techos NO se disparan —
    si lo hicieran, la prueba de abajo no distinguiría nada."""
    rep = _repeticion(poses[nombre], fps_contenedor)
    assert not _hay_techo_disparado(rep), _motivos(rep)


@pytest.mark.parametrize("nombre,rel,fps_contenedor", _CLIPS)
def test_normal_declarado_camara_lenta_240_no_sale_como_reporte_limpio(poses, nombre, rel, fps_contenedor):
    """Lo observado el 2/10/2026: los tres quedan con un techo disparado y la repetición no
    auditable. Es la red de seguridad que hoy existe (condicional, ver el docstring del módulo)."""
    rep = _repeticion(poses[nombre], 240.0)
    assert _hay_techo_disparado(rep), (
        f"{nombre} (factor {240 / fps_contenedor:.0f}): ningún techo se disparó; motivos: {_motivos(rep)}"
    )
    assert not rep.auditable
