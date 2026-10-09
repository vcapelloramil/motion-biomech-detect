-- Reporte persistido como JSON y motivo de fallo para el archivo convertido — decisiones 024, 029 y 030.
--
-- Dos piezas del flujo de punta a punta (piezas 1 a 3 del plan):
--   1. reportes_biomecanicos.reporte (jsonb): el reporte COMPLETO, validado contra el contrato v1.1
--      (backend/app/schemas/reporte.py) antes de guardarse. Las columnas planas de la tabla se
--      mantienen: sirven para consultar sin abrir el JSON y el reporte las repite a propósito.
--   2. videos.motivo_fallo = 'archivo_convertido': el teléfono convirtió el video al subirlo (p. ej. el
--      formato por defecto de Fotos lo pasa a H.264 a 100 fps) y llegó con menos de 120 fps reales
--      aunque el usuario declaró cámara lenta. Es un motivo propio porque el mensaje correcto es otro
--      ("tocá Opciones -> Formato: Actual, o subilo desde Archivos"), no "revisá el modo de captura".
--
-- No hace falta tocar permisos: authenticated ya tiene SELECT de tabla (la RLS filtra por dueño) y
-- solo service_role escribe en reportes_biomecanicos.

-- 1. El reporte completo. Nullable: las filas anteriores (pruebas) no lo tienen y no se reconstruye.
alter table public.reportes_biomecanicos
    add column reporte jsonb
        check (reporte is null or jsonb_typeof(reporte) = 'object');

comment on column public.reportes_biomecanicos.reporte is
    'Reporte completo, validado contra el contrato (app/schemas/reporte.py) antes de guardarlo. Lleva su propia version_contrato (RNF-02). null en filas anteriores a la decisión 030.';

-- 2. Motivo de fallo propio. El CHECK de columna se llama videos_motivo_fallo_check (ver
--    20261007000000_reintento_fallido.sql); se reemplaza por uno con el código nuevo.
alter table public.videos drop constraint videos_motivo_fallo_check;
alter table public.videos
    add constraint videos_motivo_fallo_check
        check (motivo_fallo is null
               or motivo_fallo in ('modo_captura_incompatible', 'error_inesperado', 'archivo_convertido'));
