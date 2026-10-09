-- Endurecer `usuarios` — tarea 7.4, decisión 025 (pendiente anotado en la decisión 022).
--
-- Hasta hoy `authenticated` conserva INSERT y UPDATE de TABLA sobre `usuarios` (20261001090100). La RLS
-- ya limita a la fila propia, pero dentro de la fila propia el usuario podía reescribir `email` (espejo de
-- auth.users.email, con restricción de unicidad), `id` y `creado_en`: datos que escribe el sistema, no la
-- persona. La misma lección de la decisión 022 sobre `videos` y `sesiones`.
--
--   * INSERT: se retira. La fila la crea el trigger de alta (decisión 018, ajuste 3), con SECURITY
--     DEFINER; la aplicación no la crea a mano.
--   * UPDATE: solo las tres columnas que el perfil edita (especificación de frontend §4): nombre, rol y
--     vista por defecto. `id`, `email` y `creado_en` quedan fuera.
--
-- No cambia nada para el trigger (corre con los permisos de su dueño) ni para service_role (ya tiene el
-- privilegio de tabla completo). La RLS se mantiene como está.

revoke insert, update on public.usuarios from authenticated;
grant update (nombre, rol, vista_por_defecto) on public.usuarios to authenticated;
