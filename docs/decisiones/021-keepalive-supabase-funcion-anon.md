# Decisión 021 — Keep-alive de Supabase con una función ejecutable por `anon` (excepción a "nada a anon")

**Fecha:** 6 de octubre de 2026
**Estado:** vigente (excepción aprobada por Valentín el 6/10)
**Afecta a:** `supabase/migrations/20261006120000_keepalive_rpc.sql` · `.github/workflows/supabase-keepalive.yml` ·
decisión 018 (punto de RLS: "nunca se otorga nada al rol `anon`", `20261001090100_rls_policies.sql`)

## El problema

El plan gratuito de Supabase pausa el proyecto tras 7 días sin actividad. Última actividad conocida al
momento de decidir: 6/10, así que la pausa llegaría hacia el 13/10, con el proyecto aún en uso por las
pruebas y la Etapa 5. Hace falta un keep-alive automático (GitHub Actions, cada 3 días) que haga una
consulta real a la base por la API REST.

El workflow vive en GitHub, no en el contenedor del motor, así que la clave que use queda guardada como
*secret* de un servicio externo. Por eso la restricción de partida fue usar la clave `anon`/publishable y
**nunca** la `service_role`.

El obstáculo, comprobado contra el proyecto real el 6/10: las migraciones de la decisión 018 no otorgan
nada a `anon` (son datos de salud, Ley 25.326), así que con esa clave cualquier `GET` a una tabla da
`401 permission denied` (código 42501), y la raíz `/rest/v1/` responde `Invalid API key` (solo
`service_role`). Una consulta con `anon` no puede dar 2xx sin abrir algo.

## Alternativas consideradas

1. **Usar `service_role` como secret de GitHub.** Funciona sin tocar la base, pero guarda en un servicio
   externo una clave que bypasea RLS y da acceso total a datos de salud. Una filtración del repo, de un
   log de Actions o de una cuenta de GitHub comprometida expondría todo. **Descartada** (decisión explícita
   de Valentín desde el pedido original).
2. **`GRANT SELECT` a `anon` sobre una tabla** (p. ej. `versiones_motor`, la menos sensible). Abre una
   tabla real a clientes sin sesión y rompe el principio de 018 aunque sea con poco riesgo hoy; además
   queda una puerta que alguien podría ampliar sin pensarlo. **Descartada.**
3. **Función `public.keepalive()` que solo devuelve `now()`, ejecutable por `anon`.** Es una consulta real
   que pasa por la API REST y por Postgres, sin leer ninguna tabla ni exponer datos. **Elegida.**

## Decisión

Se agrega `public.keepalive()` (`returns timestamptz`, `language sql`, `stable`):

- `security invoker`: corre con los privilegios de quien llama (`anon`), sin elevarlos.
- `set search_path = ''`: sin resolución de nombres secuestrable.
- `revoke all ... from public` y `grant execute ... to anon`: es el único objeto que `anon` puede ejecutar.
- Cuerpo: `select now();`. No toca ninguna tabla, vista ni esquema `auth`/`storage`.

El workflow hace `POST /rest/v1/rpc/keepalive` con los secrets `SUPABASE_URL` y `SUPABASE_ANON_KEY` del
repo. Falla visiblemente (job en rojo, código HTTP y cuerpo en el log) si la respuesta no es 2xx, y rechaza
una clave `service_role` o `sb_secret_` puesta por error en el secret.

## Consecuencias

- **La regla de 018 queda con una excepción única y acotada:** `anon` no tiene acceso a ninguna tabla; solo
  puede ejecutar `keepalive()`. Cualquier otra función o tabla expuesta a `anon` exige una decisión nueva.
- `anon` puede llamar a la función sin límite propio; el costo es una consulta trivial. Si hubiera abuso, se
  limita en el borde (Supabase) o se revoca el `EXECUTE`, sin tocar nada más.
- **Límites que no se pueden verificar desde el repo:** (a) que Supabase cuente este llamado como actividad
  para su contador de pausa — es una consulta real a Postgres por la API, el método habitual, pero hay que
  confirmar en el panel pasado el 13/10 que el proyecto siga activo; (b) si el repo es público, GitHub
  desactiva los workflows programados tras 60 días sin actividad en el repo.
- Si el proyecto pasa a un plan de pago, el workflow y la función dejan de ser necesarios y se pueden
  retirar con una decisión que supersede a esta.
- Al rotar la clave anon hay que actualizar el secret `SUPABASE_ANON_KEY` de GitHub.
