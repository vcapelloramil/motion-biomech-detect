# Plan del MVP de punta a punta — 6/10 → 2/11/2026 (colchón hasta el 6/11)

**Estado:** **aprobado por Valentín el 7/10/2026, con ajustes** (incorporados abajo). No reemplaza a `docs/plan-desarrollo.md`: lo recomprime. Donde este
documento contradice a ese, vale este. Las decisiones que lo requerían están en `docs/decisiones/` (024 a 027) y las correcciones que quedan para la tesis, en
`docs/tesis/correcciones-pendientes-capitulo-4.md`.

## 1. Objetivo y criterio de aceptación

**Lunes 20/10:** Valentín abre la app desde el celular, **se registra (con confirmación por correo) o inicia sesión, sube un video real, ve el estado del análisis y abre
un Reporte simple con los datos reales de ese video**, sin intervención manual de nadie.

**Alcance de la validación (cambio del 7/10):** no habrá pruebas con otros usuarios; la validación la hace Valentín grabándose. **El sistema igual tiene que funcionar
para cualquier usuario nuevo** (registro, confirmación, login, carga y reporte) **como si fuera público.**

No hace falta para el 20/10: PDF, video con esqueleto, evolución, puntaje.

## 2. Punto de partida (verificado el 6–7/10)

- **Servidor:** motor + API (`POST /analisis/{id}/procesar`) en Render; reintento fallido → encolado (decisión 022); Supabase con esquema, RLS, permisos por columna, bucket privado
  `videos` (50 MB, solo mp4/mov) con política por carpeta `<usuario_id>/…`; keep-alive activo; confirmación por correo **activa** en el proyecto (verificado por prueba automática).
- **Contrato del reporte v1.0** (decisión 024): hecho el 7/10, con 18 pruebas.
- **Motor:** produce, por golpe, orden de picos, velocidades pico, cobertura y trazabilidad. **No existen** `audit.py` (alertas), `render.py` (overlay) ni el PDF.
- **Frontend** (`frontend/`, TanStack Start de Lovable): 8 rutas maquetadas con datos simulados; el "Procesando" de `upload.tsx` es una animación. **No hay cliente de Supabase ni de la API.**
  Se publica en **Cloudflare** (decisión 026); el repositorio es la única fuente del código.

## 3. Decisiones de diseño (aprobadas)

| # | Decisión | Dónde |
| --- | --- | --- |
| D1 | **Un solo cambio de contrato** (v1.0): severidad de 4 estados, trazabilidad con `modo_captura`/`factor_ralentizacion`/`origen_factor`, artefactos opcionales con **rutas** (no URL) y `fotogramas_clave`. | 024 |
| D2 | El reporte se guarda **como JSON validado** por el contrato (columna `jsonb` en `reportes_biomecanicos`, además de las columnas actuales). | 024 |
| D3 | **Carga directa a Storage** con la sesión del usuario (bucket limitado a 50 MB y solo tipos de video), sin "Alta de análisis" por la API. Desvío de §4.2.3 y §4.2.5 de la tesis. | 025 |
| D4 | **Estado, reporte y listado = lectura directa a Supabase** (polling, RLS), sin endpoints nuevos. | 025 |
| D5 | **API autenticada con el JWT de Supabase validado contra su JWKS** + chequeo de que el video es del usuario (404 si no). El token compartido se retira. | 025 |
| D6 | Primera entrega con **tres fotogramas clave con esqueleto**; video con esqueleto y PDF, después. | 024 |
| D7 | **Frontend en Cloudflare**; **el repositorio es la única fuente** (Lovable deja de editar código). | 026 |
| D8 | **SMTP propio** para el correo de confirmación (el de Supabase no sirve para usuarios reales). **Pendiente de elegir:** dominio propio + Brevo (recomendado) o cuenta Gmail dedicada (puente). | 027 |

## 4. Plan por semanas

### Semana 1 · 6/10 – 12/10 — el servidor produce un reporte real y acepta usuarios reales

| Cuándo | Qué | Hecho cuando |
| --- | --- | --- |
| **7–8/10** | **Prueba de riesgo del iPhone:** página mínima (`tools/prueba-iphone/`) publicada en Cloudflare; Valentín graba un golpe a 240 fps, lo deja en Fotos y lo sube desde Safari con **cuatro selectores distintos** (cada uno le pide algo diferente al navegador); el servidor mide cada archivo (`app.inspeccionar_subidas`). | Se sabe si Safari entrega el video con sus fotogramas y duración. Si transcodifica, se descubre acá y no el 19/10. |
| 7–8/10 | **E5.4 mínimo:** ensamblador del reporte (trazabilidad, cobertura, secuenciación, métricas y observación de secuenciación, con la **confianza por pico** que el contrato exige), migración de la columna `jsonb`, validación contra el contrato. **E5.7:** prueba automática de vocabulario R2. | Un video real produce un JSON v1.0 que valida y queda guardado. |
| 9–10/10 | **7.4 en el servidor** (decisión 025): JWT por JWKS + chequeo de propiedad (404), **CORS** acotado al dominio del frontend, retiro del token compartido, y endurecer `usuarios` (pendiente de la 022). | Un `curl` con el token de un usuario procesa su video; con el de otro, 404. |
| 10–12/10 | **Correo de confirmación** (decisión 027): SMTP elegido y cargado en Supabase, plantilla en español, *Site URL* apuntando al frontend publicado; **una prueba manual de entrega real**. | Un correo real llega y su enlace lleva al frontend. |
| **(a) 10–12/10, si hay atraso** | **Los tres fotogramas clave pasan a la semana 3** (el Reporte simple sale con la observación y la trazabilidad, sin los tres momentos). | — |
| 10–12/10 | **Fotogramas clave con esqueleto** (3 PNG en el pico de pelvis, torso y brazo, en Storage; las rutas quedan en `videos`). | Tres rutas en `videos`. |

### Semana 2 · 13/10 – 19/10 — la interfaz conectada: probarlo desde el celular el 20/10

| Qué | Detalle |
| --- | --- |
| **Sesión y datos** | Cliente de Supabase, contexto de sesión, rutas protegidas. **Registro** con rol y consentimiento (Ley 25.326) y **aviso de revisar la carpeta de spam**; **Login**. Solo valores públicos en el frontend (URL, clave anon, URL de la API). |
| **Cargar real** | Formulario de la sesión, validación previa (50 MB, aviso <120 fps con **"¿Lo grabaste en cámara lenta?"**), subida directa con progreso, alta de `sesión` + `video`, llamada a la API. **El atleta se crea ahí mismo** (mano dominante y nivel): `sesiones` lo exige y Perfil queda simulado. |
| **Procesando real** | Polling del estado, mensajes por estado y por `motivo_fallo`, botón de reintento (decisión 022). |
| **Reporte simple real** | Observación de secuenciación, tres momentos con los fotogramas reales (si entraron), trazabilidad. "Desde tu 2.ª sesión" donde corresponde. |
| **Render** | **Primero en Free**, sesiones de **2 o 3 golpes**; se mide espera, RSS pico y cortes. **Pasa a Standard solo si la espera o los cortes molestan** (decisión 023). El cambio lo hace Valentín en el panel y **en el mismo paso** se actualiza `render.yaml`. |
| **Lunes 20/10: prueba de punta a punta** | Valentín, con el celular, de cero a reporte, **con un usuario nuevo registrado de verdad**. Lo que falle entra a la semana 3. |

### Semana 3 · 20/10 – 26/10 — lo que hace falta para medir y para que funcione "como público"

- **Sesión de varios golpes** (selección múltiple; los criterios piden ≥10 repeticiones) y estado agregado de la sesión (la vista `sesiones_resumen` ya existe).
- **Biblioteca real** (promovida desde simulada: es lo que permite volver a ver y comparar los resultados) y vista de sesión con todos sus golpes.
- **Registro de tiempos por video** (encolado, inicio y fin del procesamiento): hace falta para medir la latencia del Criterio 4.
- **Reporte detallado:** tabla de magnitudes y bloque de trazabilidad (niveles 1 y 3). Los tres fotogramas clave, si se atrasaron.
- **Eliminar cuenta y datos, funcional** (incluye los objetos de Storage; la cascada de Postgres no los borra). Con el requisito "como si fuera público" deja de poder estar simulado (derecho de supresión,
  Ley 25.326). **Nuevo en este plan; a confirmar.**
- **Recuperación al arranque (6.5).**
- **(c) Respaldo manual de la base con una restauración probada de punta a punta**, **terminado antes de la semana 4** (Supabase Free no incluye respaldos). Los datos del respaldo no van al repositorio.
- **Alertas con fundamento (E5.1), solo si hay umbrales con referencia bibliográfica en el Capítulo 3.** Sin referencia no hay alerta: no se inventan números (R4).
- **(b) Fuera de la semana 3: puntaje de rendimiento y comparación con la sesión anterior.** En una primera sesión saldrían "no auditable" o "desde tu 2.ª sesión". **Diferidos**; si se muestran, solo con datos de ejemplo
  **marcados como tales**.

### Semana 4 · 27/10 – 2/11 — autovalidación (la Etapa 9, con MVP completo al cierre) · colchón hasta el 6/11

Cambio de alcance del 7/10: **no hay pruebas con otros usuarios; se mide con grabaciones propias subidas desde el celular.**

- **(d) Criterios 1 a 4 del apartado 4.3.4 medidos con las grabaciones de Valentín subidas desde el celular**, por el camino real (celular → Safari → Storage → Render → reporte):
  1. Ordenamiento de picos (≥ 8 de cada 10 repeticiones válidas).
  2. Error angular en articulaciones proximales (< 20,6°, contra goniometría manual: es el criterio con más trabajo manual de Valentín).
  3. Repetibilidad de la comparación consigo mismo.
  4. **Latencia de procesamiento, de punta a punta**, con los tiempos registrados en la semana 3.
- **Capturas y evidencia para la tesis** de cada etapa del flujo; resultados en `docs/resultados/`, con el script que los reproduce.
- **(e) Criterio 4 (umbral de tolerancia) y Criterio 5 (utilidad percibida):** como el umbral de latencia y la utilidad los definían los usuarios, queda una de dos:
  1. **Validación exploratoria opcional:** Valentín manda su reporte a un entrenador o kinesiólogo con tres preguntas; las respuestas se registran tal cual; o
  2. **"No evaluados, trabajo futuro".** De cualquier modo, el valor medido de latencia se reporta **sin umbral** y **nada se simula**.
- Pruebas de punta a punta automatizadas y de regresión. Entre el 3 y el 6/11 queda el colchón; la Etapa 10 (hasta el 17/11) no cambia.

## 5. Qué queda simulado, qué queda diferido

### Simulado con datos precargados (cuando se conecte lo real, se reemplaza el origen de los datos, no la pantalla)

| Pantalla | Qué se muestra | Regla |
| --- | --- | --- |
| **Evolución** | `evolucion-mock.ts` | Real recién con ≥2 sesiones comparables. |
| **Perfil** | Rol, vista por defecto, privacidad | El atleta mínimo se crea en Cargar. **Eliminar cuenta y datos pasa a ser real en la semana 3.** |
| Landing, Tecnología | Contenido estático | — |
| Biblioteca | Tarjetas de ejemplo, **solo hasta la semana 3** | Pasa a real en la semana 3. |

**Toda pantalla simulada lleva una marca visible "Datos de ejemplo".** Un dato de ejemplo presentado como del usuario es un dato equivocado presentado como bueno (R3/R4).

### Diferido (fuera del MVP de punta a punta; si el tiempo aprieta, se recorta en este orden: primero lo primero de la lista)

1. PDF exportable (E5.6) y video con esqueleto (E5.5) con el reproductor sincronizado (8.7); el Nivel 2 del reporte queda sin el reproductor.
2. **Puntaje de rendimiento y comparación con la sesión anterior** (E5.2), y con ellos la **Evolución real** (8.8).
3. Reintento desde `parcial` (anotado en la decisión 022; mitigado con el aviso de "¿cámara lenta?" antes de subir).
4. Control contra historial (decisión 020, requiere datos del Criterio 3).
5. Política de retención de siete días (7.6).
6. Notificaciones en tiempo real (se usa polling).

## 6. Riesgos

| Riesgo | Probabilidad / impacto | Respuesta |
| --- | --- | --- |
| El navegador del iPhone altera el video al subirlo (transcodifica, pierde fotogramas) | Media / **bloquea el objetivo** | Prueba de los primeros dos días, con cuatro selectores. Plan B: subir desde "Archivos" o desde un recorte exportado. |
| **Correo de confirmación sin dominio propio** (Brevo reemplaza el remitente y la entrega a Gmail puede fallar sin avisar) | Alta si se elige mal / **el registro no funciona** | Decisión 027: dominio propio + Brevo (recomendado) o Gmail dedicado como puente. Hasta cerrarla, usuarios de prueba creados ya confirmados desde el panel. |
| "Como si fuera público" agrega trabajo (borrar cuenta, abuso de carga, consentimiento) | Media / se come tiempo de la semana 3 | Se acota a lo legal y a lo mínimo; lo demás queda como límite declarado (decisión 025, riesgo aceptado). |
| Los criterios necesitan ≥10 repeticiones por sesión y la medición del Criterio 2 es manual | Media / retrasa la semana 4 | Selección múltiple y Biblioteca real en la semana 3; goniometría con un subconjunto de fotogramas, como en la decisión 015. |
| Render Free: ~7 min por golpe y riesgo de suspensión | Alta / molesta, no bloquea | Se prueba primero con 2–3 golpes; Standard por criterio y para la defensa (decisión 023). |
| Falta de umbrales con referencia para las alertas | Media / afecta el valor del reporte | No se inventan: se documenta y se pasa a limitaciones. |
| Ancho de banda de Valentín (acciones en paneles, grabaciones, goniometría) | Alta | Este plan agrupa tus acciones (§7). |

## 7. Lo que necesito de vos

1. **Elegir la opción del correo (decisión 027):** A (dominio propio + Brevo) o B (cuenta Gmail dedicada). Es lo único que bloquea el registro de usuarios nuevos.
2. **Publicar la página de prueba del iPhone** (pasos en el mensaje de entrega) y avisarme; **grabar el golpe a 240 fps y dejarlo en Fotos.**
3. **Crear en el panel de Supabase un usuario de prueba ya confirmado** (Authentication → Users → Add user, con *Auto Confirm User*) para esa prueba.
4. **Confirmar en Lovable que el proyecto deje de sincronizar cambios hacia el repositorio** (decisión 026).
5. **Confirmar que "eliminar cuenta y datos" real entra en la semana 3** (nuevo por el requisito "como si fuera público").
6. **Render:** el cambio a Standard lo hacés vos cuando decidas, y en el mismo paso me avisás para actualizar `render.yaml`.
