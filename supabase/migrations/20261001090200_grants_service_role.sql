-- GRANT faltantes para service_role — Etapa 4.5, tarea 4.5.1.
--
-- Encontrado al correr tests/integration/ contra el proyecto real: "permission denied for
-- table usuarios" con service_role. Corrección del supuesto equivocado de
-- 20261001090100_rls_policies.sql ("service_role ya tiene BYPASSRLS y acceso total al esquema
-- public por defecto" — la primera mitad es cierta, la segunda no en este proyecto).
--
-- BYPASSRLS (atributo del ROL service_role) exime de las políticas de fila; el GRANT de tabla
-- (privilegio SQL estándar: SELECT/INSERT/UPDATE/DELETE) es una capa aparte y Postgres exige las
-- dos. Supabase normalmente otorga privilegios por defecto a service_role cuando una tabla se
-- crea desde su panel; con "exponer tablas automáticamente" desactivado y las tablas creadas por
-- SQL crudo desde el editor, eso no pasó solo. Migración nueva porque 20261001090000 y
-- 20261001090100 ya están aplicadas contra el proyecto real (no se editan retroactivamente).
--
-- service_role es el rol del contenedor del motor (tarea 4.5.3) y, por ahora, el que usan las
-- pruebas de integración para preparar y limpiar datos de prueba: necesita CRUD completo en las
-- nueve tablas, no un subconjunto de columnas como authenticated.

grant select, insert, update, delete on public.usuarios to service_role;
grant select, insert, update, delete on public.atletas to service_role;
grant select, insert, update, delete on public.sesiones to service_role;
grant select, insert, update, delete on public.videos to service_role;
grant select, insert, update, delete on public.versiones_motor to service_role;
grant select, insert, update, delete on public.reportes_biomecanicos to service_role;
grant select, insert, update, delete on public.metricas to service_role;
grant select, insert, update, delete on public.alertas to service_role;
grant select, insert, update, delete on public.reportes_sesion to service_role;
grant select on public.sesiones_resumen to service_role;
