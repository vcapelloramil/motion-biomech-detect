# Plan del MVP de punta a punta — 6/10 → 2/11/2026 (colchón hasta el 6/11)

**Estado:** **aprobado por Valentín el 7/10/2026, con ajustes** (incorporados abajo). No reemplaza a `docs/plan-desarrollo.md`: lo recomprime. Donde este
documento contradice a ese, vale este. Las decisiones que lo requerían están en `docs/decisiones/` (024 a 027) y las correcciones que quedan para la tesis, en
`docs/tesis/correcciones-pendientes-capitulo-4.md`.

## 1. Objetivo y criterio de aceptación

**Martes 20/10** (el 20/10 de 2026 cae martes; el plan decía "lunes"): Valentín abre la app desde el celular, **se registra (con confirmación por correo) o inicia sesión, sube un video real, ve el estado del análisis y abre
un Reporte simple con los datos reales de ese video**, sin intervención manual de nadie.

**Alcance de la validación (cambio del 7/10):** no habrá pruebas con otros usuarios; la validación la hace Valentín grabándose. **El sistema igual tiene que funcionar
para cualquier usuario nuevo** (registro, confirmación, login, carga y reporte) **como si fuera público.**

No hace falta para el 20/10: PDF, video con esqueleto, evolución, puntaje.

## 1a. Decisiones de Valentín del 9/10/2026 (rigen sobre el resto de este documento)

1. **Prioridad absoluta: el flujo de punta a punta** (registro, carga desde el celular, procesamiento en Render, reporte simple). Todo lo demás va a "Después del MVP" (bitácora, nota de traspaso). **Sin investigaciones nuevas:** se anota y se sigue.
2. **Fechas:** se trabaja cualquier día. **Objetivo: martes 20/10. Compromiso: viernes 23/10.** MVP completo funcionando **antes del 2/11**, para que los profesores lo vean con semanas de anticipación.
3. Entran al flujo: el **motivo de fallo propio** para archivos convertidos (con migración) y la **integración en el reporte persistido**.
4. Recálculo del corpus: **solo el Paso A y después de la prueba de punta a punta**; el Paso B, opcional, después del MVP (`docs/plan-recalculo-corpus-tasa-real.md`).
5. `IMG_6391` queda como está; las 6 repeticiones de la toma 02 quedan fuera.

**Efecto sobre la evaluación de abajo:** con trabajo todos los días son 11 días (vie 9 a lun 19) para ~11 sesiones: el 20/10 deja de ser "margen cero por días hábiles" y pasa a ser **ajustado pero posible** (mi estimación:
~60 % de llegar el 20/10, ~85 % el 23/10). El compromiso del 23/10 da tres días de colchón.

## 1b. Estado al 9/10/2026 y fecha realista (honesto) — *escrito antes de las decisiones de 1a*

**Hecho desde el 7/10** (decisiones 024–030): contrato v1.1; carga directa, estado directo y autenticación diseñadas; hosting y fuente única; correo (A/B documentados); casos a/b/c; **lectura de E0 corregida**
(fotogramas visibles, tasa real media), **rotación de videos verticales**, **regularización temporal con trazabilidad** (R4), `procesar_video` con la tasa del archivo; diagnóstico del corpus (la escala real es ×2) y plan de recálculo.
El camino de subida del iPhone existe (**Opciones → Formato: Actual** o Archivos) y los 16 originales reales están emparejados.

**Lo que costó:** tres días (7–9/10) de trabajo no previsto en este plan: la prueba del iPhone y, sobre todo, descubrir que el corpus es 120 fps con rampas. Valioso para la tesis; no avanzó el flujo de punta a punta.

**Lo que falta para el flujo de punta a punta**, en sesiones de trabajo de ~medio día:

| # | Pieza | Sesiones | Depende de |
| --- | --- | --- | --- |
| 1 | Ensamblador del reporte (E5.4 mínimo): JSON v1.1, confianza por pico, columna `jsonb`, vocabulario R2 (+ migración) | 2 | aplicar la migración (Valentín) |
| 2 | Motivo de fallo propio para el archivo convertido (+ migración) | 0,5 | aplicar la migración (Valentín) |
| 3 | 7.4: JWT por JWKS, propiedad del video, CORS, retiro del token compartido, `usuarios` | 1,5 | — |
| 4 | Frontend: cliente de Supabase, sesión, Registro/Login | 1,5 | SMTP (o usuario ya confirmado) |
| 5 | Cargar real: formulario, **instrucción "Opciones → Actual"**, subida directa, alta de sesión y video, llamada a la API | 2 | 3 |
| 6 | Procesando real + reintento | 1 | 5 |
| 7 | Reporte simple real | 1,5 | 1 y 6 |
| 8 | Publicación (Cloudflare), variables, CORS en Render, prueba con el celular | 1 | todo |
| | **Total** | **~11** | |

Hay 7 días hábiles hasta el martes 20/10 (vie 9, lun 12, mar 13, mié 14, jue 15, vie 16, lun 19). A ~1,5 sesiones por día son ~10–11 sesiones: **entra con margen cero**, sin un solo imprevisto, y
con tus acciones en paneles (aplicar dos migraciones, confirmar el correo, Student Pack) llegando a tiempo.

**Mi evaluación:** el martes 20/10 **sigue en pie solo con estos recortes**: sin fotogramas clave (ya permitido por el ajuste (a)), sin Biblioteca real, sin prueba de registro con correo real (usuario creado ya confirmado
desde el panel), Render en Free y **sin el recálculo del corpus compitiendo por el tiempo de trabajo**. Con eso lo veo en torno al **40–50 %**. Lo que **sí recomiendo**: tomar como fecha de la prueba de punta a punta el
**viernes 23/10** (la del 20/10 queda como adelanto si todo sale), porque cuesta tres días y devuelve margen. **El MVP completo del 2/11 se mantiene** (la semana 3 ya había diferido puntaje y comparación).

**El recálculo del corpus no bloquea el MVP**, pero compite por mi tiempo: el Paso A son ~medio día y el B ~1 día más 8 h de cómputo en tu PC. Mi propuesta de orden: flujo de punta a punta primero (1–8), Paso A en un hueco, y el Paso B de noche
cuando la PC pueda quedar encendida.

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
| **7–8/10** | **Prueba de riesgo del iPhone:** página mínima (`tools/prueba-iphone/`) **publicada el 7/10 en https://kinetiq-prueba-iphone.pages.dev/**; Valentín graba un golpe a 240 fps, lo deja en Fotos, **recorta un golpe del medio** y lo sube desde Safari con **cuatro selectores distintos**; el servidor mide cada archivo (`app.inspeccionar_subidas`) y lo clasifica en uno de **tres casos** (decisión 028): (a) 240 fps en tiempo real, (b) cámara lenta horneada a 30, (c) 30 fps con fotogramas descartados (el único inválido). También detecta rampas de velocidad. | **RESULTADO (7/10): el riesgo se materializó.** Los cuatro selectores entregaron **el mismo archivo: H.264 a 100 fps** (no 240), por debajo del mínimo de R1; con cualquier declaración el sistema no lo analizaría (`camara_lenta_*` falla, `normal` queda `parcial`). **ACTUALIZACIÓN 9/10 (decisión 029): el camino existe.** Archivos y **Opciones → Formato: Actual** entregan el HEVC original con las marcas de tiempo reales (**~199 fps medios**, 240 nominales; el mismo archivo por los dos caminos). El formato por defecto de Fotos convierte a H.264 y descarta fotogramas. **Falta probar "cámara lenta sin recortar" con "Actual"**; luego, que E0 lea la tasa real de las marcas (hoy lee 169,28 fps de ese archivo y lo trata mal) y regularice el tiempo (decisión 029, a aprobar). |
| 7–8/10 | **E5.4 mínimo:** ensamblador del reporte (trazabilidad, cobertura, secuenciación, métricas y observación de secuenciación, con la **confianza por pico** que el contrato exige), migración de la columna `jsonb`, validación contra el contrato. **E5.7:** prueba automática de vocabulario R2. | Un video real produce un JSON v1.0 que valida y queda guardado. |
| 9–10/10 | **7.4 en el servidor** (decisión 025): JWT por JWKS + chequeo de propiedad (404), **CORS** acotado al dominio del frontend, retiro del token compartido, y endurecer `usuarios` (pendiente de la 022). | Un `curl` con el token de un usuario procesa su video; con el de otro, 404. |
| 10–12/10 | **Correo de confirmación** (decisión 027): **A en curso** (dominio `.me` del GitHub Student Developer Pack + Brevo, verificación estudiantil pendiente) y **B de respaldo** (Gmail dedicado) si el Pack no sale a tiempo; plantilla en español, *Site URL* apuntando al frontend publicado; **una prueba manual de entrega real**. | Un correo real llega y su enlace lleva al frontend. |
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
| **Martes 20/10: prueba de punta a punta** | Valentín, con el celular, de cero a reporte, **con un usuario nuevo registrado de verdad**. Lo que falle entra a la semana 3. |

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
| El navegador del iPhone altera el video al subirlo (transcodifica, pierde fotogramas) | **OCURRIÓ el 7/10** (100 fps en lugar de 240); **mitigado el 9/10**: "Opciones → Formato: Actual" o Archivos conservan la captura | El formulario de Cargar debe indicar ese camino **antes** de elegir el archivo. Pendiente: probar cámara lenta sin recortar con "Actual"; E0 debe leer la tasa real del archivo (decisión 029). |
| **Correo de confirmación sin dominio propio** (Brevo reemplaza el remitente y la entrega a Gmail puede fallar sin avisar) | Alta si se elige mal / **el registro no funciona** | Decisión 027: dominio propio + Brevo (recomendado) o Gmail dedicado como puente. Hasta cerrarla, usuarios de prueba creados ya confirmados desde el panel. |
| "Como si fuera público" agrega trabajo (borrar cuenta, abuso de carga, consentimiento) | Media / se come tiempo de la semana 3 | Se acota a lo legal y a lo mínimo; lo demás queda como límite declarado (decisión 025, riesgo aceptado). |
| Los criterios necesitan ≥10 repeticiones por sesión y la medición del Criterio 2 es manual | Media / retrasa la semana 4 | Selección múltiple y Biblioteca real en la semana 3; goniometría con un subconjunto de fotogramas, como en la decisión 015. |
| Render Free: ~7 min por golpe y riesgo de suspensión | Alta / molesta, no bloquea | Se prueba primero con 2–3 golpes; Standard por criterio y para la defensa (decisión 023). |
| Falta de umbrales con referencia para las alertas | Media / afecta el valor del reporte | No se inventan: se documenta y se pasa a limitaciones. |
| Ancho de banda de Valentín (acciones en paneles, grabaciones, goniometría) | Alta | Este plan agrupa tus acciones (§7). |

## 7. Lo que necesito de vos

1. **Prueba del iPhone:** grabar el golpe a 240 fps, **recortar un golpe del medio** en Fotos, subirlo con los cuatro selectores en https://kinetiq-prueba-iphone.pages.dev/, y avisarme **con cuánto dura el golpe en la vida real** (para distinguir los casos b y c). **Opcional pero muy útil:** un segundo video con **rampas reales** (en Fotos → Editar, dejar los extremos a velocidad normal moviendo las barras de la cámara lenta, sin recortar) subido con el selector A: el corpus no tiene ninguna rampa y sin una no se puede calibrar un detector (decisión 028).
2. **Correo (decisión 027):** esperar la verificación del Student Pack (A); si no sale, B. Es lo único que bloquea el registro de usuarios nuevos.
3. **Render:** el cambio a Standard lo hacés vos cuando decidas, y en el mismo paso me avisás para actualizar `render.yaml`.
4. Hechos el 7/10: usuario de prueba creado y confirmado en Supabase; Lovable desconectado de GitHub; tarea de eliminar cuenta y datos aprobada para la semana 3.
