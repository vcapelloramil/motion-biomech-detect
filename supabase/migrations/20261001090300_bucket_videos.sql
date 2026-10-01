-- Bucket privado de video — Etapa 4.5, tarea 4.5.2.
--
-- Un bucket por ahora ("videos"): clips subidos, overlays, miniaturas y fotogramas clave viven
-- todos ahí bajo prefijos de ruta distintos (p. ej. "<usuario_id>/<video_id>/original.mov",
-- ".../overlay.mp4"), no en buckets separados — no hay razón hoy para separarlos y "exponer
-- tablas/buckets automáticamente" ya está desactivado en el proyecto, así que cada bucket nuevo
-- es trabajo explícito (como esta migración).
-- file_size_limit y allowed_mime_types son un segundo cerco, no el único: la validación del
-- navegador (especificación de frontend §5) "es una cortesía; la definitiva la hace el motor". El
-- límite de 50 MB es el de la decisión 016 (tentativa); si esa decisión cambia, este valor cambia
-- con ella, en una migración nueva.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('videos', 'videos', false, 52428800, array['video/mp4', 'video/quicktime'])
on conflict (id) do nothing;

-- RLS de storage.objects para este bucket: convención de ruta "<usuario_id>/...", el mismo
-- principio que las políticas de las tablas (20261001090100_rls_policies.sql) — auth.uid() tiene
-- que ser dueño del primer segmento de la ruta. storage.foldername(name) devuelve los componentes
-- de carpeta del nombre del objeto; (...)[1] es el primero.
--
-- service_role NO necesita una política acá: bypasea RLS, y a diferencia de las tablas de public/,
-- el servicio de Storage de Supabase le da acceso completo por su cuenta — es una API aparte de
-- PostgREST, no pasa por los GRANT que hubo que agregar en 20261001090200 para las tablas de
-- public creadas por SQL crudo. Confirmado al correr la prueba de subida real, no asumido en seco
-- después del error con service_role de la tarea 4.5.1.
create policy videos_storage_select_propio on storage.objects
    for select to authenticated
    using (
        bucket_id = 'videos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

create policy videos_storage_insert_propio on storage.objects
    for insert to authenticated
    with check (
        bucket_id = 'videos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

create policy videos_storage_update_propio on storage.objects
    for update to authenticated
    using (
        bucket_id = 'videos'
        and (storage.foldername(name))[1] = auth.uid()::text
    )
    with check (
        bucket_id = 'videos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

create policy videos_storage_delete_propio on storage.objects
    for delete to authenticated
    using (
        bucket_id = 'videos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );
