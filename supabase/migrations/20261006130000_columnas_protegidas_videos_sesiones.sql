-- Permisos por columna para videos y sesiones — decisión 022, paso (a).
--
-- Problema: 20261001090100_rls_policies.sql dio a "authenticated" INSERT y UPDATE sobre TODAS las
-- columnas de videos. RLS decide QUÉ FILAS puede tocar un usuario (las suyas), no QUÉ COLUMNAS:
-- desde el navegador, con su propia sesión, un usuario podía escribir videos.estado (marcar
-- 'completado' un video sin analizar, o 'fallido' uno ya analizado para forzar un reintento),
-- videos.motivo_fallo, fps_real, apto_fase_rapida, etc. Esas columnas las escribe el motor
-- (service_role); el usuario no tiene ninguna razón legítima para tocarlas, y la máquina de estados
-- del reintento (decisión 022) no vale nada si el estado lo puede falsificar quien lo consulta.
--
-- Criterio, verificado contra el esquema, la especificación de frontend (§5, §9) y lo que escribe
-- hoy cada cliente (el frontend todavía no escribe nada contra Supabase: solo hay maquetas):
--
--   videos, INSERT  — el usuario da de alta el golpe: id, sesion_id, usuario_id, ruta_almacenamiento.
--                     Todo lo demás lo escribe el motor o tiene default (estado = 'pendiente').
--   videos, UPDATE  — ninguna columna. No hay hoy ningún flujo en que el usuario modifique un golpe ya
--                     creado (borrarlo sí: DELETE sigue intacto). Si aparece uno real (p. ej. mover un
--                     golpe a otra sesión), se agrega esa columna con una migración propia, no antes.
--   sesiones, UPDATE — todo lo que el usuario declara (atleta_id, gesto, encuadre, lado_camara, fecha,
--                     modo_captura). Quedan fuera id, usuario_id y creado_en: no se reasignan ni se
--                     reescribe la fecha de carga. El motor no escribe nada en sesiones.
--
-- No se tocan: SELECT, DELETE, INSERT de sesiones, ni las políticas de RLS (siguen filtrando filas);
-- ni los permisos de service_role. La política videos_update_propio queda sin efecto práctico
-- (sin privilegio de UPDATE no llega a evaluarse); se deja a propósito, no se borra.
--
-- Revocar el privilegio de tabla revoca también los de columna que hubiera, y después se otorgan
-- solo las columnas permitidas.

revoke insert, update on public.videos from authenticated;
grant insert (id, sesion_id, usuario_id, ruta_almacenamiento) on public.videos to authenticated;

revoke update on public.sesiones from authenticated;
grant update (atleta_id, gesto, encuadre, lado_camara, fecha, modo_captura) on public.sesiones to authenticated;
