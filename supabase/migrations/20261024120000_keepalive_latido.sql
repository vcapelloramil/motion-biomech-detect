-- Ajuste de la decisión 021 (24/10/2026): el keep-alive además ESCRIBE en la base.
--
-- Supabase mandó el aviso de inactividad el 24/10 aunque el workflow corría bien (7 de 7 en verde, cada 3 días). Su documentación
-- (https://supabase.com/docs/guides/platform/free-project-pausing) pide "unos pocos pedidos de usuario por día" de actividad en la
-- base, y un `select now()` cada 3 días no lo es. Ahora el workflow corre 3 veces por día y cada llamada hace un upsert en una tabla
-- de UNA sola fila: una escritura real, de un usuario real (anon), todos los días.
--
-- Qué NO cambia respecto de la 021:
--   - `anon` sigue sin poder leer ni escribir NINGUNA tabla: la tabla nueva tiene RLS activado y NINGUNA política, y se le revocan
--     todos los privilegios a PUBLIC, anon y authenticated.
--   - La función sigue sin parámetros y devuelve la hora, así que el workflow no cambia de contrato (POST /rest/v1/rpc/keepalive).
--   - No se usa service_role en ningún lado.
--
-- Qué cambia: la función pasa de SECURITY INVOKER a SECURITY DEFINER (corre con los privilegios de su dueño, que es quien puede
-- escribir en la tabla; el dueño no queda sujeto a RLS porque NO se fuerza). Por eso:
--   - search_path fijo y vacío (todo calificado con `public.`): sin resolución de nombres que se pueda secuestrar;
--   - EXECUTE revocado a PUBLIC y otorgado solo a anon (Supabase no lo hace solo);
--   - lo único que puede hacer es actualizar la hora de la fila 1: no recibe parámetros ni lee nada.

create table if not exists public.keepalive_latido (
  id            smallint primary key check (id = 1),   -- una sola fila: solo se admite el id 1
  ultimo_latido timestamptz not null default now()
);

comment on table public.keepalive_latido is
  'Una sola fila (id = 1) con la hora del último keep-alive. La escribe public.keepalive(); nadie más (decisión 021, ajuste del 24/10/2026).';

alter table public.keepalive_latido enable row level security;
-- Sin políticas, a propósito: ningún rol con RLS puede leer ni escribir. Solo la función (SECURITY DEFINER) toca la tabla.

revoke all on table public.keepalive_latido from public, anon, authenticated;

create or replace function public.keepalive()
returns timestamptz
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  hora timestamptz := now();
begin
  insert into public.keepalive_latido (id, ultimo_latido)
  values (1, hora)
  on conflict (id) do update set ultimo_latido = excluded.ultimo_latido;
  return hora;
end;
$$;

revoke all on function public.keepalive() from public;
grant execute on function public.keepalive() to anon;
