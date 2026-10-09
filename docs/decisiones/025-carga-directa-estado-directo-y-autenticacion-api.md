# Decisión 025 — Carga directa a Storage, estado por lectura directa y autenticación de la API con JWKS (desvío de §4.2.3 y §4.2.5)

**Fecha:** 7 de octubre de 2026
**Estado:** vigente — decisión de Valentín (plan de punta a punta, D3–D5). La **corrección del Capítulo 4 queda pendiente**
(ver `docs/tesis/correcciones-pendientes-capitulo-4.md`).
**Afecta a:** Capítulo 4 §4.2.3 (flujo de datos) y §4.2.5 (superficie de la API) · `backend/app/security.py` ·
`backend/app/routers/analisis.py` · tarea 7.4 · decisiones 016, 018 y 022

---

## El problema

La tesis (§4.2.3 y §4.2.5) diseñó una API de **siete operaciones**; las dos que el plan de punta a punta cuestiona son:

- **Alta de análisis:** crea el registro y **devuelve la URL firmada de carga** (el video sube a Storage con esa URL, el cliente no escribe en la base).
- **Consulta de estado / Obtención del reporte / Listado / Evolución:** lecturas que pasarían por la API.

Ese diseño supone que el cliente no puede escribir en Storage ni leer la base por su cuenta. Pero el proyecto ya construyó, en la Etapa 4.5, **las garantías
equivalentes en la base**: política de RLS por carpeta en Storage (`<usuario_id>/…`), RLS en las nueve tablas, y permisos por columna sobre `videos` y
`sesiones` (decisión 022). Con eso, mediar cada operación con una API es duplicar código sin ganar seguridad.

Además la API de hoy se protege con **un token compartido** (decisión 019), que no puede vivir en un navegador y no identifica a nadie.

## Decisión

1. **Carga directa a Storage con la sesión del usuario.** El navegador sube el video al bucket `videos`, bajo su propia carpeta. La RLS de Storage lo
   permite solo en `<usuario_id>/…`. **El bucket queda limitado a 50 MB por archivo y a tipos de video** (`video/mp4`, `video/quicktime`), según la
   decisión 016 (ya está así en la migración `20261001090300`). La validación del navegador es una cortesía; la definitiva la hace el motor.
2. **"Alta de análisis" deja de ser una operación de la API:** el cliente crea la `sesión` y el `video` con la sesión del usuario (RLS + permisos por columna:
   el estado y todo lo que escribe el motor no se pueden tocar).
3. **Consulta de estado, reporte, listado y evolución = lectura directa a Supabase** con RLS (el estado se consulta por *polling* cada pocos segundos). Sin
   endpoints nuevos. La lectura de archivos usa **URL firmadas de vida corta** creadas por el cliente al leer (la tesis ya pide ese principio para la lectura).
4. **La API queda con tres operaciones:** verificación de servicio (pública), y **confirmación de carga / reintento** (`POST /analisis/{id}/procesar`,
   decisión 022), que es la única que dispara cómputo del motor.
5. **Autenticación de esa operación con el JWT de Supabase, validado contra sus claves públicas (JWKS):**
   - Se verifican firma (ES256), expiración (`exp`), emisor (`iss`) y audiencia (`aud = authenticated`); la identidad es el `sub` del token, **nunca un
     parámetro del cliente** (tarea 7.4).
   - Las claves se leen de `<SUPABASE_URL>/auth/v1/.well-known/jwks.json` y se guardan en caché; si llega un `kid` desconocido, se refresca (rotación de claves).
     Verificado el 7/10/2026 contra el proyecto real: el endpoint es público y publica una clave ES256.
   - **Chequeo de propiedad del video, obligatorio:** la API usa `service_role`, que **ignora RLS**; sin este chequeo cualquier usuario autenticado podría
     procesar el video de otro. Si el video no es del usuario, se responde **404** (igual que si no existiera: no se revela qué ids existen). *Ajuste sobre el
     plan, que decía 403.*
   - El **token compartido se retira** del endpoint cuando entre este mecanismo; las pruebas que lo usan (`test_api_analisis_e2e.py`,
     `test_render_modo_captura.py`) pasan a autenticarse con un usuario de prueba real.

## Alternativas consideradas

- **Mantener las siete operaciones de la tesis.** Más código, más superficie de ataque (el criterio de la propia §4.2.5: "cada punto de acceso adicional es una
  superficie de ataque y una unidad de mantenimiento") y nada que la base no garantice ya. Descartada.
- **Validar el token preguntándole a Supabase Auth en cada pedido** (`get_user`). Más simple, pero agrega una ida y vuelta a Supabase por pedido. Descartada a
  favor de JWKS (pedido de Valentín).
- **Validar con el secreto HS256 compartido.** Obliga a guardar en Render un secreto que firma tokens. Con claves asimétricas solo se publica la clave de verificación.
  Descartada.

## Consecuencias

- **Capítulo 4 (pendiente de corrección):** §4.2.3 (diagrama y texto del flujo: ya no hay "solicita URL firmada" a la API) y §4.2.5 (la tabla de operaciones). Detalle
  en `docs/tesis/correcciones-pendientes-capitulo-4.md`.
- **Riesgo aceptado:** un usuario autenticado puede subir directo a su carpeta (hasta 50 MB por archivo, solo mp4/mov) sin que la API medie. No hay cuota por usuario;
  el límite real es el tamaño total del plan de Storage. Aceptable para un MVP sin registro público masivo; a revisar antes de abrirlo al público.
- **El estado del análisis lo escribe el motor y lo lee el cliente:** gracias a los permisos por columna (decisión 022), el cliente no puede falsificarlo.
- **Nuevas dependencias del servidor:** una librería de JWT con soporte de curvas elípticas (a fijar al implementar); `SUPABASE_URL` ya está en Render.
- La implementación es parte de la semana 1 del plan de punta a punta; esta decisión fija el diseño, no el código.

## Avance (9/10/2026) — tarea 7.4 implementada

- **`backend/app/security.py`:** `usuario_autenticado` valida el JWT contra el JWKS del proyecto con PyJWT (`PyJWKClient`: caché de claves y recarga ante un `kid` desconocido). Fija `ES256`
  (la lista de algoritmos la decide el servidor: un HS256 o `alg: none` se rechaza), exige `exp`, `sub`, `iss = <SUPABASE_URL>/auth/v1` y `aud = authenticated`. **401** sin Bearer, inválido o
  vencido; **503** si no se pudo pedir el JWKS (no es culpa del token).
- **`routers/analisis.py`:** compara `videos.usuario_id` con el `sub`; **404** igual que un video inexistente (mismo mensaje y código). Un id que no es uuid (22P02 de Postgres) también es 404.
  La identidad no sale de ningún parámetro: hay una prueba que manda otro `usuario_id` por query, cuerpo y header.
- **Token compartido retirado:** `verificar_token`, `KINETIQ_API_TOKEN` y `get_kinetiq_api_token` ya no existen; `render.yaml` y `backend/.env.example` lo reflejan. **Acción de Valentín:** borrar
  `KINETIQ_API_TOKEN` del panel de Render (es inofensivo, pero es un secreto sin uso) y cargar `KINETIQ_CORS_ORIGINS`.
- **CORS:** `KINETIQ_CORS_ORIGINS` (lista separada por comas, sin comodines: un `*` es `ConfigError`); sin valor, ningún origen. `allow_credentials=False`: la sesión viaja en `Authorization`, no en cookies.
- **`usuarios`:** migración `20261009130000_endurecer_usuarios.sql` (INSERT retirado; UPDATE solo de `nombre`, `rol` y `vista_por_defecto`) y `tests/integration/test_usuarios_columnas_protegidas.py`.
  **Pendiente de aplicar por Valentín**; la prueba está en rojo hasta entonces.
- **Pruebas:** `test_security_jwt.py` (26 casos: claims, firma ajena, alterado, confusión de algoritmos, `kid` desconocido, JWKS caído, CORS), `test_api_analisis.py` (identidad, propiedad, 404 indistinguible,
  el token viejo ya no abre) y las integraciones (`test_api_analisis_e2e`, `test_reintento_supabase`, `test_render_modo_captura`) migradas a un usuario de prueba real con su JWT, con el control del usuario ajeno.
