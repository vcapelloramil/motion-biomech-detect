-- Seguridad a nivel de fila (RLS) y permisos — Etapa 4.5, tarea 4.5.1.
--
-- Decisión 018, punto 3: RLS completo en las nueve tablas ahora (no solo una de prueba), con una
-- prueba automática de aislamiento (tests/integration/test_rls_aislamiento.py) que verifica RNF-07
-- del Capítulo 4 contra el proyecto real.
--
-- Principio aplicado en todas las políticas: "auth.uid() = usuario_id" (directo, o por join hasta
-- llegar a usuario_id en las tablas que el motor genera y el usuario no escribe).
--
-- Con "exponer tablas automáticamente" desactivado en el proyecto Supabase, cada tabla necesita
-- GRANT explícito. Nunca se otorga nada al rol "anon": son datos de salud/identificables (Ley
-- 25.326, apartado 3.4.1.7 de la tesis), así que ni siquiera llegan a evaluarse las políticas de
-- RLS para un cliente sin sesión — ya no tiene privilegio para seleccionar.
--
-- El rol service_role (el que usa el contenedor del motor) tiene BYPASSRLS, así que no necesita
-- NADA de las políticas de este archivo. SÍ necesita sus propios GRANT de tabla (privilegio SQL
-- aparte de RLS: ver 20261001090200_grants_service_role.sql) — "no necesita nada de esto" se
-- quedaba corto, y en la práctica causó "permission denied for table usuarios" al correr las
-- pruebas de integración contra el proyecto real. Corregido en la decisión 018.

alter table public.usuarios enable row level security;
alter table public.atletas enable row level security;
alter table public.sesiones enable row level security;
alter table public.videos enable row level security;
alter table public.versiones_motor enable row level security;
alter table public.reportes_biomecanicos enable row level security;
alter table public.metricas enable row level security;
alter table public.alertas enable row level security;
alter table public.reportes_sesion enable row level security;

-- =============================================================================================
-- usuarios — el propio perfil. select/insert/update (no delete: la baja de cuenta es un flujo
-- aparte, Etapa 7, probablemente vía función que también limpia Auth).
-- =============================================================================================
grant select, insert, update on public.usuarios to authenticated;

create policy usuarios_select_propio on public.usuarios
    for select to authenticated
    using (auth.uid() = id);

create policy usuarios_insert_propio on public.usuarios
    for insert to authenticated
    with check (auth.uid() = id);

create policy usuarios_update_propio on public.usuarios
    for update to authenticated
    using (auth.uid() = id)
    with check (auth.uid() = id);

-- =============================================================================================
-- atletas — el usuario gestiona sus propios atletas: CRUD completo.
-- =============================================================================================
grant select, insert, update, delete on public.atletas to authenticated;

create policy atletas_select_propio on public.atletas
    for select to authenticated
    using (auth.uid() = usuario_id);

create policy atletas_insert_propio on public.atletas
    for insert to authenticated
    with check (auth.uid() = usuario_id);

create policy atletas_update_propio on public.atletas
    for update to authenticated
    using (auth.uid() = usuario_id)
    with check (auth.uid() = usuario_id);

create policy atletas_delete_propio on public.atletas
    for delete to authenticated
    using (auth.uid() = usuario_id);

-- =============================================================================================
-- sesiones — el usuario gestiona sus propias sesiones: CRUD completo.
-- =============================================================================================
grant select, insert, update, delete on public.sesiones to authenticated;

create policy sesiones_select_propio on public.sesiones
    for select to authenticated
    using (auth.uid() = usuario_id);

create policy sesiones_insert_propio on public.sesiones
    for insert to authenticated
    with check (auth.uid() = usuario_id);

create policy sesiones_update_propio on public.sesiones
    for update to authenticated
    using (auth.uid() = usuario_id)
    with check (auth.uid() = usuario_id);

create policy sesiones_delete_propio on public.sesiones
    for delete to authenticated
    using (auth.uid() = usuario_id);

-- =============================================================================================
-- videos — el usuario sube y gestiona sus propios videos (golpes): CRUD completo. El estado de
-- procesamiento lo actualiza normalmente el contenedor con service_role, que bypasea esto.
-- =============================================================================================
grant select, insert, update, delete on public.videos to authenticated;

create policy videos_select_propio on public.videos
    for select to authenticated
    using (auth.uid() = usuario_id);

create policy videos_insert_propio on public.videos
    for insert to authenticated
    with check (auth.uid() = usuario_id);

create policy videos_update_propio on public.videos
    for update to authenticated
    using (auth.uid() = usuario_id)
    with check (auth.uid() = usuario_id);

create policy videos_delete_propio on public.videos
    for delete to authenticated
    using (auth.uid() = usuario_id);

-- =============================================================================================
-- versiones_motor — referencia global, sin dueño. Lectura para cualquier usuario autenticado;
-- solo el motor (service_role) da de alta una versión nueva al desplegar.
-- =============================================================================================
grant select on public.versiones_motor to authenticated;

create policy versiones_motor_select_todos on public.versiones_motor
    for select to authenticated
    using (true);

-- =============================================================================================
-- reportes_biomecanicos, metricas, alertas, reportes_sesion — generados por el motor. El
-- frontend solo LEE (nunca inserta, actualiza ni borra un resultado de análisis). El dueño se
-- determina por join hasta usuario_id.
-- =============================================================================================
grant select on public.reportes_biomecanicos to authenticated;

create policy reportes_biomecanicos_select_propio on public.reportes_biomecanicos
    for select to authenticated
    using (
        exists (
            select 1
            from public.videos v
            where v.id = reportes_biomecanicos.video_id
              and v.usuario_id = auth.uid()
        )
    );

grant select on public.metricas to authenticated;

create policy metricas_select_propio on public.metricas
    for select to authenticated
    using (
        exists (
            select 1
            from public.reportes_biomecanicos r
            join public.videos v on v.id = r.video_id
            where r.id = metricas.reporte_id
              and v.usuario_id = auth.uid()
        )
    );

grant select on public.alertas to authenticated;

create policy alertas_select_propio on public.alertas
    for select to authenticated
    using (
        exists (
            select 1
            from public.reportes_biomecanicos r
            join public.videos v on v.id = r.video_id
            where r.id = alertas.reporte_id
              and v.usuario_id = auth.uid()
        )
    );

grant select on public.reportes_sesion to authenticated;

create policy reportes_sesion_select_propio on public.reportes_sesion
    for select to authenticated
    using (
        exists (
            select 1
            from public.sesiones s
            where s.id = reportes_sesion.sesion_id
              and s.usuario_id = auth.uid()
        )
    );

-- =============================================================================================
-- sesiones_resumen (vista) — nada que otorgar aparte: hereda el GRANT y la RLS de sesiones y
-- videos porque se creó con security_invoker = true. Un usuario autenticado que ya puede
-- seleccionar de sesiones puede seleccionar de la vista sin paso extra.
-- =============================================================================================
grant select on public.sesiones_resumen to authenticated;
