-- Bucket privado de artefactos del reporte (decisión 032, ajuste del 12/10): los tres fotogramas clave con esqueleto y el video corto
-- con esqueleto. Es un bucket APARTE del de videos por tres razones:
--
--   1. El bucket "videos" solo admite mp4/mov (20261001090300) y el usuario puede escribir en él; los fotogramas son JPEG y los
--      genera el servidor: acá el usuario solo LEE y BORRA lo suyo, no escribe.
--   2. La política de retención (apartado 4.5.3 de la tesis) elimina el video ORIGINAL a los 7 días y conserva el video con esqueleto
--      en baja resolución como evidencia visual. Con buckets separados, borrar un original nunca puede arrastrar la evidencia.
--   3. Es lo único que el reporte muestra sin el original: minimización de datos (Ley 25.326, apartado 3.4.1.7) sin perder el reporte.
--
-- Convención de ruta igual que "videos": "<usuario_id>/<video_id>/clave_pelvis.jpg" (y torso, brazo) y ".../esqueleto.mp4". El
-- servidor (service_role) escribe sin política, igual que en "videos". Límite de 15 MB por objeto: el video de 360 px pesa unos
-- cientos de KB; el techo es un cerco, no una medida.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('artefactos', 'artefactos', false, 15728640, array['image/jpeg', 'video/mp4'])
on conflict (id) do nothing;

create policy artefactos_storage_select_propio on storage.objects
    for select to authenticated
    using (
        bucket_id = 'artefactos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

-- Borrar lo propio (derecho de supresión): el usuario puede eliminar sus artefactos. No hay política de insert ni de update: no los
-- escribe el usuario.
create policy artefactos_storage_delete_propio on storage.objects
    for delete to authenticated
    using (
        bucket_id = 'artefactos'
        and (storage.foldername(name))[1] = auth.uid()::text
    );
