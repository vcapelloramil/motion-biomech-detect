# Bitácora de desarrollo

Registro de cierre de cada sesión de trabajo con Claude Code. Una entrada por sesión, la
más reciente arriba. Cada entrada anota: **qué se hizo**, **qué quedó pendiente** y el
**siguiente paso concreto**.

---

## 2026-10-09 (noche, 2) — Pieza 4 (tarea 7.4): la API autentica con el JWT de Supabase

**Commit anterior, ya en `main`: `43fc159`** (piezas 1 a 3 + decisión 031 + tolerancia de R1). Esta pieza está **commiteada en local, sin pushear** (espera a que Valentín aplique la migración de `usuarios` para subir todo junto).

- **JWT por JWKS** (`backend/app/security.py`, PyJWT): ES256 fijado por el servidor, exige `exp`, `sub`, `iss` y `aud = authenticated`; caché de claves y recarga ante un `kid` desconocido. 401 sin Bearer, inválido o vencido
  (el vencido lo dice); 503 si no se pudo pedir el JWKS. La identidad es el `sub`: una prueba manda otro `usuario_id` por query, cuerpo y header y no cambia nada.
- **Propiedad del video:** `POST /analisis/{id}/procesar` compara `videos.usuario_id` con el `sub`; **404** igual que un video inexistente (un id que no es uuid también). La API usa `service_role`, que ignora RLS.
- **CORS acotado:** `KINETIQ_CORS_ORIGINS` (lista; sin valor = ningún origen; un `*` es `ConfigError`); `allow_credentials=False`.
- **Token compartido retirado:** `verificar_token`, `KINETIQ_API_TOKEN` y `get_kinetiq_api_token` ya no existen; `render.yaml` y `.env.example` actualizados.
- **`usuarios` endurecido** (migración `20261009130000_endurecer_usuarios.sql`, **sin aplicar**): INSERT retirado y UPDATE solo de `nombre`, `rol` y `vista_por_defecto`; prueba en rojo hasta aplicarla.
- **Verificado:** suite rápida **447 passed**; `test_api_analisis_e2e`, `test_reintento_supabase` y `test_registro_confirmacion_login` (18 pruebas, contra el JWKS real y con el usuario ajeno recibiendo 404) en verde.
  `test_render_modo_captura` (contra el despliegue) quedó migrada pero **no se corrió**: hace falta desplegar.

### Acciones que son de Valentín

1. **Aplicar** `supabase/migrations/20261009130000_endurecer_usuarios.sql` y avisar (después `pytest tests/integration/test_usuarios_columnas_protegidas.py`).
2. En el panel de Render: **borrar `KINETIQ_API_TOKEN`** y, al publicar el frontend, **cargar `KINETIQ_CORS_ORIGINS`** con su dominio (sin barra final).
3. Confirmar que se pushea (el push dispara un despliegue en Render si el servicio tiene despliegue automático).

### Siguiente

Pieza 5 (frontend: cliente de Supabase, sesión, Registro con aviso de spam y Login). Lo que necesita el frontend de la API: `Authorization: Bearer <session.access_token>` (especificación §5).

---

## 2026-10-09 (noche) — Migración aplicada y corridas en verde; decisión 031 (veredicto por gesto y encuadre); tolerancia del 5 % en R1

**Corridas (con la migración `20261009120000` ya aplicada por Valentín): `test_procesar_video_e2e.py` pasó (2 min) y `pytest -m requiere_supabase` completo dio 79 passed, 0 failed (8 min 55 s), sin restos.
Suite rápida: 419 passed.** El e2e ahora verifica que el `reporte` guardado valida contra el contrato y que cada métrica trae `confianza_media`.

### Decisiones de Valentín (9/10, a continuación del cierre de arriba)

1. **Veredicto de la secuencia → decisión 031.** Mi propuesta (veredicto solo en revés, el resto `no_auditable`) fue rechazada: contradecía la tesis (§4.3.3, tabla 4.8: el saque tiene el respaldo bibliográfico) y
   `no_auditable` significa "no se pudo medir". **Regla:** veredicto del par cadera → tronco solo donde hay **(a)** referencia del orden esperado y **(b)** Criterio 1 cumplido para ese gesto y encuadre; donde falta una,
   el orden se documenta como **`sin_evaluar`** (la etiqueta del brazo, decisión 011). Contrato **v1.2** (aditivo: `Observacion.severidad` admite `sin_evaluar`; los cuatro estados de R3 no cambian).
2. **Escala desconocida → velocidades `null`:** aprobado, implementado.
3. **Citas:** Kovacs y Ellenbecker (2011), Fleisig et al. (2003) y Martin et al. (2014), sin capítulos. Verificadas contra el **texto** de los capítulos 3 y 4; **la lista formal de Referencias no está en el repositorio**
   (queda cotejar autores, título y revista contra ella). Martin (2014) no se usa en estos veredictos: no respalda "tronco antes que cadera".
4. **R1 con fotogramas perdidos:** tolerancia del 5 %: **114 fps** para la secuenciación completa y **57** para la preparación; el umbral de 240 no tiene tolerancia. Documentado en la decisión 029 (actualización) y en
   CLAUDE.md R1. Con eso el clip de 60 fps (59,26 reales por un hueco de 3 fotogramas) vuelve a ser `solo_preparacion`.

### Qué grupos quedan con veredicto (cifras de `criterio1-resumen.md`, sesión 2, τ = 1, par pelvis-torso)

| Gesto · encuadre | (a) referencia | (b) Criterio 1 | Veredicto |
| --- | --- | --- | --- |
| **Saque · perfil** | Kovacs y Ellenbecker (2011); Fleisig et al. (2003) | cumple (1a 1,00 · 1b 1,00) | **sí** |
| Saque · tres cuartos | sí | no (1a 0,50) | sin evaluar |
| Drive · perfil | no | cumple (1,00 · 1,00) | sin evaluar |
| Drive · tres cuartos | no | no (0,00) | sin evaluar |
| Revés · perfil | no | no (0,67) | sin evaluar |
| Revés · tres cuartos | no | cumple (1,00 · 0,83) | sin evaluar |

**Se revisa cuando se haga el recálculo (Paso A):** anotado en la decisión 031 y en `docs/plan-recalculo-corpus-tasa-real.md`.

### Hallazgos que quedan anotados (sin investigar)

- **El Criterio 1 no lo cumplió solo el drive de perfil:** a τ = 1 lo cumplen tres grupos (saque perfil, drive perfil, revés tres cuartos); a τ = 2 y 3, dos (saque perfil y drive perfil). La frase de la decisión 029
  ("el único grupo que cumple es `drive|perfil`, 1a = 0,83") no coincide con `criterio1-resumen.md`: reconciliar al recalcular.
- **Efecto visible de la regla:** en el saque de perfil el orden modal medido es tronco antes que cadera (6 de 6; coincidencia con lo esperado 0,00). Con la regla, **todo saque de perfil con ese orden sale como
  `desvío leve`** (nunca alerta de carga). Puede ser una característica del jugador o un artefacto de la vista de perfil monocular: la 015 (salvedad 2) lo había evitado por falta de fuente. Anotado para el Capítulo 7.
- Mi reproche a una prueba vieja: `test_normal_60fps_queda_parcial_solo_preparacion` estaba desactualizada respecto de la 029 (tasa medida, no la del contenedor); ahora cubre la tolerancia.

---

## 2026-10-09 (tarde) — `requiere_supabase` corrido; piezas 1 a 3 del flujo listas, **falta aplicar una migración**

**Corrida real contra el proyecto Supabase (primera desde el 6/10): 78 passed, 1 failed** (9 min 21 s, sin restos). La falla era una prueba vieja, no un fallo del producto:
`test_normal_60fps_queda_parcial_solo_preparacion` pedía `fps_real == 60` y la aptitud "solo_preparacion". Desde la decisión 029 la tasa es la **medida**: ese clip es nominal 60 fps pero trae **un hueco de 3 fotogramas
(66,7 ms) en 4,3 s**, así que la media real es **59,26** (1,2 % bajo 60) y la aptitud sale "rechazado". Para el producto da lo mismo (queda `parcial`, sin reporte, en los dos casos), pero la etiqueta cambió. Actualicé la prueba
a la semántica de la 029 (`fps_real` entre 59 y 60,1; `R1` en el motivo) y volvió a pasar.
**Anotado, no investigado:** los umbrales de 60 y 120 fps sobre la media medida son frágiles con pocas pérdidas (un 120 fps legítimo con un par de fotogramas perdidos da 118,6 → `parcial`). Decisión tuya si conviene
una tolerancia o evaluar sobre la grilla nominal; hoy se aplica la 029 tal cual.

### Qué se hizo (piezas 1, 2 y 3 del plan; sin commit, sin push)

- **Migración única `20261009120000_reporte_json_y_motivo_archivo_convertido.sql`:** `reportes_biomecanicos.reporte jsonb` (nullable, debe ser un objeto) y el código `archivo_convertido` en `videos.motivo_fallo`.
  **Sin aplicar.** El código nuevo depende de ella: hasta aplicarla, `procesar_video` falla al guardar el reporte (no desplegar ni pushear antes).
- **Ensamblador del reporte** `backend/app/ensamblar_reporte.py` (E5.4 mínimo): arma el JSON v1.1 y lo **valida contra el contrato antes de guardarlo**. Confianza por pico = media de la confianza de las articulaciones del
  segmento en el fotograma del pico (como pidió la 024); tramos no auditables en segundos; cobertura auditable = unión de los tramos excluidos de la cadena; observaciones en el vocabulario de R2 con **prueba automática del
  vocabulario** (E5.7). `procesar_video` guarda el JSON, el mismo `secuencia_correcta` y las métricas **desde esa única fuente**, y ahora escribe `confianza_media` en cada métrica.
- **Motivo `archivo_convertido`:** `fallido` con `fps_real` medido, cuando se declaró cámara lenta, el archivo llegó en tiempo real y **la grilla nominal de sus marcas ya está bajo 120 fps** (100 o 60 fps convertidos). No aplica con
  "normal" (60 fps genuinos → `parcial` por R1) ni a una captura de 120 con fotogramas perdidos. Reintento: solo si cambia la declaración (igual que `modo_captura_incompatible`); el arreglo real es subir otro archivo.
  Texto y botón "Subir otro archivo" en la especificación de frontend §5.
- **Pruebas:** 34 nuevas (21 del ensamblador, 13 de archivo convertido con cliente falso y vocabulario de la migración); suite rápida **400 passed**. `test_procesar_video_e2e` ahora exige el `reporte` válido y `confianza_media`.
- **Corrida en seco** de `procesar_video` con un clip real de Fase B y un cliente falso (96 s, sin tocar la base): el JSON sale válido y serializable. Ahí apareció un defecto mío (cobertura 100 % junto a tramos no
  auditables) que quedó corregido y con prueba.

### Decisiones mías que necesitan tu confirmación (están aisladas, se cambian en un solo lugar)

1. **Veredicto de la secuencia (la 015 lo dejó abierto "para la Etapa 5").** Solo el **revés** emite `correcto` / `desvío leve`. En **saque y drive** el orden se documenta (`orden_observado`, instantes) pero `correcto = null` y la
   observación va en gris (`no_auditable`) con el texto "se documenta el orden pero no se clasifica como correcto o incorrecto". Razón: perfil invertido sin fuente (salvedad 2) y tres cuartos no ordenable (salvedad 1).
   Constante `GESTOS_CON_VEREDICTO` en `ensamblar_reporte.py`. **Consecuencia visible:** en el MVP, saque y drive nunca salen en verde ni en ámbar. El gris para "medido pero sin veredicto" es el estado más cercano de los cuatro de R3.
2. **Escala desconocida** (`escala_temporal_conocida = false`): las velocidades pasan a `valor = null`, `auditable = false` y se agrega una observación; el orden sí se documenta. Antes quedaban como auditables (R3).
3. **Referencia del orden:** "Capítulo 3, apartado 3.3.3", no una cita con año; no inventé una.

### Siguiente paso concreto

1. **Valentín aplica la migración** `supabase/migrations/20261009120000_reporte_json_y_motivo_archivo_convertido.sql` en el SQL Editor y avisa.
2. Correr `pytest tests/integration/test_procesar_video_e2e.py` y después `pytest -m requiere_supabase` (el e2e tarda ~1,5 min).
3. Pieza 4 (7.4: JWT por JWKS, propiedad del video, CORS, retiro del token compartido) y recién después el frontend.

---

## 2026-10-09 (cierre) — NOTA DE TRASPASO (antes de /clear) · decisiones de Valentín y estado

**Rama:** `main`. **Último commit de código: `18942d5`** (E0 lee fotogramas visibles y tasa real, rotación, regularización, contrato v1.1); `68df5ff` es el de documentación (decisión 030, plan de recálculo). El commit
de esta nota es el siguiente. Árbol limpio. **Suite rápida: 366 passed.** `pytest -m requiere_supabase` **no se volvió a correr** desde el 6/10 (77 passed): el motor cambió desde entonces (`probe`, `procesar_video`); correrlo antes
de confiar en el camino real.

### Reglas de trabajo fijadas por Valentín (9/10)

1. **PRIORIDAD ABSOLUTA: el flujo de punta a punta** — registro, carga desde el celular, procesamiento en Render, reporte simple. **Todo lo demás va a la lista "Después del MVP" (abajo). Nada de investigaciones nuevas:
   si aparece algo, se anota y se sigue.**
2. **Fechas:** se trabaja cualquier día, no solo hábiles. **Objetivo: martes 20/10. Compromiso: viernes 23/10.** El **MVP completo, funcionando antes del 2/11**, para que los profesores lo vean con semanas de anticipación.
3. **`IMG_6391` no está incompleto:** es un video corto en el iPhone (2503 fotogramas, 12,5 s). **No se vuelve a bajar.** Las **6 repeticiones de la toma 02** (`saque|trescuartos|toma 02`, sesión 2) **quedan afuera** del recálculo. *(Anotado, no investigado: el
   horneado de esa toma tiene 7011 fotogramas, que a la razón de los otros 15 pares corresponderían a ~15 200 reales; la fecha de creación coincide. Se deja como está por decisión de Valentín.)*
4. **Recálculo del corpus:** **pre-registro aprobado tal cual** — umbral 0,8, mismos grupos, tolerancia en ms (**primaria 8,3; sensibilidad 4,2; 12,5; 16,7**). **Solo el Paso A, y después de la prueba de punta a punta.** El **Paso B es opcional y
   queda después del MVP.** El **Capítulo 7 tiene que anotar el ×2 y su corrección** (ya anotado en `docs/tesis/correcciones-pendientes-capitulo-4.md`).
5. **Entran al flujo** (no son "después"): el **motivo de fallo propio para archivos convertidos** (con migración) y la **integración en el reporte persistido**.

### Qué está hecho (resumen; detalle en las entradas de abajo y en las decisiones 021–030)

- **Servidor:** keep-alive, reintento y permisos por columna aplicados y verificados (77 passed el 6/10); contrato del reporte **v1.1**; E0 lee la tasa real de las marcas de tiempo y los fotogramas visibles; rotación de videos verticales;
  regularización temporal con trazabilidad de puntos interpolados; `procesar_video` toma la tasa del archivo (`origen_factor = marcas_de_tiempo`).
- **Subida desde el iPhone:** el camino que funciona es **Opciones → Formato: Actual** o la app **Archivos** (HEVC con marcas reales, ~200 fps medios). El formato por defecto de Fotos convierte a H.264 y baja a 100 fps o menos.
  Página de prueba publicada: https://kinetiq-prueba-iphone.pages.dev/ (usuario de prueba ya confirmado en Supabase).
- **Corpus:** el horneado es un remuestreo a **~120 fps con rampas**, no 240 (decisión 030): velocidades ×2 sobreestimadas, ms ×0,5 subestimados, ángulos sin cambio. Los 16 originales reales están emparejados (15 pares alineados, 88 repeticiones ubicadas).
- **Frontend:** sigue siendo la maqueta de Lovable con datos simulados; **no hay cliente de Supabase ni de la API todavía.**

### Lo que FALTA para el flujo de punta a punta, en orden (≈ 11 sesiones de ~medio día)

| # | Pieza | Sesiones | Depende de |
| --- | --- | --- | --- |
| 1 | **Migración única** (columna `jsonb` del reporte + código de motivo de fallo para archivo convertido) y su aplicación | 0,5 | Valentín aplica la migración |
| 2 | **Ensamblador del reporte** (E5.4 mínimo): JSON v1.1 validado, confianza por pico, vocabulario R2 (prueba automática), persistencia con la trazabilidad de la regularización | 2 | 1 |
| 3 | **Motivo de fallo propio** en `procesar_video` y mensaje en la especificación | 0,5 | 1 |
| 4 | **7.4:** JWT de Supabase por JWKS, chequeo de propiedad del video (404), CORS acotado, retiro del token compartido, endurecer `usuarios` | 1,5 | — |
| 5 | **Frontend:** cliente de Supabase, sesión, Registro (con aviso de spam) y Login | 1,5 | SMTP o usuario ya confirmado |
| 6 | **Cargar real:** formulario, **instrucción "Opciones → Actual" / Archivos antes de elegir el archivo**, subida directa, alta de sesión y video, llamada a la API | 2 | 4 |
| 7 | **Procesando real** + reintento | 1 | 6 |
| 8 | **Reporte simple real** | 1,5 | 2 y 7 |
| 9 | Publicación en Cloudflare, variables, CORS en Render, **prueba con el celular** | 1 | todo |

Con trabajo todos los días son **11 días hasta el martes 20/10** (vie 9 a lun 19): ~1 sesión por día, **sin colchón**; el compromiso del vie 23/10 da 3 días de margen.

### Siguiente paso concreto

**Pieza 1+2+3:** escribir **una sola migración** (columna `jsonb` en `reportes_biomecanicos` y el código de `motivo_fallo` para archivo convertido), avisar a Valentín para aplicarla, y construir el ensamblador del reporte y el motivo de fallo.
Después 7.4, y recién entonces el frontend. **No tocar el corpus ni el recálculo hasta que la prueba de punta a punta pase.**

### Acciones que son de Valentín (paneles y dispositivos)

- Aplicar la migración de la pieza 1 en el SQL Editor y avisar.
- **Correo:** esperar el Student Pack (opción A: dominio `.me` + Brevo); si no sale antes del 20/10, usar la B (Gmail dedicado) o crear los usuarios de prueba ya confirmados desde el panel. Confirmar el *Site URL* en Supabase al publicar el frontend.
- Render: Free primero; pasar a Standard si la espera o los cortes molestan (decisión 023), y avisar para actualizar `render.yaml` en el mismo paso.
- Probar desde el iPhone con **Opciones → Formato: Actual** cuando esté Cargar.

### Después del MVP (no se toca hasta pasar la prueba de punta a punta y tener el MVP)

- **Paso B del recálculo** (pose desde los originales reales, ~8 h) y la **decisión 031** con los resultados.
- Reetiquetar `escala_temporal` en `catalogo.csv` (fuera del repositorio) y marcar el factor 8 como supuesto.
- PDF y video con esqueleto (E5.5/E5.6) y el reproductor sincronizado (8.7); fotogramas clave con esqueleto **si no entran** en el flujo.
- Puntaje de rendimiento, comparación con la sesión anterior y Evolución real; reintento desde `parcial`; control contra historial (decisión 020).
- Biblioteca real; sesión de varios golpes y estado agregado; **eliminar cuenta y datos** (Ley 25.326) y sus objetos de Storage; recuperación al arranque (6.5); **respaldo manual con restauración probada** (7.7);
  retención de siete días (7.6).
- Probar "cámara lenta sin recortar" con Opciones → Actual; la rampa real que no se probó; la prueba manual de entrega del correo.
- Capítulos 4, 6 y 7 (redacción) con `docs/tesis/correcciones-pendientes-capitulo-4.md`; autovalidación de la semana 4 (Criterios 1 a 4 con grabaciones desde el celular).
- Los reportes de prueba ya guardados en Supabase tienen `fps_real = 240` (supuesto): sin impacto, no hay datos de usuarios; se borran con las pruebas.

### Para retomar sin perder tiempo

- Python del proyecto: `backend/.venv/Scripts/python.exe`, con `PYTHONPATH=backend:tests` para pytest. `ffmpeg`/`ffprobe` están en el PATH.
- `wrangler` (Cloudflare) tiene la sesión abierta con permisos mínimos; se publica con `frontend/node_modules/.bin/wrangler.exe pages deploy …`. **`armar.py` hay que correrlo con el Python del proyecto**, o se publica la versión vieja.
- La caché local `backend/.cache` (818 MB: miniaturas del corpus real, poses, energías) está **ignorada por git**; se puede borrar.
- **Los videos nunca van al repositorio** (`*.mov`, `*.MOV`, `*.mp4`, `.cache/` están ignorados): antes de cada commit, `git ls-files | grep -i -E "\.(mov|mp4|npy|npz)$"` tiene que dar vacío.
- Los originales reales están en `C:\Users\valen\Desktop\corpus-originales-reales`; no se copian.
- Convención: decisiones en `docs/decisiones/` (no se reescriben: las correcciones se marcan con nota visible); resultados en `docs/resultados/`.

---

## 2026-10-09 (noche) — Los 16 originales reales: el corpus horneado es 120 fps con rampas (decisión 030)

- **Inventario de `corpus-originales-reales`:** son **16 archivos** (no 18). HEVC 1920×1080, marcas de tiempo reales, tasa real media **199,9–201,0 fps**, ninguno horneado, sin rotación. **`IMG_6391` está incompleto** (2503 fotogramas, ~15 200 esperados): hay que volver a bajarlo.
- **Emparejamiento:** 16 de 16 por fecha y hora de creación. Los 2 horneados sin par son los controles de velocidad normal (030 y 060): no entran.
- **Los fotogramas NO corresponden uno a uno.** El horneado trae el 46 % de los fotogramas del real: es un **remuestreo a 120,2 fps en tiempo real** (1,665–1,675 reales por horneado en los 15 pares; ~7 % repetidos) con **rampas a velocidad normal** en los extremos.
  Hay una asignación monótona horneado→real (99,1–99,9 %). 88 repeticiones ubicadas: 86 en la meseta, 2 empiezan en una rampa (`saque_perfil_240_01_rep01`, `reves_perfil_240_02_rep01`).
- **Corrección de magnitud:** las velocidades del corpus están **×2,0** sobreestimadas y los ms **×0,5** subestimados (la 029 decía ×1,2). Los ángulos no cambian. **Mi simulación de la 029 suponía fotogramas consecutivos reales: la suposición era falsa.**
- **Error mío anterior (7–9/10):** había dicho "el corpus no tiene rampas": **sí las tiene** (en los extremos de los originales, a velocidad normal). Lo que vi al final del original era manejo de la cámara *dentro* de un tramo a velocidad normal.
- **Motor (obligatorio, aprobado):** `probe()` lee fotogramas visibles y tasa real media; `evaluar()` la usa; rotación automática de videos verticales; `_tasa_del_archivo` (factor 1 con marcas reales, `origen_factor = marcas_de_tiempo`);
  **regularización temporal** con trazabilidad de puntos interpolados; contrato **v1.1**. Humo de punta a punta sobre un recorte real (398 fotogramas, 82 interpolados = 17,1 %). La tarea de la rotación ofrecida queda cumplida.
- **Plan de recálculo escrito, NO ejecutado:** `docs/plan-recalculo-corpus-tasa-real.md` (Paso A rápido sobre poses cacheadas a 120,2 fps; Paso B definitivo desde los originales reales, ~8 h de pose; pre-registro de la tolerancia en ms).
- **Calendario:** el 20/10 cae **martes**. Sigue en pie solo con recortes y margen cero (~40–50 %); recomendación: **viernes 23/10** como fecha de la prueba de punta a punta. MVP completo del 2/11 intacto.
- **Anotaciones para el Capítulo 7** en `docs/tesis/correcciones-pendientes-capitulo-4.md` (RNF-01, fragilidad del Criterio 1, escala, tasa por grabación).

---

## 2026-10-09 (más tarde) — Resultado de las pruebas de Archivos / cámara lenta / Opciones; la tasa real varía (decisión 029)

- **Archivos y "Opciones → Formato: Actual" entregan el MISMO archivo** (42 bytes de metadatos de diferencia): **HEVC 1920×1080, 398 fotogramas visibles, 2,005 s, marcas de tiempo reales**, nominal 239,98 fps y **real media 198,9 fps** (17,1 % de fotogramas perdidos, con un patrón casi periódico:
  cada ~12 fotogramas faltan dos). Coincide con los ~200 fps de Fotos (ⓘ). El camino por defecto de Fotos reexporta a H.264 y **descarta** fotogramas (100 fps en el recorte; 60 nominales y **43 reales** en la cámara lenta de 9,5 s, que además trae **rotación −90°**).
- **`probe()` lee mal el archivo "Actual":** 169,28 fps y 479 fotogramas (cuentan 81 de pre-roll ocultos); hoy `camara_lenta_240` falla y `normal` lo analiza con 169,28 fps. `uniformidad_temporal.marcas_de_tiempo` ahora lee solo los **fotogramas visibles** y mide tasa nominal, **real media**, intervalos y pre-roll; el inspector los informa.
- **Diagnóstico del corpus (sin recalcular), decisión 029.** Simulación de sensibilidad con la huella real de pérdidas sobre las 84 repeticiones (1008 corridas, `docs/resultados/tasa-real-sensibilidad.json`; el arnés reproduce 48/48 picos guardados): velocidades **×1,12–1,16** (hasta ×1,38 en el brazo; teórico ×1,21), ms **×0,83**; el pico se corre ~4 ms (1 fotograma);
  **el orden estimado cambia en ~11–14 %** de las corridas (los picos de pelvis y torso están casi siempre a 0–3 fotogramas: mediana 2); el único grupo que cumple el Criterio 1 (`drive|perfil`) es **frágil** (10/12 y 6/12 mundos) y las conclusiones negativas son robustas (19 de 25 nunca cumplen). Los ángulos no cambian. **Mi lectura inicial ("el orden no cambiaría") valía para el orden real, no para el estimado.**
- **Catálogo:** `escala_temporal: conocida` en los 97 clips propios no tiene base (la huella de fotogramas únicos no detecta fotogramas perdidos); a reetiquetar como nominal.
- **No se recalcula** el corpus: lo más útil es la autovalidación de la semana 4 con archivos de marcas reales. Si Valentín re-exporta las 17 grabaciones originales con "Actual", se puede rehacer el eje de tiempo y recalcular Criterios 1 y 3.
- **Propuesta de producto (a aprobar):** aceptar como auditable completo solo archivos con marcas reales; regularización temporal antes de E3; R1 sobre la tasa real media; horneado (b) solo degradado (orden y ángulos; velocidades y ms no auditables); `modo_captura` como trazabilidad; motivo de fallo propio; contrato v1.1.
- **Pendiente (Valentín):** subir una **cámara lenta sin recortar con Opciones → Actual**. **Pendiente (técnico, separado):** aplicar la rotación de videos verticales en E0 (tarea ofrecida).

---

## 2026-10-09 — Página del iPhone: corregido el "Invalid key" del campo Nota

- **Causa (confirmada contra el Storage real):** la clave del objeto llevaba `~` como separador de la nota (`A-video-todos~recortado-...`) y Supabase Storage la rechaza con `InvalidKey` (400). **Error mío**, de la versión que agregó el campo "Nota".
- **Arreglo:** la nota y el separador ahora solo usan letras ASCII, números, guion y guion bajo (separador `_`); las tildes pasan a su letra base y todo lo demás a guion; la página valida la clave antes de subir y muestra el error si no es válida. Probado con entradas hostiles (tildes, `~`, `/`, emoji, textos largos) y contra el Storage real (la clave con `~` falla, la nueva sube). Republicada.
- **Dato de Valentín, sin subir todavía:** el mismo recorte guardado en **Archivos** pesa **16,47 MB** (contra 8,21 MB desde Fotos), dura 2,005 s, 1920×1080 y conserva la fecha original (24/09): sugiere que Archivos entrega el original sin convertir. **Falta subirlo y medirlo con el inspector.**

---

## 2026-10-07 (noche) — Resultado de la prueba del iPhone: el recorte llegó a 100 fps (decisión 028)

- **Valentín subió el mismo recorte (2 s, se reproduce a velocidad normal) con los cuatro selectores.** Los cuatro archivos son **el mismo video** (15 bytes de metadatos distintos): **H.264 a 100 fps, 201 fotogramas, 2,01 s, 8,2 MB, con audio**, sin
  etiqueta de cámara lenta. **La hipótesis "el recorte conserva los 240 fps" no se cumple por este camino.** Un saque entero entra en esos 201 fotogramas (en el corpus un saque dura 436–656 a 240 fps): se infiere tiempo real a 100 fps, no medido.
- **El sistema no lo analizaría con ninguna declaración** (calculado con las funciones de producción): `camara_lenta_240`/`120` → `fallido` por `modo_captura_incompatible` (240/100 = 2,4); `normal` → `parcial` por R1 (100 < 120). **Riesgo grave para el 20/10.**
- **Error mío corregido:** el primer informe del inspector clasificó los archivos como (c) por un umbral mal elegido (100 fps justo en el límite); ahora cualquier archivo con marcas ≥ 45 fps es "tiempo real" y se informa su aptitud (R1). El inspector además calcula qué haría el sistema según la declaración.
- **Página republicada** con un campo "nota" para distinguir cada prueba. **Pendiente (Valentín):** (1) el mismo recorte guardado en **Archivos** y subido con "Elegir archivos"; (2) una cámara lenta **sin recortar** (≤ ~3 s reales); (3) anotar si el selector de Fotos muestra "Opciones" y qué ofrece.
- **Especificación §5 corregida:** se retiró la afirmación de que el recorte conserva los 240 fps. El mensaje `modo_captura_incompatible` ("revisá el modo de captura") es **engañoso** para este caso (la declaración está bien, cambió el archivo): hace falta un motivo propio o tratarlo como `parcial` por R1; no se implementa hasta conocer los caminos alternativos.

---

## 2026-10-07 (más tarde) — Página del iPhone publicada; casos a/b/c; Student Pack (decisiones 027 y 028)

- **Página de prueba del iPhone PUBLICADA:** https://kinetiq-prueba-iphone.pages.dev/ (Cloudflare Pages, proyecto `kinetiq-prueba-iphone`). Se publicó con `wrangler`. El primer `wrangler login` falló con `request_forbidden`; el
  reintento con permisos mínimos (`--scopes account:read user:read pages:write`) funcionó. Valentín creó el usuario de prueba (confirmado) en Supabase. **Pendiente: que grabe, recorte un golpe del medio y suba con los cuatro selectores.**
- **Decisión 028 — tres casos de llegada de un golpe a 240 fps:** (a) 240 fps en tiempo real, (b) cámara lenta horneada a 30, (c) 30 fps con fotogramas descartados (el único inválido). Las marcas de tiempo distinguen (a) de (b)/(c),
  **no (b) de (c)**: hace falta la duración real del gesto. Implementado `engine/uniformidad_temporal.py` (17 pruebas) y el inspector informa el caso por selector. `_factor_y_motivo` con 240 fps en tiempo real declarado
  `camara_lenta_240`: factor 1, 240 efectivos (8 pruebas nuevas). (c) **no se puede detectar con `_factor_y_motivo`** (30 × 8 = 240 cierra igual): solo lo cubren, de forma condicional, los techos de plausibilidad (decisión 020).
- **Rampas de velocidad: error mío corregido.** Primero interpreté que los saltos de movimiento al principio y al final de los originales eran rampas; **era manejo de la cámara** (el final del original muestra a la persona agarrando el teléfono), y
  los dos originales de velocidad normal dan el mismo patrón. **El corpus no tiene ninguna rampa real.** Medido en los 115 clips (`docs/resultados/uniformidad-temporal-corpus.json`, reproducible): el detector marca los 18 originales, los 2 clips
  completos de velocidad normal y 5 de 95 recortes de golpe válidos (5,3 %; 0 con 8×). **Decisión: E0 no rechaza por velocidad no uniforme**; queda como diagnóstico experimental. Para calibrar uno hace falta una rampa real (pedido a Valentín).
- **Decisión 027 actualizada:** opción **A en curso** (dominio `.me` gratis del GitHub Student Developer Pack con Namecheap —1 año, verificado en la página del Pack— + Brevo) y **B de respaldo** (Gmail dedicado). Procedimientos de las dos documentados.
- **Decisión 026:** Lovable desconectado de GitHub por Valentín (hecho). **Especificación de frontend §5:** explica qué elegir en "¿Cómo lo grabaste?" (cómo se grabó, no cómo se ve ni llega el archivo).

---

## 2026-10-07 — Plan de punta a punta aprobado; contrato v1.0; decisiones 024 a 027

**Rama:** `main`. Valentín aprobó el plan de punta a punta (`docs/plan-mvp-punta-a-punta.md`) con ajustes (puntaje y comparación diferidos; fotogramas clave a la
semana 3 si hay atraso; respaldo con restauración probada antes de la semana 4; **autovalidación** en la semana 4, sin pruebas con otros usuarios; el sistema igual
tiene que funcionar para cualquier usuario nuevo).

- **Decisión 024 — contrato del reporte v1.0, IMPLEMENTADO:** `schemas/reporte.py` + `contrato-reporte.ejemplo.json` + 18 pruebas (`test_contrato_reporte.py`). Severidad de 4 estados;
  `modo_captura`/`factor_ralentizacion`/`origen_factor` en la trazabilidad; `version_contrato`; `dispersion` opcional; artefactos opcionales **por ruta, no URL** (refinamiento mío sobre lo aprobado:
  una URL firmada vence) y `fotogramas_clave`. Dos pruebas mantienen alineados el contrato y las migraciones. El Anexo A queda superado.
- **Decisión 025 — carga directa a Storage, estado por lectura directa, API autenticada con JWT por JWKS + chequeo de propiedad (404).** Desvío de §4.2.3/§4.2.5. Verificado contra el proyecto
  real: el JWKS es público y publica una clave ES256; los tokens de usuario se validan contra él (prueba automática).
- **Decisión 026 — frontend en Cloudflare; el repositorio es la única fuente (Lovable deja de editar).** `CLAUDE.md` §5 actualizado. Correcciones del Capítulo 4 en
  `docs/tesis/correcciones-pendientes-capitulo-4.md` (nueve ítems).
- **Decisión 027 — correo de confirmación: PROPUESTA, pendiente de que Valentín elija.** **Hallazgo:** la propuesta "Brevo sin dominio propio" no es confiable: Brevo exige dominio propio
  (no deja autenticar `gmail.com`, reemplaza el remitente por `t-sender-sib.com`/`brevosend.com`, y hay reportes de correos a Gmail que no llegan sin error). Supabase: el SMTP integrado entrega 2
  por hora y solo a miembros del equipo. Opciones: **A** dominio propio + Brevo (recomendada) o **B** cuenta Gmail dedicada (puente; límites sin verificar). Plantilla en español en
  `supabase/templates/confirmar-registro.html`.
- **Prueba automática de registro → confirmación → login** (`test_registro_confirmacion_login.py`): un usuario nuevo no entra sin confirmar, confirma con el enlace y entra; el token se valida por JWKS.
  Confirma que **la confirmación por correo está activa en el proyecto**. No prueba la entrega del correo (el enlace sale de la API de administración, sin enviar nada).
- **Decisión 023 actualizada:** Free primero (sesiones de 2–3 golpes), Standard si la espera o los cortes molestan y siempre para la defensa; precios verificados por Valentín en render.com/pricing.
  El cambio lo hace Valentín y en el mismo paso se actualiza `render.yaml` (hoy `plan: free`).
- **Prueba de riesgo del iPhone, lista para publicar:** `tools/prueba-iphone/` (página con cuatro selectores) + `armar.py` (genera `publicar/` con URL y clave **anon**, nunca la `service_role`) +
  `backend/app/inspeccionar_subidas.py` (mide cada archivo subido: códec, fps, fotogramas, duración). Probado el inspector con un archivo real; la página, solo su sintaxis (no se la ejercitó con un
  login real). **Pendiente: que Valentín la publique, grabe y suba.**
- Con "como si fuera público" aparece trabajo nuevo, ahora en el plan (semana 3): **eliminar cuenta y datos funcional** (incluye objetos de Storage), a confirmar por Valentín.

---

## 2026-10-06 (al final del día) — Reintento `fallido → encolado`, permisos por columna y plan de Render (decisiones 022 y 023)

**Rama:** `main`. Diseño aprobado por Valentín y registrado como **decisión 022**. Orden de trabajo: (a) migración de
seguridad + prueba → (b) migración del reintento → (c) `procesar_video` y API → (d) pruebas → (e) especificación de
frontend. Regla: no se pushea código que dependa de una migración sin aplicar; se avisa a Valentín cuando cada
migración está lista.

- **Hallazgo:** `authenticated` podía escribir cualquier columna de `videos` (`estado`, `motivo_fallo`, `fps_real`…).
  Comprobado contra el proyecto real: la prueba nueva dio 20 fallas / 3 pasadas antes de la migración.
- **(a) HECHO, aplicado y pusheado:** `20261006130000_columnas_protegidas_videos_sesiones.sql` +
  `tests/integration/test_columnas_protegidas.py` (commit `4a666f0`). Valentín aplicó la migración;
  `pytest -m requiere_supabase` dio 62 passed (39 anteriores + 23 nuevos), sin restos (0 usuarios Auth, 0 objetos
  Storage, 1 `versiones_motor`). Se restringió también el INSERT de `videos` (aprobado por Valentín).
- **(b)–(e) HECHOS, aplicados y pusheados:** (b) `20261007000000_reintento_fallido.sql`, aplicada por Valentín; (c)
  `app/reintento.py`, `routers/analisis.py`, `procesar_video.py` (escribe `modo_captura_intentado`, reemplaza el
  reporte previo, marca `error_inesperado`), `config.get_max_intentos` (`KINETIQ_MAX_INTENTOS`, 3 por defecto); (d)
  `tests/unit/test_reintento.py`, `test_api_analisis.py` ampliado, `tests/integration/test_reintento_supabase.py` y
  un reporte previo sembrado en `test_procesar_video_e2e.py`; (e) especificación de frontend §5. Verificado:
  suite rápida 284 passed; `pytest -m requiere_supabase` **77 passed** (8 min 42 s), sin restos. El trigger cubre
  también `atleta_id` (aprobado por Valentín). **Frente del servidor cerrado.**
- **Decisión 023 registrada:** instancia de Render. Free y Starter descartados para las pruebas con usuarios;
  **Standard (1 CPU, 2 GB, USD 25/mes) solo durante pruebas y defensa, cambio hacia el 20/10**, después vuelve a
  Free; `render.yaml` se actualiza en el mismo paso del cambio, no antes. Corregido en la 017 el error "Standard =
  2 vCPU". Resuelve el pendiente "criterio de instancia" que figuraba acá.
- **Siguiente:** plan de punta a punta en `docs/plan-mvp-punta-a-punta.md` (propuesta, a aprobar por Valentín).
- **PENDIENTE (anotado a pedido de Valentín): procedimiento de respaldo manual de la base antes de las pruebas
  con usuarios.** Supabase se queda en el plan Free (el keep-alive de la decisión 021 resuelve la pausa; el límite
  de 50 MB por archivo coincide con la decisión 016), y **Free no incluye respaldos**: un error propio (migración
  mal aplicada, `delete` sin filtro) o una pérdida del proyecto no tendría vuelta atrás. Hay que definir y probar
  UNA restauración real de punta a punta (volcado de las tablas del esquema `public` y de los usuarios de Auth, con
  qué herramienta, dónde se guarda —nunca en el repo, son datos de salud—, cada cuánto y cómo se restaura) antes
  de que entre el primer usuario real (Etapa 9).
- **Decisiones de Valentín:** `error_inesperado` reintentable con tope 3 (parámetro); `parcial` queda fuera
  (anotado como pendiente: reintento desde `parcial` cuando se declaró "normal" un slow-mo); el aviso de "<120 fps"
  del frontend pregunta "¿Lo grabaste en cámara lenta?" antes de subir; trigger en `sesiones` sí.

---

## 2026-10-06 (más tarde) — Keep-alive de Supabase (pendiente 1 de la nota de traspaso)

**Rama:** `main`. Workflow `.github/workflows/supabase-keepalive.yml` (cron cada 3 días + `workflow_dispatch`,
`POST /rest/v1/rpc/keepalive` con la clave anon desde los secrets `SUPABASE_URL` y `SUPABASE_ANON_KEY`; falla si
no hay 2xx) y migración `20261006120000_keepalive_rpc.sql` (aplicada por Valentín; `select public.keepalive()`
devuelve la hora). **Decisión 021:** con `anon` no se podía consultar ninguna tabla (401, comprobado), así que se
aprobó una excepción acotada: una función que solo devuelve `now()`; alternativa descartada, `service_role` como
secret de GitHub.

Verificado: el script exacto del YAML corrido en local contra el proyecto real dio HTTP 200; falla con exit 1 en
secretos vacíos, clave service_role/`sb_secret_`, URL inalcanzable y función inexistente (404). **Falta** la
corrida manual en GitHub (Actions → Supabase keep-alive → Run workflow) y confirmar en el panel, pasado el 13/10,
que el proyecto sigue activo. Quedan los pendientes 2 y 3 de la nota de traspaso.

---

## 2026-10-06 — Trazabilidad del modo y el factor en el reporte · NOTA DE TRASPASO (antes de /clear)

**Rama:** `main`. **Último commit de código: `36a60fd`** ("feat: trazabilidad del modo de captura y del factor de
ralentizacion en el reporte"), pusheado. La nota de traspaso va en el commit siguiente (solo documentación).

### Qué se hizo

- **Control contra historial: DIFERIDO** (decisión 020, propuesta no implementada; requiere datos del
  Criterio 3 para calibrar). Sumada a las limitaciones de la tesis: la detección del error inverso (normal
  declarado como cámara lenta) por techos de plausibilidad es **condicional** — un factor ×2 o golpes lentos
  pueden pasar sin ser detectados.
- **Trazabilidad (R4):** migración `20261006000000` (aplicada y verificada por Valentín): `modo_captura` y
  `factor_ralentizacion`, ambas NOT NULL sin default, en `reportes_biomecanicos`. Se congelan en el reporte
  (la declaración de la sesión es editable después). `procesar_video` las escribe; el e2e las verifica.
  Especificación de frontend: el nivel 3 muestra modo, factor y origen.
- **Prueba contra Render** con marcador propio `requiere_render`: no corre en la suite normal ni con
  `-m requiere_supabase`; solo con `-m requiere_render` (la corrida real pasó en 74 s).
- **Tropiezo propio, ya corregido:** al hacer NOT NULL las columnas nuevas, la primera corrida de
  `requiere_supabase` dio 1 failed + 24 errors: dos pruebas (`test_rls_aislamiento`, `test_cascada_borrado_usuario`)
  insertaban reportes a mano sin esas columnas. Corregidas; el esquema NO se aflojó (sin default a propósito).

### Estado verificado (6/10)

| Suite | Comando | Resultado |
| --- | --- | --- |
| Rápida | `pytest -m "not slow"` | 253 passed |
| Supabase real | `pytest -m requiere_supabase` | 39 passed (~7 min); sin restos: 0 usuarios Auth, 0 objetos Storage, 1 `versiones_motor` |
| Render real | `pytest -m requiere_render` | a demanda, no corre sola |

### PENDIENTES, EN ORDEN

1. **URGENTE — keep-alive de Supabase con GitHub Actions.** El plan gratuito **pausa el proyecto tras 7 días
   sin actividad**; última actividad conocida: hoy 6/10 (pruebas) → vence ~13/10 si no se hace nada. Ya existe
   `.github/workflows/` pero está **vacío**. Idea: workflow con `schedule` (cron cada ~3 días) +
   `workflow_dispatch`, que haga una consulta barata vía PostgREST con la clave guardada como *secret* del repo
   (nunca en el repo). Valentín tiene que cargar los secrets en GitHub (Settings → Secrets); el workflow no
   puede crearlos. Verificar con una corrida manual.
2. **Reintento `fallido → encolado`.** Hoy `POST /analisis/{id}/procesar` pone `encolado` sin validar el estado
   previo. Falta definir las transiciones permitidas, limpiar `videos.motivo_fallo`, y resolver la restricción
   única `reportes_biomecanicos.video_id` (~~hoy `procesar_video` borra el reporte previo~~ — **dato FALSO,
   corregido el 6/10 más tarde:** `procesar_video` NO borra nada; no hay `delete` ni `upsert`, así que un segundo
   análisis falla en el `insert` por la restricción única y marca `fallido` un video que ya tenía reporte válido).
   ~~Valentín quiere ver el diseño y aprobarlo antes de implementar.~~ **Diseño aprobado el 6/10: decisión 022.**
3. **Control contra historial** (decisión 020): diferido; recién con datos del Criterio 3.

### Otros pendientes, sin orden de urgencia

- **Primer paso de la Etapa 5:** alinear `schemas/reporte.py` — `severidad` de 4 estados (decisión 018) y
  los campos de `Trazabilidad` `modo_captura`, `factor_ralentizacion`, `origen_factor` (decisión 020) —
  antes de generar cualquier JSON real. Un solo cambio de contrato, registrado.
- Render Free → Starter por criterio (RSS > 460 MB o corte por suspensión), antes de la Etapa 9.
- Captura del editor de tablas de Supabase (apartado 4.4.6) pendiente.
- Borrado de objetos de Storage al eliminar la cuenta (Etapa 7; la cascada de Postgres no los toca).
- Frontend: campo "¿Cómo lo grabaste?" (especificación §5).
- Redacción del Capítulo 4 y de los Capítulos 6 y 7 (lista en `CLAUDE.md` §5; incluye las limitaciones de la 020).

### Siguiente paso concreto

Pendiente 1 (keep-alive): escribir el workflow y pedirle a Valentín que cargue los secrets; después presentar el
diseño del reintento (pendiente 2) para aprobación; recién después la Etapa 5.

---

## 2026-10-02 (más tarde) — El arreglo del bug de fps no servía para producción: diseño final con declaración del usuario

**Rama:** `main`. Continuación directa de la entrada anterior. Valentín objetó el primer arreglo del bug de
fps (decisión 020) antes de que llegara a aplicarse: buscar el factor en `catalogo.csv` por nombre de archivo
solo funciona con clips del corpus de prueba — un usuario real sube `IMG_4012.MOV` sin fila de catálogo, y
confirmó con sus propios clips que los slow-mo de iPhone declaran 30 fps aunque se hayan capturado a 240, se
recorten donde se recorten. Pidió diseño nuevo, lo presenté, lo aprobó con dos correcciones, e implementé.

**Diseño:** el usuario declara el modo de captura al cargar, una vez por sesión (`sesiones.modo_captura`:
`normal` | `camara_lenta_120` | `camara_lenta_240`). El motor combina esa declaración con el fps real del
contenedor (`_factor_y_motivo`, reemplaza a `_factor_de_catalogo`); si no cierra con un factor entero, el
video queda `fallido` con un código cerrado (`videos.motivo_fallo`), nunca se adivina en silencio.

**Las dos correcciones de Valentín sobre mi primera propuesta, las dos reales, no cosméticas:**

1. **"`normal` nunca falla por fps altos."** Mi primera versión hacía fallar `normal` si el contenedor
   declaraba ≥ 120 fps, razonando que era "una combinación inusual". Valentín: equivocado — `normal` significa
   "sin cámara lenta", no "fps bajo"; hay teléfonos que graban 120+ fps en modo normal, y eso es válido.
   Saqué esa rama de fallo por completo: `normal` usa el fps del contenedor tal cual, sea cual sea, y R1
   decide después si alcanza para el análisis completo.
2. **`motivo_fallo` como código cerrado, no texto libre.** Mi primera versión iba a guardar el texto técnico
   directo en la columna. Valentín: el texto en lenguaje llano para el jugador lo resuelve el frontend (R2);
   el detalle técnico (fps del contenedor, factor calculado) va al log, no a lo que ve el usuario ni a la
   base. `videos.motivo_fallo` queda con un `check` de vocabulario cerrado (hoy un solo código,
   `modo_captura_incompatible`; motivos nuevos se agregan cuando existan de verdad, no se anticipan).

**Esquema (migración `20261002000000_modo_captura_y_trazabilidad_escala.sql`, nueva, no toca las ya
aplicadas — no aplicada todavía, queda para que Valentín la corra):**
- `sesiones.modo_captura` (`not null`, sin default — fuerza a declarar).
- `videos.motivo_fallo` (código cerrado).
- `reportes_biomecanicos.escala_temporal_conocida` + `.origen_factor`: el contrato JSON congelado
  (`schemas/reporte.py: Trazabilidad.escala_temporal_conocida`) nunca se persistía en la base — se cierra ese
  hueco de trazabilidad (R4) de paso, ya que se estaba tocando la escala temporal por el mismo motivo.

**Pruebas:**
- `tests/unit/test_procesar_video_factor.py` (15 casos, sin red, nuevo): `normal` nunca falla en ningún fps
  probado (23,976 a 480), los factores de cámara lenta dan el entero esperado incluida la normalización
  NTSC, las combinaciones inconsistentes fallan con el código cerrado.
- `tests/integration/test_procesar_video_modo_captura_fallido.py` (nuevo): un clip real de 25 fps del corpus
  público declarado `camara_lenta_240` (240/25 = 9,6, no cierra) deja el video `fallido` de verdad contra
  Supabase real, con `fps_real`/`apto_fase_rapida` en `null` (no se guesea un valor ya demostrado no
  confiable) y sin `reportes_biomecanicos`.
- **No hay en el corpus ningún clip de un solo golpe grabado en modo normal** (todos los recortes de la Fase
  B son cámara lenta) para probar de punta a punta "normal con fps alto → análisis completo" contra un
  archivo real — se prueba con la unidad pura en vez de forzar un archivo que no existe; anotado así en el
  test, no silenciado.
- `test_procesar_video_e2e.py` y `test_api_analisis_e2e.py` actualizados: declaran `camara_lenta_240` (los
  clips reales de la Fase B lo son) en vez de depender del catálogo.
- Las otras dos pruebas que insertan `sesiones` (aislamiento, cascada) actualizadas con `modo_captura:
  'normal'` — no procesan video de verdad, cualquier valor válido alcanza.
- Suite rápida: ver más abajo si terminó antes del commit. Las pruebas que dependen de Supabase no se
  pueden correr todavía — necesitan la columna `sesiones.modo_captura`, que no existe hasta que se aplique
  la migración.

**Especificación de frontend (`docs/ux/especificacion-frontend.md` §5):** campo nuevo "¿Cómo lo grabaste?",
una vez por sesión, sin opción marcada por defecto; nota de que el aviso de "< 120 fps" del navegador usa el
fps crudo del archivo (sin corregir por cámara lenta, eso lo hace el motor) y no debería asustar al usuario
si ya eligió cámara lenta más arriba; y que una combinación que no cierra se muestra como error en lenguaje
llano, nunca procesada adivinando.

**Decisión 020 ampliada** con el diseño final, las dos correcciones de Valentín documentadas explícitamente
(para que quede el razonamiento, no solo el resultado), y la verificación completa.

### Pendiente

1. Valentín aplica `supabase/migrations/20261002000000_modo_captura_y_trazabilidad_escala.sql` desde el
   editor SQL.
2. Con la migración aplicada: correr `pytest -m requiere_supabase` completo (ahora con 2 archivos nuevos) y
   confirmar limpieza, como siempre.

### Siguiente paso concreto

Avisarle a Valentín que la migración está lista; cuando la aplique, correr la suite completa y commitear.

---

## 2026-10-02 — Tarea 4.5.4 cerrada: medición real en Render, bug de fps corregido, Etapa 4.5 completa

**Rama:** `main`. Continuación directa de la entrada anterior (semilla de la API lista, 1/10 noche). Valentín
conectó el repo a Render (plan Free) y corrió el análisis real; esta entrada cubre las seis tareas que pidió
al traer el resultado.

### 1. Números de Render registrados (decisión 017 ampliada)

Free: 414,1 s, RSS pico 480,4 MB, sin cortes por suspensión, sobre el mismo video de prueba. Comparado contra
Docker local (0,5 vCPU simulado): 176–185 s / 426–427 MB. **Decisión de Valentín: Render Free durante el
desarrollo; pasar a Starter antes de las pruebas de usabilidad de la Etapa 9**, con criterio explícito (no
"ya se verá"): memoria pico > 460 MB en cualquier clip real, o cualquier corte por suspensión.

### 2. Investigado el salto de memoria (426→480 MB) — parcialmente explicado, con dato limpio

Con Docker Desktop recuperado (mismo bug del "Inference manager" de sockets huérfanos que ya documentó la
bitácora el 29/9 — mismo arreglo, renombrar las carpetas y desactivar `EnableDockerAI`), medido DENTRO del
contenedor real, sin contaminar con nada más:

- Solo motor (numpy + mediapipe + engine/*, igual que `medir_contenedor.py`): **89,2 MB** tras los imports.
- Motor + FastAPI + uvicorn + supabase (igual que `app.main`, lo que corre en Render): **127,8 MB** tras los
  imports, antes de procesar nada.

**38,6 MB de los ~54 MB de diferencia salen de tener FastAPI/uvicorn/supabase en el mismo proceso que el
motor — confirmado, no una sospecha.** El resto queda sin explicación limpia: una corrida completa dentro de
Docker dio 485,4 MB, pero compitiendo por CPU con el diagnóstico del corpus (tarea 3) corriendo al mismo
tiempo — no es una medición limpia, se dice así en vez de maquillarla. Se aplicó igual una corrección real y
justificada en `app/procesar_video.py`: los bytes del clip descargado quedaban vivos en memoria durante toda
la inferencia (se liberan con un `del` explícito apenas se escribe el archivo temporal) — reduce la
superposición de memoria en principio, no remedida limpia todavía. La medición que importa de verdad es la
próxima vez que Valentín corra esto en Render.

### 3. Frecuencia del brazo no auditable — tabla hecha, y un hallazgo más importante en el camino

`app/diagnostico_brazo_corpus.py` (nuevo, de solo lectura, sobre la pose ya cacheada de los 84 clips
propios de perfil/tres cuartos a 240 fps, sesiones 1 y 2 — mismo método que `medicion_criterio1.py`):

| gesto | encuadre | lado cámara | n | no auditable | oclusión | cálculo | señal plana |
| --- | --- | --- | --- | --- | --- | --- | --- |
| drive | perfil | opuesto al dominante | 12 | 8,3% | 0 | 0 | 1 |
| drive | tres cuartos | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| revés | perfil | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| revés | tres cuartos | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| saque | perfil | opuesto al dominante | 12 | 8,3% | 0 | 1 | 0 |
| saque | tres cuartos | opuesto al dominante | 24 | 4,2% | 0 | 0 | 1 |

**El lado de cámara no discrimina nada: es "opuesto al dominante" en las 84 repeticiones**, porque la
decisión 013 ya fijó "no se graba del lado derecho" como protocolo para toda la Fase B — no hay variación
que medir en este corpus sobre ese eje, no es un error del script.

**Cero casos de oclusión** dentro de la ventana anclada al torso (±300 ms) — la oclusión del brazo que
documentan las decisiones 011/013 existe en el clip completo, pero en la ventana angosta del pico el codo
dominante suele estar justo arriba del umbral de confianza. Solo 3 de 84 golpes (3,6%) no auditables: 2
"señal plana" (hay serie pero ningún pico se destaca) y 1 "velocidad implausible... probable error de
detección" (saque de perfil, rep03) — la única que calza con "problema de cálculo" tal como lo pidió
Valentín, y es un caso aislado, no un patrón. Resultado completo en
`docs/resultados/diagnostico-brazo-corpus.json`.

**Al cruzar este resultado contra lo que procesaba `procesar_video.py` en vivo apareció un bug real y más
serio, no solo el que se estaba buscando** — ver el punto siguiente.

### Bug encontrado y corregido: `procesar_video.py` ignoraba la cámara lenta (decisión 020)

El clip que disparó el aviso "pico de brazo no finito" en las dos pruebas anteriores
(`..._drive_perfil_240_01_rep01.mov`) daba auditable en el diagnóstico del corpus (pose cacheada) pero NaN en
`procesar_video.py` (extracción en vivo). Comparando landmark por landmark: **idénticos, diferencia 0** — no
es un problema de determinismo de MediaPipe. La diferencia real: `fps_efectivos` cacheado = 240,0; en vivo =
30,0. Es una captura Apple en cámara lenta (contenedor declara 30 fps, captura real 240, factor 8, confirmado
en `catalogo.csv`). `procesar_video.py` (escrito en la tarea 4.5.3) tomaba `fps_declarados` directo, con un
comentario ("los clips de la Fase B ya vienen a la frecuencia real") que resultó **falso**, nunca verificado
contra el catálogo. Con el valor sin corregir, toda velocidad salía calculada 8 veces mal — no solo el brazo,
cualquier resultado de ese clip.

**No es un bug del motor** (`engine/sequencing.py` hizo lo correcto con el fps que le dieron); es un bug de
`procesar_video.py`, que no llamaba a la detección de cámara lenta que `engine/ingest.py::evaluar` ya tenía
desde la Etapa 1. Corregido: `_factor_de_catalogo()` busca el factor real en `catalogo.csv` cuando el archivo
tiene fila (todo lo que se prueba hoy); sin catálogo (un upload real futuro, Etapa 8) usa `factor=1.0` sin
inventar nada, y **R1 ahora se aplica de verdad**: por debajo de 120 fps efectivos no se corre la
secuenciación completa, el video queda `parcial` en vez de un resultado inválido presentado como bueno. Las
pruebas de integración tenían el mismo problema (subían el clip con nombre aleatorio, impidiendo la búsqueda
en el catálogo) — corregidas para conservar el nombre real. Verificado: con la corrección, las pruebas de
punta a punta vuelven a pasar y **ya no aparece el aviso de pico no finito** en ese clip. Detalle completo en
la decisión 020.

### 4. Aviso de MediaPipe confirmado también en local

`Using NORM_RECT without IMAGE_DIMENSIONS is only supported for the square ROI` aparece igual corriendo
`medir_contenedor.py` en Windows que en Render — no es un resultado distinto por el entorno, es el
comportamiento normal de MediaPipe con esta configuración.

### 5. Versión del motor — no está desactualizada

Revisadas las cinco etiquetas de etapa cerradas (`v0.1.0-etapa0` … `v0.5.0-etapa4`): el `__version__` del
motor en cada una es siempre un minor menos que la etiqueta (etapa4 → tag `v0.5.0`, motor `0.4.1`) — patrón
consistente en las cinco, no una excepción de la Etapa 4. Ningún commit tocó `engine/` entre el último bump
(`0.4.1`, decisión 010) y el cierre de la Etapa 4 (decisión 015) salvo un comentario sin cambio numérico
(decisión 011). `engine/version.py` ahora documenta el desfasaje a propósito para que no vuelva a generar la
duda.

### 6. Datos de prueba borrados, Docker reparado

Usuario/atleta/sesión/video de prueba de Render borrados (cascada). Docker Desktop, que volvió a chocar con
el bug conocido del "Inference manager", reparado con el mismo procedimiento documentado el 29/9.

**Confirmado en carne propia el límite que ya anotaba la decisión 018:** borrar el usuario no se llevó el
clip de Storage (26 MB, `f16a8b3f-.../00e1efba....mov`) — son dos sistemas distintos, la cascada de Postgres
no toca `storage.objects`. Encontrado al verificar la limpieza final, no asumido; borrado a mano. Sigue
pendiente de la Etapa 7 (el flujo real de "eliminar mi cuenta" tiene que borrar Storage aparte).

### Pendiente

- La medición limpia de RSS en Docker local (sin contención con otro proceso), si hace falta más precisión
  que la medición real de Render — no bloquea nada, Render es la fuente de verdad de todos modos.
- Detección automática de cámara lenta para un upload SIN fila de catálogo: declarado como límite conocido,
  no resuelto, depende del diseño de la pantalla de carga real (Etapa 8).

### Siguiente paso concreto

Commit y push de todo lo de esta entrada. Con eso, **la Etapa 4.5 completa queda cerrada** (4.5.1 a 4.5.5):
siguiente paso del plan es la Etapa 5 (auditoría y reporte) — y lo primero ahí, por pedido explícito de
Valentín en la decisión 018, es resolver la desalineación entre `alertas.severidad` en la base (cuatro
estados de R3) y el `Literal` de tres valores todavía congelado en `reporte.py`, antes de generar cualquier
JSON real.

---

## 2026-10-01 (noche, aún más tarde) — Tarea 4.5.4: semilla de la API lista, falta conectar Render

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.3 cerrada y pusheada, commit `aa8d0ee`).

**Pedido de Valentín:** antes de pagar el plan Starter, probar primero el plan gratuito de Render con datos
reales. Con cuatro condiciones explícitas: endpoint protegido por token (401 sin él, `/health` público
aparte), responde 202 y procesa en segundo plano (para medir de verdad si la suspensión del plan gratis
corta un análisis en curso), ningún secreto en el repo, y que sea la semilla real de la API de la Etapa 6
(estructura `routers/`), no código descartable.

**Hecho — decisión 019, detalle completo ahí:**

- **`backend/app/{main.py, security.py, routers/, workers/}`:** la estructura que la decisión 003 reservó
  para la Etapa 6 desde la Etapa 0 (hasta ahora solo `.gitkeep`), llenada por primera vez. `GET /health`
  (público, estado + versión del motor) y `POST /analisis/{video_id}/procesar` (protegido por
  `X-Kinetiq-Token` contra `KINETIQ_API_TOKEN`, `secrets.compare_digest`; 202 inmediato,
  `BackgroundTasks` de FastAPI llama a `procesar_video` de la tarea 4.5.3 — decisión de MVP del apartado
  4.4.2, sin cola externa). `backend/app/schemas/api.py` con los esquemas Pydantic de entrada/salida.
- **`render.yaml`** en la raíz: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `KINETIQ_API_TOKEN` con
  `sync: false` — Render los pide al aplicar el blueprint, no quedan en el repo.
- **`backend/Dockerfile`:** `CMD` pasa de `["bash"]` (abierto desde la 4.5.3) a
  `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` — el comando de producción real.
- **`app/procesar_video.py`** ahora mide tiempo total y RSS pico desde adentro del proceso (mismo método que
  `medir_contenedor.py`, decisión 017) y lo imprime en el log — para leer los números reales del log de
  Render directamente, sin depender de una lectura aparte del panel de métricas.
- **8 pruebas nuevas:** `tests/unit/test_api_salud.py` y `test_api_analisis.py` (rápidas, con un cliente de
  Supabase falso y el worker de fondo espiado — sin red: 401 sin token, 401 con token incorrecto, 404 si no
  existe el video, 202 si todo está bien, 500 si el servidor no tiene el token configurado) y
  `tests/integration/test_api_analisis_e2e.py` (dispara un análisis real a través de la API, contra Supabase
  real, con inferencia de MediaPipe completa — confirma que el cableado nuevo funciona con el stack real,
  no solo con falsos).
- **Suite completa confirmada en verde** tras los cambios: 238 pasan en la rápida, 37 en
  `pytest -m requiere_supabase` (después, 1 más al re-correr solo la de 4.5.3 tras agregar la instrumentación
  de tiempo/memoria). Limpieza confirmada de nuevo: 0 usuarios, 0 objetos, una sola fila real de
  `versiones_motor`.
- **No verificado en Docker local:** Docker Desktop no estaba corriendo en esta sesión; no se insistió en
  levantarlo porque el propio build de Render es la verificación real (y reporta cualquier error del
  `Dockerfile` en su log), no hace falta duplicarla en local.

### Pendiente — lo que le toca a Valentín

1. Generar `KINETIQ_API_TOKEN` (comando en la decisión 019).
2. Conectar el repo a Render con `render.yaml` (plan Free).
3. Cargar a mano, en el panel → Environment del servicio: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
   `KINETIQ_API_TOKEN`.
4. Probar `GET /health` y disparar un análisis real con `POST /analisis/<video_id>/procesar`.
5. Leer el log del servicio para tiempo/RSS pico y observar si la suspensión por inactividad corta un
   análisis en curso. Con esos números: Free alcanza, o se pasa a Starter (actualiza `render.yaml` y la
   decisión 017).

### Siguiente paso concreto

Commit y push de 4.5.4. Pasos exactos de conexión a Render, para Valentín, en el mensaje de cierre de esta
tarea (no se repiten acá para no desincronizarse si cambian).

---

## 2026-10-01 (noche, más tarde) — Tarea 4.5.3: el contenedor habla con Storage y la base

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.2 cerrada y pusheada, commit `e1c2604`).

**Hecho:**

- **`backend/app/procesar_video.py`** (nuevo, `python -m app.procesar_video <video_id>`): baja un video de
  Storage por su `video_id`, resuelve el lado dominante (`sesiones` → `atletas.mano_dominante`), corre el
  pipeline existente sin tocarlo (ingesta → pose → E3 → secuenciación) y escribe `reportes_biomecanicos` +
  `metricas` + los campos reales de `videos` (fps, fotogramas, duración, resolución, `apto_fase_rapida`). Es
  el primer código que cierra el círculo completo de la arquitectura del apartado 4.5 (Storage → motor →
  base) con datos reales. **No es la Etapa 5:** no calcula alertas ni el puntaje de sesión a propósito, esos
  módulos no existen todavía.
- **`versiones_motor` se reutiliza, no se duplica por análisis:** `_version_motor_id()` busca por
  `version_motor` + `backend_pose` antes de insertar — confirmado con la prueba real, sigue habiendo una sola
  fila tras varias corridas.
- **Hallazgo real al correr contra un clip real, no anticipado:** un pico de velocidad del brazo salió `NaN`
  en un clip de perfil (consistente con las limitaciones del brazo en esa vista ya documentadas en las
  decisiones 011/013/015) — `json`/Postgres no aceptan un valor no finito, y al principio tiró la prueba
  abajo (`ValueError: Out of range float values are not JSON compliant`). Corregido: un pico no finito se
  trata igual que un pico ausente (se omite la métrica, con aviso en el log), no se escribe un dato inventado
  — mismo principio R3 aplicado a un caso que no estaba cubierto todavía.
- **`tests/integration/test_procesar_video_e2e.py`:** sube un clip real de la Fase B, registra la
  sesión/atleta/video que le correspondería, corre `procesar_video` de verdad (inferencia de MediaPipe
  completa, no simulada) y confirma el reporte, las métricas y los campos de `videos`. Limpia usuario de
  prueba y objeto de Storage al terminar; **no borra la fila de `versiones_motor`** a propósito — es un dato
  real, no sintético (se reutiliza entre corridas de prueba y reales por igual).
- **36 pruebas en verde** con `pytest -m requiere_supabase` (la de este archivo tarda ~100 s: es inferencia
  real de MediaPipe, no una medición simulada). Limpieza confirmada de nuevo con `list_users()` y
  `storage.from_("videos").list()` en 0, y una sola fila de `versiones_motor` (la real, no una de prueba).

### Pendiente

**No verificado todavía dentro de un contenedor Docker real** — Docker Desktop no estaba corriendo en esta
sesión y no se insistió en levantarlo, porque la tarea 4.5.4 (despliegue real en Render) de todos modos
necesita correr esto dentro de un contenedor de verdad para desplegarlo; no tiene sentido duplicar ese paso
acá. Si al llegar a 4.5.4 conviene primero una prueba en Docker local antes del despliegue en la nube, se
decide ahí, no se da por hecho ahora.

### Siguiente paso concreto

Commit y push de 4.5.3, y arrancar la tarea 4.5.4 (desplegar el contenedor en Render Starter, correrlo de
punta a punta contra el proyecto real, y medir el plan gratuito como pidió Valentín antes de pagar nada).

---

## 2026-10-01 (noche) — Tarea 4.5.2: bucket de Storage, cerrada

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.1 cerrada y pusheada, commit `030cd84`).

**Hecho:**

- **`supabase/migrations/20261001090300_bucket_videos.sql`** (aplicada por Valentín desde el editor SQL):
  bucket privado `videos`, con `file_size_limit` (52428800 bytes = 50 MB, decisión 016) y
  `allowed_mime_types` (`video/mp4`, `video/quicktime`) — un segundo cerco del lado del servidor, no solo la
  validación del navegador de la especificación de frontend §5. RLS de `storage.objects` con la misma
  convención de ruta `<usuario_id>/...` que ya usan las tablas de `public/`.
- **Tres archivos de prueba nuevos**, los dos últimos a pedido explícito de Valentín:
  - `tests/integration/test_storage_bucket.py`: sube un clip real de la Fase B (lo resuelve solo vía
    `KINETIQ_DATA_DIR`, cualquier recorte de una repetición sirve) y confirma la descarga byte a byte, tanto
    con `service_role` como por URL firmada sin ninguna credencial — lo que haría el frontend.
  - Sumado al mismo archivo: rechazo del servidor para un archivo de 50 MB + 1 byte y para un tipo no
    permitido (`text/plain`) — confirma que `file_size_limit`/`allowed_mime_types` del bucket se aplican de
    verdad, no solo están declarados.
  - `tests/integration/test_storage_aislamiento.py`: mismo principio RNF-07 de `test_rls_aislamiento.py`
    (Etapa 4.5.1) aplicado a objetos en vez de a filas — un usuario no puede leer ni subir archivos en la
    carpeta de otro, y un cliente sin sesión no lee nada.
- **Hallazgo distinto al de la 4.5.1:** acá `service_role` sí tuvo acceso completo a Storage sin necesitar un
  `GRANT` aparte — confirmado corriendo la prueba real, no asumido. La Storage API de Supabase es un servicio
  separado de PostgREST (no pasa por los `GRANT` de tabla que hubo que agregar en 4.5.1 para `public/`), así
  que la lección de la decisión 018 (RLS y privilegios de tabla son capas independientes) no se repite acá de
  la misma forma — documentado en la propia migración para que quede donde se vuelve a leer.
- **Limpieza confirmada, no asumida** (pedido explícito de Valentín): `auth.admin.list_users()` en 0 y
  `storage.from_("videos").list()` en 0 después de la corrida completa.
- **35 pruebas en verde** con `pytest -m requiere_supabase` contra el proyecto real (las 28 de la 4.5.1 más
  las 7 nuevas de Storage).

### Pendiente

Nada bloqueante para 4.5.2. Sigue abierta la captura del editor de tablas del apartado 4.4.6 (heredada de la
4.5.1, no bloquea).

### Siguiente paso concreto

Commit y push de 4.5.2, y arrancar la tarea 4.5.3 (completar el contenedor: que descargue el clip de Storage
y escriba el resultado mínimo en la base — ya tiene la medición de tiempo/memoria hecha desde el 29/9, ahora
existen el esquema y el bucket que le faltaban).

---

## 2026-10-01 (tarde) — Esquema de datos rediseñado (decisión 018) y migraciones escritas

**Rama:** `main`. Continuación de la tarea 4.5.1 desde el checkpoint de esta misma mañana.

**Lo pedido por Valentín al retomar:** antes de escribir las migraciones, revisar que el esquema del apartado
4.4.6 contemplara lo que ya muestra `docs/ux/especificacion-frontend.md` §9 (sesión como grupo de videos, rol
y vista por defecto del usuario, reporte a nivel de sesión con puntaje) — para no tener que rehacer las
migraciones en la Etapa 5. Presentar el esquema propuesto y esperar el OK antes de aplicarlo.

**Hecho:**

- **Decisión 018:** esquema de nueve tablas, no siete. Se agregan `sesiones` (agrupa videos del mismo
  atleta/gesto/encuadre/lado de cámara) y `reportes_sesion` (puntaje, componentes, observaciones agregadas);
  se modifican `usuarios` (`vista_por_defecto`) y `videos` (`sesion_id`, pierde `gesto`/`atleta_id`, gana
  rutas de miniatura y de los tres fotogramas clave). Tres puntos de diseño confirmados por Valentín, cada
  uno con su razón documentada en la decisión:
  1. `estado_agregado` de la sesión es una vista (`sesiones_resumen`), no una columna — evita un trigger de
     sincronización que el volumen actual no justifica.
  2. `alertas.severidad` usa los cuatro estados de R3 (`correcto`/`desvio_leve`/`alerta_de_carga`/
     `no_auditable`), no los tres que trae congelados `reporte.py` desde la Etapa 0. **Desalineación
     conocida entre la base y el contrato del motor, dejada a propósito**: Valentín pidió que sea
     explícitamente **lo primero que se resuelve al arrancar la Etapa 5**, antes de generar cualquier JSON
     real — no se toca `reporte.py` ahora.
  3. RLS completo en las nueve tablas ahora (no solo una de prueba, aunque el plan lo permitía diferir a la
     Etapa 7), con una prueba automática de aislamiento pedida por Valentín (verifica RNF-07: un usuario no
     lee/modifica/borra datos de otro, y un cliente sin sesión no lee nada).
  - Además, a pedido de Valentín: el puntaje total de `reportes_sesion` sale del jsonb y queda en columnas
    tipadas (`puntaje`, `estado_puntaje`, `version_formula`) — la pantalla de Evolución lo consulta a
    través de varias sesiones, y la versión de la fórmula es trazabilidad (R4). `componentes` y
    `observaciones` siguen en jsonb: su forma recién se congela en una decisión de la Etapa 5.
- **Migraciones escritas, no aplicadas todavía:** `supabase/migrations/20261001090000_esquema_inicial.sql`
  (extensión, nueve tablas, restricciones, índices, la vista `sesiones_resumen` con
  `security_invoker = true` — sin eso, una vista ignora la RLS de quien consulta) y
  `supabase/migrations/20261001090100_rls_policies.sql` (RLS + políticas + `GRANT` explícito a
  `authenticated` por tabla, nunca a `anon`). *(Corrección más abajo: lo que decía acá sobre
  `service_role` resultó estar mal — sí necesita su propio GRANT.)*
- **Prueba de aislamiento:** `tests/integration/test_rls_aislamiento.py`. Crea dos usuarios de prueba y datos
  de ejemplo del usuario A contra el proyecto Supabase real (vía `service_role`), verifica que el usuario B y
  un cliente sin sesión no pueden leer/modificar/borrar nada ajeno (incluida la vista `sesiones_resumen`, que
  es justo donde se notaría si `security_invoker` se hubiera olvidado), y limpia todo al terminar. Se salta
  sin `SUPABASE_URL`/`SUPABASE_ANON_KEY`/`SUPABASE_SERVICE_ROLE_KEY`. Agregado `supabase==2.31.0` a
  `backend/requirements.txt` (lo va a necesitar también el contenedor en la tarea 4.5.3) y helpers
  `get_supabase_*()` en `backend/app/config.py`, mismo patrón que `get_data_dir()`.
- **`backend/.env.example`:** se agrega `SUPABASE_ANON_KEY` (antes decía "no hace falta hasta la Etapa 6-8";
  hace falta ahora porque la prueba de aislamiento se autentica como los usuarios de prueba). No es secreta,
  pero sigue sin versionarse.
- **Render, plan gratuito — verificado contra la documentación oficial (no folletos), a pedido de Valentín:**
  misma RAM que Starter (512 MB), pero **0,1 vCPU contra 0,5 de Starter** (5 veces menos) y **el tipo de
  servicio "Background Worker" no existe en el plan gratuito** (solo Web Service, Postgres, Key Value,
  estático). Para probarlo gratis, el contenedor se va a tener que desplegar como Web Service (responde a
  HTTP), no como worker. Con la CPU 5 veces menor, es esperable que el mismo clip de la decisión 017 tarde
  bastante más que los 176–185 s medidos a 0,5 vCPU — posiblemente cerca o por encima de los 10 minutos que
  Valentín marcó como aceptable, pero **no se proyectó, queda para medir de verdad en la tarea 4.5.4**, con el
  mismo clip, cuando se despliegue. Fuentes: render.com/docs/free, render.com/docs/compute-plans,
  render.com/docs/background-workers.

**Tres ajustes de Valentín al esquema, mismo día, antes de aplicar nada** (migraciones editadas directamente,
no aplicadas todavía — no hay regla de "nunca editar" que violar):

1. **`estado_puntaje` reemplaza a `puntaje_auditable`.** Un booleano no distinguía "no auditable" de "Desde tu
   2.ª sesión de este golpe" (sin referencia previa), y la especificación de frontend §7 los muestra distinto.
   Ahora `estado_puntaje check in ('calculado', 'no_auditable', 'sin_referencia')`, `not null` sin default;
   `puntaje` no nulo solo si `estado_puntaje = 'calculado'`.
2. **Borrado en cascada: confirmado, no corregido.** Las FK ya estaban bien encadenadas desde
   `auth.users` hasta las siete tablas de datos de usuario; lo que faltaba era demostrarlo. Prueba nueva:
   `tests/integration/test_cascada_borrado_usuario.py`. Anotado lo que la cascada NO hace: no borra los
   archivos en Storage (son `storage.objects`, no filas de estas tablas) — pendiente de la Etapa 7.
3. **Trigger de alta de usuario.** `public.manejar_alta_usuario()` + trigger `al_registrarse` sobre
   `auth.users` (`after insert`): crea la fila de `usuarios` sola al registrarse, `rol` desde los metadatos
   del registro o `'jugador'` por defecto. Un rol inválido en los metadatos hace fallar el alta completa (la
   restricción CHECK corre en la misma transacción) — comportamiento buscado, no un bug. Prueba nueva:
   `tests/integration/test_trigger_alta_usuario.py`.

Con el trigger de alta, la prueba de aislamiento ya no inserta la fila de `usuarios` a mano: la crea el
trigger. Decisión 018 actualizada con los tres ajustes.

**Render:** confirmado por Valentín — se mide una sola vez en la tarea 4.5.4, con el mismo clip de la
decisión 017; si no entra en el plan gratis (10 minutos o suspensión que corta un análisis), se pasa directo
a Starter sin iterar buscando que entre gratis.

### Aplicación real contra Supabase (mismo día, más tarde) — falló una vez, dos hallazgos reales

Valentín aplicó las dos migraciones desde el editor SQL y agregó `SUPABASE_ANON_KEY`. Al instalar las
dependencias nuevas en el venv hizo falta subir `pydantic` de `2.10.3` a `2.11.7` (piso que exige
`realtime`, dependencia de `supabase==2.31.0`; no se tocó nada más, la suite completa se re-corrió para
confirmarlo — sigue en verde, 232 en verde).

**`pytest -m requiere_supabase` falló la primera vez**, con `permission denied for table usuarios` sobre
`service_role`. El comentario de `20261001090100_rls_policies.sql` ("service_role no necesita nada de
esto, ya tiene BYPASSRLS") estaba mal: `BYPASSRLS` exime de las políticas de fila, pero el `GRANT` de tabla
es una capa de permisos de Postgres **aparte**, y hace falta igual. Con "exponer automáticamente"
desactivado y las tablas creadas por SQL crudo (no desde el panel), Supabase no se lo dio solo a
`service_role` — **la misma razón por la que `authenticated` ya necesitaba `GRANT` explícito, aplicada
también al rol que no tiene RLS.** Corregido con una migración nueva (las dos primeras ya estaban
aplicadas, no se editan): `supabase/migrations/20261001090200_grants_service_role.sql`. Comentario de la
migración de RLS corregido a pedido de Valentín, para que la lección quede donde se vuelve a leer.

**Esa primera corrida fallida dejó 3 usuarios de Auth de prueba sin borrar** (`kinetiq-rls-a-*`,
`kinetiq-rls-b-*`, `kinetiq-cascada-*`) — confirmado con `auth.admin.list_users()`, a pedido explícito de
Valentín de verificar que las pruebas no dejaran cuentas sueltas. Causa: el `try/finally` que borra el
usuario de prueba envolvía solo una parte del cuerpo de la prueba; cuando el insert siguiente fallaba por
el permiso faltante, la excepción saltaba por encima del borrado sin ejecutarlo. Se borraron las 3 cuentas a
mano y se corrigió la causa en `test_rls_aislamiento.py` y `test_cascada_borrado_usuario.py`: el
`try/finally` ahora envuelve todo lo que pasa después de crear los usuarios de Auth, no solo la parte que se
esperaba que fallara (`test_trigger_alta_usuario.py` ya estaba bien escrito desde el principio). Con la
corrección: 28 pruebas en verde, `list_users()` en 0 antes y después — limpieza confirmada.

**Decisión 018 ampliada** con esta sección (la lección para tablas futuras: RLS y privilegios de tabla son
dos sistemas independientes, hay que otorgar los dos siempre).

### Pendiente

Captura del editor de tablas de Supabase con el esquema aplicado (pendiente del apartado 4.4.6; no bloquea
seguir). **Tarea 4.5.1 cerrada.**

### Siguiente paso concreto

Commit y push de todo lo de 4.5.1, y arrancar la tarea 4.5.2 (bucket de Storage).

---

## 2026-10-01 — Checkpoint de la Etapa 4.5 antes de limpiar contexto

**Rama:** `main`. Punto de situación exacto para retomar, sin trabajo nuevo esta entrada (pedido explícito
de Valentín: solo documentar y commitear).

### Qué está HECHO de la Etapa 4.5

- **Decisión 016 (tentativa):** el MVP parte de un video por golpe, hasta 50 MB; la pantalla de carga
  rechaza archivos más grandes pidiendo recortar. Subida por partes queda fuera del MVP. Protocolo de
  grabación actualizado. Se confirma o se revierte recién probando el flujo completo con clips reales — no
  antes.
- **Decisión 017:** proveedor y plan de contenedor del motor decididos con datos reales, no con folletos:
  **Render Starter, USD 7/mes** (512 MB, 0,5 vCPU) procesa un clip real de una repetición en 176–185 s sin
  caerse (426–427 MB de pico, 3 corridas). No se paga el plan de USD 25.
- **`model_complexity` queda en `2` hasta nuevo aviso** (instrucción explícita de Valentín, 1/10/2026). El
  hallazgo de que `complexity=1` corta tiempo y memoria a la mitad en el mismo plan de 7 dólares sigue
  anotado en la decisión 017 como candidato, **no aplicado**: cambiarlo exige repetir el Criterio 2
  (se midió con `complexity=2`) y eso no se hace por iniciativa propia.
- **Dockerfile + `app/medir_contenedor.py`** (`backend/`): corren el pipeline completo dentro de un
  contenedor Linux real y miden tiempo/RSS por etapa, con el modelo de MediaPipe precalentado en el build.
  Soportan `--model-complexity` y `--reducir-resolucion` para comparar, no para cambiar el default.
- **Docker Desktop**, que no arrancaba (bug del "Inference manager"/IA integrada con sockets huérfanos de un
  apagado anterior sucio), quedó resuelto: carpetas renombradas, `EnableDockerAI` desactivado. Documentado
  por si vuelve a pasar tras otro apagado sucio.
- **Supabase:** proyecto creado por Valentín (São Paulo, sin integración GitHub, Data API activa, "exponer
  tablas nuevas automáticamente" desactivado, RLS automático activado). `backend/.env.example` documenta
  `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`; `.env` sigue ignorado por git.
- **`docs/ux/`** agregado (especificación del frontend + maquetas: HTML y capturas de Biblioteca, Cargar,
  Evolución, Perfil, Procesando, Registro, Reporte en sus variantes). **Contenido de Valentín, commiteado sin
  que Claude lo modifique.**

### Qué FALTA de la Etapa 4.5 (en orden)

1. **4.5.1 — Migraciones SQL.** No empezadas. Esquema del apartado 4.4.6: siete tablas, restricciones,
   políticas RLS. Con "exponer automáticamente" desactivado en Supabase, cada tabla nueva va a necesitar
   `GRANT` explícitos además de sus políticas — tenerlo presente al escribirlas.
2. **4.5.2 — Bucket de Storage.** No empezado.
3. **4.5.3 — Completar el contenedor.** Hoy corre sobre un archivo montado a mano; falta que descargue el
   clip de Storage y escriba el resultado mínimo en la base (espera a 4.5.1 y 4.5.2).
4. **4.5.4 — Despliegue real en Render Starter.** Hoy la medición es con Docker local; falta desplegarlo de
   punta a punta contra el proyecto Supabase real.
5. Recién con eso cerrada, el criterio de aceptación completo de la Etapa 4.5 y pasar a la Etapa 5.

### Siguiente paso concreto

Retomar por la tarea 4.5.1 (migraciones SQL del esquema del apartado 4.4.6), con los `GRANT` explícitos que
pide la configuración de Supabase ya creada.

---

## 2026-09-29 (tarde) — Etapa 4.5 en marcha: medición real en contenedor, decisión 016 y 017

**Rama:** `main`. Continuación de la entrada de esta misma fecha (cierre de la Etapa 4).

**Correcciones a lo ya escrito hoy** (Valentín):
- La decisión 015 decía que el contrato necesitaba "un tercer estado" para "auditable pero no ordenable" —
  **mal formulado**. "No ordenable" **no es un quinto estado de R3** (que se queda en sus cuatro: correcto,
  desvío leve, alerta de carga, no auditable): es un **motivo** dentro de la observación de secuenciación,
  mostrado en gris con una explicación, igual que los demás motivos que ya usa el motor. Corregido en la
  decisión 015 y en la entrada anterior de esta bitácora.

**Decisión 016 (tentativa):** para el MVP, se sube un video por golpe, hasta 50 MB; la pantalla de carga
rechaza archivos más grandes pidiendo recortar. Subida por partes queda fuera del MVP. Se confirma o se
revierte probando el flujo completo (subida → procesamiento → reporte) con clips reales — no antes.
Protocolo de grabación actualizado (`docs/protocolo-grabacion.md`, §7) con la indicación de recortar a un
solo golpe.

**Docker Desktop no arrancaba** (bug conocido del "Inference manager" / IA integrada de Docker, sockets
huérfanos de un apagado anterior sucio en `%LOCALAPPDATA%\Docker\run\` y `%LOCALAPPDATA%\docker-secrets-engine\`).
Solucionado: se renombraron ambas carpetas para que Docker las recree limpias y se desactivó
`EnableDockerAI` en `settings-store.json` (la función de IA no la necesita este proyecto). Reproducible si
vuelve a pasar tras un apagado sucio.

**Medición real en contenedor** (`backend/Dockerfile`, `app/medir_contenedor.py`, resultados en
`docs/resultados/e4.5-contenedor-tiempo-memoria.json`, decisión **017**):
- **512 MB/0,5 vCPU (Render Starter, USD 7/mes) alcanza:** procesa un clip real de una repetición en
  176–185 s (3 corridas) sin caerse, 426–427 MB de pico. La lectura inicial de 516 MB sin restricciones
  (sesión de la mañana) era un artefacto de la descarga del modelo en caliente, no reproducible con el
  modelo precalentado en la imagen. **No se paga el plan de USD 25/mes.**
- **Hallazgo colateral, pendiente de decisión:** `model_complexity=1` en vez de `2` (el default del motor)
  corta el tiempo a la mitad (91 s) y la memoria ~100 MB, en el mismo plan de 7 dólares. **No se aplica
  ahora:** la cobertura (100 % en los tres niveles) no discrimina precisión en este clip fácil, y el
  Criterio 2 (decisión 015, "cumple") se midió con `complexity=2` — bajarlo necesitaría repetir esa
  medición. Reducir la resolución del fotograma no aportó nada más sobre `complexity=1`.

**Supabase:** proyecto creado por Valentín (región São Paulo, sin integración GitHub, Data API activada,
"exponer tablas nuevas automáticamente" desactivado, RLS automático activado). Variables nuevas documentadas
en `backend/.env.example` (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`); confirmado que `.env` sigue
ignorado por git. Con "exponer automáticamente" desactivado, cada tabla nueva va a necesitar `GRANT`
explícitos además de sus políticas RLS — anotado para cuando se escriban las migraciones (tarea 4.5.1, no
hecha todavía).

### Pendiente

- **Tarea 4.5.1** (migraciones SQL) y **4.5.2** (bucket de Storage): no empezadas.
- **Tarea 4.5.3:** falta que el contenedor descargue el clip desde Storage y escriba en la base (hoy usa un
  archivo montado localmente).
- **Tarea 4.5.4:** desplegar de verdad en Render Starter (hoy la medición es con Docker local).
- **Valentín:** decidir sobre `model_complexity` (decisión 017) cuando corresponda. El Criterio 2 ya se
  midió (goniometría manual completa, ver la entrada de esta misma fecha más abajo): no está pendiente.

---

## 2026-09-29 — Cierre de la Etapa 4 (decisión 015): sin repliegue, cinco salvedades

**Rama:** `etapa/4-cinematica` → merge a `main`, tag `v0.5.0-etapa4`, push. Con los tres criterios medidos
(Criterio 1: decisión 014; Criterio 3 redefinido con override: decisiones 012/014; Criterio 2: goniometría
manual ciega), Valentín decidió **sin repliegue de arquitectura**: se mantiene `pelvis → torso → brazo`
completo, con cinco salvedades documentadas en la **decisión 015**:

1. Tres cuartos: el par pelvis-torso solo es auditable en revés (6/6); en drive es 0/6 y en saque 9/18 —
   se reportan "no ordenables", no como fallo.
2. Perfil: saque y drive dan el orden repetible pero invertido (sin etiqueta correcto/incorrecto, falta
   fundamento bibliográfico); revés de perfil no llega al umbral de repetibilidad (4/6).
3. Brazo: a lo ya dicho en la decisión 011, se suma que las únicas 2 mediciones ciegas del codo dominante
   dieron 27,2° de error medio (11,9° y 42,5°) — causa no separada entre sistema, medición manual o
   escorzo; trabajo futuro.
4. **Drive de perfil** (no drive de tres cuartos — ver la corrección de atribución de esta misma fecha,
   más abajo): orden estable (Criterio 1, 6/6) pero magnitud e instante NO estables entre sesiones
   (Criterio 3, p = 0,044 y p = 0,050): grupo de menor confianza.
5. Criterio 2 del codo: cumple por la media (12,5°), pero el p95 (36,4°) supera la meta — se informan
   siempre juntos.

**Corrección (mismo día, Valentín):** "no ordenable" **no es un quinto estado** — R3 se queda en sus cuatro.
Es un motivo dentro de la observación de secuenciación, mostrado en gris (no auditable) con una explicación,
igual que los demás motivos que ya usa el motor. Lo que sí queda abierto para la Etapa 5 es distinto: cómo
representar un orden auditable Y ordenable (perfil invertido, salvedad 2) sin veredicto de correcto/incorrecto
por falta de referencia bibliográfica — ver decisión 015, corregida.

**Siguiente paso concreto:** Etapa 5 — Auditoría y reporte, sobre `main` desde la etiqueta `v0.5.0-etapa4`.

---

## 2026-09-26 — Medición formal: Criterio 1, Criterio 3 (métrica i) y paquete ciego del Criterio 2

**Rama:** `etapa/4-cinematica`. Motor `0.4.1`. Diseño y reglas: decisión **014**, vigente desde el commit de
congelamiento `cefadb6` (Criterio 3 con lectura calibrada: `c970bf6`). Cada resultado registra su commit y que
el árbol estaba limpio. **Sesión 2 = medición; sesión 1 = réplica exploratoria.** Resumen legible y reproducible:
`docs/resultados/criterio1-resumen.md` (`python -m app.resumen_criterio1`).

### Criterio 1 (τ = 1 fotograma, primaria; sesión 2)

Dos mediciones separadas (1 = repetibilidad del orden, regla del criterio; 1c = coincidencia con el orden esperado,
aparte y sin umbral). n = 6 por grupo salvo el saque de tres cuartos (18, tres tomas).

| Grupo (sesión 2) | Ordenables / n (1a) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | --- | --- | --- |
| drive · perfil (par) | 6/6 | 1,00 `tp` | 0,00 | **cumple** (repetible pero invertido) |
| saque · perfil (par) | 6/6 | 1,00 `tp` | 0,00 | **cumple** (repetible pero invertido) |
| revés · tres cuartos (par / cadena) | 6/6 | 0,83 `tp` / 0,83 `tpb` | 0,17 / 0,17 | **cumple** (orden invertido) |
| revés · perfil (par) | 4/6 | 0,75 `pt` | 0,75 | no cumple |
| saque · tres cuartos (par / cadena) | 9/18 y 9/18 | 1,00 `pt` / 0,89 `ptb` | 1,00 / 0,89 | no cumple (1a = 0,50) |
| drive · tres cuartos (par / cadena) | **0/6** | — | — | no cumple |

- **Sensibilidad (τ = 2 y 3, declarada de antemano):** solo cumplen el saque y el drive de perfil (par pelvis-torso);
  el revés de tres cuartos deja de cumplir (1a 0,33).
- **Réplica exploratoria (sesión 1, no independiente):** **ningún grupo cumple** con τ = 1 (1a entre 0,33 y 0,67).
  Donde el orden es ordenable, coincide con la sesión 2 (perfil: torso primero; tres cuartos: saque `pt`).
- **Complemento DESCRIPTIVO (no pre-registrado), sesión 2:** el eslabón que limita a la cadena es **pelvis-torso**,
  no el brazo. En tres cuartos |pelvis − torso| tiene mediana de 1,0–2,0 fotogramas (en el drive, los 6 picos caen
  a 0 o ±1 fotograma: no es un artefacto, todos son válidos y auditables), mientras que torso→brazo se separa
  22–28,5 fotogramas (≈ 92–119 ms) con el brazo después en 6/6, 6/6 y 16/17 (la sesión 1: 5/6, 6/6, 6/6).
- **Con n = 6 por grupo** el intervalo de Wilson de "6 de 6" es [0,61–1,00]: "cumple" no establece estadísticamente
  la meta de 0,8. Se informa en el JSON y en el resumen.
- **No se decide nada sobre el punto de decisión de la Etapa 4** (tabla del plan: Criterio 1 falla → replegarse a
  la fase de preparación). Lo que se observa es que, a 240 fps, **pelvis y torso en tres cuartos no se separan más
  de 1–2 fotogramas**, un límite de resolución; y que perfil los separa de forma repetible pero invertida.

### Criterio 3, métrica (i): separación cadera-hombro máxima (parcial)

Sesión 1 contra sesión 2, saque de tres cuartos solo con la toma `02` (pedido de Valentín). **5 de 6** combinaciones
con Δ ≤ σ_w (83 %, umbral 75 %); 5 de 6 sin evidencia de diferencia (p de permutación > 0,05). El grupo que no
cumple es el **drive de perfil**: Δ = 6,03° contra σ_w = 3,14° (medianas 30,65° y 24,62°; p = 0,044, **sin corrección
por 6 comparaciones**). El revés de tres cuartos queda al borde (p = 0,074) y es donde el encuadre difiere más
entre sesiones (torso en píxeles 17 %, por debajo del 20 % de señalamiento). **Falta la métrica (ii); no hay
veredicto del Criterio 3.** Corrección previa a medir: con n = 6 por sesión y ningún cambio real la regla
Δ ≤ σ_w da "consistente" solo 75,6 % de las veces (igual al umbral); por eso se agregó el p de permutación (014).

### Criterio 2: paquete ciego listo

`C:\Users\valen\kinetiq-data\fase-b\criterio2\`: 18 recortes sin esqueleto (`ciego/C2-01.png` … `C2-18.png`),
`planilla-manual.csv` (36 mediciones: rodilla y codo), `LEEME.md`; la clave está en `.clave-NO-ABRIR/` y **no se abre
hasta terminar**. Selección con semilla `26092026`, 3 fotogramas por estrato (gesto × encuadre), solo donde el sistema
reporta confianza ≥ 0,6; 5 fotogramas marcados para repetir la medición. Al completar la planilla:
`python -m app.criterio2 analizar <carpeta>`.

### Pendiente (al cierre de esta entrada)

- **Valentín:** goniometría manual del Criterio 2; y confirmar la **definición del "instante de pico"** del
  Criterio 3 (la propuesta es el instante del pico de torso desde el instante de máxima separación cadera-hombro;
  la métrica (ii) queda detrás de un flag y no se mide hasta entonces).
- Veredictos del Criterio 2 y del Criterio 3 completo; punto de decisión de la Etapa 4 (Valentín).

---

## 2026-09-29 — Criterio 3 completo (ambas métricas) y hallazgo de censura en la métrica (ii)

**Rama:** `etapa/4-cinematica`. Motor `0.4.1`, sin cambios de motor. Decisión 014 confirmada por Valentín
(instante de pico = desde la máxima separación cadera-hombro: "la única de las tres opciones que corresponde
a un evento medido, no a una decisión de diseño o de edición") y **queda vigente sin excepciones** desde el
commit `260d03c`. Resultado: `docs/resultados/criterio3.json` (reemplaza a `criterio3-parcial-metrica-i.json`,
que queda como registro histórico de la corrida parcial del 26/9 — mismos números en la métrica (i)).

**Resultado combinado (ambas métricas, 6 grupos × 2 = 12 combinaciones):**

- **Regla original (Δ ≤ σ_w): 10/12 = 83 %** (umbral 75 %).
- **Lectura calibrada (sin evidencia de diferencia, p de permutación > 0,05): 11/12 = 92 %.**
- **El único grupo con señal de diferencia real en las DOS métricas es drive · perfil:** separación
  cadera-hombro Δ = 6,03° (σ_w = 3,14°, p = 0,044) e instante de pico Δ = 156 ms (σ_w = 37 ms, p = 0,050),
  sin corrección por las 6 comparaciones. Sesión 1: mediana −166,7 ms (el pico de torso antecede a la máxima
  separación); sesión 2: mediana −10,4 ms (casi simultáneos).
  **CORRECCIÓN (29/9/2026, Valentín):** el párrafo original decía acá que este era "el mismo grupo que en el
  Criterio 1 tuvo 0 de 6 repeticiones ordenables" — **es un error**. El drive de perfil dio **6 de 6**
  ordenables en el Criterio 1 (cumple, orden `tp` invertido); el que dio 0 de 6 es el **drive de tres
  cuartos**, un grupo distinto. Son dos hallazgos separados, en dos grupos distintos: el drive de perfil
  tiene el orden estable pero la magnitud/instante inestables entre sesiones (este hallazgo, Criterio 3); el
  drive de tres cuartos no llega a ser ordenable en ninguna repetición (Criterio 1). No hay convergencia
  entre ambos criterios sobre un mismo grupo: cada uno señala un problema distinto en un grupo distinto.
- Revés de tres cuartos queda al borde en la métrica (i) (p = 0,074) y es donde el encuadre difiere más entre
  sesiones (torso en píxeles, 17 %, señalado pero bajo el 20 %).

**Hallazgo metodológico, encontrado ANTES de aceptar el resultado, no buscado a propósito:** la máxima
separación cadera-hombro se busca dentro de la misma ventana de ±300 ms de todo lo demás. Se agregó un
diagnóstico de censura (`max_sep_dist_borde_ms`, umbral `CERCA_DEL_BORDE_MS = 50`, commit `699778d`, antes de
volver a correr la medición) que muestra:

| grupo | en el borde exacto (de 12) | cerca del borde (< 50 ms) |
| --- | --- | --- |
| revés · perfil | **5** | **9** |
| revés · tres cuartos | 0 | 4 |
| resto (4 grupos) | 0 | 0–1 |

**La métrica (ii) del revés de perfil no es confiable:** en 9 de 12 repeticiones el "máximo" encontrado está
pegado al borde de la ventana, así que el verdadero instante de máxima separación probablemente cae fuera de
ella. Que ese grupo saliera "consistente" (Δ = 6,25 ms, p = 0,868) podía ser solo el artefacto de que las dos
sesiones chocan contra el mismo límite, no evidencia real de consistencia. **No se ensanchó la ventana**
(afectaría también la métrica (i), ya aceptada, y el Criterio 1, ya medido y commiteado): queda como
limitación a declarar en los Capítulos 6 y 7, no como corrección aplicada.

### Override aplicado y resultado final (mismo día, commit `6773ffd`)

Decisión de Valentín: revés de perfil, métrica (ii), se reporta **NO AUDITABLE** (motivo: censura de ventana),
no "consistente" — "reportar Δ=6,25ms/p=0,868 ahí sería presentar un artefacto de censura como dato bueno".
Override manual y puntual (`GRUPOS_NO_AUDITABLES` en `medicion_criterio3.py`), no una regla automática de
umbral; el cálculo bruto queda en el JSON (`bruto_censurado`) para trazabilidad y se excluye de las
combinaciones de cumplimiento. La métrica (i) de ese grupo no se tocó. Candidato de trabajo futuro (no
aplicado): ventana específica por gesto, pre-registrada antes de volver a medir.

**Resultado final del Criterio 3 (11 combinaciones evaluables, no 12):**

- **Regla original (Δ ≤ σ_w): 9/11 = 82 %** (antes 10/12 = 83 %; el grupo excluido contaba como consistente,
  así que numerador y denominador bajan juntos).
- **Lectura calibrada (p de permutación > 0,05): 10/11 = 91 %** (antes 11/12 = 92 %).
- Ambos siguen por encima del umbral de 75 %. El único grupo con señal de diferencia real en las dos métricas
  sigue siendo **drive de perfil**.

**Paquete ciego del Criterio 2 — confirmado sin cambios.** Valentín preguntó si la estratificación incluía
codo derecho (dominante) del revés de tres cuartos, el único caso de cobertura alta durante el golpe
(decisión 013). Se verificó contra los metadatos de la clave (solo `estrato`/`clip`/`lado`, sin abrir los
valores del sistema): **2 de los 3 fotogramas de ese estrato (`C2-10`, `C2-15`) ya usan el codo derecho** por
tener mayor confianza que el izquierdo. No hizo falta regenerar el paquete; Valentín puede medir sobre el que
ya tiene.

**Decisión 013 ampliada:** el revés de tres cuartos (brazo dominante cercano a la cámara, cobertura alta
incluso durante el golpe) se documenta como evidencia más fuerte a favor de la hipótesis geométrica sobre la
de desenfoque puro — sin ser concluyente con un solo jugador. Una sesión con encuadre invertido queda como
trabajo futuro candidato, explícitamente no programada ahora.

### Criterio 2 medido — cumple en agregado; el codo dominante (n=2) queda sin validar bien

Planilla completa (36 mediciones). `python -m app.criterio2 analizar` →
`docs/resultados/criterio2.json` (commit del paquete: `cefadb6`).

| articulación | n | media | mediana | p95 | sesgo | veredicto (< 20,6°) |
| --- | --- | --- | --- | --- | --- | --- |
| rodilla | 18 | 8,5° | 5,9° | 19,2° | −1,5° | **cumple** |
| codo | 18 | 12,5° | 10,5° | 36,4° | +2,1° | **cumple** |

Error intra-observador (5 fotogramas repetidos, 10 mediciones): 4,1°.

**Hallazgo al abrir la clave (Claude, no pedido por Valentín):** el codo agregado "cumple" está dominado por
16 mediciones del lado **no dominante** (media 10,7°). Las únicas **2 mediciones del codo dominante**
(las que decisión 013 identificó como el único caso de cobertura alta durante el golpe: `C2-10` y `C2-15`,
ambas revés · tres cuartos) dan **27,2° de media (11,9° y 42,5°)** — el 42,5° es el error máximo de todo el
conjunto. Valentín comentó en la planilla, sobre `C2-10`, dificultad para medir "por posición del brazo (otro
frame estaría mejor tal vez para codo derecho)", pese a calificar la imagen como nítida (calidad 1): apunta a
escorzo (el codo gira hacia/desde la cámara) más que a desenfoque. Dato adicional, no decisivo: el ángulo 3D
filtrado (secundario, no validado por esta vía) de `C2-10` está más cerca del valor manual (129,8° vs
manual 118,5°, diferencia 11,3°) que el 2D (160,9°, diferencia 42,5°), compatible con que el problema sea
específico de la proyección 2D en esa vista.

**Con n = 2 no se puede concluir nada formal**, pero es una alerta a tener presente: la confianza de MediaPipe
(0,81 y 0,89, ambas por encima del umbral 0,6) mide si el punto se detectó, no si el ángulo derivado es
preciso — "cobertura alta" (decisión 013) no implica "ángulo preciso". El único caso de validación directa
del brazo dominante salió mal en 1 de 2. No se tocó código ni se recalculó nada: se deja documentado tal cual
para que Valentín lo pondere en el punto de decisión.

### Pendiente

- **Valentín toma el punto de decisión de la Etapa 4** con los tres criterios ya medidos (resumen consolidado
  en la conversación de la sesión, no volcado aparte a un documento de decisión: es una decisión de Valentín,
  no de Claude).

---

## 2026-09-26 — Sesión 2 completa, Criterio 3 redefinido y diseño de la medición formal (propuesta)

**Rama:** `etapa/4-cinematica`. Motor `0.4.1` (sin cambios). Sesión 2 catalogada: 48 repeticiones
(saque: 6 de perfil y 18 de tres cuartos en tres tomas `02`/`02b`/`02c`; drive 12; revés 12), 240 fps;
catálogo de 110 clips sin errores.

**Decisiones de Valentín:**
1. **No se graba del lado derecho** (el piloto no se justifica). Razón dada: la evidencia sugiere que el
   límite es el desenfoque durante el golpe y no el lado de la cámara. *Nota de Claude:* la evidencia
   (en reposo el brazo se ve mejor en la sesión 2, la ventana del gesto no mejora) es compatible con
   desenfoque **o** autooclusión y no las separa; y "grabar del lado dominante mejora la cobertura" queda
   **sin probar, no refutada** (el revés de tres cuartos, con el brazo de cara a la cámara, sí se ve
   bien). Va a la decisión 013.
2. **Extraer las 35 poses restantes** de la sesión 2 (en curso al escribir esto) y **documentar la
   cobertura del brazo tal como está, como limitación física conocida** (decisión 013, a escribir con las
   cifras de la sesión 2 completa).
3. **Criterio 3 redefinido, sin esperar una semana** (decisión 012): mide la repetibilidad del método
   aplicado por el mismo jugador en dos sesiones distintas, con variación natural y sin intervención
   deliberada. **Demuestra consistencia del sistema entre tomas del mismo jugador; NO permite afirmar que
   detectaría un cambio real de técnica** (fuera de alcance con este diseño, sin importar los días entre
   sesiones). Consecuencias anotadas en la 012: no restablece el criterio original (la base clínica de
   "comparar consigo mismo" queda sin validación de sensibilidad); el encuadre no es idéntico entre
   sesiones; el espaciado se aparta del plan.

**Hecho:** pose extraída para los **110 clips** (110/110 cachés). Diagnóstico de oclusión con la sesión 2
completa (n = 18 perfil y 30 tres cuartos) y **decisión 013** con la cobertura del brazo dominante por
sesión, encuadre y gesto: cámara del lado no dominante (izquierdo cercano en 74 de 84 clips; saque 36/36 y
drive 24/24); codo dominante con cobertura 0,03–0,53 en la ventana del saque y el drive y 0,87–0,99 en el
revés; en la sesión 2 de tres cuartos el codo se ve bien en reposo (0,79–0,84) pero vuelve a caer en la
ventana (0,30–0,46). Causa (desenfoque o autooclusión) no separada.

**Herramientas:** `--sesion` en `explorar_fase_b` y en los diagnósticos por grupo (`corte-brazo`,
`ventana-brazo`, `fleisig-brazo`), para no mezclar sesiones.

**Sesión 2 = conjunto de medición reservado.** Una tanda automática llegó a ejecutar `explorar_fase_b` sobre
la sesión 2 **sin leer los resultados**; se detuvo el resto y se **descartaron** los archivos generados,
porque la propuesta 014 exige fijar las definiciones antes de mirar órdenes y tiempos de esa sesión. De la
sesión 2 solo se leyeron confianza y cobertura de pose. Se regenera tras confirmar la 014.

**Propuesta, NO vigente:** decisión 014, diseño de la medición formal de los Criterios 1, 2 y 3
(definiciones, umbrales y reglas de cumplimiento a fijar **antes** de mirar la sesión 2; la sesión 1 =
exploratoria, la sesión 2 = medición). Tiene cinco grupos de preguntas para Valentín. **El Criterio 2
requiere goniometría manual sobre fotogramas y no puede hacerla Claude.**

**Siguiente paso:** Valentín confirma o corrige la **decisión 014** (τ del Criterio 1 y reglas de
cumplimiento; qué sesión es la de medición; grupos del Criterio 1; Criterio 2: ángulos, cantidad de
fotogramas y quién mide; Criterio 3: métricas, regla y las tres tomas del saque de tres cuartos). Se
commitea la 014 como vigente (congelamiento, con el hash del motor `0.4.1`) y **recién entonces** se
corren `explorar_fase_b --sesion 2` y los diagnósticos sobre la sesión 2, y la medición formal. El
Criterio 2 espera además la goniometría manual de Valentín.

---

## 2026-09-25 — Diagnóstico de oclusión del lado dominante (sesiones 1 y 2 de la Fase B)

**Rama:** `etapa/4-cinematica`. Sin cambios en el motor. Pedido de Valentín: en ambas sesiones la cámara
quedó del mismo lado y es diestro; ¿oclusión sistemática del brazo dominante? Decidir si hace falta una
tercera sesión con la cámara del otro lado **antes** de extraer pose del resto y medir formalmente.

**Herramienta:** `python -m app.diagnosticos_e3 oclusion-lado` (`docs/resultados/pose-oclusion-lado-dominante.json`;
7 pruebas en `tests/unit/test_oclusion_lado.py`). Solo lee la caché de pose.
**Muestra:** sesión 1 completa (36 clips de perfil y tres cuartos a 240 fps) y de la sesión 2 **solo 13 de 48**
(2 por grupo y 1 por cada toma `02`/`02b`/`02c` del saque de tres cuartos); las otras 35 no tienen pose
(no se extrajeron a propósito). n de la sesión 2 = 6 (perfil) y 7 (tres cuartos).
**Método:** por clip y pareado, confianza media (`visibility`) y cobertura (fracción de fotogramas con
confianza ≥ 0,5, la definición del motor) de hombro, codo, muñeca y cadera del lado dominante (der) contra
el no dominante (izq), en tres tramos: **reposo** (a más de 0,6 s del pico crudo del torso: sin desenfoque
posible), **ventana del gesto** (± 0,3 s) y clip completo. Criterio declarado antes de mirar (juicio de
Claude, ajustable): mediana de Δcobertura ≤ −0,10, Δ < 0 en ≥ 75 % de los clips y p del signo < 0,05.

**Resultados:**
- **La cámara ve el lado izquierdo (no dominante):** es el más cercano en 43 de 49 clips; los 6 restantes son
  todos revés (1 de perfil, 5 de tres cuartos), o sea que ese "lado cercano" está **confundido con el gesto**
  (en el revés el giro del cuerpo expone el brazo derecho).
- **Hombro y cadera: 1,00 en ambos lados en todos los grupos y sesiones.** Ojo: `visibility` satura en 1,0
  para estos puntos; no prueba que estén bien ubicados (no descarta un error de profundidad de la cadera o
  el hombro lejanos en perfil).
- **Codo y muñeca dominantes en reposo (sin desenfoque):** perfil, codo 0,10 (s1) y 0,14 (s2) contra 0,99 del
  izquierdo, cobertura 0,02 y 0,05; muñeca 0,29 y 0,37 contra 0,97–0,98; Δ < 0 en el 100 % de los clips
  → **oclusión geométrica confirmada en perfil, en ambas sesiones** (p = 0,031 con n = 6, el mínimo posible).
  Tres cuartos sesión 1: codo 0,21 (cobertura 0,16), muñeca 0,61 → marcado. Tres cuartos sesión 2 (n = 7):
  codo 0,82, muñeca 0,95 → **no** marcado.
- **En la ventana del gesto** el codo dominante ronda 0,45–0,53 de confianza y 0,46–0,54 de cobertura en todos
  los grupos (no dominante 0,94–0,96 y 1,00); muñeca 0,71–0,81. Con mi criterio no se marca (Δ < 0 en 67–83 %
  de los clips, p 0,02–0,45, porque los revés dejan ver el brazo y diluyen el signo), pero el efecto es grande
  (Δ mediana de cobertura del codo −0,47 a −0,54).
- **Revés de tres cuartos:** brazo dominante bien visible (confianza 0,84–0,89, cobertura 0,97–1,00 en la
  ventana). Explica por qué fue el único grupo con la serie del brazo completa (y por eso ya estaba filtrado
  antes del arreglo de E3, decisión 010).
- **Sesión 2, saque y drive de tres cuartos:** en reposo se ve mucho mejor que en la sesión 1 (0,59–0,92 contra
  0,03–0,27), pero **la ventana del gesto no mejora** (0,27–0,58). Es decir: aun con el brazo visible en reposo,
  durante el golpe el codo se pierde (desenfoque o autooclusión), no solo por la posición de la cámara.

**Lectura (para decidir; no se decidió):** la oclusión geométrica del brazo dominante está confirmada en perfil
y en el saque/drive de tres cuartos de la sesión 1. Pero mover la cámara al lado dominante no garantiza
resolver la cobertura durante el golpe: la mejora de reposo de la sesión 2 no se trasladó a la ventana. El
único caso "brazo que golpea de cara a la cámara" es el revés de tres cuartos (cobertura ~1,0), que es un gesto
más lento que el saque. Recomendación de Claude: **piloto corto** (p. ej. 6 saques y 6 drives de tres cuartos con
la cámara del lado dominante) antes de una tercera sesión completa, comparando la cobertura en la ventana.
**No se extrajeron las otras 35 poses de la sesión 2** a la espera de esa decisión.

**A tener presente:** las dos sesiones son de fechas consecutivas (24 y 25/9), y el plan pide al menos una
semana entre sesiones para el Criterio 3.

---

## 2026-09-25 — Fase B: extracción de pose, ventana anclada y corrección de E3 (motor 0.4.1)

Sesión larga: primera pasada de la Fase B, corrección de E3, y tres correcciones de rumbo de lo
que se había concluido (ver "CORRECCIÓN" y las decisiones 010 y 011).

### Estado al cierre de la sesión

**Rama/motor/tests:** `etapa/4-cinematica`, motor `0.4.1`, `pytest -m "not slow"` → **194 en verde**
(los 5 tests lentos que usan E3 sobre pose real también pasan). Sin merge ni tag de la Etapa 4.

**Decisiones de Valentín en esta sesión:**
1. `recortes/` es la única carpeta de unidades de análisis de la Fase B; el catalogador,
   `extraer_pose` y `analizar` recorren `fase-a/` y `fase-b/` y saltean `originales/`.
2. Arreglo de E3 (series con huecos, decisión 010, motor 0.4.1); se mantiene **un corte de Winter
   por clip** (sin cambio de contrato).
3. Codo vs muñeca: la decisión anatómica se mantiene; la justificación empírica de la 008 queda
   invalidada y es **pendiente de redacción del Capítulo 4**.
4. Referencia de Fleisig del brazo: error conceptual (decisión 011). El techo del brazo no se
   reancló a 1510 °/s; queda 7104 °/s como cota provisional sin respaldo en la literatura.
5. **El orden del brazo en perfil se declara NO CONCLUYENTE; las afirmaciones que dependen del
   brazo se apoyan en tres cuartos.** No se implementó ventana acotada del brazo.
6. El marcador de fase independiente queda como **trabajo futuro** (no implementar ahora).

**Lo medido (E3 0.4.1; 36 repeticiones propias, un jugador, una sesión):**
- Pelvis y torso no se vieron afectados por el defecto de E3 (diferencia 0,0000 °/s); pelvis más
  rápida que el torso en el saque (1,15–1,46×); gradiente saque > drive > revés en ambos encuadres.
- Brazo (orientación del segmento, p99 de ω a k=1): 790–2165 °/s por grupo, caída k1→k8 de 1–10 %.
  No hay referencia de Fleisig equivalente (decisión 011).
- **Por encuadre** (ancla de torso): **torso → balanceo del brazo** con el brazo después en **17 de 18**
  en tres cuartos (estable con el corte entre 6 y 15 Hz —a 20 Hz, 16 de 18— y con la ventana) y en **5 de 16** en perfil (no
  concluyente). **Pelvis vs torso:** perfil con el torso primero en 11 de 15 (saque 3/3, drive 6/6);
  tres cuartos 9 pelvis primero / 7 torso primero, |Δ| ≤ 3 fotogramas en 16 de 18.

**Lo que NO queda establecido:**
- **La cadena completa `pelvis → torso → brazo` no queda establecida en ningún encuadre**; tres
  cuartos sostiene su segunda mitad (torso→brazo). Perfil no sostiene pelvis→torso (lo invierte
  sistemáticamente), contra la formulación inicial; corregido en la decisión 011.
- Etiquetar "correcto/incorrecto" cuando interviene el brazo no tiene fuente (R4).
- Criterio 1 no medido formalmente; exploratoriamente, solo el saque de tres cuartos repite un mismo
  orden completo en 5 de 6.

**Pendientes (todos requieren decisión de Valentín salvo indicación):**
- Redacción: Cap. 3 (tabla 3.3.2.8 y cadena cinética), Cap. 4 (hipótesis I1, Criterio 1, gráfico de
  secuenciación; justificación de hombro→codo), CLAUDE.md §1 y §3, interfaz (R2/R3), y la
  terminología "balanceo del brazo" vs "rotación interna" (lista completa en la decisión 011).
- Propuesta: mapear el orden del brazo en perfil al estado gris "no auditable" (R3), y el orden que
  incluye al brazo como "orden observado" sin juicio de correcto/incorrecto. No implementado.
- Protocolo: recomendar tres cuartos para todo lo que involucre al brazo.
- Umbral de salto imposible en unidades físicas (punto 2); opcional: Winter sobre el tramo continuo
  más largo. Ambos con datos de ajuste y de medición separados.
- 4.7 / 4.8 y el punto de decisión de la Etapa 4; segunda sesión de la Fase B (Criterio 3).
- **Trabajo futuro (NO implementar ahora):** marcador de fase independiente (p. ej. punto más bajo
  de la muñeca como inicio del golpe hacia adelante), validado con fotogramas; depende de la
  cobertura de la muñeca (25–57 % en el saque; baja justo en el impacto).

**Siguiente paso concreto — ETAPA 4 EN PAUSA (indicación de Valentín, 25/9):** no se toca más código
de la Etapa 4 ni se decide nada sobre el **Criterio 1** ni el **punto de decisión** hasta que Valentín
vuelva con material nuevo: la **segunda sesión de la Fase B** (necesaria para el Criterio 3) y más
repeticiones de **tres cuartos**, el encuadre con la señal más clara. Al volver: catalogar
(`python -m app.catalogador`), extraer pose, correr `python -m app.explorar_fase_b` y
`python -m app.diagnosticos_e3` sobre lo nuevo, y recién entonces la medición formal (4.7 / 4.8) con
umbrales congelados y datos de ajuste separados de los de medición. La decisión 011 se deja como está.
Hallazgo a retomar: la inversión sistemática pelvis/torso en perfil (torso primero en 11 de 15).

### Referencia de Fleisig del brazo (2026-09-25, decisión 011)

- Prueba `test_omega_vector_vs_angulo.py` (geometrías de resultado conocido): el vector hombro→codo
  mide el balanceo del brazo (ω real), da **0** ante extensión de codo y **0** ante rotación axial;
  el ángulo de tres puntos ve la extensión y también da 0 ante rotación axial.
- Comparación equivalente (`diagnosticos_e3 fleisig-brazo`, saque, E3 0.4.1): ángulo del codo vs
  1510 °/s = **0,88×** en perfil y **0,50×** en tres cuartos, con baja cobertura (25–57 % de
  fotogramas con los tres puntos). ω del vector = 1315/1379 °/s: 0,56–0,58× de 2368 (referencia
  equivocada) y 0,87–0,91× de 1510 (coincidencia numérica, no comparación equivalente).
- La "subestimación" que veníamos arrastrando desaparece **como argumento** (no había comparación
  válida), y NO se reemplaza por "medido correctamente": no hay referencia equivalente.
- **Techo del brazo:** sin cambios numéricos (7104 °/s), ahora rotulado como cota provisional sin
  respaldo en la literatura. Reanclarlo a 1510 (×3 = 4530) da el mismo resultado práctico en la
  Fase B pero repetiría el error con otro valor; **pendiente de decisión de Valentín**.

**Alcance ampliado (decisión 011):** el "brazo" de `pelvis → torso → brazo` es un proxy de la
**orientación espacial del segmento superior** (balanceo del brazo), no de la rotación interna del
hombro que describe la literatura. Son dos eventos distintos que pueden no coincidir en el tiempo.
Se sostiene "el sistema documenta el orden de los picos de pelvis, torso y balanceo del brazo" y el
Criterio 1 (repetibilidad); NO se sostiene "el orden descripto en la literatura" ni etiquetar
correcto/incorrecto cuando interviene el brazo (R4: sin fuente). Pendiente de decisión y de
redacción: CLAUDE.md §1 y §3, Cap. 3 (3.3.2.8 y cadena cinética), Cap. 4 (I1, Criterio 1, gráfico de
secuenciación), arquitectura, plan (Anexo A), interfaz. Lista completa en la decisión 011.

### Ventana del brazo: barrido del adelanto (2026-09-25) — NO se implementó en el motor

`python -m app.diagnosticos_e3 ventana-brazo` (`docs/resultados/e3-ventana-brazo-fase-b.json`).
Se permite buscar el pico del brazo desde `torso − adelanto` hasta `torso + 300 ms` (adelanto 300,
200, 150, 100, 50, 0 ms) y se mide cuántos picos CAMBIAN respecto de la ventana de ±300 (lo que la
acotación enmascara). Con adelanto 0, "brazo antes que torso" es imposible por construcción.

- **Tres cuartos (saque, drive y revés): la ventana es irrelevante.** El pico del brazo no cambia
  al acotar (0 desplazados de 6 en casi todos los adelantos), y llega después del torso: +110 ms
  (saque), +115–121 (drive), +79 (revés) de mediana.
- **Drive de perfil:** brazo antes del torso en 4/5 con adelanto ≥ 150 ms (mediana −50 ms) y 3/4 a
  100 ms; con adelanto ≤ 50 ms el brazo queda **no auditable** en 5 de 6 (1/6 auditable): no hay un
  pico posterior identificable. Es decir, acotar no "arregla" el drive, lo vuelve no medible. Los
  picos se ubican 50–100 ms antes del torso.
- **Revés de perfil:** con ±300 el brazo va primero en 5/6 (mediana −19 ms), pero 2 de esos picos
  están 200–300 ms antes del torso; con adelanto ≤ 200 la mediana pasa a 0 ms (3/6 antes, los tres con
  −12 a −21 ms, prácticamente simultáneos) y con adelanto 0 los 4 auditables pasan a +165 ms
  (4/4 desplazados). Coherente con que esos 2 picos tempranos sean la preparación.
- **Saque de perfil:** 2/5 con el brazo antes (≥ 100 ms antes); con adelanto ≤ 50 esos 2 se
  desplazan a picos posteriores (dt +67). Confirma la fragilidad de ese grupo (n = 3–5).

**Lectura:** el patrón "brazo antes en perfil, después en tres cuartos" se sostiene con claridad
solo en el **drive de perfil** (y en los tres grupos de tres cuartos como "después"); en el revés
de perfil el brazo es casi simultáneo con el torso salvo dos picos de preparación; el saque de
perfil depende de la ventana. **Ninguna ventana por sí sola discrimina golpe de preparación:**
haría falta un marcador de fase independiente (p. ej. el punto más bajo de la muñeca como inicio del
golpe hacia adelante), validado con fotogramas. Pendiente de decisión de Valentín.

### Corte de Winter para el brazo (2026-09-25)

Pregunta de Valentín: ¿un solo corte por clip sigue siendo válido para el brazo? **No se tocó
código ni contrato** (`trazabilidad.filtro.corte_hz`). Datos: `docs/resultados/e3-corte-brazo-fase-b.json`,
`python -m app.diagnosticos_e3 corte-brazo`.

- **El corte del clip ya lo fija el brazo:** `elegir_corte` toma el MÁXIMO entre los cortes de las
  series de codo y muñeca (ambos lados). No sale de pelvis/torso.
- **Los cortes por articulación son parecidos:** codo 4–11 Hz (casi todos 7–9), muñeca 7–9,
  pelvis 5–9, torso 6–9; el corte del clip es 8–11 (mayoría 8–9). Diferencia por articulación
  ≲ 2 Hz: **no hay evidencia de que el brazo necesite un corte propio.**
- **No es el corte lo que hace ver "bajo" al brazo:** barriendo solo el corte del codo, el p99
  varía entre −2 % y +28 % entre 6 y 10 Hz (más al ir a 20 Hz), y a la vez la caída k1→k8 crece (p. ej. drive
  tres cuartos 10 % → 28 %, revés perfil 4 % → 25 %): más corte mete ruido, no revela movimiento.
- **Debilidades reales de la implementación (no del criterio "un corte por clip"):**
  (a) Winter concatena los valores válidos saltando los huecos: las uniones son discontinuidades;
  usando el tramo continuo más largo el corte del clip cambia en 19 de 36 clips (de −1 a +3 Hz,
  mediana 0, media +0,4);
  (b) el corte de una serie individual es inestable (codo 4 Hz en un clip); el máximo entre ~12
  series lo vuelve conservador; (c) el corte tiene efecto sobre el orden del saque de perfil
  (arriba): conviene registrar la sensibilidad en la trazabilidad.
- Recomendación: **mantener un corte por clip y el contrato**; si se quiere tocar algo, arreglar
  (a) sin cambiar el contrato. No hecho: espera la decisión de Valentín.

### Qué se hizo

- `extraer_pose` y `analizar` recorren `fase-a/` y `fase-b/` (mismas `CARPETAS_EXCLUIDAS` y
  `FASES_POR_DEFECTO` que el catalogador) y saltean `originales/`.
- `analizar` deducía `corpus_publico=True` siempre; ahora sale de la columna `fuente` del
  catálogo (`propio` → sin caveat; sin dato → caveat, el error seguro).
- Extracción de pose de fase-b (~2 min por clip, CPU).

### Primera lectura: saque de perfil (6 repeticiones, 240 fps reales)

Cualitativa, sin umbrales tocados. Ver la tabla completa en la conversación de la sesión.

- **Pelvis-torso:** las 3 repeticiones auditables dan `torso → pelvis` (4, 12 y 13 ms):
  mismo rango invertido que el corpus público. No se estabilizó con condiciones controladas.
- **Brazo (codo):** 4 de 6 bajo el techo (4000–6100 °/s, 1,7–2,6× Fleisig); una en 37 124.
- **Inversiones de z:** 8–28 por clip (público: 16–45 / 3): **no bajaron** con `z` métrica.
- **Pelvis 1000–1400 °/s (2,3–3,2× Fleisig 440)** y ~1,4× más rápida que el torso
  (Fleisig: al revés). Revisado el cálculo: **no hay error** (fórmula y `fps_efectivos`
  correctos; el pico casi no cambia con el paso k=1,2,4,8; ~todo en el plano x–z; curva de
  ángulo suave; caderas bien ubicadas en los fotogramas). No se puede distinguir "gira así"
  de "cadera lejana mal estimada por la oclusión del perfil" sin una medición independiente.

### Comparación entre gestos y encuadres (36 repeticiones, 1 jugador, 1 sesión)

Medianas por grupo (pico p99 de ω sobre el clip completo, `puntos_mundo` filtrados, °/s;
6 clips por grupo; **exploratorio**, umbrales sin tocar). Referencia de Fleisig: **solo saque**.

| grupo | pelvis | torso | pelvis/torso | caída pelvis k=1→8 | inv. z por clip (mediana) | orden pelvis-torso |
| --- | --- | --- | --- | --- | --- | --- |
| saque perfil | 1174 | 791 | 1,46 | 4 % | 14,5 | 3 auditables: 3 invertidas (−4/−12/−13 ms) |
| saque tres cuartos | 975 | 837 | 1,15 | 4 % | 5 | 6 auditables: 4 pelvis primero (0–13 ms), 1 empate 0 ms, 1 invertida (−13 ms) |
| drive perfil | 702 | 628 | 1,12 | 3 % | 9,5 | — |
| drive tres cuartos | 814 | 680 | 1,19 | 3 % | 7,5 | — |
| revés perfil | 324 | 435 | 0,72 | 3 % | 5,5 | — |
| revés tres cuartos | 257 | 507 | 0,46 | 3 % | 5 | — |

- **Sensibilidad al paso (pregunta 3):** la pelvis cae 3–4 % entre k=1 y k=8 en los seis
  grupos: no es un artefacto del saque; es una señal suave en todos los gestos.
- **Hipótesis del salto: resultado mixto, no confirmada.** El revés (sin vuelo) no muestra
  exceso (pelvis 257–324 °/s, pelvis/torso < 1, como en Fleisig). El drive (sin vuelo)
  mantiene pelvis ≥ torso y 700–800 °/s. El orden de gestos saque > drive > revés se repite
  en ambos encuadres; el encuadre mueve la magnitud (±20 %) sin cambiar ese orden.
- **Tres cuartos vs perfil (saque):** mejora el orden auditable (6/6 vs 3/6) y baja las
  inversiones de z (5 vs 14,5). Pero de los 5 "pelvis primero/empate", 3 quedan a ≤ 1
  fotograma (4,17 ms): en el límite de resolución.
- **Segmentación automática:** parte en 2–3 ventanas clips que contienen 1 repetición
  (revés perfil rep02, revés tres cuartos rep04/rep05, etc.). Para el Criterio 1 la unidad
  debe ser el clip (1 repetición), no las ventanas.
- **Drive:** varios clips dan el orden `brazo > torso > pelvis` (invertido); no reproduce la
  cadena que sí dio `drive_lateral_01` del corpus público. Sin analizar aún.
- **Revés tres cuartos, brazo:** ω ~850–980 °/s y casi constante con k (2 % de caída), muy
  distinto del resto (2000–5000 °/s, ~65–80 % de caída). Sospechoso; sin analizar aún.
- Límites: n = 6 por grupo, un jugador, una sesión; detector de vuelo aproximado (tobillos
  en imagen); p99 sobre el clip completo, no sobre la ventana del gesto.

### Segmentación: `clip completo` vs `auto` (2026-09-25, mismo día)

Hipótesis de Valentín: la segmentación automática elegía ventanas parciales y era la causa
común del drive invertido y del brazo anómalo del revés de tres cuartos. Se agregó el modo
explícito **`clip_completo`** (`segmentar`/`secuenciar`, `analizar --clip-completo`; excluyente
con `manual`) y se comparó con el automático (`docs/resultados/e4-fase-b-exploratorio-*.json`).

- **No era la causa.** Drive perfil: el pico del brazo cae 200–500 ms **antes** que los de
  torso y pelvis en las 4 repeticiones auditables, con ventana automática y con clip completo.
  Revés tres cuartos, brazo: los picos son los mismos valores (1001,7 / 917,6 / 855,0 /
  803,7 °/s) en ambos modos; solo cambia el instante (relativo a la ventana).
- **El clip completo tampoco es neutro:** el pico de cada segmento es el máximo global del
  clip y puede ser otro evento. Saque de perfil: brazo primero en 2 de 3 auditables (0 con
  auto); saque tres cuartos: pelvis→torso→brazo correcto 5 → 4 de 6; drive perfil 1 → 0; en el
  revés aparecen desfases pelvis→torso de −842, −142 y +208 ms (picos de eventos distintos).
- **Sí resuelve** el sobre-particionado (7, 7, 8 y 12 ventanas → 6 por grupo): para el
  Criterio 1 la unidad es el clip.
- Conclusión: las dos anomalías siguen abiertas y no son de ventana. La medición del orden
  es sensible a la ventana en ambos sentidos; falta una ventana anclada al gesto (p. ej.
  alrededor del pico de pelvis/torso, o marcas manuales).

### Ventana anclada al gesto (2026-09-25)

Se implementó `secuenciar(..., ancla="torso"|"pelvis", margen_ancla_s=0.3)` (`instante_ancla`,
`ventana_anclada`; `analizar --ancla`; excluyente con `manual` y `clip_completo`): UNA
repetición por clip, ventana centrada en el pico global del segmento ancla ± 300 ms. Si el
ancla no es auditable (tramo excluido o techo de plausibilidad) no se inventa una ventana
(R3). Salidas en `docs/resultados/e4-fase-b-exploratorio-ancla-{torso,pelvis}.json`.

**Sesgo a tener presente:** restringir la búsqueda a la vecindad del tronco excluye por
construcción los picos tempranos del brazo. Por eso cada repetición registra
`brazo_global_fuera_de_ventana`. Y anclar en un segmento no vuelve circular el orden
pelvis→torso solo si se compara contra el otro segmento (el ancla queda en el centro).

- **Las dos anclas coinciden:** torso vs pelvis difieren ≤ 75 ms en 30 de los 33 clips con
  ambas auditables (mediana 8–21 ms por grupo). Excepciones: 142 y 208 ms (revés perfil) y
  842 ms (revés tres cuartos rep05). En saque de perfil solo 3 de 6 clips tienen ambas auditables.
- **Saque tres cuartos (ancla torso):** el brazo llega DESPUÉS del torso en 6/6 (+12 a
  +138 ms) y pelvis→torso→brazo sale en 5/6 (igual que `auto`).
- **Drive de perfil: la inversión PERSISTE.** En las 4 repeticiones con brazo auditable el
  pico del brazo llega 133–288 ms ANTES del torso, con la ventana anclada y con las dos anclas.
  En rep03 y rep06 el máximo dentro de la ventana queda a ≤ 21 ms del borde: el pico real
  está aún más atrás. (Drive tres cuartos: brazo después del torso en 2/2 auditables.)
- **Revés tres cuartos, brazo: la anomalía PERSISTE.** Los picos son idénticos a los del clip
  completo (0 fuera de ventana): 4 de 6 en 800–1000 °/s, casi constantes con k; los otros 2 en
  2590–2830. El brazo queda último en 5/6: lo anómalo es la magnitud, no el orden.
- Criterio de Valentín cumplido: ambas anomalías persisten con la ventana bien anclada, así
  que se tratan como hallazgos a investigar, no como artefactos de ventana.

### CORRECCIÓN (2026-09-25, misma sesión): las "anomalías del brazo" vienen de E3 y de la validación

La serie fotograma a fotograma del codo (drive perfil rep04) y una revisión de `procesar_e3`
**invalidan la lectura anterior** ("ambas anomalías persisten → hallazgos"). Lo que se vio:

- **No es un salto de un fotograma.** Entre 0,196 y 0,242 s (fotogramas 47–58) el codo derecho
  se mueve 5,0 cm/fotograma (mediana; máx. 11,9 cm = 28 m/s), con confianza 0,65–0,98 y `z`
  alternando (0,168 → 0,225 → 0,172). Es una ráfaga de jitter, no un salto ni una inversión.
- **Por qué la validación no lo atrapó:** (1) la confianza está por encima de 0,5; (2) el
  umbral de salto imposible es 0,5 torsos = 25,7 cm/fotograma = **62 m/s** (torso 0,514 m): el
  máximo de todo el clip es 24,4 cm (0,47 torsos) y el de la ráfaga 11,9 cm (0,23); un codo
  real no supera ~10 m/s (≈ 4 cm/fotograma) y 79 de 299 fotogramas válidos lo superan;
  (3) no hay cambio de signo de `z`. El umbral detecta teletransportes, no jitter.
- **Hueco en E3 (`pipeline.py`, "Simplificación"):** toda serie con algún NaN (tramo largo
  excluido, > 5 fotogramas) **se deja SIN filtrar completa**. En rep04 el codo tiene 223 de 368
  fotogramas en NaN (60 %). Resultado: el codo crudo (ruidoso) entra a E4 contra un hombro ya
  filtrado. Sobre las 36 repeticiones: **pelvis 0 % y torso 0 % sin filtrar; hombro/codo
  derecho sin filtrar en 6/6 clips de cinco grupos** y en 2/6 del revés de tres cuartos.
- **Lo que explica todo:** en el revés de tres cuartos, los 4 clips donde el brazo SÍ se filtra
  dan 800–1000 °/s, planos con k (2 % de caída); los 2 sin filtrar dan 2590–2830 °/s y caen
  ~58 %, igual que el resto de los grupos (58–81 %). La "anomalía" era el único grupo bien
  filtrado; lo anómalo son los demás.
- Diagnóstico (interpolando y filtrando el codo a 8 Hz, solo para mirar): en los fotogramas
  47–58 la ω pasa de 4790 a 386 °/s. La cifra de todo el clip de ese diagnóstico NO es válida
  (interpolé 223 fotogramas de hueco) y 8 Hz podría ser bajo para el brazo.

**Consecuencias:**
- Todas las velocidades del **brazo** reportadas hasta acá (incl. "1,7–2,6× Fleisig", los picos
  de 4000–6100 °/s, el orden `brazo > torso > pelvis` del drive) están contaminadas por codo
  sin filtrar: **no son evidencia**. (Ver la re-medición de abajo: las MAGNITUDES eran ruido;
  el ORDEN del drive de perfil persiste aunque con un adelanto mucho menor. Esta frase decía
  antes "el drive invertido NO es un hallazgo fisiológico": era demasiado fuerte.)
- Pelvis y torso NO están afectados por este hueco: las conclusiones sobre ellos se mantienen.
- La ventana acotada del brazo sigue siendo razonable, pero es secundaria: primero E3 y el
  umbral de salto.

**Candidatos (NO aplicados; tocan E3 y validación, y cambian todo lo medido del brazo):**
1. E3: filtrar los segmentos continuos válidos de una serie con NaN en vez de dejarla cruda.
2. Umbral de salto imposible en unidades físicas (cm/fotograma o m/s) y calibrado, no 0,5
   torsos; evaluarlo separando datos de ajuste y de medición.
3. Chequeo de consistencia entre pasos k (ver "pico sostenido"), con su límite para el brazo.
4. Revisar el corte de Winter único por clip (8–9 Hz) para el brazo.

Los diagnósticos que se hicieron primero en un scratchpad (serie del codo, conteo de series sin
filtrar, comparación por grupo, salto por fotograma, montaje de fotogramas, ángulo en el plano)
quedaron **versionados** en `backend/app/diagnosticos_e3.py` (principio 5).

### Re-medición con E3 corregido (motor 0.4.1) sobre los 36 clips — validada por Valentín (25/9)

**Estado:** Valentín validó esta re-medición el 25/9 (la conclusión previa sobre el drive y el
revés de tres cuartos quedó reemplazada por ésta). Punto 1 de E3 hecho (decisión 010, `dsp.py`,
`pipeline.py`, pruebas `test_dsp_segmentos.py` y `test_pipeline_e3_huecos.py`, que fallan con el
E3 anterior). Los puntos 2 (umbral de salto) y 3 (corte de Winter) NO se tocaron.
Datos: `docs/resultados/e4-fase-b-exploratorio-<modo>-e3-0.4.1.json` (0.4.0: sin sufijo).

- **Regresión:** pelvis y torso idénticos entre 0.4.0 y 0.4.1 (diferencia máxima 0,0000 °/s).
- **Brazo, p99 de ω a k=1 (mediana por grupo, viejo → nuevo, °/s):** saque perfil 4847 → 1300;
  saque tres cuartos 3771 → 1371; drive perfil 3857 → 790; drive tres cuartos 6600 → 2165; revés
  perfil 5226 → 953; revés tres cuartos 940 → 908 (ya estaba filtrado). Caída k=1→8: 63–81 % →
  1–10 %. **La "anomalía" del revés de tres cuartos desaparece**: era el único grupo bien filtrado.
- **Drive de perfil: la inversión persiste, más chica.** Brazo antes del torso en 4 de 5
  repeticiones con ancla de torso, pero con un adelanto de 38–92 ms (antes 133–288 ms) y
  velocidades de 380–676 °/s (antes 2594–4546). Con el fotograma: el pico cae en la caída de la
  raqueta, justo antes del golpe hacia adelante. Drive tres cuartos: brazo después del torso en
  5 de 6 (96–146 ms).
- **Revés de perfil: aparece brazo primero en 5 de 6** (−12 a −233 ms; antes 0, porque casi
  no era auditable). Saque perfil: brazo después del torso en 3/3 auditables (+62 a +79 ms) con
  1072–1356 °/s. Saque tres cuartos: pelvis>torso>brazo en 5/6, sin cambios.
- Patrón: con el brazo bien filtrado, **en perfil el pico del brazo (hombro→codo) tiende a llegar
  ANTES que el del torso en drive y revés; en tres cuartos y en el saque, después.** Candidata
  a explicación (no probada): el pico global del brazo captura la caída de la raqueta y no el
  golpe (ventana de búsqueda del brazo); alternativa: el ángulo de perfil.
- **Cuidado con las magnitudes:** con el corte de Winter por clip de 8–9 Hz el brazo probablemente
  está subestimado (el saque queda en ~0,55× Fleisig). Es el punto 3.

**Revisión retroactiva del corpus público** (`diagnosticos_e3 comparar-brazo`; A = E3 viejo sin
detector de z = estado de la decisión 008):
- En A, el codo "plausible" era el que SÍ se había filtrado y la muñeca "implausible" la que
  quedaba cruda: `zverev_saque_lateral_01` (codo filtrado 2126 vs muñeca cruda 10 076),
  `drive_lateral_01` (1567 vs 10 322). En `zverev_saque_lateral_03` ambas estaban filtradas y daban
  lo mismo (1821 vs 1756). En `_02` ambas crudas (16 283 vs 26 063). La preferencia por el codo
  estaba **confundida con qué serie se filtraba**.
- Con E3 nuevo (C): muñeca/codo = 0,95–2,0 (mediana 1,39, n = 13), no 10–40; cobertura igual
  (codo 0,83, muñeca 0,84). La decisión codo-vs-muñeca **no se revoca aquí**, pero su
  justificación original ("la muñeca da 15 000–42 000 °/s") no se sostiene: hay que decidirla de
  nuevo con datos limpios (anatomía: el codo es el eslabón del "brazo" de la cadena; desenfoque de
  la muñeca en el impacto sigue siendo un argumento).
- **Techo ×3 (Fleisig × 3 = 7104 °/s):** el codo filtrado del corpus público está en 0,40–0,94×
  Fleisig (946–2234 °/s). Su justificación de "ruido de MediaPipe" ya no aplica (el ruido era el
  hueco). Ojo: en el corpus público la escala temporal es estimada, así que estos múltiplos son
  aproximados. No se recalibra todavía.

### Hipótesis a contrastar (Valentín, 2026-09-25)

El saque tiene fase aérea y drive/revés no. **Si la pelvis de drive y revés se acerca más a
la referencia de Fleisig que la del saque, el salto explica el exceso** y no el ángulo de
cámara. Si mantiene el mismo exceso, apunta a la estimación de la cadera en perfil. Se
contrasta con el mismo análisis de sensibilidad al paso (k=1,2,4,8) aplicado a drive/revés.

### Candidato de recalibración (NO aplicado)

El techo de plausibilidad por segmento (Fleisig × `MARGEN_PLAUSIBILIDAD`) descartó picos de
pelvis de 1325 y 1386 °/s (techo 1320) que se comportan como movimiento continuo. Un error
de detección real es un salto puntual: **no sobrevive al cambio de paso de muestreo**.
Criterio candidato, "pico sostenido": comparar el pico a k=1 contra k=4 (o k=8); si se
mantiene (p. ej. cae menos de ~10 %), es movimiento; si colapsa, es glitch. Reemplazaría o
complementaría el techo fijo. **Límite conocido:** un pico real pero breve (el brazo en el
impacto dura <30 ms) también cae al promediar más fotogramas (saque de perfil: el brazo cae
~70 % entre k=1 y k=8, la pelvis solo ~4 %). El criterio discrimina bien en segmentos lentos
(pelvis, torso) y **no** debe aplicarse tal cual al brazo; para el brazo hay que buscar otra
firma (p. ej. duración del pico a mitad de altura). **No se toca ahora**: recalibrar sobre estas mismas
repeticiones contaminaría la medición del Criterio 1 (hace falta separar datos de ajuste y
de medición: p. ej. ajustar con perfil, medir con la sesión 2).

---

## 2026-09-24 — Catalogador: soporte de `fase-b/`

**Rama:** `etapa/4-cinematica`. Primera sesión de Fase B: 6 repeticiones del saque de perfil
(iPhone, 240 fps, `r_frame_rate=30/1`, factor 8, `escala_temporal = conocida`) catalogadas
a mano en `catalogo.csv`.

### Qué se hizo

- `app/catalogador.py`: sin `--dir` recorre `fase-a/` y `fase-b/` (rutas relativas a
  `KINETIQ_DATA_DIR`); `originales/` se saltea junto a `compilaciones/`; subcarpeta
  inexistente → aviso; chequeo cruzado `fps_declarados` catálogo vs archivo.
- Verificado que la normalización NTSC no confunde el caso Apple (30 + conocida + factor 8
  → 240 efectivos) con el caso público (factor estimado, escala desconocida): son
  mecanismos independientes. Pruebas en `test_ingest_normalizacion.py`.
- `test_corpus_fase_a.py` ajustado (escanea ambas fases, evalúa solo fase-a).
- Docs: decisión 004 §8, `backend/README.md`.
- Corrida real: 20 clips, 6 filas de fase-b OK (240 ef., unicidad 1.0), 0 avisos globales.
- `pytest -m "not slow"` → 146 en verde.

### Convención de carpetas (Fase B)

`fase-b/<sesion>/<gesto>/recortes/` = unidades de análisis (también los clips sin corte,
copiados tal cual); `originales/` = solo fuentes con recortes hermanos.

### Pendiente

Sumar al catálogo el resto de los cortes y los controles/deficientes; correr
`python -m app.catalogador` y luego `extraer_pose` (checklist de Fase B, arriba).

---

## 2026-08-27 (fix) — Detector de inversión de profundidad (z), `v0.3.1` + `v0.3.2`

**Ramas:** `fix/inversion-z` (`v0.3.1`) y `fix/inversion-z-calibracion` (`v0.3.2`),
ambas mergeadas a `main`. Fix a E2/E3, antes de seguir con la Etapa 4.

Surgió de la validación cualitativa de la Etapa 4: `zverev_saque_lateral_02` daba un
pico de brazo de 24 932 °/s. Investigado (decisión 009): `CODO_DER` **invierte el signo
de `z`** en el frame 566 (+0,098 → −0,050 m). Confianza 0,65 (pasa el umbral de 0,5) y
desplazamiento 3D 0,31 torsos (< 0,5): **ni la baja confianza ni el salto imposible lo
marcaban.**

### Qué se hizo

- `engine/validation.py`: `detectar_inversiones_z`. Firma de un glitch puntual real —
  **cinco condiciones**: confianza previa ≥ 0,80, cambio de signo de `z`,
  `|Δz|/torso > 0,20`, dominado por `z` (`|Δz| > 1,8·|Δxy|`), y **`z` vuelve** al signo
  original en ≤ 15 fotogramas. `ResultadoValidacion.inversiones_z`.
- `engine/preparacion.py`: excluye la franja `[frame_desde, frame_hasta]` antes de filtrar.
- `v0.3.1` era más laxa (sin confianza previa ni retorno) y disparaba 35–95 veces por
  clip, removiendo picos plausibles del brazo y exponiendo peores. `v0.3.2` la acota a
  3–45/clip sin perder el caso real.

### Hallazgo (para el Capítulo 6/7)

Aun con las cinco condiciones, sobre el corpus público el detector **dispara 16–45 veces
por saque** de Zverev (solo 3 en el drive). No son falsos positivos: en **toma lateral**
la `z` de las articulaciones rápidas del brazo/mano que da MediaPipe es poco más que
ruido que cruza el cero. Consecuencia: al excluir esas franjas, **las repeticiones de
saque del corpus público quedan "no auditables"** en vez de reportar un orden con un
número plausible por casualidad — correcto por R3, y la misma conclusión de la decisión
008: la toma lateral no sirve para el brazo rápido; **Fase B con tres cuartos**. El
`drive` (brazo más en el plano) sigue recuperando `pelvis → torso → brazo`.

### Pruebas

`pytest -m "not slow"` → **123 en verde**. `-m slow` → `test_inversion_z_corpus.py`
atrapa el frame 566 real y la franja queda como `TramoExcluido` en E3.

---

## 2026-08-27 (sesión 3) — Etapa 4: Cinemática y secuenciación (arranque, 4.1–4.6)

**Rama:** `etapa/4-cinematica` (desde `main`). **La Etapa 4 NO se cierra en esta sesión.**
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.3.3 y §3.3.4.1–§3.3.4.5. Confirmado con
Valentín: se construyen 4.1–4.6 (+ 4.6b con caveat en el reporte) usando el corpus
público; se difieren 4.7 (Criterio 1), 4.8 (Criterio 2) y el punto de decisión hasta
tener la Fase B. Lado dominante: columna nueva en `catalogo.csv`, sin default.

### Qué se hizo

- **Housekeeping (al abrir la sesión):** `.gitattributes` con `eol=lf` (commit
  `4fbce0e`; `renormalize` no tocó nada, los blobs ya estaban en LF). ADR 006 ampliado
  con el orden de palancas de optimización de inferencia (`model_complexity` más bajo →
  Vía A sobre ONNX). Ambos ya en `main`.
- **`engine/segmentos_corporales.py`** — cadena `pelvis → torso → brazo` como vectores
  directores. `brazo = HOMBRO_{dom} → MUNECA_{dom}`; `{dom}` de la columna
  `lado_dominante` del `catalogo.csv` (agregada esta sesión), sin valor por defecto.
- **`engine/kinematics.py`** (4.1–4.3) — `angulo_tres_puntos`, `serie_angulo_articular`,
  `serie_separacion_cadera_hombro`, `velocidad_angular_segmento` (°/s, escalar).
- **`engine/sequencing.py`** (4.4–4.6b) — `detectar_pico` (`find_peaks`; no auditable si
  cae en `TramoExcluido` o supera 8000 °/s = techo de plausibilidad física, no un
  ajuste), `orden_observado`, `segmentar` (auto/manual/fallback), `evaluar_repeticion`,
  `agregar` (con `nota` de caveat de corpus público en la estructura).
- **`app/analizar.py`** — CLI `python -m app.analizar --clip X` (pose caché → E3 → E4).
- **`catalogo.csv`** — columna `lado_dominante` (zverev/sinner = `der`; `reves_lateral_01`
  de Federer y los dos `desconocido` quedaron vacíos — ver pendientes).
- Versión del motor → `0.4.0`. Decisión 008 (incluye los hallazgos de la validación).

### Validación cualitativa sobre el corpus público (registrada tal cual salió)

Corrida de `analizar` sobre 3 saques de Zverev + drive de Sinner:

- **El pipeline corre de punta a punta sobre material profesional sin romperse.** El
  manejo de no auditables funciona.
- **La muñeca de la raqueta no es auditable en gestos rápidos:** `HOMBRO→MUNECA` da
  15 000–42 000 °/s en 3 de 4 clips (MediaPipe pierde la mano por desenfoque). Con
  `HOMBRO→CODO` (brazo superior) los valores son plausibles (1 700–2 300 °/s) en 3 de 4
  y en el **drive el orden sale `pelvis → torso → brazo` completo y plausible**.
- **Vista lateral:** en los saques, pelvis y torso pican a ~12–18 ms — al borde de lo
  resoluble; el orden entre ambos se invierte según el clip. Es el riesgo anticipado:
  rotación transversal sobre el eje de profundidad (§3.3.2.8). El brazo, cuando es
  auditable, queda claramente último.
- **Lectura para la tesis:** evidencia positiva (el drive recupera la cadena pese al
  sesgo y a la vista lateral; la prueba sintética de ordenamiento con sesgo lo confirma)
  y de límite (pelvis-vs-torso lateral ≈ 15 ms; muñeca no auditable). Ambas útiles;
  guían el encuadre de la Fase B (tres cuartos pone la rotación en el plano de imagen).

### Pruebas

`pytest -m "not slow"` → **128 en verde**. Incluye la **prueba de ordenamiento con
sesgo** (3 series sintéticas con offset constante + ruido → recupera pelvis→torso→brazo),
ángulos de geometría conocida, pico en tramo no auditable → no se reporta. `-m slow`:
`test_analizar_e4.py` (estructura coherente sobre pose real, sin aseverar correctitud).

### Ajustes tras la revisión de Valentín (misma sesión)

- **`brazo = HOMBRO→CODO` por defecto, configurable** (`brazo_via`).
- **`catalogo.csv`:** `reves_lateral_01` → `lado_dominante = der` (Federer juega de
  derecha; el "zurdo" era un dato equivocado).
- **Techo de plausibilidad POR SEGMENTO, anclado a Fleisig et al. (2003)** (§3.4.2.2):
  pelvis 440, torso 870, brazo 2368 °/s × `MARGEN_PLAUSIBILIDAD = 3` → 1320 / 2610 /
  7104 °/s. Criterio del margen en decisión 008 (incertidumbre del factor de
  ralentización estimado + ruido de MediaPipe).
- **`zverev_saque_lateral_02` investigado:** el pico de 24 932 °/s (codo) es un error
  de detección puntual, no un techo mal calibrado. Frame 566: la `z` de `CODO_DER`
  **cambia de signo** (~14 cm) con `x`,`y` suaves (inversión de profundidad de
  MediaPipe). Confianza 0,65 (pasa el umbral de 0,5) y desplazamiento 0,33 torsos
  (< `MAX_SALTO_TORSOS = 0,5`): **ni E2 ni E3 lo marcaron**. El techo lo corta →
  repetición no auditable (correcto). Propuesta (no aplicada): detector de inversión
  de signo en `z` en `engine/validation.py`.
- Efecto lateral del codo: la segmentación automática, antes inundada por los
  *glitches* de 40 000 °/s de la muñeca, empieza a funcionar (el drive se parte y una
  repetición sale `pelvis → torso → brazo` **correcta**, 827/1666/1744 °/s).

`pytest -m "not slow"` → **130 en verde**.

### Detector de inversión de z (aplicado, `v0.3.1` → `v0.3.2`)

Salió de investigar el pico de 24 932 °/s del punto anterior. Se hizo en ramas
propias (`fix/inversion-z`, `fix/inversion-z-calibracion`) y se mergeó a `main`
antes de rebasar `etapa/4-cinematica`. Detalle completo en la entrada **"(fix)"** de
más arriba y en la decisión 009.

### Comparación con dos clips públicos de tres cuartos (Valentín los consiguió)

`drive_trescuartos_01`, `saque_trescuartos_01` (240 fps efectivos, factor 8).
`catalogo.csv` actualizado a 14 clips (`test_corpus_fase_a.py` a 14, corre limpio).
También: `control_oclusion_02` jugador → alcaraz; `fps_efectivos` de los tres cuartos
corregido a 240 (el catalogador detectó la discrepancia 480 arrastrada).

**El tres cuartos, sobre estos dos clips no controlados, NO mejoró ninguna métrica:**

| | lateral | tres cuartos |
| --- | --- | --- |
| separación pelvis–torso | ~2–18 ms, orden que se invierte | 271 / 317 ms **pero torso antes que pelvis**, sin pico claro de pelvis |
| brazo auditable | drive sí (1744 °/s), saques no | drive al borde (6399 °/s), saque no (23365) |
| inversiones de z | 16–45 saques / 3 drive | 40 saque / 14 drive |
| tramos excluidos E3 | decenas | 75 (drive) / 150 (saque) — ~40 % del clip |

**Dos lecturas distintas, no confundirlas:**

1. **"El ángulo no lo resolvió":** con estos dos clips, cambiar a tres cuartos **no**
   convirtió la ambigüedad pelvis-torso (~15 ms) en una secuencia limpia, **no**
   volvió auditable el brazo del saque, y **no** bajó las inversiones de z. Si el
   único cambio fuera el ángulo, no alcanzaría.
2. **"No fue una prueba justa del ángulo":** estos dos clips son públicos, de baja
   tasa de bits (3–4 MB para 13–16 s), origen desconocido, sin segmentar (la
   ventana automática los recorta mal), `escala_temporal_conocida = False` y factor
   estimado a ojo. La Fase B es otra cosa: 240 fps **reales**, luz controlada,
   encuadre fijo medido, pausas en posición neutra que hacen la segmentación
   trivial, y repeticiones del mismo gesto. La comparación honesta pelvis-torso
   lateral vs tres cuartos **todavía no se hizo**; esto solo descartó el atajo.

La única evidencia positiva limpia sigue siendo `drive_lateral_01` (toma lateral):
`pelvis → torso → brazo` correcto, velocidades plausibles. Que el drive recupere la
cadena y el saque no, mismo encuadre y mismo pipeline, apunta a que el cuello de
botella es el gesto (velocidad de la mano en el impacto — límite del apartado 1),
no el pipeline.

---

## Estado al cerrar la sesión (2026-08-27)

**En `main` (pusheado):** Etapas 0–3 (`v0.1.0-etapa0` … `v0.4.0-etapa3`) + fixes
`v0.3.1` y `v0.3.2` (detector de inversión de z). El motor en `main` está en
`0.3.2`.

**En `etapa/4-cinematica` (rama abierta, sin merge, sin tag):** pasos 4.1–4.6 de la
Etapa 4 sobre esa base. Motor `0.4.0`. `pytest -m "not slow"` → **139 en verde**;
`-m slow` → 15 (incluye `test_corpus_fase_a.py` con 14 clips, `test_analizar_e4.py`,
`test_inversion_z_corpus.py`). Nada pendiente de commitear.

**Corpus (`kinetiq-data/`):** 14 clips catalogados y verificados, catalogador limpio
(solo avisos informativos de normalización NTSC). 12 laterales + 2 de tres cuartos.
Caché de pose (`backend/.cache/`) poblada para los 14.

**Lo que NO se hizo, a propósito** (precondición del plan — no tiene sentido pulir un
detector cuyos criterios de éxito todavía no se pueden medir): tareas 4.7 (Criterio 1),
4.8 (Criterio 2), 4.6b como medición formal, y el **punto de decisión de repliegue**.
La Etapa 4 no se cierra hasta tener el material propio.

## Cuando llegue el material de la Fase B — checklist

Precondición: el conjunto propio grabado y verificado (protocolo de grabación,
hito C1). Trabajar en `etapa/4-cinematica`.

1. **Ingesta y catálogo.** Copiar los clips a `kinetiq-data/fase-b/`. Agregar una
   fila por clip a `catalogo.csv` con **`escala_temporal = conocida`**, `factor_estimado = 1`,
   `fps_efectivos` reales (240), `lado_dominante` del jugador. Correr, desde `backend/`:
   `python -m app.catalogador` — debe salir sin avisos (ni siquiera de NTSC si se grabó
   a 240 exactos).
2. **Pose.** `python -m app.extraer_pose` (procesa lo nuevo, ~3–4 min por clip). Deja
   la caché lista.
3. **Análisis por clip.** `python -m app.analizar --clip <archivo> [--manual d1:h1,d2:h2]`.
   Para clips con 6 repeticiones y pausas del protocolo, la segmentación automática
   debería andar; si no, marcar las ventanas con `--manual`.
4. **Qué comparar (las tres preguntas que quedaron abiertas):**
   - **Pelvis-torso:** ¿la separación es estable y en el orden esperado
     (pelvis→torso) entre repeticiones del mismo saque? ¿El encuadre de tres cuartos
     da una separación más limpia que el de perfil? Comparar contra los ~2–18 ms
     invertidos de la toma lateral (decisión 008 §2).
   - **Brazo:** ¿el pico del segmento `brazo` (con `--brazo-via codo`) cae por debajo
     del techo de plausibilidad, o el desenfoque en el impacto lo mantiene no
     auditable también a 240 fps reales? Probar además `--brazo-via muneca`.
   - **Inversiones de z:** ¿cuántas veces dispara `detectar_inversiones_z` con `z`
     métrica real? Debería ser mucho menos que las 16–45/clip del corpus público.
5. **Recalibrar con datos reales** (todo con `escala_temporal_conocida = True`):
   - **Criterio de "pico sostenido vs. paso de muestreo"** como alternativa al techo fijo
     (ver entrada 2026-09-25); no calibrar y medir sobre las mismas repeticiones.
   - `MARGEN_PLAUSIBILIDAD` del techo (hoy ×3; sin la incertidumbre del factor
     estimado, probablemente conviene bajarlo). `_FLEISIG_MAX` / `techo_velocidad` en
     `engine/sequencing.py`.
   - Los cinco umbrales de `detectar_inversiones_z` en `engine/validation.py`.
   - `find_peaks` (`PROMINENCIA_*`, `SEPARACION_MIN_S`) y la segmentación
     (`QUIETUD_REL`, `DUR_MIN_REPETICION_S`) en `engine/sequencing.py`.
6. **Medición formal (4.7 / 4.8).** Implementar `4.7` (Criterio 1: proporción de
   repeticiones con orden repetible; meta 8/10) y `4.8` (Criterio 2: error angular vs
   medición manual sobre los mismos fotogramas; meta < 20,6°). Volcar los números a
   `docs/resultados/` con un script versionado (principio 5 del plan).
7. **Pruebas a activar / agregar:**
   - En `tests/integration/test_analizar_e4.py`: pasar de "estructura coherente" a
     aserciones reales sobre las repeticiones de la Fase B (orden, auditabilidad).
   - Nueva prueba de **repetibilidad del orden** entre las 6 repeticiones de un clip
     (base del Criterio 1).
   - Nueva prueba de **coherencia temporal** con el par real 240 fps / ralentizado
     del mismo gesto (pendiente desde la Etapa 1: hoy es sintética en
     `test_slowmo_coherencia.py`).
   - Reemplazar las pruebas de integración que hoy usan clips sintéticos de control
     por el material real equivalente de la Fase B, si lo hay.
8. **Punto de decisión.** Con los Criterios 1 y 2 medidos, aplicar la tabla del plan
   (continuar a E5 / repliegue a fase de preparación / repliegue a 2D / reformular
   alcance) y **documentar el resultado en `docs/decisiones/`** cualquiera sea —
   alimenta los Capítulos 6 y 7. Recién ahí: merge `etapa/4-cinematica` → `main`,
   tag `v0.5.0-etapa4`.

---

## 2026-08-27 (sesión 2) — Etapa 3: Procesamiento de señales

**Rama:** `etapa/3-senales` (desde `main`, con Etapas 0–2 mergeadas y pusheadas).
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.4.2.1–§3.4.2.6. Puntos A/B/C confirmados
por Valentín: re-extracción simple del corpus; un corte de Winter por clip (como
simplificación deliberada por el contrato congelado); interpolar huecos de hasta 5
fotogramas.

### Qué se hizo

- **Paso 0 — Coordenadas métricas.** `PoseFrame.puntos_mundo` (metros, centrado en
  caderas), `PoseFrame.get_mundo()`, `SecuenciaPose.tiene_mundo`. `MediaPipeBackend`
  lee `pose_world_landmarks`; `FakeBackend` emite `puntos_mundo` sintéticos (dims=3).
  Caché: arrays `kpw__*`, **esquema v2** — `cargar_si_vigente` descarta las cachés v1,
  así el corpus se **re-extrae solo**. `puntos` (imagen) queda para el overlay de E5.
- **`engine/dsp.py`** (3.1): `butterworth_fase_cero` con `filtfilt` (nunca `lfilter`).
  Guarda de Nyquist explícita (`corte_hz >= fps/2` → error). Rechaza NaN y series
  cortas.
- **`engine/preparacion.py`** (3.3): `preparar_series` excluye fotogramas sin
  detección, puntos de baja confianza y saltos imposibles (de `validation` de E2);
  interpola huecos ≤ 5 fotogramas; los largos → `TramoExcluido`. Una articulación
  totalmente excluida → tramo que abarca todo el clip.
- **`engine/winter.py`** (3.2): `analizar_serie` (residuo RMS vs corte) y `elegir_corte`
  (un corte por clip = el máximo de los cortes de las articulaciones rápidas).
- **`engine/pipeline.py`** (3.4): `procesar_e3` encadena validar → preparar → Winter →
  filtrar sobre la secuencia completa. `SecuenciaFiltrada.trazabilidad_filtro()` arma
  el bloque `trazabilidad.filtro` del contrato — **sin cambio de contrato** (el campo
  `corte_hz` ya existía; E3 lo llena).
- **`validation.py`**: parámetro `espacio` (`"imagen"` | `"mundo"`); `_dist` 3D. E3
  valida en `"mundo"`.
- Versión del motor → `0.3.0`. Decisión 007.

### Criterio de aceptación de la Etapa 3

| Punto | Estado |
| --- | --- |
| Prueba de fase cero pasa y su versión unidireccional falla | ✅ `test_dsp.py::test_fase_cero_conserva_el_instante_del_pico_y_la_unidireccional_no` |
| Señal con ruido conocido: reduce el ruido sin tocar la componente lenta | ✅ |
| Corte por encima de Nyquist: rechazado | ✅ |
| Winter elige un corte entre señal y ruido | ✅ |
| Pipeline completo sobre pose real → secuencia filtrada coherente | ✅ `test_pipeline_e3.py` (`slow`) *(pendiente de la re-extracción; ver abajo)* |

### Pruebas

`pytest -m "not slow"` → **114 en verde** (nuevas: `test_dsp`, `test_winter`,
`test_preparacion`, `test_validation` ampliado, `test_pose_base`/`test_pose_cache`
ampliados para `puntos_mundo`).

### Pendiente

- **Re-extracción del corpus con esquema v2** en curso al momento de escribir esto
  (background). El `test_pipeline_e3.py` (`slow`) se corre en cuanto termine.
- El filtro sobre clips con `escala_temporal_conocida = False` usa un `fps_efectivos`
  estimado → corte en Hz y velocidades absolutas aproximados; el **orden** de picos es
  inmune (§3.3.4.2). Sin acción, coherente con lo que ya marca E1.
- Si E4 muestra que un corte único por clip distorsiona alguna articulación → pasar a
  corte por articulación (ampliaría el contrato).

### Siguiente paso concreto

Cerrar la Etapa 3 (correr `test_pipeline_e3` sobre la caché re-extraída, merge
`etapa/3-senales` → `main`, tag `v0.4.0-etapa3`) y abrir la **Etapa 4 — Cinemática y
secuenciación** (el punto de decisión; dos semanas en el plan). Precondición del plan:
la Fase B (grabación propia) — Valentín la adelantó a esta semana. Lecturas de la
convención para E4: `capitulo-3` §3.3.3 y §3.3.4.1–§3.3.4.5.

---

## 2026-08-27 — Etapa 2: Estimación de pose

**Rama:** `etapa/2-pose` (desde `main`, con Etapas 0 y 1 ya mergeadas y pusheadas).
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.3.2.3–3.3.2.9 y `capitulo-4` §4.4.3.
Cuatro puntos de diseño confirmados por Valentín: A `static_image_mode=True`; B
interfaz + mapa canónico + MediaPipeBackend + FakeBackend (que **también** simula el
caso 2D-solo con `z=None`), sin Vía A real todavía; C `docs/resultados/` arranca en E2;
D distancia cadera-hombro como referencia interna para el umbral de salto imposible.

### Qué se hizo

- **2.1 · Contrato `PoseBackend`** (`engine/pose/base.py`). ABC: cada backend implementa
  `estimar_frame(frame_bgr, indice) -> PoseFrame`; la base arma la `SecuenciaPose`
  (`procesar`). `Punto` (x,y normalizados, z relativo o None, confianza), `PoseFrame`,
  `SecuenciaPose` (con `dims` 2/3, `cobertura`, `cobertura_articulacion`, `config_hash`).
  Context manager para liberar recursos.
- **2.3 · Mapa articular canónico** (`engine/pose/articulaciones.py`). 19
  `ArticulacionCanonica`; `MEDIAPIPE_A_CANONICO` (33→canónico) y `COCO_A_CANONICO`
  (17→canónico); `ARTICULACIONES_CORE` (13, lo que ambos entregan). Puntos de mano/pie
  solo MediaPipe (habilitan el indicador indirecto de rotación de hombro, §3.3.3.4).
- **2.2 · `MediaPipeBackend`** (`engine/pose/mediapipe_backend.py`). `static_image_mode=True`,
  `model_complexity=2`. `visibility` → confianza. `version` = `"mediapipe-0.10.18"`
  (va a `trazabilidad.backend_pose`).
- **`FakeBackend`** (`engine/pose/fake_backend.py`). Esqueleto plausible (posiciones
  nominales + balanceo + oscilación por articulación), `dims=2|3`, simula oclusión
  (confianza baja por articulación) y fotogramas sin detección. Es el segundo backend
  contra el que se prueba que la interfaz aguanta el caso 2D-solo.
- **2.4 · `engine/validation.py`**. `marcar_baja_confianza` (umbral 0.5),
  `detectar_saltos_imposibles` (umbral 0.5 longitudes de torso; sin torso no se juzga),
  `validar()` → `ResultadoValidacion` con cobertura auditable **por articulación**
  (§3.3.2.8).
- **2.5 · Caché** (`engine/pose/cache.py` + `config.get_cache_dir()`). `.pose.npz` +
  `.pose.json`. Clave = stem + backend id + hash de config. `cargar_si_vigente` compara
  una firma rápida del video y descarta la caché si el archivo cambió.
  `KINETIQ_CACHE_DIR` (default `backend/.cache/`, ignorado).
- **`app/extraer_pose.py`**. CLI: recorre el corpus, corre el backend, cachea. Si ya
  está y el video no cambió, no re-infiere. Probado con `--backend fake` sobre los 12
  clips.
- **2.6 · `app/bench_pose.py` + `docs/resultados/`**. Mide fps de inferencia y agrega la
  corrida a `docs/resultados/e2-velocidad-inferencia.json`.

### Criterio de aceptación de la Etapa 2

| Punto | Estado |
| --- | --- |
| Un video de la Etapa 0 produce un archivo de coordenadas completo con confianzas | ✅ `extraer_pose` → `.pose.npz`/`.pose.json` |
| Video con jugador visible: cobertura > 95 % | ✅ `test_mediapipe_backend.py` sobre `zverev_saque_lateral_01` (cobertura > 0.95) |
| Video con oclusión: puntos ocluidos marcados de baja confianza | ✅ `test_mediapipe_backend.py` sobre `control_oclusion_02` |
| El cambio de backend no altera la estructura de la salida | ✅ FakeBackend (2D y 3D) y MediaPipe producen la misma `SecuenciaPose` |
| Velocidad de inferencia medida y registrada | ✅ `docs/resultados/e2-velocidad-inferencia.json` |

### Dato duro (tarea 2.6, primer punto del indicador §2.4)

`static_image_mode=True` + `model_complexity=2`, 1080p, **CPU** (MediaPipe-Python no usa
la GTX 1050ti): **~3,6 fotogramas/segundo** (~280 ms/frame, p95 ~322 ms). Un clip de
~750 fotogramas ≈ 3–4 min; el corpus entero ≈ 40 min, **una sola vez** (después la
caché). Si en E4 el tiempo molesta: `model_complexity=1`, `static_image_mode=False`
(tracking), o bajar resolución antes de inferir. No se toca ahora ("no optimizar antes
de medir").

**Choca con la tesis:** el apartado 4.2.3 usó ~25 fps para justificar el procesamiento
asincrónico y estimar tiempos; 4.5.4 apoyó los costos en ese número. Casi 7× de
diferencia. Es un pendiente de **redacción** (no de código): reescribir 4.2.3 y 4.5.4
con el número medido antes de la entrega. Registrado en `docs/decisiones/006`.

### Pruebas

`pytest -m "not slow"` → **96 en verde** (unit de pose: articulaciones, base/FakeBackend,
validación, caché; integración con clips sintéticos). `-m slow` → MediaPipe sobre video
real (4) + corpus Fase A de la Etapa 1 (5).

### Pendiente

- **Vía A (YOLOv8-Pose 2D + elevación)**: no implementada. Se hace si el punto de
  decisión de E4 lo pide (plan de repliegue). La interfaz ya está lista para un backend
  de 17 puntos.
- `pose_world_landmarks` métricos de MediaPipe: no se guardan aún. **La Etapa 3 los va a
  necesitar**: el filtro va a operar sobre coordenadas métricas (ver plan de E3), así
  que E3 empieza extendiendo la captura de pose y re-extrayendo el corpus.
- Reevaluar la config de MediaPipe (complexity / tracking) si la velocidad molesta en E4.
- `.gitattributes` con `eol=lf`: **resuelto** (commit `4fbce0e`). `renormalize` no tocó
  ningún archivo; los blobs ya estaban en LF.
- **Calendario:** Valentín adelanta la Fase B (grabación propia, hito C1) a esta semana
  en vez del 22/9. No cambia nada del desarrollo en curso.

### Siguiente paso concreto

Abrir la **Etapa 3 — Procesamiento de señales**. Lecturas de la convención (hechas):
`capitulo-3` §3.4.2.1–3.4.2.6. Plan propuesto; pendiente de aprobación antes de escribir
código.

---

## 2026-08-26 (sesión 2) — Etapa 1: Ingesta y validación de FPS

**Rama:** `etapa/1-ingesta` (desde `etapa/0-fundaciones`, todavía sin merge a `main`).
**Modelo:** Sonnet 5 Medio.

Antes de planificar se leyeron los apartados de tesis que sustentan la etapa
(`capitulo-3`: 3.3.1.1, 3.4.2.2, y 3.3.4.2) y se releyó `decisiones/001`, según la
convención fijada.

### Qué se hizo

- **1.1 / 1.2 / 1.3 · `engine/ingest.py`.** Núcleo puro separado de la entrada/salida:
  - `clasificar_fps()` — tabla de aptitud (≥240 completo, 120–239 reducido, 60–119 solo
    preparación, <60 rechazado).
  - `evaluar()` — `fps_efectivos = fps_declarados × factor`; propaga la frecuencia de
    **captura**, nunca la de reproducción. El factor es externo (catálogo o manual).
    `<60` devuelve un resultado con `motivo_rechazo`, no una excepción.
  - `detectar_inconsistencias()` — contrasta tasa declarada vs `nb_frames/duración` vs
    `avg_frame_rate` (verificación 1 de la decisión 001).
  - `probe()` — OpenCV + enriquecimiento con `ffprobe` si está. Archivo corrupto →
    `IngestaError`, sin crash.
  - `iterar_fotogramas()` — generador, memoria constante (tarea 1.4).
- **Decisión 001 en código · `engine/framehash.py`.** `ratio_fotogramas_unicos()` por
  huella md5 exacta sobre la ventana central (no `mpdecimate`). `interpretar_ratio()` →
  `captura_real` / `repeticion_aislada` / `duplicacion_sistematica`.
- **1.5 · `app/catalogador.py`.** `python -m app.catalogador` (desde `backend/`).
  Recorre el corpus, toma el factor del `catalogo.csv`, combina las dos verificaciones
  en un "uso" final, escribe `catalogo-verificado.csv`. **No toca `catalogo.csv`.**
  `--sin-hash` para una pasada rápida. Detectó que las 4 filas de `catalogo.csv` tienen
  13 columnas en vez de 14 (fila mal formada): lo reporta y no cruza semánticamente
  contra esas filas.
- **Contrato.** Se agregó `escala_temporal_conocida: bool` (obligatorio) a
  `Trazabilidad` en `schemas/reporte.py` + ejemplo JSON. Cambio al contrato de la
  Etapa 0, hecho antes de integrar nada a `main`. Registrado en decisión 004.
- **Versión del motor** → `0.1.0`.
- **Decisión 004** (`docs/decisiones/004-ingesta-fps-y-verificacion.md`), `arquitectura.md`
  y `backend/README.md` actualizados (ffmpeg como dependencia del catalogador, cómo
  correr el catalogador).

### Criterio de aceptación de la Etapa 1

| Punto | Estado |
| --- | --- |
| Archivos de 30/60/120/240 fps devuelven su tasa real | ✅ (test de integración con clips ffmpeg) |
| Clip ralentizado (240 exportado a 30, factor 8) resuelve a 240 efectivos | ✅ |
| Prueba de coherencia temporal (240 vs ralentizado: misma duración real) | ✅ **sintética** |
| Metadatos inconsistentes se detectan y advierten | ✅ |
| Archivo corrupto / formato no soportado: error claro sin caída | ✅ |
| Video 240 fps / 20 s: la iteración no acumula memoria | ✅ (`tracemalloc`, pico <100 MB) |
| El catalogador procesa la Fase A completa sin errores y clasifica cada clip | ✅ lee y clasifica los 12; marca las inconsistencias del `catalogo.csv` (ver abajo) |
| Toda la lógica sobre la frecuencia efectiva, no la declarada | ✅ |

Corrida real del catalogador sobre `kinetiq-data/fase-a/` (12 clips, `compilaciones/`
excluida): 5 gestos en cámara lenta → `fps_efectivos` 500/480/300,
`escala_temporal_conocida = False`, `ratio_unicidad ≈ 1.0` (`captura_real`), `uso = E1-E4`;
4 controles a 30 fps → `rechazado`; 3 a 60 fps → `solo preparación`.

### Pruebas

`pytest -m "not slow"` → **64 en verde** (incluye las 12 de la Etapa 0). `-m slow` →
4 pasan sobre el material real + 1 `xfail` (catálogo con inconsistencias, ver abajo).
~2 min.

### Pendiente

- Sigue con la única prueba sintética sin equivalente real: duplicación sistemática de
  fotogramas (ningún clip real la tiene) y el par de coherencia temporal 240 vs
  ralentizado (depende de la Fase B, plazo 22/9). Marcadas en el código.
- Hash md5 por fotograma sobre 1080p: ~1 min por clip de 30 s. Aceptable como
  herramienta offline; si el corpus crece, submuestrear la ventana.
- `.gitattributes` con `eol=lf` (arrastre de la Etapa 0).

### Correcciones tras la revisión (misma sesión)

El corpus de la Fase A se amplió a **12 clips reales** (3 saques + 1 drive + 1 revés en
cámara lenta; 7 de control: 4 a 30 fps, 3 a 60 fps, con oclusión en varios). Al correr
el catalogador sobre el corpus nuevo aparecieron dos bugs propios, ya arreglados:

- **Tasas NTSC.** `59.94` fps (= 60000/1001) quedaba por debajo del umbral de 60 y se
  rechazaba por redondeo. Se agregó `normalizar_fps()`: ajusta a la tasa nominal si cae
  a <0.5%. Ahora `59.94 → 60 → solo preparación`, `29.97 → 30 → rechazado`.
- **Material de origen.** El catalogador escaneaba `fase-a/compilaciones/` (videos largos
  de los que se recortan los segmentos). Ahora salta `compilaciones/` por defecto
  (`--incluir-todo` para no saltearla).
- Alineado el vocabulario: `SOLO_PREPARACION` → `uso = "E1-E2 (solo preparacion)"`
  (**sin tilde**, por pedido de Valentín: es un token que viaja al CSV y se compara
  contra `catalogo.csv`; se mantiene ASCII para no depender de la codificación de la
  consola en Windows/Git Bash). Barrido del resto del código: los otros usos de la
  palabra con tilde son comentarios y prosa de docs (se dejan con ortografía correcta);
  la única otra cadena *generada* era `motivo_rechazo` en `ingest.py`, ya pasada a ASCII.
- El catalogador ahora reporta filas del `catalogo.csv` que no tienen archivo.

**Pruebas sintéticas retiradas** (había material real equivalente): parámetros 30/60 fps
de `test_ingest_video.py`. Se mantienen las sintéticas que no tienen equivalente real:
duplicación sistemática de fotogramas (ningún clip real la tiene) y el par de coherencia
temporal 240 vs ralentizado (depende de la Fase B, plazo 22/9).

`test_corpus_fase_a.py` reescrita contra los 12 clips reales: 5 gestos aptos E1-E4
(`escala_temporal_conocida = False`, sin duplicación), controles de 30 fps → rechazado,
de 60 fps → solo preparación.

### Cierre del `catalogo.csv` y merge

Valentín arregló el `catalogo.csv`: renombró la fila fantasma a
`control_reves_30fps_01.mp4`, quitó la fila de `zverev_saque_sideview.mp4` (compilación),
y puso `uso = rechazado` en los 4 controles a 30 fps. Quedan **12 filas parejas**.

`python -m app.catalogador` sobre el corpus final: **sin avisos globales, sin
inconsistencias**. Los únicos avisos por clip son las notas informativas de
normalización NTSC (`29.97 → 30`, `59.94 → 60`). Resultado:

| grupo | clips | uso |
| --- | --- | --- |
| gestos en cámara lenta | zverev ×3 (500 fps ef.), drive_lateral_01 (480), reves_lateral_01 (300) | `E1-E4`, `escala_temporal_conocida=False`, `captura_real` |
| control 60 fps | control_rally_60fps_01/02, control_oclusion_03 | `E1-E2 (solo preparacion)` |
| control 30 fps | control_drive_30fps_01, control_reves_30fps_01/02, control_oclusion_02 | `rechazado` |

Se quitó el `xfail` de `test_el_catalogo_no_tiene_inconsistencias` (ahora pasa como
prueba real). `pytest -m "not slow"` → 64 en verde; `-m slow` → 5 en verde.

**Merge hecho:** `etapa/0-fundaciones` → `main`, etiqueta `v0.1.0-etapa0`;
`etapa/1-ingesta` → `main`, etiqueta `v0.2.0-etapa1`. `main` funcional. Sin `push`
(local). **Etapa 1 cerrada.**

### Siguiente paso concreto

**Etapa 2 — Estimación de pose**, rama `etapa/2-pose` desde `main`. Plan ya propuesto y
aprobado en su forma general (lecturas hechas: `capitulo-3` 3.3.2.3–3.3.2.9, `capitulo-4`
4.4.3). Pendiente de confirmar 4 puntos de diseño antes de escribir código:
`static_image_mode`, alcance de la Vía A (YOLOv8-Pose), `docs/resultados/` desde E2, y el
umbral de "salto imposible" sin escala métrica.

---

## 2026-08-26 — Etapa 0: Fundaciones (tareas 0.1–0.4, 0.6, 0.7)

**Rama:** `etapa/0-fundaciones` (desde `4c954e8`). `main` sin tocar.

### Qué se hizo

- **Línea de base.** Primer commit (`10e1cb1`) consolidando el trabajo que vivía solo en el
  árbol de trabajo de `ajuste-tesis`: `CLAUDE.md`, `docs/` completo (plan, protocolo,
  decisión 001, capítulos 3 y 4 de la tesis) y los ajustes del prototipo Lovable. La rama
  `ajuste-tesis` queda intacta en `4c954e8`; qué se hace con ese contenido se decide en otra
  sesión.
- **0.4 · Higiene de git.** `.gitignore` ampliado: entornos virtuales, `__pycache__`,
  `.env` (se versiona solo `.env.example`), archivos de video, `package-lock.json` (el
  frontend usa bun; se descarta el lockfile de npm).
- **0.1 · Monorepo.** Todo el proyecto Lovable movido a `frontend/` con `git mv` (conserva
  historial). Creado el esqueleto `backend/`, `supabase/`, `tests/`, `.github/workflows/`
  según el apartado 4.3.5 de la tesis, transcripto en
  `docs/decisiones/003-estructura-monorepo.md`. El frontend **levanta y compila** desde la
  nueva ubicación (`bun run dev` y `bun run build` verificados).
- **0.2 · Entorno Python.** venv en `backend/.venv` creado con **`py -3.11`**.
  `requirements.txt` con versiones fijadas. **mediapipe instala y ejecuta en esta máquina**
  (CPU/XNNPACK; la GTX 1050ti no la usa la API de Python de mediapipe). Dos ajustes que
  hicieron falta:
  - `numpy` bajado a `1.26.4` porque mediapipe exige `numpy<2`.
  - Se usa `opencv-contrib-python` (no `opencv-python`): mediapipe depende de contrib, y
    tener las dos instaladas rompe el import de `cv2`.
- **Config de la ruta del corpus** (regla de arquitectura de esta sesión).
  `backend/app/config.py` → `get_data_dir()` lee `KINETIQ_DATA_DIR` del entorno o de
  `backend/.env`. Sin valor por defecto: si falta, error claro. `backend/.env` creado local
  (ignorado), `backend/.env.example` versionado. Decisión en
  `docs/decisiones/002-config-ruta-corpus.md`.
- **0.3 · Contrato del reporte congelado.** `backend/app/schemas/reporte.py` (Pydantic v2,
  `extra="forbid"`) transcribe el Anexo A. Ejemplo válido en
  `docs/contrato-reporte.ejemplo.json`.
- **0.6 · Decisiones.** `docs/decisiones/README.md` (plantilla + índice), ADR 002 y 003
  nuevas, ADR 001 corregida (venía con el markdown escapado y no renderizaba).
- **0.7 · Bitácora.** Este archivo.
- **Pruebas.** `pytest` → **12 pruebas en verde**: smoke, validación del contrato contra el
  ejemplo (y rechazo de datos mal formados), y resolución de `KINETIQ_DATA_DIR`.

### Criterio de aceptación de la Etapa 0

| Punto | Estado |
| --- | --- |
| `pytest` corre sin errores sobre una prueba trivial | ✅ 12/12 |
| El contrato del reporte valida un ejemplo ficticio | ✅ |
| El proyecto frontend levanta desde su nueva ubicación | ✅ `dev` y `build` |
| Corpus Fase A completo y verificado | ⏳ fuera de este chat (tarea 0.5, en curso) |
| Fase B agendada y equipo de captura probado | ⏳ fuera de este chat (hito C1, límite 22/9) |

### Pendiente

- **Detalle a no olvidar:** el `python` del sistema es 3.14; el venv se crea **siempre** con
  `py -3.11`. Anotado también en `backend/README.md`.
- Decidir en otra sesión si el contenido de `ajuste-tesis` se integra a `main`.
- Integrar `etapa/0-fundaciones` a `main` y etiquetar (`v0.1.0-etapa1` corresponde a la E1;
  para el cierre de E0 se puede usar `v0.1.0-etapa0` si se quiere un punto de retorno).
- `.gitattributes` con `eol=lf`: git avisa de conversiones CRLF/LF en Windows. No es
  urgente pero conviene fijarlo antes de que se sumen colaboradores.
- Revisar con Valentín el encabezado de `catalogo.csv` (no tiene columnas propias para
  "verificado por huella" ni "etapas"): lo formaliza el catalogador de la Etapa 1 (tarea 1.5).

### Siguiente paso concreto

Abrir la **Etapa 1 — Ingesta y validación de FPS** (`docs/plan-desarrollo.md`). Antes de
pedir el plan de esa etapa, leer el apartado de la tesis que cita su sección "Por qué"
(convención fijada esta sesión). La Etapa 1 trabaja sobre los 3 segmentos de Zverev ya
catalogados en `kinetiq-data/fase-a/segmentos/`.
