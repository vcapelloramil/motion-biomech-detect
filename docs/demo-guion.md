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

**Congelar:** desde la mañana de D−1 **no se publica nada** (ni servidor ni frontend). Si hay algo que arreglar, se arregla hacia atrás con `docs/publicacion-y-vuelta-atras.md`, no hacia adelante.

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

## C. Plan de limpieza (qué borrar, qué volver a subir y en qué orden)

**Estado al 15/10/2026** (`tools/respaldo/estado_de_la_base.py`, solo lectura): 4 cuentas, 8 sesiones, 18 videos; **todas las sesiones están en la cuenta B** ("Valentín"); las cuentas A, C y D no tienen sesiones; 15 archivos sueltos (245 MB) en la carpeta
`prueba-iphone` de la cuenta A. Versiones del motor mezcladas: 0.4.1, 0.5.0, 0.5.2, 0.5.3 (12 golpes), 0.5.4.

**Por qué hay que limpiar:** dos sesiones del 24/9 y dos del 25/9 de saque en tres cuartos darían **puntos duplicados** en Evolución, y las versiones mezcladas disparan el aviso de "versiones distintas del motor".

> **Antes de empezar: un respaldo nuevo y verificado** (`docs/respaldo-y-restauracion.md`). Borrar es irreversible.

| Paso | Qué | Cómo | Verificación |
| --- | --- | --- | --- |
| **1** | **Probar "Eliminar mi cuenta" con una cuenta descartable** (todavía no se ejecutó contra la base real) | Elegir una cuenta **vacía y de prueba** (C, creada el 15/10). Subir **un** golpe corto, esperar a que termine, **Descargar mis datos**, y después Perfil → **Eliminar mi cuenta** → escribir `ELIMINAR` | La cuenta ya no entra; `estado_de_la_base.py` no la lista; **no quedan archivos** en las carpetas de esa cuenta en `videos` ni en `artefactos` |
| **2** | **Eliminar las otras cuentas de prueba vacías** (A y D) | Mismo camino. **Confirmar con Valentín que son de prueba antes de borrarlas** (D tiene el rol "entrenador" y el nombre completo). Al borrar A desaparecen sus 15 archivos huérfanos (245 MB) | `estado_de_la_base.py`: "ARCHIVOS HUÉRFANOS: 0" |
| **3** | **Eliminar en la cuenta B las 8 sesiones actuales** (6 de prueba de un golpe y las 2 del corpus procesadas con 0.5.3) | Biblioteca → cada sesión → **Eliminar sesión** (borra los archivos de los dos buckets y las filas) | Biblioteca vacía; "SESIONES" vacío |
| **4** | **Volver a subir con 0.5.5, en este orden:** (a) **sesión 1**: 6 golpes de `20260924_saque_trescuartos_toma01_golpe1..6.mov`; (b) esperar a que terminen; (c) **sesión 2**: 6 golpes de `20260925_saque_trescuartos_toma02b_golpe1..6.mov`; (d) esperar | **Datos de la carga:** jugador Valentín (mano derecha), gesto **saque**, encuadre **tres cuartos**, lado de la cámara **izquierda**, cámara lenta 240, y la **fecha real** (24/09/2026 y 25/09/2026). Los archivos se eligen desde la computadora (no hace falta "Formato: Actual"). Carpeta: `Desktop\corpus-originales-reales\recortes-evolucion\` | Cada sesión: 6 golpes con estado *medido* y motor **0.5.5** en el detalle técnico. Tiempo: 6 golpes × ~2–2,5 min en cola de a uno ≈ **12–15 min por sesión** |
| **5** | **Un golpe de drive y uno de revés** para tener "un golpe por gesto" | **Falta cortarlos:** `backend/app/recortar_evolucion.py` hoy solo corta el saque (lista `GRUPOS`); extenderlo con un drive de perfil (`IMG_6397`) y un revés de tres cuartos (`IMG_6395`) es ~0,25 sesión. Cargar cada uno en su sesión (24/09 y 25/09 u otra fecha real), lado **izquierda** | Dos sesiones de un golpe, motor 0.5.5 |
| **6** | **Dejar listo el archivo de la carga en vivo** | Un recorte **no subido** (por ejemplo `20260925_saque_trescuartos_toma02c_golpe1.mov`). Decir en la demo que **es del corpus** y subirlo con la fecha real de la grabación; **borrar la sesión después de la demo** para no dejar un tercer punto en Evolución | — |
| **7** | **Verificar todo** | `estado_de_la_base.py`: 1 cuenta de demo con 4 sesiones (12 + 2 golpes), "VERSIONES DEL MOTOR: {'0.5.5': 14}", sin golpes en curso ni fallidos, sin huérfanos. En la aplicación: Biblioteca, vista de sesión, Evolución (dos puntos, sin aviso de mezcla), Perfil ("Tu actividad": 4 sesiones, 14 golpes) | todo en verde |
| **8** | **Respaldo final** y **congelar** | `python -m app.respaldo exportar`, copia externa, `git tag` | — |

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

1. Cortar un drive y un revés del corpus y cargarlos (§C, paso 5) — ~0,25 sesión.
2. Probar "Eliminar mi cuenta" con una cuenta descartable (§C, paso 1).
3. Ensayar dos veces con cronómetro y ajustar los minutos.
4. Grabar el video de pantalla del recorrido y sacar las capturas.
5. Decidir si se muestra una diapositiva con la tabla del orden por encuadre (§A.1) o se usa la pantalla Tecnología.
6. **Si el 24/10 el núcleo está completo:** extender D a drive y revés (decisión 038), y entonces el reporte avisará también en esos gestos.
