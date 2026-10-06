# Plan del MVP de punta a punta — 6/10 → 2/11/2026 (colchón hasta el 6/11)

**Estado:** propuesta de Claude, **a aprobar por Valentín**. No reemplaza a `docs/plan-desarrollo.md`: lo recomprime. Donde
este documento contradice a ese, vale este una vez aprobado, y las decisiones que lo requieran se registran en
`docs/decisiones/` cuando se tomen.

## 1. Objetivo y criterio de aceptación (lunes 20/10)

Valentín abre la app desde el celular, **se registra o inicia sesión, sube un video real, ve el estado del análisis y abre un
Reporte simple con los datos reales de ese video**, sin intervención manual de nadie.

Hace falta, sí o sí: login (7.4), Cargar real, Procesando real, el JSON del reporte mínimo (Etapa 5) y el Reporte simple conectado.
No hace falta todavía: PDF, video con esqueleto, evolución, puntaje.

## 2. Punto de partida (verificado el 6/10)

- **Servidor:** motor + API (`POST /analisis/{id}/procesar`) en Render; reintento fallido → encolado (decisión 022, migración aplicada);
  Supabase con esquema, RLS, permisos por columna y bucket privado `videos` con política por carpeta `<usuario_id>/…`; keep-alive activo.
- **Motor:** produce, por golpe, orden de picos, velocidades pico, cobertura y trazabilidad. **No existen** `audit.py` (alertas),
  `render.py` (overlay) ni el PDF.
- **Contrato** (`schemas/reporte.py`): congelado en la Etapa 0, **desactualizado** (severidad de 3 estados; sin `modo_captura`,
  `factor_ralentizacion`, `origen_factor`; `overlay_url` y `pdf_url` obligatorios).
- **Frontend** (`frontend/`, TanStack Start generado por Lovable): 8 rutas maquetadas con datos simulados (`reporte-mock.ts`,
  `evolucion-mock.ts`); el "Procesando" de `upload.tsx` es una animación. **No hay cliente de Supabase ni de la API.** El proyecto
  trae configuración de Cloudflare Workers (`wrangler.jsonc`), no de Vercel como dice el plan.

## 3. Decisiones de diseño que propone este plan (a aprobar)

| # | Propuesta | Por qué |
| --- | --- | --- |
| D1 | **Un solo cambio de contrato** (decisión 024): severidad de 4 estados, trazabilidad con `modo_captura`/`factor_ralentizacion`/`origen_factor`, `overlay_url` y `pdf_url` opcionales, y `fotogramas_clave`. | Ya estaba pendiente; hay que hacerlo antes de generar cualquier JSON real. |
| D2 | El reporte se guarda **como JSON validado** por el contrato (una columna `jsonb` en `reportes_biomecanicos`, además de las columnas actuales). | El frontend lee una fila; la validación de "respuesta que no cumple el esquema" (pruebas de la Etapa 6) pasa en el servidor. |
| D3 | **Sin "Alta de análisis" por la API:** el navegador sube directo a Storage con su sesión (la RLS por carpeta ya existe) y crea `sesión` + `video` con permisos por columna; después llama a la API. | Menos superficie y menos código; la URL firmada del apartado 4.2.5 no aporta nada con esa RLS. Desvío de la tesis a registrar. |
| D4 | **Consulta de estado = lectura directa a Supabase** (polling cada pocos segundos, RLS), sin endpoint nuevo. | Cumple el mismo contrato de estados con cero código de servidor. |
| D5 | **Autenticación de la API con el JWT de Supabase** (verificado contra Supabase Auth) **más chequeo de que el video es del usuario**. Reemplaza al token compartido. | La API usa `service_role`, que ignora RLS: sin el chequeo de propiedad, cualquier usuario podría procesar el video de otro. |
| D6 | Primera entrega con **tres fotogramas clave con esqueleto** (PNG en Storage; las columnas `ruta_fotograma_*` ya existen). Video con esqueleto y PDF, después. | Es lo que pide el Reporte simple ("tres momentos del golpe") a una fracción del costo de `render.py`. |

## 4. Plan por semanas

### Semana 1 · 6/10 – 12/10 — el servidor produce un reporte real y acepta usuarios reales

| Cuándo | Qué | Hecho cuando |
| --- | --- | --- |
| **Primeros 2 días** | **Prueba de riesgo del celular:** subir desde el iPhone (Safari) un clip en cámara lenta con una página mínima y comprobar que el archivo que llega a Storage conserva fotogramas y duración del original. | `n_frames` y duración iguales al original. Si el navegador del iPhone transcodifica, se descubre acá y no el 19/10. |
| 7–8/10 | **E5.4 mínimo:** decisión 024 (contrato), migración de `jsonb`, ensamblador del reporte desde lo que `procesar_video` ya calcula (trazabilidad, cobertura, secuenciación, métricas, observación de secuenciación), validado con el contrato. **E5.7:** prueba automática de vocabulario R2. | Un video real produce un JSON que valida, guardado en la base. |
| 9–10/10 | **Fotogramas clave con esqueleto** (3 PNG en el pico de pelvis, torso y brazo) subidos a Storage. | Las tres rutas quedan en `videos`. |
| 10–12/10 | **7.4 en el servidor:** JWT de Supabase + chequeo de propiedad, **CORS** acotado al dominio del frontend (hoy no hay), endurecer `usuarios` (pendiente de la 022). | Un `curl` con el token de un usuario procesa su video; con el de otro responde 403. |

**Acciones tuyas en la semana 1:** desactivar la confirmación por correo en Supabase Auth (el correo integrado del plan Free admite muy pocos
envíos por hora; con varios usuarios de prueba se traba) o crear los usuarios desde el panel; elegir dónde se publica el frontend (ver §7).

### Semana 2 · 13/10 – 19/10 — la interfaz conectada: probarlo desde el celular el 20/10

| Qué | Detalle |
| --- | --- |
| **Base de datos y sesión** | Cliente de Supabase en el frontend, contexto de sesión, rutas protegidas, **Registro/Login** (rol + consentimiento de la Ley 25.326, según el spec). Variables públicas: URL y clave anon. |
| **Cargar real** | Formulario de la sesión (gesto, encuadre, lado, "¿Cómo lo grabaste?"), validación previa en el navegador (50 MB, aviso <120 fps con **"¿Lo grabaste en cámara lenta?"**), subida directa a Storage con barra de progreso, alta de `sesión` + `video`, llamada a la API. **El atleta se crea ahí mismo** con dos preguntas (mano dominante, nivel): la tabla `sesiones` lo exige y la pantalla Perfil queda simulada. |
| **Procesando real** | Polling del estado; mensajes por estado y por `motivo_fallo`; botón de reintento de la decisión 022. |
| **Reporte simple real** | Observación de secuenciación, tres momentos con los fotogramas reales, trazabilidad. "Desde tu 2.ª sesión" donde corresponde (spec §7). |
| **Render → Standard (~19/10)** | Cambio de plan según la decisión 023, **con** `render.yaml` actualizado en el mismo paso. Medir RSS y tiempo de una sesión de 6 golpes. |
| **Lunes 20/10: prueba de punta a punta** | Valentín, con el celular, de cero a reporte. Lo que falle se anota y entra a la semana 3. |

### Semana 3 · 20/10 – 26/10 — lo que hace valioso el reporte

- **Sesión de varios golpes** (hasta 6, selección múltiple) y estado agregado de la sesión (la vista `sesiones_resumen` ya existe).
- **Puntaje de rendimiento v1 y comparación con la sesión anterior (E5.2):** primero decidir y congelar la fórmula (decisión de la Etapa 5);
  a partir de la 2.ª sesión.
- **Reporte detallado:** tabla de magnitudes y bloque de trazabilidad (niveles 1 y 3).
- **Alertas con fundamento (E5.1), solo si hay umbrales con referencia bibliográfica en el Capítulo 3.** Sin referencia no hay alerta: no se inventan números (R4).
- **Biblioteca real** (promovida desde simulada: es una consulta a `sesiones_resumen` y es lo que permite volver a ver un análisis).
- **Recuperación al arranque (6.5)** y **respaldo manual con restauración probada** (7.7), obligatorio antes de usuarios reales.

### Semana 4 · 27/10 – 2/11 — validación (la Etapa 9, con MVP completo al cierre) · colchón hasta el 6/11

Medición de los criterios y pruebas con los tres perfiles, pruebas de punta a punta automatizadas y de regresión. Entre el 3 y el 6/11 queda el
colchón del MVP; la Etapa 10 (congelamiento y entrega, hasta el 17/11) no cambia.

## 5. Qué queda simulado, qué queda diferido

### Simulado con datos precargados (cuando se conecte lo real, se reemplaza el origen de los datos, no la pantalla)

| Pantalla | Qué se muestra | Regla |
| --- | --- | --- |
| **Biblioteca** (hasta la semana 3) | Tarjetas de ejemplo del mock | Se promueve a real en la semana 3. |
| **Evolución** | `evolucion-mock.ts` | Real recién con ≥2 sesiones comparables (E5.2/8.8). |
| **Perfil** | Rol, vista por defecto, privacidad | El atleta mínimo se crea en Cargar. Eliminar cuenta/datos no funciona. |
| Landing, Tecnología | Contenido estático | — |

**Toda pantalla simulada lleva una marca visible "Datos de ejemplo".** Un dato de ejemplo presentado como del usuario es un dato equivocado
presentado como bueno (R3/R4), y en las pruebas con usuarios puede confundirse con su resultado real.

### Diferido (fuera del MVP de punta a punta; si el tiempo aprieta, se recorta en este orden: primero lo primero de la lista)

1. PDF exportable (E5.6) y video con esqueleto (E5.5) con el reproductor sincronizado (8.7); el Nivel 2 del reporte queda sin el reproductor.
2. Reintento desde `parcial` (anotado en la decisión 022; mitigado con el aviso de "¿cámara lenta?" antes de subir).
3. Control contra historial (decisión 020, requiere datos del Criterio 3).
4. Política de retención de siete días (7.6) y borrado de objetos de Storage al eliminar la cuenta.
5. Notificaciones en tiempo real (se usa polling).

## 6. Riesgos

| Riesgo | Probabilidad / impacto | Respuesta |
| --- | --- | --- |
| El navegador del iPhone altera el video al subirlo (transcodifica, pierde fotogramas) | Media / **bloquea el objetivo** | Se prueba en los primeros dos días. Plan B: instruir subir desde "Archivos" o desde un recorte exportado. |
| Edición del frontend en dos lugares (Lovable y este repo) con cambios cruzados | Media / retrabajo | Decidir **una sola** vía de edición (ver §7). |
| Render Free hasta el 20/10: ~7 min por golpe y riesgo de suspensión | Alta / molesta, no bloquea | Aceptable para probar de a un golpe; se resuelve con Standard. |
| Falta de umbrales con referencia para las alertas | Media / afecta el valor del reporte | No se inventan: se documenta y se pasa a limitaciones. |
| Ancho de banda de Valentín (acciones en paneles, pruebas con el celular) | Alta | Este plan agrupa tus acciones (§7). |
| Correo de confirmación del plan Free de Supabase | Alta / se traba el registro | Desactivar confirmación en pruebas; SMTP propio después. |

## 7. Lo que necesito de vos

1. **Aprobar las seis decisiones de §3** (D1–D6), con ajustes si querés.
2. **Dónde se publica el frontend:** el proyecto viene configurado para Cloudflare Workers (Lovable) y el plan decía Vercel. Propongo publicar donde ya está
   configurado y no portar nada ahora. Hace falta una URL pública con HTTPS para probar desde el celular.
3. **Quién edita el frontend:** propongo que lo escriba yo en este repo (cliente de datos, sesión, pantallas conectadas) y que Lovable se use para el
   diseño visual, sincronizando con cuidado. Si seguís editando en Lovable en paralelo, hay que coordinar para no pisarnos.
4. **Un iPhone con cámara lenta y un clip recortado** disponibles para la prueba de riesgo de los primeros dos días.
5. **Panel de Supabase:** confirmación por correo desactivada (semana 1); **panel de Render:** cambio a Standard hacia el 19/10 (semana 2).
