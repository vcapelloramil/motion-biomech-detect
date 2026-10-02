-- Modo de captura declarado por el usuario, y trazabilidad de la escala temporal —
-- decisión 020 (ajuste del 2/10/2026), tarea 4.5.4.
--
-- El bug real encontrado en procesar_video.py (fps efectivos calculados 8 veces mal sobre
-- un clip de cámara lenta) se corrigió primero buscando el factor en catalogo.csv por
-- nombre de archivo — pero eso solo funciona con el corpus de prueba. Un usuario real sube
-- "IMG_4012.MOV" sin fila de catálogo; el archivo solo no alcanza (confirmado por Valentín:
-- los slow-mo de iPhone declaran 30 fps aunque se hayan capturado a 240, se recorten donde
-- se recorten). El usuario declara el modo de captura al cargar, una vez por sesión
-- (especificación de frontend §5); el motor combina esa declaración con el fps real del
-- contenedor (normalizado NTSC) y, si no cierra con un factor entero, el video queda
-- 'fallido' con un código de motivo — nunca se adivina en silencio (R3).
alter table public.sesiones
    add column modo_captura text not null
        check (modo_captura in ('normal', 'camara_lenta_120', 'camara_lenta_240'));

-- Motivo del estado 'fallido', como CÓDIGO cerrado, no texto libre: el texto en lenguaje
-- llano para el usuario lo resuelve el frontend (R2); el detalle técnico (fps del
-- contenedor, factor calculado) va al log del contenedor, no a esta columna ni a lo que
-- ve el jugador. Un solo código hoy porque es el único motivo de fallo implementado;
-- motivos nuevos (video corrupto, formato no soportado, etc.) se agregan con una
-- migración nueva cuando existan de verdad, no se anticipan acá.
alter table public.videos
    add column motivo_fallo text
        check (motivo_fallo is null or motivo_fallo in ('modo_captura_incompatible'));

-- Trazabilidad (R4) de la escala temporal: de dónde salió fps_efectivos y si es confiable
-- para velocidades absolutas, no solo para el orden de los picos. Ya existe en el contrato
-- JSON congelado (backend/app/schemas/reporte.py: Trazabilidad.escala_temporal_conocida)
-- pero nunca se persistía en la base — se agrega ahora, junto con el resto de este ajuste.
alter table public.reportes_biomecanicos
    add column escala_temporal_conocida boolean not null default false,
    add column origen_factor text;
