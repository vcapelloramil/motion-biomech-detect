# Decisión 018 — Esquema de datos de la Etapa 4.5: sesión como grupo de golpes

**Fecha:** 1 de octubre de 2026
**Estado:** vigente (decisión de Valentín, confirmando la propuesta de Claude)
**Afecta a:** tarea 4.5.1 (`docs/plan-desarrollo.md`) · esquema del apartado 4.4.6 de la tesis (desactualizado,
pasa a la lista de pendientes de redacción junto a las decisiones 006, 010, 011, 012, 013, 014, 015) ·
contrato del reporte (`backend/app/schemas/reporte.py`, Etapa 5) · `docs/ux/especificacion-frontend.md` §9

---

## El problema

El esquema del Capítulo 4 (apartado 4.4.6, siete tablas) se escribió antes de que existiera la especificación
del frontend. Esa especificación (`docs/ux/especificacion-frontend.md` §9, 1/10/2026) y las maquetas confirman
que el modelo real es otro: **una sesión agrupa varios videos del mismo atleta, gesto, encuadre y lado de
cámara; cada video es un golpe**, hay un puntaje de rendimiento y hasta tres observaciones a nivel de sesión
(agregando los golpes), y el reporte por golpe sigue existiendo para el detalle (Nivel 2 de evidencia,
selector G1…G6 en la maqueta `ReporteDetallado`). El esquema del Capítulo 4 no tenía ni la entidad sesión ni
el reporte agregado.

## Decisión: 9 tablas, no 7

Se agregan **`sesiones`** y **`reportes_sesion`**; se modifican **`usuarios`** (agrega `vista_por_defecto`) y
**`videos`** (agrega `sesion_id`, pierde `gesto` y `atleta_id` —se leen por la sesión—, agrega rutas de
miniatura y de los tres fotogramas clave). El resto (`atletas`, `reportes_biomecanicos`, `metricas`,
`alertas`, `versiones_motor`) se mantiene con ajustes menores. Esquema completo, columnas y tipos: ver
`supabase/migrations/20261001090000_esquema_inicial.sql` (fuente de verdad; este documento no transcribe cada
columna para no desincronizarse de él).

## Tres puntos de diseño, con la decisión final de Valentín

### 1. `estado_agregado` de la sesión: vista, no columna

Se calcula con una vista (`sesiones_resumen`) a partir de `videos.estado`, en vez de guardarse como columna.
Guardarlo exigiría un trigger que lo mantenga sincronizado cada vez que cambia el estado de un video —
infraestructura que el volumen actual no justifica (CLAUDE.md §6, MVP primero).

### 2. Vocabulario de `alertas.severidad`: los cuatro estados de R3, no los tres de `reporte.py`

La base usa `correcto | desvio_leve | alerta_de_carga | no_auditable` (CLAUDE.md, regla R3), no el
`info | atencion | riesgo | no_auditable` que todavía tiene el diagrama del apartado 4.4.6 (desactualizado,
ver CLAUDE.md §5) ni el `Literal["correcto", "atencion", "no_auditable"]` de tres valores que
`reporte.py` dejó congelado en la Etapa 0.

**Esto deja una desalineación conocida y deliberada entre la base y el contrato JSON del motor.** Decisión
de Valentín (1/10/2026): no se resuelve ahora —tocar `reporte.py` es decisión de la Etapa 5, no de esta
etapa—, pero **es lo primero que se resuelve al arrancar la Etapa 5, antes de generar cualquier JSON real**.
Hasta entonces, la base puede tener filas con severidades que el contrato congelado todavía no sabe nombrar;
no es un error, es una secuencia de trabajo explícita. Anotado también en la bitácora para que no se pierda.

### 3. RLS completo en las 9 tablas ahora, con prueba automática de aislamiento

El plan (`docs/plan-desarrollo.md`, riesgos de la Etapa 4.5, punto 2) permitía diferir la política de
seguridad a nivel de fila completa a la Etapa 7 y dejar solo una de prueba ahora. Decisión de Valentín: se
escribe completa ahora, porque el esfuerzo de migración es el mismo. Se agrega además una prueba automática
(`tests/integration/test_rls_aislamiento.py`) que verifica, con dos usuarios de prueba reales creados contra
el proyecto Supabase:

- el usuario A no puede **leer, modificar ni borrar** sesiones, videos, reportes (por golpe y de sesión),
  métricas ni alertas del usuario B;
- un cliente **sin sesión iniciada** (rol `anon`) no puede leer nada de ninguna de las 9 tablas.

Es la verificación de RNF-07 del Capítulo 4. La prueba se salta si no hay `SUPABASE_URL`,
`SUPABASE_ANON_KEY` y `SUPABASE_SERVICE_ROLE_KEY` configurados (mismo patrón que las pruebas que dependen de
`KINETIQ_DATA_DIR`), y crea y borra sus propios usuarios de prueba contra el proyecto real —no corre contra
una base local, porque RLS es exactamente la garantía del proveedor que hay que probar contra el proveedor.

**Grants:** con "exponer tablas automáticamente" desactivado en el proyecto, cada tabla necesita `GRANT`
explícito al rol `authenticated` (nunca a `anon`: dato sensible, Ley 25.326). Las entidades que el usuario
gestiona directamente (`usuarios`, `atletas`, `sesiones`, `videos`) tienen `select/insert/update/delete`
propios; las que genera el motor (`reportes_biomecanicos`, `metricas`, `alertas`, `reportes_sesion`,
`versiones_motor`) son de **solo lectura** para el rol `authenticated` —nunca las escribe el frontend, las
escribe el contenedor con `service_role`, que bypasea RLS por diseño de Supabase.

### Puntaje de `reportes_sesion`: columnas tipadas aparte del jsonb

`componentes` y `observaciones` van como `jsonb` (la fórmula del puntaje recién se congela en una decisión
de la Etapa 5, según `docs/ux/especificacion-frontend.md` §7 — normalizar antes sería adivinar una forma que
todavía puede cambiar). Pero a pedido de Valentín, el **puntaje total sale del jsonb** y queda en columnas
tipadas: `puntaje numeric`, `estado_puntaje text` (ver ajuste 1 abajo: reemplazó a un `puntaje_auditable
boolean` de la primera versión de esta decisión) y `version_formula text`. Razón: la pantalla de Evolución
necesita consultar el puntaje a través de varias sesiones sin tener que leer dentro de un jsonb cada vez, y la
versión de la fórmula es parte de la trazabilidad exigida por R4.

## Consecuencia para el Capítulo 4

El apartado 4.4.6 (diagrama de siete tablas) queda desactualizado por esta decisión, igual que las secciones
ya listadas en CLAUDE.md §5. Se agrega a esa lista de pendientes de redacción. No se edita el capítulo ahora.

## Ajustes posteriores (mismo día, antes de aplicar nada)

Valentín aprobó el esquema de arriba y pidió tres ajustes antes de aplicar las migraciones (todavía no
aplicadas en ese momento, así que se editaron los dos archivos existentes en vez de sumar una migración
nueva — no viola la regla de "nunca editar retroactivamente": esa regla es sobre migraciones ya aplicadas).

### Ajuste 1 — `estado_puntaje` reemplaza a `puntaje_auditable`

La primera versión de esta decisión tenía `puntaje_auditable boolean`. No alcanza: la especificación de
frontend §7 distingue dos razones distintas para no mostrar un número — "no auditable" (menos de dos
componentes auditables) y "Desde tu 2.ª sesión de este golpe" (todavía no hay sesión previa comparable, sin
número, texto distinto) — y un booleano no las separa. Se reemplaza por
`estado_puntaje text check (estado_puntaje in ('calculado', 'no_auditable', 'sin_referencia'))`, `not null`
(sin default: quien escribe la fila tiene que elegir a propósito, no hay un valor "neutro" razonable).
Restricción: `puntaje` no nulo si y solo si `estado_puntaje = 'calculado'`.

### Ajuste 2 — borrado en cascada, confirmado con una prueba

Pedido de Valentín: confirmar que borrar un usuario de `auth.users` arrastra en cascada sus atletas,
sesiones, videos, reportes (por golpe y de sesión), métricas y alertas — es el requisito de "eliminar mi
cuenta y mis datos" (pantalla Perfil, Ley 25.326). Repasando las FK de la migración, ya era cierto con el
esquema tal como estaba escrito (todas las FK relevantes tienen `on delete cascade`, encadenadas desde
`usuarios.id references auth.users(id) on delete cascade`); lo que faltaba era **demostrarlo**, no corregir
nada. Prueba agregada: `tests/integration/test_cascada_borrado_usuario.py` (crea un árbol completo de datos
de un usuario de prueba, lo borra, confirma que las siete tablas quedan vacías para esas filas).

**Lo que la cascada NO hace, dejado anotado:** los archivos en Supabase Storage (el video, el overlay, la
miniatura, los tres fotogramas clave, el PDF) no se borran solos — son objetos de `storage.objects`, fuera
del alcance de una cascada sobre estas tablas. Comentario agregado en la migración, junto a
`reportes_sesion.ruta_pdf`. **Pendiente de la Etapa 7:** el flujo real de "eliminar mi cuenta" tiene que
borrar esos objetos de Storage además de dejar que la base cascadee sola.

### Ajuste 3 — trigger de alta de usuario

Se agrega `public.manejar_alta_usuario()` (función `security definer`) y el trigger `al_registrarse` sobre
`auth.users` (`after insert`), que crea la fila de `usuarios` sola al registrarse: `rol` sale de
`raw_user_meta_data ->> 'rol'` si el registro lo manda, o `'jugador'` si no. Antes de este ajuste, esa fila la
tenía que crear la aplicación (o, en esta etapa, las pruebas) a mano — ya no.

**Caso límite considerado a propósito, no corregido:** si el registro manda un `rol` fuera del vocabulario
cerrado (`jugador`/`entrenador`/`profesional_salud`), la restricción `CHECK` de `usuarios.rol` lo rechaza
DENTRO de la misma transacción que el `INSERT` en `auth.users` — el alta completa falla, no se crea ni el
usuario de Auth ni el perfil. Es el comportamiento correcto (mismo principio que el resto del esquema: "un
dato inconsistente no debe poder escribirse"), no un bug a arreglar con una coerción silenciosa del valor.
Probado en `tests/integration/test_trigger_alta_usuario.py` (tres casos: default, metadatos válidos, rol
inválido).

## Render — una sola medición, sin optimizar para el plan gratis

Confirmado por Valentín: la medición de Render (RAM/CPU/suspensión del plan Free, investigada el 1/10) se
hace **una sola vez**, en la tarea 4.5.4, con el mismo clip de la decisión 017. Si un golpe supera los 10
minutos, o si la suspensión por inactividad corta un análisis en curso, se pasa directo a Starter y se agrega
a la decisión 017 — sin iterar buscando que entre en el plan gratis (p. ej. bajando `model_complexity` solo
para que entre, lo cual además ya está marcado como pendiente de decisión aparte en la 017).

## Aplicación real (1/10/2026, Valentín) y lo que salió mal

Las tres migraciones (`20261001090000_esquema_inicial.sql`, `20261001090100_rls_policies.sql`,
`SUPABASE_ANON_KEY` en `backend/.env`) se aplicaron desde el editor SQL del panel de Supabase — Claude Code no
tiene una vía para ejecutar SQL directamente contra Supabase sin una contraseña de base de datos, que no le
corresponde entrar por las reglas de seguridad de la sesión. Instalar `supabase==2.31.0` en el entorno forzó
además a subir `pydantic` de `2.10.3` a `2.11.7` (piso que exige la dependencia `realtime`; no se tocó nada
más, la suite completa se corrió de nuevo para confirmarlo).

**`pytest -m requiere_supabase` falló en la primera corrida contra el proyecto real**, con
`permission denied for table usuarios` sobre el rol `service_role`. Causa: `service_role` tiene el atributo
`BYPASSRLS` (exime de las políticas de fila), pero eso es una capa de Postgres **independiente** de los
privilegios SQL de tabla (`GRANT SELECT/INSERT/...`) — el comentario original de
`20261001090100_rls_policies.sql` decía que `service_role` "no necesita nada de esto" y daba a entender que
ya tenía acceso total por defecto; **es la lección de esta decisión para el resto del proyecto: un rol con
BYPASSRLS igual necesita su GRANT de tabla, la RLS y los privilegios SQL son dos sistemas de permisos
separados que hay que otorgar los dos, para CUALQUIER tabla nueva de acá en adelante.** Supabase normalmente
lo resuelve solo cuando una tabla se crea desde su panel; con "exponer automáticamente" desactivado y las
tablas creadas por SQL crudo desde el editor, no pasó solo. Corregido con una migración nueva (no se editan
las ya aplicadas): `supabase/migrations/20261001090200_grants_service_role.sql`. Comentario de
`20261001090100_rls_policies.sql` corregido para que no vuelva a inducir el mismo error.

**Efecto colateral encontrado al confirmar la limpieza (pedido explícito de Valentín: que las pruebas no
dejen cuentas de prueba sueltas):** la primera corrida fallida, antes del GRANT, dejó **3 usuarios de Auth
huérfanos** (`kinetiq-rls-a-*`, `kinetiq-rls-b-*`, `kinetiq-cascada-*`) — se crearon al principio de cada
prueba, pero el `try/finally` que los borra envolvía solo una parte del cuerpo de la prueba, así que cuando el
`insert` siguiente fallaba por el permiso faltante, la excepción saltaba por encima del borrado. Se confirmó
con `auth.admin.list_users()` (0 usuarios tras limpiarlos a mano) y se corrigió la causa: en
`test_rls_aislamiento.py` y `test_cascada_borrado_usuario.py`, el `try/finally` ahora envuelve **todo** lo que
pasa después de crear los usuarios de Auth, no solo la parte que se esperaba que pudiera fallar. Con esa
corrección, la segunda corrida completa (28 pruebas) no dejó ninguna cuenta: verificado con el mismo
`list_users()`. `test_trigger_alta_usuario.py` ya estaba bien escrito desde el principio (cada prueba envuelve
su propio borrado inmediatamente después de crear el usuario).

**Estado final:** las tres migraciones aplicadas, las 28 pruebas de `pytest -m requiere_supabase` en verde
contra el proyecto real, 0 usuarios de prueba sueltos. Falta la captura del editor de tablas de Supabase
(pendiente del apartado 4.4.6, como pedía la tarea 4.5.1 original) — no bloquea seguir con la tarea 4.5.2.
