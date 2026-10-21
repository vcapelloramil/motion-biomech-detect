# Guion de la demo (paso 8 del plan §8)

**Cuándo:** 28–30/10/2026 (decisión de Valentín del 12/10). **A quién:** los profesores del tribunal. **Duración:** 10 a 15 minutos de demostración + preguntas.
**Estado de este documento:** borrador para ensayar; **no se programó nada** para armarlo. Está escrito sobre lo que **ya está en producción**: el servidor con el motor 0.5.5 (`/health` verificado el 15/10/2026) y el frontend, que Valentín republica.
Las cifras que se citan salen de `docs/resultados/` y de las decisiones; la fuente está al final de cada una (§E).

## Lo que la demo tiene que dejar (tres mensajes, en este orden)

1. **Funciona de punta a punta**, desde el celular, sin GPU y en minutos: video → medición trazable → seguimiento.
2. **Sabe cuándo no puede afirmar:** no emite veredicto del orden porque, con una sola cámara y este material, **depende del encuadre**. Eso es un resultado, no un fallo.
3. **El valor es medición y seguimiento contra uno mismo** en el mismo encuadre, con la confianza y la versión de cada número.

**Vocabulario (regla R2):** se *documenta*, *se midió*, *no se pudo medir*. Nunca "diagnostica", "predice", "previene", "riesgo de lesión", "correcto/incorrecto" ni "bandera roja". La etiqueta es **"Solo registrado"**.

---

## A. Guion (≈ 13 minutos)

> **Preparación (antes de empezar):** sesión ya iniciada en la **cuenta de la demo**, navegador a pantalla completa y zoom del 125 %, pestañas abiertas en este orden: Inicio · Biblioteca · un reporte · una sesión · Evolución · Tecnología.
> El archivo para la carga en vivo ya elegido en una carpeta (ver §C, paso 5). Los PDF y las capturas de respaldo, abiertos en otra ventana (§D).

| Min | Pantalla | Qué mostrar | Qué decir |
| --- | --- | --- | --- |
| **0:00–1:00** | **Inicio** | La promesa y *"Lo que no hace"* | "KinetiQ mide un golpe de tenis con una sola cámara, a partir de un video de celular. **No te dice si tu técnica es buena o mala**: te dice qué midió, con cuánta confianza, y cuánto cambia de una sesión a otra." |
| **1:00–2:30** | **Cargar** | El formulario; el **esquema de encuadre** (cámara a la izquierda de un diestro, tres cuartos por delante) con *"Recomendado"*; el aviso de *Opciones → Formato: Actual*; **elegir el archivo y enviar** | "El iPhone dice 240 fotogramas por segundo y entrega unos 200: el sistema **lee la tasa real del archivo**, no la que dice el usuario. Y si el teléfono convirtió el video, lo **rechaza** en vez de medir mal." Mientras sube: "Mientras procesa, les muestro un golpe ya procesado." |
| **2:30–4:30** | **Reporte** (ya procesado) | **Tres momentos** con el esqueleto (cadera, tronco, brazo); el **video en cámara lenta**; la frase de secuencia | "Esto es el instante en que cada segmento llega a su velocidad máxima: son fotogramas reales del golpe, no una animación." |
| | | Las tarjetas **"Solo registrado"**; si tiene la nota del lado de la cámara, leerla | "Acá **no hay veredicto**. Más adelante les explico por qué: es una decisión basada en lo que medimos." |
| | | **Ver detalle técnico**: magnitudes con confianza, tolerancia (8,33 ms), tasa real, fotogramas interpolados, versión del motor | "Cada número lleva su confianza y de qué versión del motor salió: se puede auditar." |
| | | El **pico del brazo "no medido"** con su motivo | "El codo del brazo que saca queda tapado por el torso en el armado del golpe. El sistema dice **que no pudo** y por qué; no inventa el dato." |
| **4:30–5:30** | **Procesando → Reporte** (la carga en vivo) | Si ya terminó, abrirlo; si no, seguir con la siguiente pantalla y volver | "Un golpe de 3–4 s tarda **entre 2 y 2,5 minutos**." *(medido: 117 y 147 s en el servidor de pago)* |
| **5:30–7:30** | **Vista de sesión** | **"Tus golpes entre sí"**: variación de la separación cadera-hombro, "mismo orden en N de M", golpes medidos; el **golpe típico**; el golpe que **se aparta** | "Con varios golpes el sistema compara al jugador **consigo mismo**: cuánto varía entre golpes. Tampoco dice cuál orden es el correcto: dice **si fue el mismo**." |
| **7:30–9:30** | **Evolución** (Biblioteca → *Ver mi evolución*) | Las dos sesiones (24 y 25/9): mediana por sesión, la **variación habitual**, "se mantuvo / aumentó / disminuyó", los **huecos "sin dato"** | "Aumentó, disminuyó, se mantuvo: **no es mejor ni peor**. Se compara contra la variación del propio jugador. Si falta un dato, queda un hueco: no se interpola." |
| **9:30–12:00** | **Tecnología / resultados** *(o diapositiva)* | La tabla del orden por encuadre (abajo) | Ver **§A.1: lo que hay que decir de los límites** |
| **12:00–13:00** | **Perfil** | **Tu actividad**, **Descargar mis datos**, **Eliminar mi cuenta** (*solo mostrar el botón, no usarlo*) y **Privacidad** | "El usuario es dueño de sus datos: los descarga y los borra, con los archivos incluidos (Ley 25.326)." |
| **13:00** | Cierre | — | "Lo que queda: medición trazable y seguimiento contra uno mismo. Lo que sigue: validar el lado de cámara, medir la pelvis con una referencia independiente y detectar automáticamente el golpe y el encuadre." |

### A.1 Lo que hay que decir de los límites (no se esconde: es el resultado)

Decirlo en este orden y con estas cifras (todas medidas con los originales del iPhone a tasa real, Paso B; **un jugador, dos sesiones, la cámara siempre a la izquierda**):

1. **El orden cadera → tronco cambia con el encuadre.** En el saque: de perfil, el tronco llegó primero en **8 de 8** repeticiones ordenables y la cadera en 0; en tres cuartos, la cadera llegó primero en **7 de 7** (Fisher exacto p = 0,0002, exploratorio). En el drive: 1 de 8 contra 3 de 3 (p = 0,024). En el revés no sigue ese patrón.
2. **Un movimiento físico no depende de la cámara:** al menos uno de los dos encuadres mide mal, y sin una medición independiente de la pelvis **no se puede decir cuál**. Elegir el que coincide con la literatura sería elegir por el resultado.
3. **Los grupos que "cumplen" el criterio de repetibilidad (saque y drive de perfil, 1a = 0,83) son justamente los sospechosos:** ser repetible no es ser exacto; un sesgo fijo también es repetible. **Por eso el sistema no emite veredicto.**
4. **Y eso tiene un valor:** el sesgo es fijo por encuadre, así que al compararse con uno mismo en el mismo encuadre se cancela. Es el seguimiento.
5. **Otros límites, sin que se los pregunten:** resolución de ~5 ms por fotograma (en tres cuartos más de la mitad de las repeticiones queda dentro de la tolerancia de 8,33 ms: "no se puede saber cuál fue primero"); error angular medio **8,5° en la rodilla y 12,5° en el codo** contra goniometría manual (con un percentil 95 del codo de 36,4°); el pico del brazo no se pudo medir en **52 de 76** repeticiones (68 %); **un solo jugador, un teléfono, un lado de cámara**.
6. **Qué se hizo con eso:** se retiró el veredicto, se avisa si el encuadre declarado no coincide con el visto (saque), y la nota del lado de cámara. **Trabajo futuro:** otro lado de la cámara, cintas de color como referencia de la pelvis, más jugadores.

### A.2 Preguntas que van a hacer (y qué responder)

| Pregunta | Respuesta corta (y de dónde sale) |
| --- | --- |
| "¿Entonces no sirve para corregir la técnica?" | "No juzga. Mide y compara contra uno mismo. Decir cuál orden es el correcto exige una referencia independiente que todavía no tenemos." (decisiones 035 y 036) |
| "¿Contra qué lo validaron?" | "Los ángulos, contra goniometría manual ciega sobre 18 fotogramas por articulación (rodilla 8,5°, codo 12,5° de media). El orden, **no tiene** referencia independiente: por eso no hay veredicto." (Criterio 2; decisión 036) |
| "¿Y con otros jugadores?" | "Todo es de un jugador y dos sesiones. Es un límite declarado; no generaliza." (insumos Cap. 7, §7) |
| "¿Por qué MediaPipe y no YOLOv8?" | "YOLOv8-Pose es 2D y necesita un modelo de elevación; MediaPipe da 3D directo con una dependencia. La interfaz de pose es intercambiable; YOLOv8 está previsto y no implementado." (decisión 005) |
| "¿Por qué 200 y no 240 fps?" | "El iPhone captura ~200 fps reales (199,9–201,0 en 16 grabaciones): pierde fotogramas casi periódicos. El motor lo lee del archivo y regulariza a una grilla de 240 Hz declarando cuántos puntos interpola (16–17 %)." (decisiones 029 y 030) |
| "¿Cuánto cuesta y cuánto tarda?" | "El servidor de pago es USD 25 por mes; un golpe de 3–4 s tarda 117–147 s. En el plan gratuito tardaba 11 minutos y no alcanzaba la memoria." (decisión 023; criterio4-latencia) |
| "¿Qué pasa con la privacidad?" | "Consentimiento en el registro, lectura solo de lo propio por políticas de la base, descargar y eliminar la cuenta con los archivos, y una página de Privacidad. No hay borrado automático a los 7 días: está diferido." (correcciones del Cap. 4, filas 26 y 27) |
| "¿Es un producto médico?" | "No: documenta lo medido y no diagnostica ni predice; el vocabulario está restringido por diseño." (R2, Cap. 3 y 4) |
| "¿Por qué no hay puntaje?" | "El puntaje era la suma de juicios del orden; sin esos juicios no hay base para un número." (decisión 036) |
| Una pregunta que no se sabe | "No lo medimos; está en las limitaciones del capítulo 6. Lo anoto." **No inventar una cifra.** |

---

## B. Checklist del día anterior (D−1; si la demo es el 28/10, el 27/10)

**Congelar:** el **motor** quedó congelado el 24/10 (§C) y los datos de la demo se subieron el 25–26/10. Desde la mañana de D−1 **no se publica nada** (ni servidor ni frontend). Si hay algo que arreglar, se arregla hacia atrás con `docs/publicacion-y-vuelta-atras.md`, no hacia adelante.

| ☐ | Qué | Cómo se comprueba |
| --- | --- | --- |
| ☐ | **Servidor al día y sano** | `GET /health` → `estado: ok` y `version_motor: 0.5.5`, tres veces seguidas |
| ☐ | **Render en Standard** (no Free) | Panel de Render: plan *Standard*; `render.yaml` dice `plan: standard` |
| ☐ | **Frontend publicado = commit de `main`** | Abrir `https://kinetiqtennis.me` en ventana privada: Perfil muestra **"Tu actividad"**; Cargar muestra **"Recomendado"** |
| ☐ | **Sin análisis en curso ni fallidos sobrantes** | `tools/respaldo/estado_de_la_base.py`: "EN CURSO: ninguno", "FALLIDOS: 0" |
| ☐ | **Datos de la demo** (ver §C): 4 sesiones en la cuenta de la demo, todas con motor 0.5.5 | `estado_de_la_base.py`: "VERSIONES DEL MOTOR: {'0.5.5': …}" y sin otras versiones |
| ☐ | **Evolución sin aviso de mezcla de versiones** | Abrirla: dos puntos y ningún aviso de versión |
| ☐ | **Respaldo del día** hecho y verificado | `python -m app.respaldo exportar …` → "ÍNTEGRO"; copia a un disco externo |
| ☐ | **Correo** | Probar "Olvidé mi contraseña" con una dirección de **otro proveedor** (no la de siempre): llega y el enlace funciona |
| ☐ | **Dominio y certificado vigentes** | El sitio abre sin advertencia; el dominio vence al año (anotar la fecha) |
| ☐ | **El PDF imprime bien** | "Descargar PDF" de un reporte y de una sesión → *Guardar como PDF*: A4 vertical, imágenes cargadas, sin cortes |
| ☐ | **Material de respaldo** (§D) en una carpeta local **sin red** | capturas de cada pantalla, los dos PDF, el video de pantalla del recorrido completo, `paso-b-resumen.md` |
| ☐ | **Ensayo completo cronometrado** (dos veces, la última con la carga en vivo) | ≤ 13 min; anotar dónde se pasa |
| ☐ | **Equipo** | Notebook cargada y con cargador; el teléfono como punto de acceso (*hotspot*); adaptador de video; navegador con la sesión iniciada y las contraseñas guardadas **desactivadas** en pantalla |
| ☐ | **Archivo para la carga en vivo** | Un recorte del corpus de < 50 MB, ya probado, en el escritorio (§C, paso 5) |
| ☐ | **Cuenta de la demo limpia de notificaciones** | Sin pestañas de otras cuentas, sin mensajes del sistema, modo no molestar |
| ☐ | **Etiquetar el commit** | `git tag demo-AAAA-MM-DD` sobre `main` (para volver exactamente a lo ensayado) |

---

## C. Plan de limpieza y nueva subida (se ejecuta DESPUÉS del congelamiento del motor)

**Regla:** las sesiones de la demo se suben **una sola vez**, con el motor ya congelado. Si el motor cambia después de subirlas, quedan con otra versión y habría que volver a subirlas (y Evolución avisaría
"versiones distintas"). Por eso:

| Fecha | Qué |
| --- | --- |
| **ya** (no depende del motor) | Eliminar las cuentas de prueba vacías y, con ellas, los 15 archivos huérfanos (paso 0) |
| **23/10 — límite de la detección automática** | Lo que no esté **validado e integrado** (tipo de golpe y encuadre, decisión 038, actualización del 16/10) queda para después de la demo |
| **24/10 — congelamiento del motor** | Se **congela**: `engine/version.py` sin cambios pendientes, `git tag motor-congelado-<versión>`. Después de esa fecha, **ningún cambio en `engine/` ni en `ensamblar_reporte.py`** |
| **25–26/10** | Limpieza y nueva subida (pasos 1 a 8 de abajo) |
| **26–27/10** | Ensayo cronometrado con los datos definitivos |
| **27/10 (D−1)** | Checklist de §B y congelamiento total (nada se publica) |
| **28–30/10** | Demo |

**Estado al 15/10/2026** (`tools/respaldo/estado_de_la_base.py`, solo lectura; después de que Valentín eliminó una cuenta de prueba y verificado que no quedaron filas ni archivos): **3 cuentas.** La principal (B, "Valentín", creada el 9/10)
tiene **las 8 sesiones**, 18 videos y 65 archivos (635 MB). **A** (creada el 6/10, nombre "valencapello", último ingreso el 9/10) no tiene sesiones y guarda **15 archivos sueltos de la página de prueba del iPhone (245 MB)**. **C** (creada el 15/10,
rol "entrenador") no tiene sesiones ni archivos. Versiones del motor mezcladas en B: 0.4.1, 0.5.0, 0.5.2, 0.5.3 (12 golpes) y 0.5.4.

**Por qué hay que limpiar B:** dos sesiones del 24/9 y dos del 25/9 de saque en tres cuartos darían **puntos duplicados** en Evolución, y las versiones mezcladas disparan el aviso de versiones distintas del motor.

**Qué hace cada uno:** *vos* borrás y subís desde la aplicación; *yo* verifico con la herramienta de solo lectura después de cada paso y te aviso si algo no coincide.

| Paso | Qué hacés | Verificación (yo) |
| --- | --- | --- |
| **0** *(ya; no depende del motor)* | **Eliminar las cuentas de prueba vacías A y C**: entrar a cada una → Perfil → **Eliminar mi cuenta** → escribir `ELIMINAR`. (Descargá los datos antes si querés conservar algo.) | La cuenta ya no figura; **0 archivos huérfanos**; 0 filas sin dueño |
| **1** *(25/10)* | **Respaldo nuevo y verificado** (`python -m app.respaldo exportar …`) y copia a un disco externo. Borrar es irreversible | Manifiesto "ÍNTEGRO" |
| **2** | **En la cuenta B, eliminar las 8 sesiones** (Biblioteca → cada sesión → **Eliminar sesión**; borra los archivos de los dos buckets y las filas): las 6 de un golpe de prueba (24/9 saque perfil, 24/9 revés tres cuartos, 24/9 saque tres cuartos de 0.5.4, 25/9 revés fallido, 25/9 revés tres cuartos, 25/9 saque perfil) y las dos del corpus procesadas con 0.5.3 | Biblioteca vacía; B sin sesiones, sin videos y **sin archivos** |
| **3** | **Subir la sesión 1** (en este orden de datos): *Jugador:* Valentín (mano derecha) · *Golpe:* **Saque** · *Encuadre:* **Tres cuartos** · *Lado de la cámara:* **izquierda** · *¿Cómo lo grabaste?:* **Cámara lenta de 240 fps** · *Fecha:* **24/09/2026**. *Archivos* (los 6): `20260924_saque_trescuartos_toma01_golpe1.mov` … `golpe6.mov` de `Desktop\corpus-originales-reales\recortes-evolucion\`. Se eligen desde la computadora (no hace falta "Formato: Actual"). **Esperar a que terminen los 6** (≈ 12–15 min: de a uno en el servidor) | 6 golpes medidos, **todos con la misma versión del motor** |
| **4** | **Subir la sesión 2:** los mismos datos pero *Fecha:* **25/09/2026** y los 6 archivos `20260925_saque_trescuartos_toma02b_golpe1.mov` … `golpe6.mov`. **Esperar** (≈ 12–15 min) | 6 golpes medidos, misma versión |
| **5** | **Subir un drive y un revés** (ya cortados y verificados, en `Desktop\corpus-originales-reales\recortes-demo\`): **drive** → *Golpe:* Drive · *Encuadre:* **De perfil** · *Lado:* izquierda · *Fecha:* 25/09/2026 · archivo `20260925_drive_perfil_toma02_golpe1.mov`. **Revés** → *Golpe:* Revés · *Encuadre:* **Tres cuartos** · *Lado:* izquierda · *Fecha:* 25/09/2026 · archivo `20260925_reves_trescuartos_toma02_golpe1.mov` (cada uno en su sesión de un golpe). Si un reporte sale con el orden "no medido", probar con otro golpe de los 6 de esa carpeta | 2 sesiones de un golpe, medidos, misma versión |
| **6** | **Mirar todo en la aplicación:** Biblioteca (4 sesiones), vista de sesión, **Evolución** (dos puntos, **sin** aviso de versiones), **Perfil → Tu actividad** (4 sesiones, 14 golpes) y un PDF de golpe y de sesión | `estado_de_la_base.py`: una sola versión del motor, **0 en curso, 0 fallidos, 0 huérfanos** |
| **7** | **Dejar el archivo de la carga en vivo:** un recorte **no subido**, por ejemplo `20260925_saque_trescuartos_toma02c_golpe1.mov`. En la demo se dice que **es del corpus** y se sube con la fecha real de la grabación; **se borra la sesión después**, para no dejar un tercer punto en Evolución | — |
| **8** | **Respaldo final** y **congelar** (`git tag demo-…`; no se publica más) | Manifiesto "ÍNTEGRO" |

**Tiempo estimado (21/10/2026, con las mediciones reales de `tools/respaldo/tiempos_y_origen_de_las_subidas.py`):** el análisis es **de a un golpe por vez** (1 CPU en Render Standard). Se suben **14 golpes** (pasos 3 a 5: 6 + 6 + 1 drive + 1 revés).

| Qué | Medido | Golpes | Tiempo |
| --- | --- | --- | --- |
| Saque de tres cuartos (≈ 1 000–1 500 fotogramas, 0,18–0,19 s por fotograma) | procesamiento **mediana 193 s** (24/9) y **246 s** (25/9; máximo 280 s) | 12 | **39 a 56 min** |
| Drive y revés recortados (≈ 600 fotogramas) | 14 a 125 s (una vez, 677 s) | 2 | **1 a 4 min** (hasta 23 min si pasa como el 677 s) |
| **Total de análisis** | | **14** | **≈ 40 a 60 min; peor caso ≈ 80 min** |

*Contraste:* el 13/10 los 12 golpes de las dos sesiones tardaron **43,7 min de punta a punta** (3,6 min por golpe); 14 golpes serían ≈ 51 min. La nota anterior de «≈ 35 min» estaba **corta**: solo contaba 12–15 min por sesión.

**Cuánto dura toda la limpieza + nueva subida** (el análisis corre mientras se cargan los formularios y se verifica):

| Paso | Tiempo |
| --- | --- |
| 1 · Respaldo nuevo y verificado (≈ 840 MB) y copia al disco externo | 15 a 25 min |
| 2 · Eliminar las 8 sesiones | 5 a 10 min |
| 3 a 5 · Cargar los formularios y subir los 14 archivos (el análisis arranca con el primero) | 10 a 15 min de carga; **el análisis termina a los 40 a 80 min del primer envío** |
| 6 · Mirar todo en la aplicación y los dos PDF; `estado_de_la_base.py` | 15 a 20 min |
| 7 y 8 · Dejar el archivo de la carga en vivo; respaldo final | 15 a 20 min |
| **Total** | **≈ 1 h 35 min a 2 h 40 min (con margen: 3 h)** |

**A qué hora arrancar el 25/10:** **a las 9:00** (domingo, sin otras tareas): el análisis termina antes de las 11:00 y todo cierra antes del mediodía, con margen hasta las 12:30. **No empujar nada a `main` mientras haya análisis en curso** (Render reinicia y corta el que esté corriendo): verificar con `estado_de_la_base.py` («EN CURSO: ninguno») antes de cada push. Si el 26/10 hace falta repetir algo, las dos sesiones de saque se pueden volver a subir en ≈ 1 h.
**Si el motor cambia después de congelarlo:** repetir los pasos 1 a 8 (los pasos 3 a 5 dependen de la versión). No se sube nada antes del congelamiento.

**Qué NO va a la cuenta de la demo:** las sesiones del lado derecho (`docs/protocolo-sesion-lado-derecho.md`) —son un corpus aparte, y la aplicación avisaría que cambia el lado—, ni sesiones de prueba de ninguna clase.
**Qué NO se borra:** la cuenta B, el respaldo (`kinetiq-data\respaldos`), ni los originales del corpus (`corpus-originales-reales`, fuera del repositorio).

---

## D. Plan B (si algo falla en vivo)

**Regla general:** no se arregla en vivo. Se dice una frase, se pasa al material ya procesado y se sigue el guion. Un sistema que **dice que no pudo** es parte del mensaje.

| Qué falla | Cómo se nota | Qué hacer en el momento | Cómo se previene |
| --- | --- | --- | --- |
| **Render lento** (la carga en vivo no termina) | Procesando pasa de 3 minutos | "Un golpe tarda ~2 min cuando el servidor está caliente; mientras tanto, miremos uno ya procesado." Pasar al **reporte ya procesado** | El reporte principal **ya está procesado**; la carga en vivo es un extra, no el hilo del guion |
| **Render caído** (`/health` no responde) | Cargar y Evolución fallan; **Biblioteca, reportes y sesiones siguen abriendo** (se leen directo de la base) | Continuar con lo que abre; para Evolución usar la **captura/PDF de respaldo** | `/health` en D−1 y 10 minutos antes; no publicar el día anterior |
| **Supabase lento o pausado** | El ingreso o la Biblioteca no cargan | Mostrar capturas y el **video de pantalla** del recorrido | El workflow `keep-alive` ya evita la pausa por inactividad; abrir la sesión **antes** y no cerrarla |
| **No hay red en la sala** | Nada carga | Hotspot del teléfono; si no, el **video de pantalla** completo y los PDF locales | Probar el hotspot en D−1 |
| **El sitio no abre en el dominio** | Error de dominio o certificado | La dirección `workers.dev` del Worker (anotada en el panel de Cloudflare) | Anotar esa dirección; no cambiar nada de DNS en D−1 |
| **Un cambio publicado rompe algo** | Pantalla en blanco o error 5xx | `wrangler rollback` y, si hace falta, rollback de Render (`docs/publicacion-y-vuelta-atras.md`) | Congelar desde D−1 |
| **El archivo se rechaza** (más de 50 MB o "archivo convertido") | Mensaje de error en Cargar | "Esto es justamente el comportamiento que queremos: no mide lo que no puede medir." Usar el archivo de respaldo | Probar el archivo en el ensayo |
| **El correo no llega** (si se muestra el registro) | No hay mensaje de confirmación | No mostrar el registro en vivo: usar la cuenta ya creada y la **captura** del correo | Probar con otro proveedor en D−1 |
| **El reporte muestra algo que no se esperaba** (la nota del lado de cámara, un pico "no medido") | — | Leerlo: "Esto es el sistema diciendo lo que no pudo afirmar." | Abrir todos los reportes del guion en el ensayo |
| **El PDF no imprime bien** | Imágenes cortadas | Mostrar el PDF ya generado | Generarlos en D−1 |
| **Una pregunta sin respuesta** | — | "No lo medimos; está en las limitaciones." | §A.2 |

**Material de respaldo (carpeta local, sin red):** capturas de cada pantalla del guion · PDF de un reporte y de una sesión · video de pantalla del recorrido completo (≈ 10 min) · `docs/resultados/paso-b-resumen.md` y `paso-a-resumen.md`
impresos o en PDF · esta guía. **Dos pestañas con los reportes del guion ya abiertas** antes de empezar.

---

## E. De dónde sale cada cifra que se dice

| Cifra | Fuente |
| --- | --- |
| Tasa real ~200 fps (199,92–200,96 en 16 originales) | `docs/resultados/corpus-real-alineacion.json`; decisión 030 |
| Saque 0/8 y 7/7; drive 1/8 y 3/3; revés sin patrón; Fisher 0,0002 y 0,024 | `docs/resultados/paso-b-resumen.md` |
| Saque y drive de perfil cumplen el Criterio 1 con 1a = 0,83 | `paso-b-resumen.md` §3 |
| Error angular 8,5° (rodilla) y 12,5° (codo); p95 del codo 36,4°; codo dominante n = 2 | `docs/resultados/criterio2.json`; decisión 015 |
| Pico del brazo no medido en 52 de 76 (68 %) | `docs/resultados/brazo-por-golpe.md` |
| 117,4 y 146,7 s por golpe; 677,8 s en el plan gratuito; USD 25/mes | `docs/resultados/criterio4-latencia.md`; decisión 023 |
| Resolución ~5 ms y tolerancia de 8,33 ms | decisión 032 |
| Un jugador, dos sesiones, cámara a la izquierda | decisión 013 (actualización del 13/10) |

## F. Lo que falta para que este guion esté listo

1. ~~Cortar un drive y un revés del corpus~~ **Hecho el 15/10:** 12 recortes verificados en `recortes-demo` (6 de drive de perfil y 6 de revés de tres cuartos de la sesión 2).
2. ~~Probar "Eliminar mi cuenta"~~ **Probado el 15/10 en producción** (Valentín): la cuenta, sus filas y sus archivos desaparecieron (verificado).
3. **Congelar el motor el 24/10** y ejecutar §C el 25–26/10.
4. Ensayar dos veces con cronómetro y ajustar los minutos.
5. Grabar el video de pantalla del recorrido y sacar las capturas.
6. Decidir si se muestra una diapositiva con la tabla del orden por encuadre (§A.1) o se usa la pantalla Tecnología.
7. **Detección automática (decisión 038, actualización del 16/10):** si la etapa 1 cumple y Valentín da el OK a la etapa 2, tiene que estar **validada e integrada el 23/10**, antes de congelar; si no, queda para después de la demo y la demo se hace con la carga declarada.
