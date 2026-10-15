# Protocolo opcional: una sesión de saques con un solo teléfono para probar si el orden depende del encuadre

**Estado:** opcional (pedido de Valentín, 13/10/2026: "si sobra tiempo"). **No bloquea la demo.** Es el reemplazo de la grabación simultánea desde dos ángulos, que **queda como trabajo futuro** porque
no hay un segundo teléfono.
**Para qué:** el Paso A mostró que, en el saque, el orden cadera-tronco medido depende del encuadre (perfil: tronco primero; tres cuartos: cadera primero). El Paso B (originales a tasa real) dice si
eso es del corpus convertido. Esta sesión agrega el dato que falta: **el mismo jugador, el mismo día, la misma luz y los mismos 240 fps, alternando los dos encuadres.** Con un solo teléfono el movimiento
no es *el mismo golpe*, pero sí la misma condición, y alcanza para ver si la diferencia entre encuadres se repite o fue de las tomas del corpus.

## Qué tenés que decidir antes

- **Cuántos saques por encuadre:** 10 (mínimo para que un 8 de 10 tenga sentido, como los criterios de la tesis). Con 6 por encuadre se ve la dirección pero no el intervalo.
- **Quién saca:** el mismo jugador del corpus (vos), con la misma raqueta y las mismas zapatillas.

## Preparación (10 minutos)

1. **Lugar y luz:** el mismo del corpus si se puede (césped, fondo parejo, luz de día sin sombras duras). Ropa de color liso y contrastante con el fondo, **sin cosas que tapen la cadera** (campera larga, remera suelta).
2. **Celular en trípode, horizontal, a la altura de la cadera**, a ~5 m del jugador, **fijo toda la sesión** (no se mueve entre golpes).
3. **Cámara:** "Cámara lenta" a **240 fps**, 1080p. Verificar que el modo diga 240.
4. **Marcas en el suelo:** dos cruces con cinta, una donde se para el jugador y otra donde se pone el celular, para repetir la geometría después de cambiar de encuadre.
5. *(Opcional, muy útil)* **Cintas de color en cuatro puntos:** cresta ilíaca izquierda y derecha (cadera) y acromion izquierdo y derecho (hombro), cuatro colores distintos. Permiten medir la rotación
   de la pelvis **sin el estimador** (siguiendo el color en el mismo video) y comparar con lo que dice MediaPipe. Sin esto, la pregunta "¿mide mal el estimador?" no se puede contestar con un solo teléfono.

## Orden de la sesión (bloques alternados, no todos de un encuadre y después el otro)

Alternar evita que el cansancio o el cambio de luz se confundan con el encuadre.

| Bloque | Encuadre | Cámara respecto del jugador | Saques |
| --- | --- | --- | --- |
| 1 | **Tres cuartos** | a ~45° **por delante** del jugador (en diagonal, lo ves un poco de frente), **del lado izquierdo del jugador** (el no dominante, como todo el corpus) | 5 |
| 2 | **Perfil** | a 90° (de costado), **del lado izquierdo del jugador** | 5 |
| 3 | **Tres cuartos** | igual que el bloque 1 | 5 |
| 4 | **Perfil** | igual que el bloque 2 | 5 |

**El lado es el mismo del corpus (izquierda del jugador, no dominante), a propósito:** todas las grabaciones con que se midió el orden se hicieron con la cámara a la izquierda de un jugador diestro
(confirmado por Valentín el 13/10/2026). Cambiar de lado mezclaría dos variables (encuadre y lado) y rompería la comparación con lo ya medido. Grabar del lado de la raqueta queda como trabajo futuro, con
esa salvedad (`docs/resultados/brazo-por-golpe.md`).

- Entre bloques: mover el celular **a la marca**, no "a ojo". Anotar la hora.
- **Un video por saque o uno por bloque:** lo que sea más cómodo, pero **recortá cada saque** después.
- **Calentamiento:** 5 saques sueltos antes del bloque 1, sin grabar.
- **Descanso:** 1 minuto entre saques (el saque a ritmo de entrenamiento, no a tope).

## Después de grabar (con lo que ya sabés)

1. En Fotos: **recortar** cada saque y **sacar la cámara lenta** (barra de rayitas, todo el tramo a velocidad normal). Es lo que pide Cargar.
2. Subir con **Opciones → Formato: Actual** o desde Archivos.
3. En Cargar: *"¿Cómo lo grabaste?"* = **cámara lenta 240**, gesto **saque**, encuadre **perfil** o **tres cuartos** según el bloque.
4. Guardar los **originales sin modificar** (Archivos / iCloud) aparte: son los que usa el Paso B y no se suben al repositorio.

## Qué se va a mirar (se fija antes, como en el pre-registro)

| Qué | Cómo | Se interpreta |
| --- | --- | --- |
| Diferencia t_tronco − t_cadera, por encuadre | Mediana y cuartiles, con la misma tolerancia unificada (8,33 ms) | Si en perfil sigue siendo negativa y en tres cuartos positiva, la dependencia del encuadre es **del sistema**, no de las tomas del corpus |
| Fracción de saques con la cadera primero entre los ordenables | 10 por encuadre | Es la medida del Criterio 1c por encuadre |
| Si hay cintas: instante del pico de rotación de la cadera según el color contra el de MediaPipe | Diferencia en ms por saque | Si el color dice "cadera primero" en perfil y MediaPipe "tronco primero", el sesgo es del estimador (hipótesis del perfil, decisión 013) |

**Qué NO se puede concluir con esto:** que uno de los dos encuadres "está bien". Solo qué dice el sistema en cada uno y si el sesgo se repite. Es **un jugador, una sesión**: descriptivo.

## Costo

~1 hora de grabación y 30 minutos de recorte y carga. El análisis es el del Paso B con las 20 repeticiones nuevas: ~0,5 sesión.
