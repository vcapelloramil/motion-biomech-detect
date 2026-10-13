# El valor del producto sin veredictos: qué se destaca, qué texto y qué se compara (propuesta, 13/10/2026)

**Estado:** propuesta, sin aplicar. Parte de las decisiones 035 y 036 (ningún grupo emite veredicto del orden) y de la regla del 9/10 (sin investigaciones nuevas: todo lo que se propone usa datos que el motor ya
mide o que el plan §8 ya tiene en cola). Es la base de la fila 7 (reporte), 10 (Evolución) y 1 (Landing) de `docs/ux/auditoria-pantallas-13-10.md`.

## 1. El argumento en cuatro líneas

1. Con una sola cámara, **el orden cadera → tronco medido depende del encuadre** (saque y drive) o **no es confiable** (revés). Por eso el sistema **no dice si tu orden es correcto**.
2. Pero ese sesgo es **fijo por encuadre**: la misma cámara, desde el mismo lugar, le hace el mismo error a la misma persona. **Al compararte contra vos mismo en el mismo encuadre, el sesgo se cancela.**
3. Lo que queda, y es verificable con lo ya medido: (a) **medir** con trazabilidad (los datos, su confianza y su error), (b) **cuánto variás entre golpes** de una sesión, y (c) **cuánto cambiás de una sesión
   a otra**, siempre contra la variación que ya tenés tú.
4. Por eso **el producto es seguimiento, no juicio**: *"no te dice si tu técnica es buena o mala; te dice qué midió, con cuánta confianza, y cuánto cambia de una sesión a otra"*.

Esto no inventa nada nuevo: es el eje del proyecto (CLAUDE.md §3: "comparar al jugador consigo mismo") y es lo único que el Criterio 3 de la tesis validó (consistencia entre sesiones).

## 2. Lo que se puede afirmar y con qué respaldo

| Qué se compara | Respaldo ya medido | Cómo se lee sin juzgar | Cuándo se muestra |
| --- | --- | --- | --- |
| **Separación cadera-hombro máxima (°)**, mediana de la sesión | Criterio 3 (i): σ dentro de una sesión ≈ 2,8–3,1° y consistente entre sesiones en la mayoría de los grupos; una diferencia de 6° (drive de perfil) **sí** supera la variación habitual | "Tu mediana fue 31°; la sesión anterior, 37°. Cambió 6°: más que lo que variás entre golpes de una sesión (3°)." | Desde la 2.ª sesión del mismo gesto y encuadre |
| **Variación entre golpes** (dispersión de la separación, en °) | σ intra-sesión (MAD × 1,4826), la misma regla de la decisión 014 | "En tus 6 saques la separación varió ±3°." | Desde 4 golpes medidos en una sesión |
| **Repetibilidad del orden** ("el mismo orden en N de M golpes ordenables") | Es el Criterio 1b (≥ 0,8), pre-registrado; mide **si es el mismo**, no **cuál es el correcto** | "En 5 de 6 golpes, tu cadera y tu tronco llegaron en el mismo orden." (sin decir cuál) | Desde 5 golpes ordenables |
| **Golpes medidos completos** (N de M) | Trazabilidad y cobertura ya en el reporte | "Se pudieron medir completos 5 de 6 golpes." | Siempre |
| **Magnitudes articulares** (rodilla, codo) con su error | Criterio 2: error medio 8,5° (rodilla) y 12,5° (codo, con p95 36°; el codo dominante tiene poca cobertura) | "Flexión de rodilla en el pico del tronco: 142° (error esperable ±9°)." Solo se habla de cambio si supera ese error | Siempre como dato; comparación desde la 2.ª sesión |
| **Velocidad pico por segmento (°/s)** | Depende de la tasa real (ya leída del archivo); sin goniometría | Dato sin comparar al principio; después, "más rápido / igual / más lento" solo si supera la dispersión de la sesión | Detalle técnico; Evolución en segundo plano |

**Lo que NO se afirma** (y por qué):

- **Cuál orden cadera → tronco es el correcto** (suspendido; 035 y 036).
- **El instante del pico del tronco desde la separación máxima** (Criterio 3 (ii)): hay que recalcularlo con el tiempo real (pendiente 2 de la 036). **No entra a Evolución hasta entonces.**
- **Un rango "habitual" de la literatura** o de otros jugadores (R5). El único "rango habitual" posible es el **propio** (con ≥ 3 sesiones: tu mediana ± tu variación).
- **Que un cambio sea una mejora.** No hay referencia para decir qué dirección es mejor.

## 3. Qué cambia en cada pantalla

### 3.1 Reporte simple de **un** golpe (la primera vez, sin historial)

**Qué se destaca:** los tres momentos reales (foto con esqueleto en el pico de cada segmento) y la frase de secuencia; es lo que ya está y es lo más tangible.

**Qué se agrega:** una tarjeta **"Tu punto de partida"** en lugar de la ausencia de comparación.

| Elemento | Texto propuesto |
| --- | --- |
| Estado del orden (hoy: "Solo registrado") | **"Solo registrado"** + *"Medimos el orden de tu cadera y tu tronco y lo guardamos. Con una sola cámara no podemos asegurar cuál es el correcto, pero sí vas a poder ver cuánto cambia en tus próximas sesiones."* |
| Primera sesión | *"Este es tu primer registro de saque de perfil. A partir de la próxima sesión vas a ver cuánto cambia."* |
| Aviso de encuadre | *"Para que la comparación sea válida, grabá siempre desde el mismo lugar y con la cámara a la misma altura."* |

### 3.2 Sesión con **varios** golpes (la vista que carga el valor)

Orden de las tarjetas, de lo más a lo menos informativo:

1. **"Tus golpes entre sí"** (consistencia): variación de la separación, "mismo orden en N de M" y "golpes medidos N de M". **No es un puntaje**: son tres datos con su explicación, sin número agregado.
2. **"Tu golpe típico"**: los tres momentos del golpe **más cercano a la mediana** de la sesión, con selector de golpe. Se elige por **representativo, no por "mejor"**: elegir el mejor sería juzgar y sería
   elegir a mano.
3. **"Un golpe se apartó"** (si hay): el que más se aleja de la mediana más que la dispersión de los demás (la regla robusta con MAD de la decisión 014). Texto: *"El golpe 4 se pareció menos a los demás.
   Puede ser tu golpe o la medición: miralo en el video."* Con enlace a sus tres momentos.
4. **Magnitudes con su error** (rodilla, codo, separación), en el detalle.

### 3.3 Evolución ("Vos, frente a vos mismo")

- **Un panel por magnitud** (separación cadera-hombro primero), con **la mediana por sesión**, **una banda con tu variación habitual** y **huecos "sin dato"** donde no se pudo medir (nunca interpolados;
  eso ya lo hace el componente).
- **Solo sesiones del mismo gesto y encuadre** (la especificación §3) y **aviso si el encuadre parece distinto** entre dos sesiones (el criterio de la medición: tamaño del torso en píxeles que cambia > 20 %,
  y, para el saque, el giro de hombros de la decisión 035).
- **Vocabulario neutro:** *aumentó / disminuyó / se mantuvo* en lugar de *mejoró / empeoró*; **sin verde ni ámbar** en las flechas (el turquesa de datos, nunca el color de un estado).
- **Qué dice cada tarjeta de arriba:** *"Separación cadera-hombro: 31°. Antes 37°. Cambió más que tu variación habitual (±3°)."* / *"Orden cadera-tronco: el mismo en 4 de 6 golpes ordenables. Antes: 5 de 6."* /
  *"Golpes medidos completos: 5 de 6. Antes: 3 de 6."*
- **Con 2 sesiones** solo hay un cambio (Δ) y se lo compara con la variación de cada una; **con ≥ 3**, aparece la banda propia.

### 3.4 Landing y textos de producto

- Titular: *"Tu técnica, medida cuadro a cuadro."* (en vez de "documentada" o "evaluada").
- Una frase de valor: *"KinetiQ no te dice si tu técnica es buena o mala: mide tu golpe con su confianza y te muestra cuánto cambia de una sesión a otra."*
- **"Lo que no hace"** gana una línea: *"No te dice si tu orden de cadera y tronco es el correcto: con una sola cámara eso depende desde dónde grabes. Por eso compara tus sesiones contigo."*
- **"Cómo leer el reporte"** reemplaza los "cuatro estados" por los que realmente aparecen: **Solo registrado** (un dato medido, sin juicio) y **No auditable** (no se pudo medir con confianza).

## 4. Lo que hay que construir (todo cabe en el plan §8)

| Pieza | Dónde | Esfuerzo |
| --- | --- | --- |
| **Agregador por sesión**: mediana y dispersión de la separación, repetibilidad del orden, golpe más cercano a la mediana, golpe que se aparta, golpes medidos completos | `reportes_sesion` (la tabla ya existe); **no toca el contrato por golpe** | 0,5 (plan §8 #5) |
| Vista de sesión y selector de golpe | Frontend | 1 (plan §8 #5) |
| Evolución real mínima: una mediana por sesión, la banda propia y los huecos | Frontend + lectura de `reportes_sesion` | 1 (fila 10 de la auditoría) |
| Texto de "punto de partida" y de aviso de encuadre | Frontend | dentro de la fila 7 |

**Una nota sobre el contrato:** `comparacion_propia` del contrato 1.3 está definido como `desfase_torso_ms` con una dirección. Es la métrica (ii), que está pendiente de recalcular con el tiempo real, y es un
dato **por golpe**. Conviene **no usarlo** y dejar la comparación en el agregador de la sesión, que sí puede evolucionar sin cambiar el contrato por golpe.

## 5. Riesgos, y cómo los atiende el texto

| Riesgo | Respuesta |
| --- | --- |
| Que el jugador lea "cambió 6°" como "empeoré" | El texto lo dice: *"No es mejor ni peor: es lo que cambió."* y no usa color de estado |
| Que compare sesiones de encuadres distintos | La comparación solo existe dentro del mismo gesto y encuadre; si el encuadre parece distinto, avisa y no compara |
| Que un golpe mal medido parezca un cambio real | Cada comparación va contra la variación de la sesión y el error esperable; un golpe que se aparta se marca como "se pareció menos", no como "peor" |
| **Un solo jugador y dos sesiones**: la validación del Criterio 3 es de un jugador | Se declara en el Capítulo 7. Es un límite de la validación, no del diseño |
| Que sin veredicto el reporte "parezca vacío" para los profesores | El valor visible es la cadena: fotos reales con esqueleto, datos con confianza, y Evolución con **sesiones reales**. Por eso las dos sesiones reales de un jugador (auditoría, "lo que necesito de Valentín") son parte del núcleo, no un extra |
