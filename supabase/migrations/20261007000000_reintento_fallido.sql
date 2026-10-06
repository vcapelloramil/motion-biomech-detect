-- Reintento fallido -> encolado — decisión 022, paso (b).
--
-- Tres piezas, todas para que reintentar sea posible sin reanalizar lo que no falló por la declaración:
--   1. Un código de motivo para el fallo inesperado (hoy el `except` de procesar_video deja
--      motivo_fallo en null, indistinguible de "nunca falló", o con el motivo viejo de otra corrida).
--   2. Dos columnas de trazabilidad por video: con qué modo de captura se intentó, y cuántos intentos.
--   3. Un trigger que impide cambiar lo que invalida un análisis cuando la sesión ya tiene golpes
--      analizados o en proceso.
--
-- Las dos columnas nuevas las escribe el motor: no se otorgan a "authenticated" (20261006130000 dejó
-- el INSERT de videos limitado a 4 columnas y ningún UPDATE) y service_role ya tiene el privilegio de
-- tabla completo.

-- 1. Motivo de fallo inesperado. El CHECK de columna inline se llama videos_motivo_fallo_check
--    (convención de Postgres: tabla_columna_check); se reemplaza por uno con el código nuevo.
alter table public.videos drop constraint videos_motivo_fallo_check;
alter table public.videos
    add constraint videos_motivo_fallo_check
        check (motivo_fallo is null or motivo_fallo in ('modo_captura_incompatible', 'error_inesperado'));

-- 2. Trazabilidad (R4) del intento.
alter table public.videos
    add column modo_captura_intentado text
        check (modo_captura_intentado is null
               or modo_captura_intentado in ('normal', 'camara_lenta_120', 'camara_lenta_240')),
    add column intentos integer not null default 0
        check (intentos >= 0);

comment on column public.videos.modo_captura_intentado is
    'sesiones.modo_captura vigente al empezar el último intento. Sin él no se puede saber si el usuario corrigió la declaración antes de reintentar (decisión 022).';
comment on column public.videos.intentos is
    'Cantidad de veces que se encoló este video para procesarlo (decisión 022). Acota los reintentos de error_inesperado.';

-- 3. Cambiar lo que invalida un análisis con golpes ya analizados deja escalas, encuadres o atletas
--    mezclados dentro de una sesión: los reportes congelan el modo con el que se calcularon
--    (decisión 020), pero no se re-calculan solos. Se rechaza en la base y no solo en el frontend,
--    porque el usuario edita sesiones directo con RLS.
--
--    Campos vigilados: modo_captura (escala temporal), gesto y encuadre (qué se evalúa y cómo se
--    lee), lado_camara (qué lado se ve), atleta_id (de él sale la mano dominante). `fecha` no: es una
--    corrección de calendario que no cambia ningún cálculo.
--
--    Estados que bloquean: encolado, procesando, completado, parcial. Quedan libres 'pendiente' y
--    'fallido': si todos los golpes fallaron (o aún no se procesaron) no hay nada analizado que
--    contradecir, y es justamente el caso del reintento.
--
--    SECURITY DEFINER para ver TODOS los videos de la sesión sin depender de la RLS de quien edita;
--    search_path vacío y nombres calificados, como en 20261006120000_keepalive_rpc.sql.
create function public.bloquear_cambio_con_golpes_analizados()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
    if exists (
        select 1
        from public.videos v
        where v.sesion_id = old.id
          and v.estado in ('encolado', 'procesando', 'completado', 'parcial')
    ) then
        raise exception 'sesion_con_golpes_analizados'
            using detail = 'No se puede cambiar el modo de captura, el gesto, el encuadre, el lado de cámara ni el atleta de una sesión con golpes encolados, en proceso o ya analizados.',
                  hint = 'Creá una sesión nueva para ese video.';
    end if;
    return new;
end;
$$;

revoke all on function public.bloquear_cambio_con_golpes_analizados() from public;

create trigger sesiones_bloquear_cambio_con_golpes_analizados
    before update on public.sesiones
    for each row
    when (
        old.modo_captura is distinct from new.modo_captura
        or old.gesto is distinct from new.gesto
        or old.encuadre is distinct from new.encuadre
        or old.lado_camara is distinct from new.lado_camara
        or old.atleta_id is distinct from new.atleta_id
    )
    execute function public.bloquear_cambio_con_golpes_analizados();
