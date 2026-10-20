# Textos de los reportes — decisión 039 (versión 2, con los ajustes de Valentín del 20/10)

**Estado:** textos **aprobados por Valentín el 20/10/2026** (10 ajustes en la primera ronda; 5 en la segunda, tras revisar la matriz: ver «Segunda ronda»). **Implementados** en la pantalla del golpe, la de la sesión y los dos PDF.
**Cómo se escribió este documento:** las secciones A, B y C **no están escritas a mano**: las genera el programa que arma los textos de verdad (`frontend/src/lib/textos-reporte.ts`) sobre la sesión **real** del 25/9/2026 (saque, tres cuartos, 6 golpes, motor 0.5.3, leída de la base en solo lectura) y sobre variantes de ese mismo dato. Se regeneran con `bun tests/generar-textos-doc.ts` (desde `frontend/`). Así este documento **no puede decir otra cosa que el sistema**.
**Versión de los textos:** <!-- GENERADO:version -->

Textos **v1** · generado con `bun tests/generar-textos-doc.ts` desde `frontend/src/lib/textos-reporte.ts` y la sesión real del 25/9/2026.

<!-- /GENERADO:version -->

Reglas generales (decisión 039): primero lo medido; después lo no medido, con el porqué en una línea; recomendaciones **solo** de cuatro tipos (medir mejor, usar los datos, contexto de la literatura aparte, preguntas para el entrenador); **nada** de «deberías», «corregí», «bien/mal», riesgo de lesión, comparaciones con profesionales ni promesas de mejora. Una prueba automática recorre cada frase de cada caso y falla si aparece una palabra prohibida o jerga interna. Entre `ⓘ` va el dato que en la pantalla lleva su explicación corta (el glosario está en el programa; en el PDF esa explicación va en el detalle técnico).

---

## Los 10 ajustes del 20/10 y cómo quedaron

| # | Pedido de Valentín | Cómo quedó |
| --- | --- | --- |
| 1 | «En una frase» arriba de «Qué vimos», con reglas fijas | Golpe: «Un saque típico de tu sesión: te enroscaste 34° y tu cadera y tu tronco aceleraron casi juntos.» (si no es el típico: «En este saque, …»). Sesión (versión de la segunda ronda): «En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°). En 3 de tus 6 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.» |
| 2 | Todo ángulo de articulación con su referencia en una línea | «180° es la pierna totalmente estirada» / «180° es el brazo totalmente estirado» en cada frase que da un ángulo de rodilla o de codo, en el detalle técnico, en los encabezados de la tabla de la sesión y en el ⓘ. Una prueba lo verifica caso por caso. |
| 3 | En «Qué vimos» no va el codo del brazo que no golpea; va la rodilla | La rodilla ocupa su lugar («Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172°…»). El codo del brazo que no golpea pasó al detalle técnico, con la aclaración de que es el del lanzamiento de pelota. Solo el codo del brazo dominante, si se midió, puede ocupar el lugar de la rodilla. |
| 4 | Recuadro de literatura: frase general, sin Fleisig | «La literatura describe el saque como una cadena que transmite energía desde las piernas, a través de la cadera y el tronco, hacia el brazo y la raqueta (Kovacs y Ellenbecker, 2011). La forma exacta varía de un jugador a otro.» Para drive y revés: «Para este golpe todavía no hay una referencia incorporada al proyecto.» **Registrado en la decisión 039:** una secuencia específica (el orden de los picos, valores) requiere verificar el pasaje antes de escribirla. |
| 5 | Pregunta 3 de la sesión | «¿Cuál de estos 6 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?» (la valoración la hace el jugador, no el sistema; pasa la prueba de palabras prohibidas). |
| 6 | «Esto vale para esta posición de cámara» y «valor central» | «Desde otra posición de cámara, este orden podría verse distinto.» y «valor típico» (el ⓘ explica que es la mediana). |
| 7 | Aviso sin «riesgo de lesión» | «KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.» (R2 sin excepción). |
| 8 | «Cuánto se puede confiar» | «…goniometría manual a ciegas (medición manual del ángulo sobre la imagen)…» |
| 9 | Preguntas solo en la sección 4 | Solo están en «Para tu entrenador o profesional»; una prueba verifica que no aparezcan en «Qué podés hacer». |
| 10 | Vencimiento exacto del dominio | **12 de octubre de 2027** (Namecheap), corregido en los insumos del cap. 7, la decisión 034 y la bitácora. |

**Dos cosas que agregué para que los casos nuevos tuvieran sentido** (revisalas): (a) la **nota de la cámara del lado de la mano dominante** (decisión 013: ese lado todavía no está validado), que aparece en «Para medir mejor»; (b) cuando **no se midió nada**, el texto lo dice **una sola vez** y no culpa al brazo (antes decía «el cuerpo lo tapó» aunque la cadera y el tronco tampoco se hubieran seguido).

## Hallazgos de los datos que cambian cómo se redacta

1. **El golpe 4 es el «golpe típico» de la sesión** (torsión 34,0° contra un valor típico de 33,0°).
2. **«0,296 s desde el inicio de la ventana» no es un dato del jugador:** la ventana de 0,6 s se ancla en el pico del tronco, que da 0,300 s en los seis golpes. Lo único con significado es la diferencia entre cadera y tronco, en milésimas de segundo; los instantes absolutos quedan en el detalle con esa aclaración.
3. **Cadera y tronco quedaron a 4 ms en el golpe 4:** las dos fotos «del pico» son casi el mismo fotograma; cuando están dentro de la tolerancia (8,3 ms) se muestra **una sola foto**.
4. **El golpe 6 se aparta en dos magnitudes:** torsión 11,2° (los otros cinco, de 28,8° a 41,5°) y rodilla izquierda 100,7° (los otros cuatro con dato, de 172,0° a 178,1°, con un error validado de 8,5° de media y 19,2° en el 95 %).
5. **En los 3 golpes ordenables la cadera llegó antes que el tronco** (17, 42 y 17 ms); en los otros 3 quedaron a 8, 4 y 4 ms. Son 3 golpes: por debajo del mínimo de 5 que el proyecto exige para hablar de repetición, así que **no se dice «se repite»**.
6. **La contradicción «33° ± 4°» junto a «de 11° a 42°»** se resuelve mostrando el rango de los golpes que **no** se apartan, el golpe 6 aparte, y llevando la «variación típica» al detalle con su explicación.

---

# A. Golpe 4 — saque, tres cuartos, 25 de septiembre (real)

*Cabecera:* Saque · tres cuartos · 25 de septiembre de 2026 · 201 fps reales · Valentín

<!-- GENERADO:golpe4 -->

**En una frase**

> Un saque típico de tu sesión: te enroscaste 34° y tu cadera y tu tronco aceleraron casi juntos.

#### 1. Qué vimos

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 34°. ⓘ
> - Tu cadera y tu tronco alcanzaron su giro más rápido casi a la vez: los separan 4 milésimas de segundo y el video no permite distinguir menos de 8. Por eso no se puede decir cuál fue primero. ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** desde la cámara, a tu izquierda, el cuerpo lo tapó durante buena parte del golpe. ⓘ
> - **La rodilla izquierda:** en ese momento el sistema no la vio con suficiente seguridad.

#### 2. Fotos y video

> **Una sola foto** — Cadera y tronco en su giro más rápido · a los 5,21 s del video
>
> **Qué mirar:** La línea violeta marca tus caderas y la turquesa tus hombros. Fijate si acompañan a tu cuerpo: si el dibujo no se parece a tu cuerpo, esa medición no es confiable.
>
> **Video.** Video con el esqueleto dibujado, en cámara lenta (8 veces más lento que la realidad): es el tramo de 1,6 s alrededor del golpe. Qué mirar: que las líneas sigan tu cuerpo sin saltos.

#### 3. Qué podés hacer con esto

> **Para medir mejor**
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás cuando armás el golpe. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que cadera y tronco de esa sesión no se podrían comparar con los de esta.
> - Este golpe es uno de los 6 de su sesión. Para ver cuánto se parece a los demás, mirá la sesión. *(enlace a la sesión)*
> - Un encuadre que muestre el cuerpo entero, con los pies a la vista, y buena luz pueden ayudar a que el sistema vea las rodillas con seguridad.
>
> **Para usar estos datos al entrenar**
> - Para comparar con otro día, grabá desde el mismo lugar (lado y ángulo de la cámara): el mismo movimiento puede dar números distintos desde otro punto de vista.
> - Más que un número suelto, sirve mirar si un número se vuelve más parejo de golpe a golpe y de sesión a sesión. En Evolución se ve la variación de tu propia sesión. *(enlace a Evolución)*
>
> **Contexto de la literatura** *(recuadro aparte)*
> Contexto general: no es una comparación con tus datos. La literatura describe el saque como una cadena que transmite energía desde las piernas, a través de la cadera y el tronco, hacia el brazo y la raqueta (Kovacs y Ellenbecker, 2011). La forma exacta varía de un jugador a otro.

#### 4. Para tu entrenador o profesional

> **Preguntas para llevar**
> 1. En este saque la cadera y el tronco giraron casi a la vez (4 ms). ¿Lo ves igual en el video? ¿Se parece a lo que sentís al sacar?
> 2. Este es el golpe más cercano al valor típico de su sesión (torsión de 34°; la sesión va de 11° a 42°). ¿Te parece representativo de tus saques?
>
> **[Descargar PDF]**
>
> **Cuánto se puede confiar en cada medición**
> - **Ángulos de rodilla y codo:** se contrastaron con goniometría manual a ciegas (medición manual del ángulo sobre la imagen). En el codo, el ángulo de KinetiQ difirió 12,5° de media del medido a mano (en el 95 % de los casos, hasta 36,4°); en la rodilla, 8,5° de media (hasta 19,2°). El codo del brazo que golpea suele tener poca cobertura.
> - **Momentos:** el video permite distinguir diferencias de unos 8 ms; por debajo no se sabe cuál fue primero.
> - **Torsión cadera-hombro:** se midió que se repite entre sesiones; no se contrastó con goniometría.
>
> **Aviso**
> KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.

#### 5. Detalle técnico *(cerrado)*

**Mediciones**

| Dato | Valor | Qué significa |
| --- | --- | --- |
| Torsión cadera-hombro máxima | 34,0° · confianza 1,00 | Es el ángulo entre la línea de tus caderas y la de tus hombros, en su máximo. 0° sería caderas y hombros alineados; cuanto mayor es el número, más enroscado estaba el tronco respecto de la cadera. |
| Giro más rápido de la cadera | 793 °/s · confianza 1,00 | Cuántos grados por segundo gira la línea de las caderas en su momento más rápido (793 °/s son unas 2,2 vueltas por segundo). |
| Giro más rápido del tronco | 545 °/s · confianza 1,00 | Lo mismo para la línea de los hombros (545 °/s son unas 1,5 vueltas por segundo). |
| Diferencia entre los dos momentos | 4 ms (casi a la vez) | Es menor que los 8,3 ms necesarios para poder decir cuál fue primero. |
| Rodilla izquierda | no medida · confianza 0,46 | Se informa solo si las tres articulaciones del ángulo se vieron con confianza de 0,6 o más. 180° es la pierna totalmente estirada. |
| Codo izquierdo | 157,1° · confianza 0,75 | Ángulo en el instante del giro más rápido del tronco; 180° es el brazo totalmente estirado. Error medido contra goniometría manual: 12,5° de media. Es el brazo que no golpea (el del lanzamiento de pelota). |
| Brazo que golpea | no medido | Faltaron datos del brazo durante gran parte del golpe, así que no hay un momento claro de giro más rápido. |

**Cuándo y con qué cobertura**

| Dato | Valor | Qué significa |
| --- | --- | --- |
| Tramo analizado | 4,91 s a 5,51 s del video | El análisis mira un tramo corto alrededor del giro más rápido del tronco. Los momentos de cada parte se cuentan desde su inicio; el del tronco cae siempre en el centro porque el tramo se arma alrededor de él. Lo que importa es la diferencia entre los momentos. |
| Parte del golpe medida con seguridad | 78,8 % | El resto son tramos donde alguna articulación no se vio con confianza. Sin datos confiables: codo derecho, de 2,28 s a 2,38 s del video; codo derecho, de 2,56 s a 2,59 s del video; codo derecho, de 2,65 s a 2,68 s del video; codo derecho, de 4,02 s a 5,28 s del video. |

**Cómo salió el video**

| Dato | Valor | Qué significa |
| --- | --- | --- |
| Fotogramas por segundo reales | 200,8 (el teléfono anuncia 240) | Faltó el 16,3 % de los fotogramas. |
| Resolución en el tiempo | 1 fotograma ≈ 5 ms | Por eso hay una diferencia mínima para poder ordenar dos momentos. |
| Fotogramas reconstruidos | 486 de 1607 (30,2 %) | Para tener un muestreo parejo se estimó el punto entre dos vecinos (interpolación), con huecos de hasta 12,9 ms. Un momento que cae en uno de esos puntos es una estimación, no una medición. |
| Suavizado de la señal | Butterworth de 4.º orden, corte 8 Hz, sin retraso | Quita el temblor de la detección sin correr los momentos en el tiempo. |
| Tiempo del video | confirmado | Se pudo leer cuándo se tomó cada fotograma. |
| Modo de captura declarado | cámara lenta de 240 fps | Lo que se indicó al subir el video. |

**Versiones y tiempos**

| Dato | Valor | Qué significa |
| --- | --- | --- |
| Motor | 0.5.3 · mediapipe | Versión del programa que calculó el reporte y detector de pose. |
| Textos | v1 | Versión de las frases de este reporte; si cambian, sube el número. |

<!-- /GENERADO:golpe4 -->

---

# B. La sesión completa — saque, tres cuartos, 25 de septiembre, 6 golpes (real)

<!-- GENERADO:sesion -->

**En una frase**

> En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°). En 3 de tus 6 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.

#### 1. Qué vimos

> **Lo que se midió**
> - Se midieron los 6 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 33°: 5 golpes quedaron entre 29° y 42° y el golpe 6 fue de 11°. ⓘ
> - En 3 de los 6 golpes (1, 3 y 5) se pudo establecer cuál giró primero, y en los 3 fue la cadera: llegó a su giro más rápido entre 17 y 42 milésimas de segundo antes que el tronco. En los otros 3 quedaron casi a la vez (entre 4 y 8 ms) y no se puede decir cuál fue primero. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 172° y 178° en los 4 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Un golpe que se aparta**
> - **El golpe 6 se parece menos a los demás:** su torsión fue de 11° y, además, tu rodilla izquierda estaba mucho más flexionada (101°, contra 172° a 178° en los otros 4 con dato; 180° es la pierna totalmente estirada). Puede ser tu golpe o la medición: miralo en el video. ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ
> - **La rodilla izquierda:** no se pudo medir en 1 golpe (el 4); en ese momento el sistema no la vio con suficiente seguridad.

#### 2. Fotos y video

> **Golpe típico (golpe 4): el más cercano al valor típico de la sesión (34° de torsión). No es un golpe ejemplar ni un juicio sobre tu técnica.**
>
> **Qué mirar:** Fijate que la línea violeta (caderas) y la turquesa (hombros) acompañen tu cuerpo. Después abrí el golpe 6 y compará.

#### 3. Qué podés hacer con esto

> **Para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 3 de 6 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Para usar estos datos al entrenar**
> - Para comparar esta sesión con otra, grabá desde el mismo lugar: saque, tres cuartos, cámara a la izquierda.
> - En Evolución podés mirar si el valor típico de la torsión (hoy 33°) y la variación entre golpes (hoy ±4°) se mantienen o se vuelven más parejos de una sesión a otra. *(enlace a Evolución)*
>
> **Contexto de la literatura** *(recuadro aparte)*
> Contexto general: no es una comparación con tus datos. La literatura describe el saque como una cadena que transmite energía desde las piernas, a través de la cadera y el tronco, hacia el brazo y la raqueta (Kovacs y Ellenbecker, 2011). La forma exacta varía de un jugador a otro.

#### 4. Para tu entrenador o profesional

> **Preguntas para llevar**
> 1. En el golpe 6 la torsión fue de 11° (en los otros, entre 29° y 42°) y tu rodilla izquierda estaba mucho más flexionada. ¿Qué ves en el video de ese golpe? ¿Fue un saque distinto a los demás?
> 2. En 3 golpes la cadera llegó antes que el tronco y en otros 3 llegaron casi juntos. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?
> 3. ¿Cuál de estos 6 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?
>
> **[Descargar PDF]**
>
> **Cuánto se puede confiar en cada medición**
> - **Ángulos de rodilla y codo:** se contrastaron con goniometría manual a ciegas (medición manual del ángulo sobre la imagen). En el codo, el ángulo de KinetiQ difirió 12,5° de media del medido a mano (en el 95 % de los casos, hasta 36,4°); en la rodilla, 8,5° de media (hasta 19,2°). El codo del brazo que golpea suele tener poca cobertura.
> - **Momentos:** el video permite distinguir diferencias de unos 8 ms; por debajo no se sabe cuál fue primero.
> - **Torsión cadera-hombro:** se midió que se repite entre sesiones; no se contrastó con goniometría.
>
> **Aviso**
> KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.

#### 5. Detalle técnico *(cerrado)*

| Golpe | Torsión | Cadera y tronco | Rodilla (180° = estirada) | Codo (180° = estirado) | Parte medida | Qué se midió |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 34,7° | cadera 17 ms antes | 178° | 122° | 77,0 % | cadera y tronco, sin el brazo |
| 2 | 28,8° | casi a la vez (8 ms) | 176° | 165° | 64,1 % | cadera y tronco, sin el brazo |
| 3 | 31,9° | cadera 42 ms antes | 172° | 139° | 78,7 % | cadera y tronco, sin el brazo |
| 4 | 34,0° | casi a la vez (4 ms) | no medida | 157° | 78,8 % | cadera y tronco, sin el brazo |
| 5 | 41,5° | cadera 17 ms antes | 174° | 132° | 73,7 % | cadera y tronco, sin el brazo |
| 6 | 11,2° | casi a la vez (4 ms) | 101° | 168° | 67,5 % | cadera y tronco, sin el brazo |

*Rodilla y codo: 180° es la pierna (o el brazo) totalmente estirada. El codo que se muestra es el del brazo que no golpea (el del lanzamiento de pelota).*

- **Valor típico:** Es la mediana: el valor del medio al ordenar los golpes de menor a mayor. No se deja arrastrar por un golpe muy distinto de los demás.
- **Variación típica:** Cuánto se aleja, en general, un golpe del valor típico. Está calculada de modo que un golpe muy distinto no la agrande. Se da desde 4 golpes. En esta sesión: ±4,4°.
- **Golpe típico:** El golpe de la sesión más cercano al valor típico de la torsión. Es el más representativo; no es un golpe ejemplar ni un juicio sobre tu técnica.
- **Un golpe que se aparta:** Su torsión quedó a más de 3 variaciones típicas del valor típico de la sesión. Puede ser tu golpe o la medición: conviene mirarlo en el video.
- **Casi a la vez:** Con la resolución de estos videos, menos de 8,3 ms de diferencia no se puede ordenar. La repetición del orden se informa desde 5 golpes en que se pudo establecer.

*Motor 0.5.3 · textos v1*

<!-- /GENERADO:sesion -->

---

# C. Matriz de casos

Cada caso muestra el «En una frase» y el «Qué vimos» que salen con las mismas reglas, más las partes de «Qué podés hacer» y de las preguntas que cambian en ese escenario. **Cada uno es también un caso de prueba** (`frontend/tests/matriz-casos.test.ts`). Los casos 1 a 6 usan un golpe real del 25/9 (o su reflejo en un espejo, para el zurdo); 7 a 11 son variantes de la sesión real con la consistencia calculada por el servidor.

<!-- GENERADO:matriz -->

### Caso 1 — Cadera claramente antes que el tronco

*Saque de tres cuartos, cámara a la izquierda, jugador diestro. Cadera 42 ms antes que el tronco; brazo no medido.*

**En una frase**

> En este saque, te enroscaste 32° y tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 32°. ⓘ
> - Tu cadera alcanzó su giro más rápido 42 milésimas de segundo antes que tu tronco. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172° (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** desde la cámara, a tu izquierda, el cuerpo lo tapó durante buena parte del golpe. ⓘ

---

### Caso 2 — Tronco antes que la cadera

*El mismo golpe con los instantes invertidos: tronco 42 ms antes que la cadera.*

**En una frase**

> En este saque, te enroscaste 32° y tu tronco aceleró antes que tu cadera.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 32°. ⓘ
> - Tu tronco alcanzó su giro más rápido 42 milésimas de segundo antes que tu cadera. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172° (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** desde la cámara, a tu izquierda, el cuerpo lo tapó durante buena parte del golpe. ⓘ

---

### Caso 3 — Golpe sin nada medido

*Ni cadera, ni tronco, ni brazo con confianza; ninguna magnitud auditable.*

**En una frase**

> De este golpe no se pudo medir lo suficiente como para resumirlo en una frase.

**Qué vimos**

> **Lo que se midió**
> - *(nada)*
>
> **Lo que no se pudo medir**
> - **Este golpe:** el sistema no pudo seguir tu cuerpo con confianza, así que no hay mediciones de la cadera, el tronco, el brazo ni las rodillas.

> **Qué podés hacer → para medir mejor**
> - Cuando casi no se mide nada, ayudan el cuerpo entero a la vista durante todo el golpe, buena luz y la cámara quieta, sin que nada tape al jugador.

---

### Caso 4a — Drive (recuadro de literatura sin referencia)

*Drive, tres cuartos, cámara a la izquierda. (Se usa el dato del saque: solo importa el lenguaje.)*

**En una frase**

> En este drive, te enroscaste 32° y tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 32°. ⓘ
> - Tu cadera alcanzó su giro más rápido 42 milésimas de segundo antes que tu tronco. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172° (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** el sistema no pudo seguirlo con confianza durante buena parte del golpe.

> **Contexto de la literatura** *(recuadro aparte)*
> > Contexto general: no es una comparación con tus datos. Para este golpe todavía no hay una referencia incorporada al proyecto.

---

### Caso 4b — Revés (recuadro de literatura sin referencia)

*Revés, perfil, cámara a la izquierda.*

**En una frase**

> En este revés, te enroscaste 32° y tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 32°. ⓘ
> - Tu cadera alcanzó su giro más rápido 42 milésimas de segundo antes que tu tronco. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172° (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** el sistema no pudo seguirlo con confianza durante buena parte del golpe.

> **Contexto de la literatura** *(recuadro aparte)*
> > Contexto general: no es una comparación con tus datos. Para este golpe todavía no hay una referencia incorporada al proyecto.

---

### Caso 5 — Cámara del lado de la mano dominante (brazo visible)

*Jugador diestro con la cámara a la derecha: el pico del brazo se midió (52 ms después del tronco).*

**En una frase**

> En este saque, te enroscaste 32° y tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 32°. ⓘ
> - Tu cadera alcanzó su giro más rápido 42 milésimas de segundo antes que tu tronco. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba a 172° (180° es la pierna totalmente estirada). ⓘ

> **Qué podés hacer → para medir mejor**
> - Grabaste con la cámara del lado de tu mano dominante: el brazo con el que golpeás queda más a la vista, pero ese lado todavía no está validado en KinetiQ, así que cadera y tronco de este golpe no se pueden comparar con los de sesiones grabadas desde el otro lado.

---

### Caso 6 — Jugador zurdo

*Zurdo, cámara a la derecha (el lado recomendado para él), con el golpe típico de la sesión reflejado en un espejo.*

**En una frase**

> Un saque típico de tu sesión: te enroscaste 34° y tu cadera y tu tronco aceleraron casi juntos.

**Qué vimos**

> **Lo que se midió**
> - En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de 34°. ⓘ
> - Tu cadera y tu tronco alcanzaron su giro más rápido casi a la vez: los separan 4 milésimas de segundo y el video no permite distinguir menos de 8. Por eso no se puede decir cuál fue primero. ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás:** desde la cámara, a tu derecha, el cuerpo lo tapó durante buena parte del golpe. ⓘ
> - **La rodilla derecha:** en ese momento el sistema no la vio con suficiente seguridad.

> **Qué podés hacer → para medir mejor**
> - Con la cámara a tu derecha, el cuerpo tapa el brazo con el que golpeás cuando armás el golpe. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que cadera y tronco de esa sesión no se podrían comparar con los de esta.
> - Este golpe es uno de los 6 de su sesión. Para ver cuánto se parece a los demás, mirá la sesión. *(enlace a la sesión)*
> - Un encuadre que muestre el cuerpo entero, con los pies a la vista, y buena luz pueden ayudar a que el sistema vea las rodillas con seguridad.

---

### Caso 7 — Sesión con el orden mezclado entre golpes

*Los 6 golpes del 25/9, pero en el golpe 3 el tronco llega antes que la cadera.*

**En una frase**

> En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°). En 3 de tus 6 saques se pudo distinguir el orden: en 2 tu cadera aceleró antes que tu tronco y en 1, al revés.

**Qué vimos**

> **Lo que se midió**
> - Se midieron los 6 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 33°: 5 golpes quedaron entre 29° y 42° y el golpe 6 fue de 11°. ⓘ
> - En 3 de los 6 golpes se pudo establecer cuál giró primero: en 2 fue la cadera y en 1, el tronco. En los otros 3 quedaron casi a la vez (entre 4 y 8 ms) y no se puede decir cuál fue primero. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 172° y 178° en los 4 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Un golpe que se aparta**
> - **El golpe 6 se parece menos a los demás:** su torsión fue de 11° y, además, tu rodilla izquierda estaba mucho más flexionada (101°, contra 172° a 178° en los otros 4 con dato; 180° es la pierna totalmente estirada). Puede ser tu golpe o la medición: miralo en el video. ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ
> - **La rodilla izquierda:** no se pudo medir en 1 golpe (el 4); en ese momento el sistema no la vio con suficiente seguridad.

> **Qué podés hacer → para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 3 de 6 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Qué podés hacer → para usar estos datos al entrenar**
> - Para comparar esta sesión con otra, grabá desde el mismo lugar: saque, tres cuartos, cámara a la izquierda.
> - En Evolución podés mirar si el valor típico de la torsión (hoy 33°) y la variación entre golpes (hoy ±4°) se mantienen o se vuelven más parejos de una sesión a otra. *(enlace a Evolución)*
>
> **Para tu entrenador → preguntas**
> 1. En el golpe 6 la torsión fue de 11° (en los otros, entre 29° y 42°) y tu rodilla izquierda estaba mucho más flexionada. ¿Qué ves en el video de ese golpe? ¿Fue un saque distinto a los demás?
> 2. En 2 golpes la cadera llegó antes que el tronco y en 1, al revés. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?
> 3. ¿Cuál de estos 6 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?

---

### Caso 8 — Sesión de 3 golpes (menos del mínimo para la variación y la repetición)

*Los golpes 1, 3 y 5 del 25/9: los tres con orden distinguible. Mínimos del proyecto: variación desde 4 golpes, repetición desde 5 ordenables.*

**En una frase**

> En tus 3 saques te enroscaste entre 32° y 42°. En tus 3 saques se pudo distinguir el orden, y en todos tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - Se midieron los 3 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 35°: los 3 golpes quedaron entre 32° y 42°. ⓘ
> - En los 3 golpes se pudo establecer cuál giró primero, y en todos fue la cadera: llegó a su giro más rápido entre 17 y 42 milésimas de segundo antes que el tronco. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 172° y 178° en los 3 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ

> **Qué podés hacer → para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 3 de 3 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Qué podés hacer → para usar estos datos al entrenar**
> - Para comparar esta sesión con otra, grabá desde el mismo lugar: saque, tres cuartos, cámara a la izquierda.
> - En Evolución podés mirar si el valor típico de la torsión (hoy 35°) se mantiene de una sesión a otra. *(enlace a Evolución)*
>
> **Para tu entrenador → preguntas**
> 1. ¿Cuál de estos 3 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?

---

### Caso 9 — Sesión sin ningún golpe que se aparte

*Los golpes 1 a 5 del 25/9 (sin el 6): 5 golpes, ninguno se aparta.*

**En una frase**

> En tus 5 saques te enroscaste entre 29° y 42°. En 3 de tus 5 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - Se midieron los 5 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 34°: los 5 golpes quedaron entre 29° y 42°. ⓘ
> - En 3 de los 5 golpes (1, 3 y 5) se pudo establecer cuál giró primero, y en los 3 fue la cadera: llegó a su giro más rápido entre 17 y 42 milésimas de segundo antes que el tronco. En los otros 2 quedaron casi a la vez (entre 4 y 8 ms) y no se puede decir cuál fue primero. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 172° y 178° en los 4 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ
> - **La rodilla izquierda:** no se pudo medir en 1 golpe (el 4); en ese momento el sistema no la vio con suficiente seguridad.

> **Qué podés hacer → para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 3 de 5 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Qué podés hacer → para usar estos datos al entrenar**
> - Para comparar esta sesión con otra, grabá desde el mismo lugar: saque, tres cuartos, cámara a la izquierda.
> - En Evolución podés mirar si el valor típico de la torsión (hoy 34°) y la variación entre golpes (hoy ±3°) se mantienen o se vuelven más parejos de una sesión a otra. *(enlace a Evolución)*
>
> **Para tu entrenador → preguntas**
> 1. En 3 golpes la cadera llegó antes que el tronco y en otros 2 llegaron casi juntos. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?
> 2. ¿Cuál de estos 5 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?

---

### Caso 10 — Sesión con UN solo golpe ordenable

*Los golpes 1, 2, 4 y 6 del 25/9: solo el 1 tiene el orden distinguible (cadera 17 ms antes); los otros tres quedaron casi a la vez.*

**En una frase**

> En tus 4 saques te enroscaste entre 11° y 35°. En 1 de tus 4 saques se pudo distinguir el orden, y en ese tu cadera aceleró antes que tu tronco.

**Qué vimos**

> **Lo que se midió**
> - Se midieron los 4 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 31°: los 4 golpes quedaron entre 11° y 35°. ⓘ
> - En 1 de los 4 golpes (el 1) se pudo establecer cuál giró primero, y fue la cadera: llegó a su giro más rápido 17 milésimas de segundo antes que el tronco. En los otros 3 quedaron casi a la vez (entre 4 y 8 ms) y no se puede decir cuál fue primero. Desde otra posición de cámara, este orden podría verse distinto. ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 101° y 178° en los 3 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ
> - **La rodilla izquierda:** no se pudo medir en 1 golpe (el 3); en ese momento el sistema no la vio con suficiente seguridad.

> **Qué podés hacer → para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 1 de 4 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Para tu entrenador → preguntas**
> 1. En 1 golpes la cadera llegó antes que el tronco y en otros 3 llegaron casi juntos. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?
> 2. ¿Cuál de estos 4 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?

---

### Caso 11 — Sesión con NINGÚN golpe ordenable

*Los golpes 2, 4 y 6 del 25/9: en los tres, cadera y tronco quedaron casi a la vez.*

**En una frase**

> En tus 3 saques te enroscaste entre 11° y 34°. En ningún golpe se pudo distinguir cuál aceleró primero: quedaron casi a la vez.

**Qué vimos**

> **Lo que se midió**
> - Se midieron los 3 golpes. La torsión entre tus caderas y tus hombros tuvo un valor típico de 29°: los 3 golpes quedaron entre 11° y 34°. ⓘ
> - En ningún golpe se pudo establecer cuál giró primero: la cadera y el tronco quedaron casi a la vez (entre 4 y 8 ms). ⓘ
> - Cuando el tronco giraba más rápido, tu rodilla izquierda estaba entre 101° y 176° en los 2 golpes en que se midió (180° es la pierna totalmente estirada). ⓘ
>
> **Lo que no se pudo medir**
> - **El brazo con el que golpeás,** en ningún golpe: desde la cámara, a tu izquierda, el cuerpo lo tapa. ⓘ
> - **La rodilla izquierda:** no se pudo medir en 1 golpe (el 2); en ese momento el sistema no la vio con suficiente seguridad.

> **Qué podés hacer → para medir mejor**
> - El orden entre cadera y tronco se pudo establecer en 0 de 3 golpes. Con 5 o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.
> - Con la cámara a tu izquierda, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.
>
> **Para tu entrenador → preguntas**
> 1. ¿Cuál de estos 3 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?

<!-- /GENERADO:matriz -->

---

# Segunda ronda (20/10, tras revisar la matriz)

| # | Pedido de Valentín | Cómo quedó |
| --- | --- | --- |
| 1 | El resumen de la sesión dice cuántos golpes fueron ordenables | «En 3 de tus 6 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.» (con todos: «En tus N saques… y en todos…»; con uno: «…y en ese tu cadera aceleró…»). |
| 2 | Dos casos más: un solo golpe ordenable y ninguno | Casos 10 y 11 de la matriz y de las pruebas. Ninguno: «En ningún golpe se pudo distinguir cuál aceleró primero: quedaron casi a la vez.» |
| 3 | «Parecidos entre sí» → el rango concreto, sin adjetivo | «En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°).» Sin golpe que se aparte: «En tus 5 saques te enroscaste entre 29° y 42°.» *(Con menos de 5 golpes el servidor no marca ninguno que se aparte, así que el rango los incluye a todos: ver caso 10, «entre 11° y 35°».)* |
| 4 | El gráfico «Cuándo giró cada parte» queda visible | Debajo de «Qué vimos», relativo al tronco (tronco = 0; «cadera 17 ms antes»; «brazo 52 ms después» si se midió), con la franja de ± 8,3 ms rotulada «Zona donde no se puede distinguir cuál fue primero». Sin segundos desde el inicio de la ventana (quedan en el detalle técnico). También está en el PDF del golpe. |
| 5 | Evolución, después y solo si queda tiempo | Fuera de este cambio. |

# Pendientes

1. **Pasaje de la cita del recuadro** (Kovacs y Ellenbecker, 2011): el texto es general a propósito. Una secuencia específica no se escribe hasta verificar el pasaje.
2. **«Aceleraron / aceleró»** en «En una frase» es la redacción de Valentín; en «Qué vimos» el texto dice «alcanzó su giro más rápido», que es lo que se mide (el momento de máxima velocidad, no de aceleración).
3. **Evolución** no está en este cambio: queda con el lenguaje de antes.

# Cómo se hace (esfuerzo)

Sin tocar el motor, el contrato (1.4) ni el servidor: solo frontend. Orden: golpe → sesión → PDF del golpe → PDF de la sesión → ⓘ y glosario. Si se aprieta, se recorta en ese orden desde el final. Límite: publicado antes de la limpieza del 25/10.
