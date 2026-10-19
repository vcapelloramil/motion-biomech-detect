# Insumos para el Capítulo 8 (implicancias, conclusiones, aportes y recomendaciones) — corte 19/10/2026

**Para quién es:** otro chat que redacta el capítulo y **no ve el repositorio**. Complementa `docs/tesis/insumos-capitulo-7.md` (que trae las cifras, su estado y su origen); acá **no se repiten las tablas de resultados: se remite a la sección del Capítulo 7** donde está cada dato.
**Quién escribe:** Claude Code, a pedido de Valentín Capello Ramil (autor). **Nada de esto es redacción de tesis: es material** (qué se puede afirmar, con qué evidencia y qué no).
**Estados:** FIRME · PROVISORIO · PENDIENTE · NO MEDIDO (definidos en `insumos-capitulo-7.md` §0). **Un jugador (el autor, diestro), un iPhone 15 Pro Max, dos sesiones consecutivas (24 y 25/9/2026), cámara siempre a la izquierda del jugador:** condiciona todo lo que sigue.
Las rutas son relativas a la raíz del repositorio `motion-biomech-detect`; los videos y el corpus **no** están en el repositorio.

---

## 1. Qué se puede concluir y qué no (base para las conclusiones)

### 1.1 Se puede afirmar

| # | Conclusión posible | Evidencia (cifra) | Dónde (Cap. 7) | Estado |
| --- | --- | --- | --- | --- |
| 1 | **Un sistema de análisis biomecánico de tenis desde un celular, sin GPU, funciona de punta a punta** (celular → Cloudflare → Supabase → Render → reporte) | 18 golpes y 17 reportes reales en producción; 117–147 s por golpe de 3–4 s y 180–280 s por golpe de 4,8–7,8 s en 1 CPU / 2 GB (≈ 0,18 s por fotograma); `/health` 0.5.5 | §1, §2.3, §10.8 | **PROVISORIO** (un usuario, un golpe a la vez, una instancia) |
| 2 | **La tasa real de captura no es la nominal y hay que leerla del archivo:** el iPhone entrega ~200 fps (no 240), con 16–17 % de fotogramas perdidos; la subida con el formato por defecto la baja a 100 fps o menos | 16 originales: 199,92 a 200,96 fps (mediana 200,62); camino por defecto: 100 fps; cámara lenta sin recortar: 42,7 fps | §2.1 | **FIRME** |
| 3 | **El corpus con que se hizo la primera medición era un remuestreo a ~120 fps** (velocidades ×2, intervalos ×0,5, resolución 8,3 ms); los ángulos no cambian | 15 pares alineados por contenido: 1,665–1,675 fotogramas reales por fotograma horneado (120,1 fps) | §2.2 | **FIRME** |
| 4 | **Con los originales a tasa real, el orden de los picos de cadera y tronco depende del encuadre en el saque y en el drive, y no es confiable en el revés**; los grupos que cumplen el Criterio 1 son los sospechosos | Saque 0/8 contra 7/7 (Fisher p = 0,0002); drive 1/7 contra 3/0 (p = 0,024); revés 3/3 contra 0/5 (p = 0,18); 76 repeticiones, 2 de 6 grupos cumplen el Criterio 1 en la medición y 0 de 6 en la réplica | §2.5 | **FIRME** (conteos) · **PROVISORIO** (inferencia: exploratoria, un jugador) |
| 5 | **Con la cámara del lado no dominante, el pico de velocidad angular del brazo dominante no se puede medir en la mayoría de los golpes** | 52 de 76 (68 %); 18 de 18 en saque de tres cuartos; 0–1 de 11–12 en el revés; ninguna repetición entre 60 y 75 % de cobertura | §2.7 | **FIRME** (conteo) · **PROVISORIO** (la causa: lado de grabación, no contrastada) |
| 6 | **El error angular de rodilla y codo contra goniometría manual cumple la meta por la media** | Rodilla 8,5° y codo 12,5° (meta < 20,6°; n = 18 por articulación); p95 del codo 36,4°; codo dominante n = 2 (27,2°) | §2.6 | **PROVISORIO** |
| 7 | **La separación cadera-hombro es estable entre dos sesiones consecutivas del mismo encuadre** (comparar al jugador consigo mismo) | Criterio 3 (i): 9 de 11 combinaciones (82 %) por la regla original y 10 de 11 (91 %) por la calibrada; Evolución con los datos de hoy: 32,05° y 32,95° (cambio −0,35°, «dentro de lo habitual») | §2.6, §10.10 | **PROVISORIO** (n = 6 por sesión; métrica (ii) sin recalcular) |
| 8 | **Reglas simples sobre la pose no alcanzan para detectar automáticamente el tipo de golpe y el encuadre** | Etapa 1 de la decisión 038: tipo de golpe 98,7 % sin determinar; encuadre 14,3 % de error y 53,9 % sin determinar (criterio: ≤ 5 % y ≤ 20 %) | §2.10 | **FIRME** el resultado negativo |
| 9 | **El encuadre declarado por el usuario se equivoca:** dos de cinco archivos subidos a mano llevaban el encuadre equivocado | `IMG_6391` y `IMG_6376` declarados «perfil», son de tres cuartos | §10.1 | **FIRME** (n = 5) |
| 10 | **El sistema puede decir cuándo no puede medir y por qué** (en lugar de rellenar) | Archivo convertido rechazado (14,0 s); pico del brazo «no medido» con motivo; «golpe medido» frente a «no auditable» | §1.2, §4 | **FIRME** (funcionamiento) |

### 1.2 No se puede afirmar (y conviene decirlo)

- Que el jugador «llegue tarde con la cadera», que el **tres cuartos sea el encuadre correcto** (coincide con la literatura, pero elegirlo así sería elegir por el resultado) ni cuál de los dos encuadres mide bien: **no hay medición independiente de la pelvis**.
- Que el sistema **detecte cambios reales de técnica** (no se indujeron ni se detectaron); que los resultados **generalicen** a otros jugadores, zurdos, otros teléfonos, el lado de la raqueta o partidos.
- Que el brazo no se mide **por** el lado de la cámara (es la lectura que mejor encaja, sin contrastar), ni que **otro estimador** (YOLOv8-Pose con elevación, otros 3D) no cambiaría la dependencia del orden con el encuadre: **no se probó** (§10.2 del Cap. 7).
- Utilidad percibida (Criterio 5, I4) y umbral de latencia (Criterio 4): **no evaluados** (sin pruebas con otros usuarios; el motivo del cambio de alcance del 7/10 **no consta** en el repositorio, §10.3).
- Objetivo específico 4 (comparación con un modelo de referencia): **no realizado** y su texto no está en el repositorio (§10.5).

### 1.3 Estado de la hipótesis (resumen; el detalle y la redacción literal a cotejar con el Capítulo 1 están en `insumos-capitulo-7.md` §5)

| Componente | Veredicto sugerido |
| --- | --- |
| Ejecución en hardware convencional, sin GPU | Se confirma (n pequeño) |
| I2 · error angular < 20,6° en articulaciones proximales | Se confirma parcialmente |
| I1 · orden repetible de los picos con una cámara | Se confirma parcialmente la **repetibilidad**; **no** el orden como medida |
| I1 · cadena completa pelvis → torso → brazo | No se confirma |
| I3 · comparar al jugador consigo mismo | Se confirma parcialmente |
| Núcleo: detectar la desincronización de la cadena cinética con una cámara | **No se confirma con este material** (el sistema deja de emitir el juicio) |
| I5 · latencia tolerable / I4 · utilidad | Medida sin umbral / no evaluada |

---

## 2. Implicancias (qué se sigue de lo medido)

Cada una cita su base; ninguna es una recomendación comercial.

1. **Para el diseño de sistemas monoculares de secuenciación cinética:** el encuadre y el lado de la cámara **son una variable del instrumento**, no un detalle de uso. Un sistema que juzgue el orden sin controlar ambos puede emitir un veredicto que depende de dónde estaba el teléfono (saque: 0/8 contra 7/7). Por eso el sistema **retiró el veredicto** y quedó en medición trazable + seguimiento contra uno mismo (decisiones 035 y 036; `docs/ux/valor-sin-veredictos.md`).
2. **Para la repetibilidad como criterio de validez:** que un orden sea repetible **no** prueba que sea correcto: los dos grupos que cumplen el Criterio 1 son los que cambian con el encuadre (un sesgo fijo es perfectamente repetible). La repetibilidad solo justifica comparar a alguien **consigo mismo en el mismo encuadre**, donde el sesgo se cancela (argumento, no medición).
3. **Para la resolución temporal:** a ~200 fps reales (5 ms) y con 16–17 % de puntos interpolados, el orden de dos picos a menos de 8,33 ms **no es resoluble**; en tres cuartos más de la mitad de las repeticiones queda dentro de esa tolerancia. El instrumento tiene que **decirlo** («sin diferencia medible»), no decidir.
4. **Para los datos de captura:** leer la tasa del archivo y rechazar el convertido es un requisito de validez, no de comodidad: con el flujo por defecto del iPhone un golpe a 240 fps llega a 100 fps y **no es analizable**; con «Formato: Actual» sí.
5. **Para la carga de datos:** si el usuario declara mal (2 de 5), el sistema debe **contrastar** (hoy solo el saque) y la sesión debe poder corregirse; una detección automática con estas reglas **no** es todavía una alternativa válida (§2.10 del Cap. 7).
6. **Para el alcance declarado (R5):** todo resultado de orden, separación, ángulos y D vale **para la cámara a la izquierda de un diestro**; el otro lado se acepta pero está **sin validar** (el reporte lo dice).

---

## 3. Aportes técnicos propios (lo que no existía antes en el proyecto)

«Propio» = diseñado e implementado en este proyecto; **no** se afirma novedad frente a la literatura (no se hizo una búsqueda de antecedentes para este documento). Cada fila: qué hace, con qué evidencia y dónde está.

| # | Aporte | Qué hace | Evidencia | Archivos · decisión | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | **Lectura de la tasa real y rechazo del archivo convertido** | Lee las marcas de tiempo de cada fotograma (no asume 240 fps); pisos de aptitud 114 y 57 fps (5 % de tolerancia); si el usuario declara cámara lenta y el archivo llegó convertido, falla con motivo propio `archivo_convertido` y explica el camino que funciona | 16 originales a 199,92–200,96 fps; camino por defecto a 100 fps (no analizable); un recorte con la cámara lenta mantenida llegó a 50 fps y se rechazó en 14,0 s; el corpus no cumplía RNF-01 y se corrigió | `backend/app/engine/ingest.py`, `procesar_video.py`; `tests/unit/test_archivo_convertido.py`, `test_tasa_del_archivo.py`, `test_ingest_*.py`; `docs/resultados/tasa-real-iphone-huella.json`; decisiones 004, 028, 029 | **FIRME** |
| 2 | **Regularización temporal con lo interpolado contado** | Interpola las poses a una grilla uniforme de 240 Hz con las marcas reales **antes** de filtrar; cuenta y declara los puntos interpolados (≈ 16–17 %); no inventa más allá de 6 períodos (25 ms) | Un orden aparente de 10 ms con el eje irregular desaparecía al regularizar (nota 8 de las correcciones); trazabilidad `regularizacion` en cada reporte | `backend/app/engine/regularizacion.py`; `tests/unit/test_regularizacion.py`; decisiones 029, 030 | **FIRME** |
| 3 | **Descubrimiento y corrección del remuestreo del corpus por alineación por contenido** | Empareja originales y archivos «horneados» por fecha de creación (16/16) y los alinea por miniaturas (15 pares) para recuperar la tasa real de lo ya medido | 120,1 fps de muestreo equivalente; velocidades ×2, intervalos ×0,5; 88 repeticiones ubicadas, 86 en la meseta | `backend/app/engine/framehash.py`, `diagnostico_tasa_real_corpus.py`; `docs/resultados/corpus-real-alineacion.json`; decisión 030 | **FIRME** |
| 4 | **Regla de cobertura del 75 %** | No reporta el pico de un segmento si se midió menos del 75 % de su ventana de ±300 ms; el brazo queda «no medido» **con su motivo**, sin máximo parcial | El motor anterior mostraba un pico del brazo en 69 de 76 golpes y era un máximo parcial; con la regla faltan 52 de 76 (ninguna repetición entre 60 y 75 %: el piso no es arbitrario) | `backend/app/engine/sequencing.py`; `docs/resultados/brazo-por-golpe.md`, `brazo-por-golpe-13-10.json`; motor 0.5.1; decisiones 013, 037 | **FIRME** (conteo) |
| 5 | **Contraste del encuadre declarado con el visto (D)** | Compara el giro de la línea de hombros en la preparación con los rangos del corpus; si discrepa, avisa y retira el veredicto, sin bloquear la carga | Saque de perfil 26–42° contra tres cuartos 50–83°; 28 de 28 repeticiones bien clasificadas (misma muestra que la calibración); da tres cuartos para `IMG_6391` (59°) y para `IMG_6376` (52,9°, calculado el 19/10 sobre el archivo subido); **no distingue el encuadre del drive y va invertido en el revés** | `backend/app/engine/encuadre.py`; `tests/unit/test_encuadre.py`; `docs/resultados/paso-b-saque.md`, `deteccion-038-etapa1.md`; decisión 035 | **PROVISORIO** (solo saque; misma muestra) |
| 6 | **Tolerancia única de «ordenable» en milisegundos** | Una sola constante (1/120 s = 8,33 ms, estricta) para el producto y para la medición; el reporte la registra | El producto y la medición usaban 4,17 y 8,33 ms (dos reglas); un revés de 8,3 ms dejó de ser «ordenable» | `backend/app/engine/tolerancia_orden.py`; `trazabilidad.tolerancia_orden_ms` (contrato 1.3); decisión 032 | **FIRME** |
| 7 | **Trazabilidad por versión** | Cada reporte lleva la versión del motor, del contrato, del backend de pose y del filtro; contrato versionado 1.0 a 1.4 con pruebas que lo alinean con las migraciones | 17 reportes en la base con su versión (0.4.1 a 0.5.4); el motor cambió cuatro veces con el mismo sello 0.4.1 hasta que se detectó (decisión 032) | `backend/app/engine/version.py`, `schemas/reporte.py`; `tests/unit/test_contrato_reporte.py`; decisiones 024, 032 (RNF-02) | **FIRME** |
| 8 | **«No medido» con motivo; «golpe medido»; «sin diferencia medible»** | Un empate a la resolución es un golpe **medido**; «no auditable» queda solo para datos no confiables; un pico que falta lleva su motivo en palabras simples | Contrato 1.4; `picos_no_medidos`; la Biblioteca cuenta «N golpes medidos · K con orden distinguible · M no medibles» | `backend/app/ensamblar_reporte.py`; decisión 037 | **FIRME** |
| 9 | **Suspensión del veredicto por grupo con tres condiciones** | El veredicto solo se emite si hay (a) referencia del orden en la literatura, (b) Criterio 1 cumplido y (c) un orden que no dependa del encuadre; la suspensión (c) **gana** aunque haya referencia | Hoy ningún grupo emite veredicto (saque y drive dependen del encuadre; el revés no es confiable) | `ensamblar_reporte.py` (`RESPALDO_POR_GRUPO`, `Suspension`); decisiones 031, 035, 036 | **FIRME** |
| 10 | **Cadena de señal robusta ante la pose** | Detector de inversión de profundidad (z) (un pico imposible de 24 932 °/s lo reveló), filtrado por segmentos continuos, corte de Winter por clip, ventana anclada al pico del tronco | Pruebas unitarias y fix etiquetado `v0.3.1`; filtro de fase cero: la prueba sintética lo distingue del de una pasada (pico en 240 contra 257, +70,8 ms) | `backend/app/engine/validation.py`, `dsp.py`, `winter.py`; `tests/unit/test_validation.py`, `test_dsp.py`; decisiones 007, 009, 010 | **FIRME** |
| 11 | **Consistencia y Evolución sin veredicto** | Variación de la separación cadera-hombro dentro de una sesión (desde 4 golpes), repetibilidad del orden (desde 5 ordenables), golpe típico y golpes que se apartan; serie de sesiones del mismo jugador, gesto y encuadre, con «dentro de lo habitual» (Δ ≤ variación), sin puntaje | Con los datos de hoy: 32,05° y 32,95°, variación habitual 2,74°, cambio −0,35°; avisa lado de cámara distinto y mezcla de versiones | `backend/app/consistencia.py`, `routers/evolucion.py`; `tests/unit/test_consistencia.py`, `test_evolucion.py`; `docs/ux/valor-sin-veredictos.md` | **PROVISORIO** (n = 6 por sesión) |
| 12 | **Medición pre-registrada y atada al código** | Los criterios y las reglas se fijan y se commitean **antes** de medir; los arneses se niegan a correr con el árbol sucio y guardan el commit en el resultado; todos los resultados se informan, también los negativos | Pasos A y B, Criterios 1 a 3, decisión 038 etapa 1 (reglas en `fee1003`, resultado negativo informado entero) | `backend/app/medicion_paso_a.py`, `medicion_paso_b.py`, `medicion_deteccion.py`; `docs/plan-recalculo-corpus-tasa-real.md`; decisiones 014, 038 | **FIRME** (método) |
| 13 | **Modo de captura declarado contra el real** | Pide al usuario cómo grabó y contrasta con la tasa del archivo: un error silencioso de fps se vuelve un fallo con motivo | Bug real de fps corregido; `modo_captura` y `factor_ralentizacion` viajan en la trazabilidad | `backend/app/procesar_video.py`; `tests/unit/test_procesar_video_factor.py`; decisión 020 | **FIRME** |
| 14 | **Operación de datos: eliminar cuenta con sus archivos, respaldo con restauración probada** | `DELETE /cuenta` borra primero los archivos de los dos buckets y, si falla uno, no borra la cuenta; respaldo lógico manual restaurado en un Postgres local | «Eliminar mi cuenta» probado en producción (0 filas y 0 archivos después); restauración 16 de 16 comprobaciones; 28 pruebas de aislamiento (RLS y Storage) pasan | `backend/app/cuenta.py`, `respaldo.py`; `tools/respaldo/`; `docs/respaldo-y-restauracion.md`; `tests/integration/test_rls_aislamiento.py` | **FIRME** en lo probado |
| 15 | **El lado de la cámara como recomendación revisable** | Recomienda el lado validado (contrario a la mano dominante), acepta los dos y agrega una nota neutra si es el de la mano dominante; el esquema se espeja para zurdos | Motor 0.5.5 en producción; esquema de Cargar con tests de geometría | `backend/app/ensamblar_reporte.py` (`nota_lado_de_camara`), `frontend/src/lib/esquema-encuadre.ts`; decisión 013 | **FIRME** (funcionamiento) · el otro lado **sin validar** |
| 16 | **Instrucciones de carga basadas en el camino medido** | Cargar explica, antes de elegir el archivo, cómo subir sin que el teléfono convierta (iPhone, Android, Computadora) | Medido con una página de prueba y `inspeccionar_subidas` en 4 selectores y 3 formatos; Android «no probado en todos los modelos» | `tools/prueba-iphone/`, `backend/app/inspeccionar_subidas.py`, `frontend/src/components/instrucciones-carga.tsx`; decisiones 028, 029 | **FIRME** (iPhone) · **PENDIENTE** (Android) |

---

## 4. Recomendaciones técnicas (todas salen del repositorio; se indica la fuente)

### 4.1 Para quien use el sistema

1. **Grabar con la cámara fija, a la altura de la cadera, de día y sin contraluz, del lado contrario a la mano dominante** (a la izquierda de un diestro: es la condición con la que se calibró y validó), de perfil a 90° o de tres cuartos por delante, y **mantener el mismo encuadre y lado en todas las sesiones**: los resultados solo se comparan entre sesiones iguales. (Decisiones 013, 035; Cargar.)
2. **Subir el original sin convertir:** en el iPhone, *Opciones → Formato: Actual* o desde Archivos; no pasar el video por mensajería ni usar copias «optimizadas»; recortar solo el golpe (2 a 5 s) **sin cambiar la velocidad**; un golpe por archivo, hasta 50 MB. En Android y en computadora, seguir las instrucciones de Cargar (Android **sin probar en todos los modelos**; el sistema avisa si no llega a 120 fps). (Decisiones 028, 029.)
3. **Declarar bien el encuadre y cómo se grabó:** dos de cinco archivos subidos a mano tenían el encuadre equivocado. Hoy el sistema solo avisa en el saque. (Decisión 035; §10.1 del Cap. 7.)
4. **Leer el reporte como medición y registro, no como juicio:** el sistema **no dice si el orden es correcto**; muestra qué midió, con qué confianza y con qué resolución, y cuándo no pudo medir. Para comparar la evolución, usar **sesiones del mismo jugador, gesto, encuadre y lado**, con **≥ 6 golpes** por sesión (la consistencia empieza a calcularse desde 4 golpes y la repetibilidad del orden desde 5 ordenables; el «centro habitual» desde 3 sesiones). (Decisión 036; `valor-sin-veredictos.md`.)
5. **Esperar un pico del brazo «no medido» con la cámara del lado no dominante** (68 % de los golpes del corpus): no es una falla del usuario. (Decisión 013.)
6. **Alcance:** saque, drive y revés, un jugador por video, entrenamiento; **zurdos y el lado de la raqueta no están validados**. Subir solo videos propios o con consentimiento: el sistema pide consentimiento en el registro pero **no por cada video de un tercero**. «Eliminar mi cuenta» borra los datos y los archivos. (`/privacidad`; correcciones del Cap. 4, fila 27.)

### 4.2 Para quien continúe el desarrollo

1. **Respetar el congelamiento del motor** (previsto el 24/10) y, después, **subir la versión del motor y del contrato ante cualquier cambio de `engine/` o `ensamblar_reporte.py`** (RNF-02); no reintroducir veredicto, puntaje ni color de estado del orden. (CLAUDE.md; decisiones 032, 036; `estado-sin-veredictos`.)
2. **Publicar con respaldo y camino de vuelta, sin análisis en curso** (`docs/publicacion-y-vuelta-atras.md`): servidor primero y frontend después; las migraciones y el frontend se aplican a mano; Render redeploya al hacer push a `main`.
3. **Mantener el método:** reglas y criterios fijados y commiteados antes de medir, partición por sesión, arnés que se niega a correr con el árbol sucio, y **todo resultado informado, también el negativo**. Una regla elegida mirando las dos sesiones del corpus **ya no se puede evaluar con ellas**. (Decisión 038, `deteccion-038-etapa1.md`.)
4. **Conseguir datos nuevos antes de volver a intentar la detección automática o calibrar D:** una sesión con saque, drive y revés (≥ 12 por celda, otro día y lugar, anotando si el revés es a una o dos manos), y la sesión del lado derecho (`docs/protocolo-sesion-lado-derecho.md`). Revisar a mano los **cinco revés de perfil** con la muñeca alta en el contacto. Para el saque, medir en el **contacto** y no en la preparación (en este jugador la altura máxima llega ahí).
5. **Pendientes de medición, en este orden** (`plan-mvp-punta-a-punta.md` §9): calibrar D para drive y revés (con la orientación invertida del revés), recalcular el Criterio 3 (ii) con el tiempo real, revisar `RESPALDO_POR_GRUPO` (b) con las cifras del Paso B, y **re-medir el Criterio 2 con el motor 0.5.x** y con más goniometría del codo dominante (n = 2).
6. **Rendimiento y cola:** el costo es ~0,18 s por fotograma y la cola es de a un golpe (12 golpes: 43,7 min de punta a punta, el último esperó 33,7 min). Palancas, en el orden de la decisión 006: bajar `model_complexity` (exige repetir el Criterio 2), después ONNX Runtime/Vía A, y menor resolución. Más de una instancia requiere revisar la recuperación al arrancar (hoy no cubre dos instancias).
7. **Seguridad y operación (todo declarado como no encontrado en el código al 13/10):** integración continua con pruebas y verificación de secretos (hoy solo existe el keep-alive de Supabase), validación del tipo de archivo por firma binaria, limitación de tasa, copia del respaldo fuera de la PC y con `pg_dump`, restauración en un proyecto Supabase real, correo con otros proveedores y límite de envíos. (Correcciones del Cap. 4, filas 28, 32 y 33.)
8. **Corregir los datos y los documentos que arrastran el error de encuadre:** la sesión `3a101dd3` (fecha equivocada), los sitios que llaman «perfil» a `IMG_6376` (`criterio4-latencia.md`, correcciones nota 8), y no volver a subir `IMG_6376` ni `IMG_6391` como perfil.
9. **Pruebas que faltan respecto del Capítulo 4:** extremo a extremo (no hay Playwright), RNF-05 (cerrar el navegador durante el procesamiento) y un caso de 30 fps en RNF-01. (Cap. 7 §10.4.)
10. **Mover un golpe entre sesiones y poner el lado de la cámara en la clave de Evolución** (aprobados el 15/10 en la 038, sin implementar): hoy Evolución solo avisa si cambia el lado.

### 4.3 Para quien investigue

1. **La pregunta abierta es cuál encuadre mide bien el orden cadera-tronco:** hace falta una **medición independiente de la pelvis** (cintas de color con un teléfono, marcadores, sensores inerciales o captura óptica) o la **grabación simultánea desde dos ángulos** (descartada por ahora: no hay un segundo teléfono). (Decisión 036; `protocolo-saques-tres-cuartos.md`; Cap. 7 §7.3.)
2. **Comparar estimadores de pose sobre el mismo corpus** (MediaPipe contra YOLOv8-Pose con elevación 2D→3D u otros 3D): **no se probó**; la interfaz `PoseBackend` lo permite. Sirve para separar «sesgo del estimador» de «movimiento». (Decisión 005; Cap. 7 §10.2.)
3. **Grabar del lado de la raqueta** y con **zurdos** para contrastar la explicación del brazo no medible (68 %) y la calibración de D; **más de un jugador, nivel y día**, con una muestra independiente. (Decisión 013.)
4. **Potencia y estadística:** n = 6 por celda y sesión, repeticiones de una toma no independientes, p exploratorios sin corrección por comparaciones, regla del 75 % que coincide con el azar con n = 6 (decisión 014). Un diseño nuevo debería fijar n, la unidad de análisis y la corrección de antemano.
5. **Definición del «orden»:** el motor usa la velocidad angular total del vector; el giro axial da el mismo sentido y, en el saque de perfil, una diferencia mayor (−129 ms contra −62 ms). Decidir cuál es el constructo. (Cap. 7 §2.4, §7.2.)
6. **Resolución temporal:** ~200 fps reales con 16–17 % de pérdida; propagar la incertidumbre del hueco interpolado (≤ 6 ms) a la decisión de «ordenable», o capturar con una fuente de 240 fps reales. (Cap. 7 §7.3.)
7. **El brazo:** el vector hombro→codo es un proxy de orientación, **no la rotación interna**, y no es comparable con los valores de Fleisig (decisión 011); medir la rotación interna requiere otro método.
8. **Detección automática de gesto y encuadre** con más datos y reglas robustas a valores atípicos (medianas y fracciones), con un «no determinado» explícito; el segundo camino de la 038 («el sistema propone y el usuario confirma») no exige el 5 %. (Cap. 7 §2.10.)
9. **Utilidad y usabilidad con usuarios reales** (entrenadores, kinesiólogos): Criterio 5, I4 y RNF-08 están sin evaluar.

---

## 5. Mejoras pendientes («agregados de mejora») y su estado al 19/10/2026

| # | Mejora | Fuente | Estado |
| --- | --- | --- | --- |
| 1 | Detección automática de tipo de golpe y encuadre en la carga | decisión 038; `plan-mvp` §9.5 | Diseño A aprobado (15/10); etapa 1 de validación **negativa** (16/10); etapa 2 **no propuesta**; integración solo si valida antes del 23/10 |
| 2 | Detección del lado de la cámara | decisión 038 (c) | **Sin hacer:** no se puede validar con el corpus (una sola clase); necesita la sesión del lado derecho |
| 3 | Sesión con la cámara del lado derecho (girando al jugador) y cintas | `protocolo-sesion-lado-derecho.md` | Protocolo escrito; **grabación: NO CONSTA** (la hace Valentín cuando el clima lo permita) |
| 4 | Cintas de color: medición independiente de la pelvis | `plan-mvp` §9.4 | **Registrada, sin diseñar** (tentativa) |
| 5 | Calibrar D para drive y revés | `plan-mvp` §9.1 | **Explorado, no calibrado** (D no distingue el drive y va invertido en el revés) |
| 6 | Criterio 3, métrica (ii) con el tiempo real | `plan-mvp` §9.2 | Pendiente |
| 7 | `RESPALDO_POR_GRUPO` (b) con las cifras del Paso B | `plan-mvp` §9.3 | Pendiente (no cambia ningún veredicto: la suspensión gana) |
| 8 | Re-medir el Criterio 2 con el motor 0.5.x; más goniometría del codo dominante | Cap. 7 §2.6 | Pendiente |
| 9 | Lado de la cámara en la clave de Evolución; mover un golpe entre sesiones | decisión 038 (15/10) | Aprobado, **sin implementar** |
| 10 | Ventana específica por gesto; marca de instante medido o reconstruido con la incertidumbre del hueco | Cap. 7 §7.3 | Pendiente |
| 11 | Alertas con umbral y referencia bibliográfica (E5.1) | plan; decisión 036 | **No** (falta referencia; R4) |
| 12 | Vía A (YOLOv8-Pose/ONNX) | decisiones 005, 006 | **No implementada** |
| 13 | Reproductor sincronizado; PDF generado en el servidor; retención de 7 días (`eliminado_en`) | correcciones 21, 26, 29 | **No** (video con esqueleto en cámara lenta fija, impresión del navegador y bucket `artefactos` aparte) |
| 14 | Reintento desde `parcial`; control contra historial | decisiones 020, 022 | Pendiente |
| 15 | Notificaciones en tiempo real (hoy polling); cola con más de una instancia | correcciones 25 | **No** |
| 16 | Respaldo: copia fuera de la PC, `pg_dump`, restauración en Supabase real | `respaldo-y-restauracion.md` | Pendiente (necesita la contraseña de la base) |
| 17 | Correo: probar con otro proveedor, límite de envíos por hora, alias de contacto | decisión 034 | Pendiente |
| 18 | Integración continua con pruebas y secretos; validación por firma binaria; limitación de tasa | correcciones 28, 32 | **No encontrado en el código** |
| 19 | Consentimiento específico por video de un tercero | correcciones 27 | **No** |
| 20 | Pruebas de extremo a extremo (Playwright), RNF-05 y un caso de 30 fps | Cap. 7 §10.4 | **No existen** |
| 21 | Instrucciones de Android en más modelos | `instrucciones-carga.tsx` | **No probado** |
| 22 | PDF impreso en papel; Evolución con los datos finales | `bitacora.md` 16/10 | **Sin ver** |
| 23 | Costo marginal por análisis y costo acumulado de Render | Cap. 7 §10.8 | **NO MEDIDO** |
| 24 | Validación de utilidad con un entrenador o kinesiólogo (Criterio 5) | `plan-mvp` §4 | Pendiente («no evaluado, trabajo futuro» es la alternativa) |
| 25 | Congelar la versión que se defiende (etiqueta de git) | bitácora 16/10 | Prevista el **24/10**; **no existe todavía** |
| 26 | Limpieza y nueva subida del corpus con el motor congelado (corregir la fecha de la sesión `3a101dd3`) | `demo-guion.md` §C | Prevista el 25–26/10 |

---

## 6. Dónde está cada cosa

`docs/tesis/insumos-capitulo-7.md` (cifras, estados y origen; §9 delta desde el 13/10, §10 pendientes resueltos) · `docs/tesis/correcciones-pendientes-capitulo-4.md` (correcciones del Cap. 4) · `docs/decisiones/` (001 a 038) · `docs/resultados/` ·
`docs/plan-mvp-punta-a-punta.md` §8 y §9 · `docs/bitacora.md` (primera entrada) · `docs/ux/valor-sin-veredictos.md` · `docs/publicacion-y-vuelta-atras.md` y `docs/respaldo-y-restauracion.md`.
