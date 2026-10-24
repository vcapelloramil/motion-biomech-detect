# Decisión 021 — Keep-alive de Supabase con una función ejecutable por `anon` (excepción a "nada a anon")

**Fecha:** 6 de octubre de 2026
**Estado:** vigente (excepción aprobada por Valentín el 6/10); **ajustada el 24/10/2026** (frecuencia y escritura real: ver el final)
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

## Ajuste del 24/10/2026 — tres veces por día y una escritura real

**Qué pasó:** el keep-alive corrió bien (7 de 7 en verde, cada 3 días, con 5 a 8 horas de atraso de GitHub), pero **Supabase mandó igual el aviso de inactividad el 24/10**. Su documentación
([Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)) pide **«unos pocos pedidos de usuario por día»** de actividad en la base. La decisión de arriba cubría la *forma*
(una consulta real por la API) pero no la *medida*: un `select now()` cada 3 días ni es frecuente ni deja ninguna huella en la base.

**Por qué el ajuste (dos cosas, las dos hacen falta):**

1. **Frecuencia:** el cron pasa de «cada 3 días» a **tres veces por día** (`17 6,14,22 * * *`: 06:17, 14:17 y 22:17 UTC, minutos no redondos). GitHub atrasa estas corridas varias horas: con tres por día siempre queda alguna dentro de cada día. El resto del workflow no cambia.
2. **Actividad real en la base:** `public.keepalive()` además **escribe**. Hace un `upsert` en `public.keepalive_latido`, una tabla de **una sola fila** (`id` fijo = 1, `check (id = 1)`; columna `ultimo_latido`), y devuelve la hora igual que antes. Es un pedido de usuario (`anon`) que modifica la base, y la fila queda como prueba de la última vez.
   Migración: `supabase/migrations/20261024120000_keepalive_latido.sql`.

**Qué NO cambia:**

- **`anon` sigue sin acceso a ninguna tabla:** `keepalive_latido` tiene **RLS activado y ninguna política**, y se revocan todos sus privilegios a `public`, `anon` y `authenticated`. Una consulta directa a la tabla con la clave anon da 401.
- La función sigue **sin parámetros** y devuelve la hora: el contrato con el workflow (`POST /rest/v1/rpc/keepalive`) no cambia.
- **`service_role` no se usa** (ni en el workflow ni en la función).

**Qué cambia en el diseño de seguridad:** la función pasa de `security invoker` a **`security definer`** (hace falta: es quien puede escribir en una tabla a la que `anon` no tiene acceso; el dueño no queda sujeto a RLS porque no se fuerza). Mitigaciones: **`search_path` fijo y vacío** (todo calificado con `public.`), `EXECUTE` revocado a `public` y otorgado solo a `anon`, y lo único que puede hacer es **actualizar la hora de la fila 1** (no recibe parámetros ni lee nada). La excepción de la 021 queda igual de acotada: `anon` puede ejecutar `keepalive()`, nada más.

**Riesgos y límites:**

- `anon` puede llamar a la función sin límite propio y ahora cada llamada **actualiza una fila** (antes era solo una lectura): el costo es una escritura mínima sobre una sola fila; si hubiera abuso, se limita en el borde o se revoca el `EXECUTE`.
- El panel de seguridad de Supabase (*Security Advisor*) puede marcar una función `security definer` ejecutable por `anon`: es **esperado** y es esta excepción.
- **No se puede verificar desde el repo** que Supabase cuente estas llamadas como actividad suficiente: hay que mirar el panel (el estado del proyecto) los próximos días y el día anterior a la demo.
- Si el repo pasa 60 días sin actividad, GitHub desactiva los workflows programados (ver la bitácora del 24/10: pendiente post-demo).
