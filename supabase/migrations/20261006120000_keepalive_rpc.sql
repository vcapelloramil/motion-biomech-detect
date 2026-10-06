-- Función de keep-alive para el workflow de GitHub Actions (.github/workflows/supabase-keepalive.yml).
--
-- El plan gratuito de Supabase pausa el proyecto tras 7 días sin actividad. El workflow necesita
-- una consulta REAL a la base por la API REST con la clave anon (nunca service_role). Pero a
-- "anon" no se le otorga nada sobre las tablas (ver 20261001090100_rls_policies.sql: datos de
-- salud), así que cualquier GET a una tabla con esa clave da 401 "permission denied" — comprobado
-- contra el proyecto real el 6/10.
--
-- Esta función no lee ninguna tabla ni devuelve ningún dato del sistema: solo la hora del
-- servidor. Es lo único que se le expone a "anon", y no abre ninguna tabla.
--   - SECURITY INVOKER: corre con los privilegios de quien llama (anon), sin elevarlos.
--   - search_path vacío: sin resolución de nombres que se pueda secuestrar.
--   - EXECUTE revocado a PUBLIC y otorgado solo a anon: con "exponer automáticamente" desactivado,
--     Supabase no lo hace solo, y no se quiere que lo llamen otros roles sin necesidad.

create or replace function public.keepalive()
returns timestamptz
language sql
stable
security invoker
set search_path = ''
as $$
  select now();
$$;

revoke all on function public.keepalive() from public;
grant execute on function public.keepalive() to anon;
