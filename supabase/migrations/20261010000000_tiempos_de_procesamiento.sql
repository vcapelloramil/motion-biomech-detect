-- Tiempos de procesamiento por video — primer dato del Criterio 4 (latencia de punta a punta).
--
-- Hasta hoy el tiempo de un análisis solo existía en el log de Render (`segundos_totales`): no había forma de
-- reconstruirlo desde la base. Tres instantes por video, los tres escritos por el servidor:
--   * encolado_en:               cuando la API aceptó la orden de analizar (POST /analisis/{id}/procesar).
--   * inicio_procesamiento_en:   cuando el contenedor empezó a procesarlo.
--   * fin_procesamiento_en:      cuando terminó, con éxito o con fallo.
-- Latencia de punta a punta = fin - encolado (incluye la espera en cola y el arranque en frío de Render);
-- tiempo de cómputo = fin - inicio.
--
-- authenticated ya tiene SELECT de tabla sobre `videos` (las ve) y ningún INSERT/UPDATE de estas columnas
-- (20261006130000 limitó el INSERT a cuatro columnas y retiró el UPDATE): no hace falta tocar permisos, y el
-- cliente no puede falsificarlas. service_role ya tiene el privilegio de tabla completo.

alter table public.videos
    add column encolado_en timestamptz,
    add column inicio_procesamiento_en timestamptz,
    add column fin_procesamiento_en timestamptz;

comment on column public.videos.encolado_en is
    'Cuándo la API aceptó analizar este video (último intento). Criterio 4: la latencia de punta a punta se mide desde acá.';
comment on column public.videos.inicio_procesamiento_en is
    'Cuándo el contenedor empezó a procesar este video (último intento).';
comment on column public.videos.fin_procesamiento_en is
    'Cuándo terminó el procesamiento (último intento), con éxito o con fallo.';
