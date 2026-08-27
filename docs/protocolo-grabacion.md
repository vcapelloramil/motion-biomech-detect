# Protocolo de Grabación — KinetiQ

Instructivo para producir el conjunto de datos propio (Fase B del plan de desarrollo, hito C1).
Documento operativo y, a la vez, instrumento de recolección declarado en el apartado 2.6 de la
tesis.

**Tiempo total estimado: 45 minutos por sesión.** Se requieren dos sesiones separadas por al
menos una semana.

---

## 1. Qué se necesita

| Elemento | Detalle | Alternativa |
| --- | --- | --- |
| Celular | Con modo de grabación a 240 fps (o 120 como mínimo) | — |
| Soporte fijo | Trípode | Silla, banco, pila de libros, repisa: cualquier apoyo que no se mueva |
| Espacio | Unos 6 metros de largo, con lugar para extender el brazo por encima de la cabeza | Patio, garaje, cochera, pasillo amplio, plaza |
| Luz | Luz natural abundante | — |
| Raqueta | Ayuda a que el gesto sea natural | Se puede grabar sin raqueta si no hay espacio seguro |
| Cinta de papel | Para marcar en el piso la posición de la cámara y del jugador | Cualquier marca que se pueda dejar |

**No se necesita:** cancha, red, pelotas, ni otra persona jugando. El sistema mide el movimiento
del cuerpo, no la trayectoria de la pelota. Los gestos se ejecutan en seco.

Sí conviene que alguien opere el celular, aunque no es imprescindible: con temporizador o
simplemente grabando de corrido también funciona.

---

## 2. Configuración del celular

### Frecuencia de captura

Este es el punto crítico de todo el protocolo. Por debajo de 120 fps el gesto rápido no es
medible y el material no sirve para el análisis principal.

**iPhone:** Ajustes → Cámara → Grabar en cámara lenta → **1080p a 240 fps**. Si el modelo no lo
ofrece, usar 1080p a 120 fps.

**Android:** varía según fabricante. Buscar en la app de cámara los modos "Cámara lenta",
"Slow motion", "Super slow motion" o "HFR / High Frame Rate". Verificar la resolución asociada:
algunos equipos solo ofrecen 240 fps a 720p, lo cual es aceptable —**es preferible 720p a 240 fps
que 1080p a 30 fps**, porque la resolución se puede compensar y la frecuencia de captura no.

Si el equipo tiene un modo de video normal a 120 fps, es preferible al modo de cámara lenta,
porque evita la ambigüedad entre frecuencia de captura y de reproducción.

### Resto de los ajustes

- **Orientación horizontal** (apaisada). Siempre.
- **Estabilización desactivada** si el menú lo permite: recorta el encuadre y deforma
  ligeramente la imagen, lo que perjudica la estimación de pose. Como la cámara está fija, no
  hace falta.
- **Enfoque y exposición bloqueados**: encuadrar, mantener presionado sobre el cuerpo del jugador
  hasta que aparezca el bloqueo, y no volver a tocar la pantalla durante la sesión. Evita que la
  cámara reajuste el enfoque en medio de un gesto.
- **Limpiar el lente.** Suena trivial y arruina sesiones enteras.

---

## 3. Condiciones del entorno

**Luz: es el segundo factor crítico.** Grabar a 240 fps significa que cada fotograma recibe una
octava parte de la luz que recibiría a 30 fps. Con poca luz el video sale oscuro y con
desenfoque de movimiento, y la estimación de pose se degrada mucho.

- **Grabar de día, al aire libre o con luz natural directa.** Media mañana o media tarde.
- **Evitar la luz artificial de interiores.** Además de ser insuficiente, las lámparas LED y
  fluorescentes parpadean a una frecuencia que a 240 fps produce bandas horizontales en la imagen.
- Evitar el contraluz: el sol o la ventana deben estar detrás de la cámara, no detrás del jugador.
- Evitar la sombra parcial: que la mitad del cuerpo esté al sol y la otra en sombra confunde al
  detector.

**Fondo y vestimenta:**

- Fondo lo más liso y despejado posible. Sin otras personas en cuadro.
- Ropa **ajustada o semiajustada**, de color contrastante con el fondo. La ropa muy suelta es uno
  de los peores enemigos de la estimación de pose: el modelo detecta el borde de la tela y no la
  articulación.
- Evitar ropa del mismo color que el fondo.
- Preferible manga corta y pantalón corto: cuanto más visible el contorno de las extremidades,
  mejor.

---

## 4. Ubicación de la cámara

| Parámetro | Valor |
| --- | --- |
| Altura | Aproximadamente 1 metro (altura de la cadera) |
| Distancia al jugador | 4 a 5 metros |
| Encuadre | Cuerpo completo, con margen por encima de la raqueta en el punto más alto del saque |
| Inclinación | Cero: el celular vertical respecto del piso, no apuntando hacia arriba ni hacia abajo |

**Verificación antes de grabar:** hacer un saque completo de prueba y confirmar que en ningún
momento la raqueta ni los pies salen del cuadro. Es el error más frecuente y obliga a repetir
toda la toma.

**Marcar el piso con cinta.** Dos marcas: dónde va el trípode y dónde se para el jugador. Es
indispensable para la segunda sesión: el Criterio 3 del plan compara al jugador consigo mismo, y
esa comparación solo es válida si el encuadre es el mismo. Anotar además la distancia medida.

### Dos ángulos

**Ángulo A — Perfil.** La cámara perpendicular al jugador, del lado del brazo dominante. Es el
encuadre principal: captura mejor la flexión de rodilla, la extensión de codo y el arqueo del
tronco.

**Ángulo B — Tres cuartos.** La cámara a unos 45° por delante del jugador. Captura mejor la
rotación de cadera y hombros, y por lo tanto la separación cadera-hombro.

---

## 5. Plan de tomas

### Bloque principal — 6 clips

Un clip por combinación de gesto y ángulo. Cada clip contiene **6 repeticiones seguidas** del
mismo gesto.

| # | Gesto | Ángulo | Repeticiones | Duración aprox. |
| --- | --- | --- | --- | --- |
| 1 | Saque | Perfil | 6 | 50 s |
| 2 | Saque | Tres cuartos | 6 | 50 s |
| 3 | Drive | Perfil | 6 | 40 s |
| 4 | Drive | Tres cuartos | 6 | 40 s |
| 5 | Revés | Perfil | 6 | 40 s |
| 6 | Revés | Tres cuartos | 6 | 40 s |

**Cómo ejecutar cada repetición:**

1. Posición neutra, quieto, **2 o 3 segundos**.
2. Gesto completo a velocidad e intensidad reales, sin frenar el movimiento.
3. Volver a posición neutra y quedarse quieto **2 o 3 segundos** antes de la repetición siguiente.

Las pausas en posición neutra no son un detalle: son lo que permite separar las repeticiones
después. Sin ellas, un clip de seis saques es una masa continua difícil de segmentar.

**El gesto debe ejecutarse en serio.** Un saque hecho a media velocidad "para la cámara" no
produce la secuencia de la cadena cinética que el sistema busca medir. Si hay espacio y es
seguro, hacerlo con raqueta y con la intención de golpear.

### Bloque de control — 4 clips

Material deliberadamente deficiente, necesario para probar que el sistema rechaza correctamente
lo que no puede medir.

| # | Contenido | Configuración |
| --- | --- | --- |
| 7 | 3 saques, ángulo perfil | Modo video **normal a 30 fps** |
| 8 | 3 saques, ángulo perfil | Modo video **a 60 fps** |
| 9 | 3 saques | 240 fps, pero **con el cuerpo parcialmente fuera de cuadro** |
| 10 | 3 saques | 240 fps, **de espaldas a la cámara** o con oclusión del brazo |

Cambiar la configuración de fps para los clips 7 y 8 y volver a 240 después. No olvidar volver.

### Total

10 clips, unos 5 minutos de material, aproximadamente 2 GB. La sesión completa lleva alrededor de
45 minutos contando el armado.

---

## 6. Segunda sesión

Repetir **exactamente** el bloque principal (clips 1 a 6) al menos una semana después. No hace
falta repetir el bloque de control.

Condición indispensable: **mismo encuadre**. Volver a las marcas de cinta, misma altura,
misma distancia, misma configuración de cámara. La comparación del jugador consigo mismo se apoya
en que el error de la cámara sea constante entre sesiones; si el encuadre cambia, el error cambia
y la comparación pierde validez.

Es preferible que la segunda sesión sea a una hora del día parecida, para tener condiciones de
luz similares.

---

## 7. Transferencia y edición

### ¿Hace falta editar?

**No. Y es importante que no se edite.**

Cualquier recorte, filtro, exportación desde una aplicación de edición o compartido por
mensajería vuelve a codificar el video, y al hacerlo puede cambiar la frecuencia de cuadros,
fijar la ralentización dentro del archivo o comprimir la imagen. Cualquiera de esas tres cosas
degrada o invalida el material.

**No usar:** WhatsApp, Telegram, Instagram, ni ninguna app de mensajería. Comprimen agresivamente.

**Sí usar:** cable USB, AirDrop entre dispositivos Apple, Google Drive o Dropbox con la opción de
carga en calidad original.

### Recorte, si hiciera falta

Si un clip quedó muy largo, se puede recortar **sin recodificar**:

```bash
ffmpeg -i entrada.mov -ss 00:00:05 -to 00:00:45 -c copy salida.mov
```

La opción `-c copy` es la que evita la recodificación. Sin ella, el archivo se vuelve a comprimir.

### Verificación obligatoria

Después de transferir, verificar **cada archivo**:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=r_frame_rate,avg_frame_rate,nb_frames,duration,width,height \
  -of default=noprint_wrappers=1 archivo.mov
```

Qué mirar:

- `r_frame_rate` debería dar `240/1` o similar. Si da `30/1` en un clip de cámara lenta, la
  ralentización quedó fijada en el archivo: anotar el factor (habitualmente 8) para que el sistema
  lo compense.
- `nb_frames` dividido por `duration` debe coincidir aproximadamente con la frecuencia declarada.
  Si no coincide, hay ralentización incorporada.
- `width` y `height`: confirmar que la resolución es la esperada.

**Hacer esta verificación el mismo día de la grabación.** Si algo salió mal, es mucho más barato
repetir la sesión ese día que descubrirlo tres semanas después.

---

## 8. Nombres de archivo

Renombrar cada clip con este formato:

```
AAAAMMDD_jugador_gesto_angulo_fps_toma.mov
```

Ejemplos:

```
20260901_VCR_saque_perfil_240_01.mov
20260901_VCR_drive_trescuartos_240_01.mov
20260901_VCR_saque_perfil_030_ctrl.mov
20260908_VCR_saque_perfil_240_02.mov
```

Los archivos van **fuera del repositorio**, en una carpeta propia. No se suben a git.

---

## 9. Planilla de la sesión

Completar durante o inmediatamente después de la grabación. Es la ficha de observación del
apartado 2.6 y se cita en la tesis.

| Campo | Valor |
| --- | --- |
| Fecha y hora | |
| Lugar | |
| Jugador (iniciales) | |
| Mano dominante | |
| Nivel | |
| Modelo de celular | |
| Resolución y fps configurados | |
| Altura de la cámara (cm) | |
| Distancia cámara–jugador (m) | |
| Condición de luz | Sol directo / nublado / sombra abierta |
| Vestimenta | Color y tipo |
| Con raqueta | Sí / No |
| Incidencias | Repeticiones fallidas, interrupciones, cambios de encuadre |

---

## 10. Lista de verificación

**Antes de grabar**
- [ ] Celular configurado a 240 fps (o 120), 1080p, horizontal
- [ ] Estabilización desactivada
- [ ] Lente limpio
- [ ] Batería por encima del 50 % y al menos 5 GB de espacio libre
- [ ] Cámara fija a 1 m de altura, 4–5 m de distancia, sin inclinación
- [ ] Marcas de cinta colocadas en el piso
- [ ] Saque de prueba: cuerpo completo y raqueta dentro del cuadro en todo momento
- [ ] Enfoque y exposición bloqueados
- [ ] Buena luz, sin contraluz ni sombra parcial
- [ ] Ropa ajustada y contrastante

**Durante**
- [ ] 6 repeticiones por clip, con pausas de 2–3 segundos en posición neutra
- [ ] Gestos ejecutados a intensidad real
- [ ] Los 6 clips del bloque principal
- [ ] Los 4 clips del bloque de control
- [ ] Configuración devuelta a 240 fps después de los clips 7 y 8

**Después**
- [ ] Transferencia por cable o nube en calidad original
- [ ] Verificación con `ffprobe` de todos los archivos, el mismo día
- [ ] Archivos renombrados según convención
- [ ] Planilla de sesión completada
- [ ] Fecha de la segunda sesión agendada
