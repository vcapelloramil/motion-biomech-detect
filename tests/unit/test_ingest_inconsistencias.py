"""Contraste de metadatos entre sí (decisión 001, verificación 1). Lógica pura."""

from app.engine.ingest import MetadatosVideo, detectar_inconsistencias, evaluar


def test_clip_coherente_no_dispara_avisos():
    md = MetadatosVideo(
        ruta="ok.mp4",
        fps_declarados=25.0,
        nb_frames=750,
        duracion_s=30.0,  # 750 / 30 = 25 -> coincide
        ancho=1920,
        alto=1080,
    )
    assert detectar_inconsistencias(md) == []


def test_declarados_no_coinciden_con_conteo_sobre_duracion():
    md = MetadatosVideo(
        ruta="raro.mp4",
        fps_declarados=30.0,
        nb_frames=750,
        duracion_s=30.0,  # 750 / 30 = 25, declarado 30 -> ~17% de diferencia
        ancho=1920,
        alto=1080,
    )
    avisos = detectar_inconsistencias(md)
    assert any("no coincide" in a for a in avisos)


def test_r_frame_rate_vs_avg_frame_rate():
    md = MetadatosVideo(
        ruta="vfr.mp4",
        fps_declarados=30.0,
        nb_frames=900,
        duracion_s=30.0,
        ancho=1920,
        alto=1080,
        r_frame_rate=30.0,
        avg_frame_rate=24.0,  # 20% por debajo
    )
    avisos = detectar_inconsistencias(md)
    assert any("avg_frame_rate" in a for a in avisos)


def test_metadatos_faltantes_se_reportan():
    md = MetadatosVideo(
        ruta="vacio.mp4",
        fps_declarados=0.0,
        nb_frames=0,
        duracion_s=0.0,
        ancho=0,
        alto=0,
    )
    avisos = detectar_inconsistencias(md)
    assert len(avisos) >= 2  # tasa, cantidad de fotogramas, duración


def test_las_inconsistencias_viajan_en_el_resultado():
    md = MetadatosVideo(
        ruta="raro.mp4",
        fps_declarados=30.0,
        nb_frames=750,
        duracion_s=30.0,
        ancho=1920,
        alto=1080,
    )
    r = evaluar(md, factor=1.0)
    assert r.inconsistencias  # no vacío
