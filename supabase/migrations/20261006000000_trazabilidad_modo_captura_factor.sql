-- Trazabilidad (R4) del modo de captura declarado y del factor de ralentización, en el propio
-- reporte — decisión 020, 6/10/2026.
--
-- La migración 20261002000000 agregó escala_temporal_conocida y origen_factor al reporte, pero
-- faltaban dos datos para poder reconstruir de dónde salió fps_efectivos:
--   * modo_captura: lo que el usuario declaró. Vive en sesiones.modo_captura, pero ESE valor es
--     editable después (el frontend va a dejar corregir una declaración equivocada y reintentar el
--     análisis): el reporte tiene que congelar lo que se usó EN ESE ANÁLISIS, no leerlo de la
--     sesión después. Misma razón por la que el reporte ya guarda version_motor_id y corte_filtro_hz.
--   * factor_ralentizacion: fps declarado por el usuario / fps del contenedor (normalizado NTSC);
--     1 en modo normal. No se guardaba en ningún lado: era un cálculo intermedio de procesar_video.
-- fps_efectivos = fps del contenedor (normalizado) x factor_ralentizacion, y el reporte ya lleva
-- videos.fps_real; con estas dos columnas la cuenta se puede rehacer y auditar.
--
-- not null sin default a propósito: un reporte sin esto no es auditable (R4), así que ningún
-- INSERT puede omitirlos. reportes_biomecanicos está vacía hoy (verificado), no hay filas que
-- rellenar.
alter table public.reportes_biomecanicos
    add column modo_captura text not null
        check (modo_captura in ('normal', 'camara_lenta_120', 'camara_lenta_240')),
    add column factor_ralentizacion numeric not null
        check (factor_ralentizacion >= 1);
