# Especificación del frontend y de la experiencia de uso — MVP KinetiQ

Versión 1 · 1 de octubre de 2026 · Estado: **vigente como punto de partida**, ajustable.

Este documento acompaña a las maquetas de `docs/ux/maquetas/`:
- `capturas/*.png`: cómo se ve cada pantalla (referencia visual principal).
- `html/*.html`: el marcado de cada maqueta, útil para copiar colores, tamaños y textos. **No es código para reutilizar**: el frontend se construye en React + Tailwind.

Las maquetas usan datos de ejemplo armados con los patrones reales del corpus. Los textos entre corchetes son marcadores.

---

## 1. Principios que no se negocian (derivan de CLAUDE.md §2)

1. **R1.** La carga lee los fps reales del archivo; por debajo de 120 fps avisa que solo se analiza la preparación y pide confirmación explícita.
2. **R2.** Vocabulario: "se observa", "se midió", "no se pudo medir", "alerta de carga". Nunca diagnosticar, predecir, prevenir, nombrar patologías ni indicar tratamientos.
3. **R3.** Cuatro estados (correcto, desvío leve, alerta de carga, no auditable), siempre con ícono + texto, nunca solo color. "No ordenable" **no** es un quinto estado: es un motivo que se muestra en gris dentro de la observación de secuenciación (decisión 015).
4. **R4.** Todo valor en la vista detallada y en el PDF lleva confianza y fundamento. Todo reporte lleva versión del motor, backend de pose y parámetros de filtrado.
5. **El frontend no calcula nada biomecánico.** Solo representa el JSON del reporte que produce el motor.
6. **El brazo (balanceo, vector hombro–codo) se informa como dato, "sin evaluar".** Nunca como correcto o incorrecto (decisión 011).

## 2. Estilo visual

- Fondo oscuro `#081015` con grilla sutil de 72 px; tarjetas `#0d181e` con borde `#1c2a32` y radio 20 px.
- Tipografías: **Sora** (títulos), **DM Sans** (texto), **JetBrains Mono** (etiquetas en mayúsculas, datos técnicos).
- Acento de marca: verde `#4ade80 → #10b981` (botones principales, palabra destacada de los títulos).
- Acento secundario: turquesa `#22d3ee` (rendimiento, procesamiento).
- Colores de estado (badge con borde y fondo propios):
  - Correcto `#4ade80` sobre `#0b2217`
  - Desvío leve `#fbbf24` sobre `#221a08`
  - Alerta de carga `#f87171` sobre `#250e10`
  - No auditable `#b4c1ca` sobre `#131e25`
- Colores de segmento en gráficos: cadera `#a78bfa`, tronco `#22d3ee`, brazo `#f1f5f9`.
- **Regla:** el verde de marca nunca se usa para comunicar un estado. Los estados siempre van en su badge.
- El PDF usa fondo blanco y la misma tipografía (pensado para imprimir).

## 3. Navegación y pantallas

Sin sesión iniciada: **Landing** → **Registro / Ingreso**.
Con sesión: **Biblioteca** · **Cargar** · **Perfil**. El reporte, el procesamiento y la evolución se abren desde la biblioteca.

| Pantalla | Maqueta | Notas |
|---|---|---|
| Landing | `Main` | Incluye "qué mide y qué no" y la explicación de los cuatro estados. |
| Registro | `Registro` | Pide el rol (jugador, entrenador, profesional de la salud) y el consentimiento (Ley 25.326). |
| Biblioteca | `Biblioteca` | Tarjetas por sesión con miniatura real del video, estado de procesamiento, puntaje de rendimiento y conteo de observaciones por estado. |
| Cargar | `Cargar`, `CargarMovil` | Ver §5. |
| Procesando | `Procesando` | Estados de la máquina de estados del Capítulo 4 §4.2.4, progreso por etapa con texto llano y la etiqueta técnica (E0–E5) en chico. Aclara que se puede cerrar la página. |
| Reporte simple | `ReporteSimple`, `ReporteMovil` | Vista por defecto del jugador. |
| Reporte detallado | `ReporteDetallado` | Vista por defecto del entrenador y del profesional. Los tres niveles de la tesis. |
| PDF | `ReportePDF1`, `ReportePDF2` | Siempre el reporte técnico completo, A4. |
| Evolución | `Evolucion` | Comparación con el propio jugador, solo entre sesiones del mismo gesto y encuadre. Las sesiones sin dato se muestran como hueco, nunca interpoladas. |
| Perfil | `Perfil` | Rol, vista por defecto, mano dominante, privacidad, descargar y eliminar datos. |

## 4. Roles y vistas (opción B)

- El rol se elige al registrarse y se puede cambiar en el perfil.
- Jugador → abre los reportes en vista **simple**. Entrenador y profesional → vista **detallada**.
- Las dos vistas muestran los mismos datos; un interruptor "Simple / Detallado" permite cambiar en cualquier momento.
- El PDF exportable es siempre el reporte técnico completo.

## 5. Carga de una sesión

- **Una sesión = un grupo de videos** del mismo atleta, gesto, encuadre y lado de cámara. **Cada video es un golpe.**
- Campos: atleta, golpe (saque, drive, revés), encuadre (perfil, tres cuartos), lado de la cámara respecto del jugador (derecha, izquierda), **¿Cómo lo grabaste?** (ver abajo).
- **¿Cómo lo grabaste?** (decisión 020, 2/10/2026): una sola vez por sesión, no por video. Tres opciones, en lenguaje llano, ninguna marcada por defecto — el usuario tiene que elegir a propósito:
  - "Modo cámara lenta de 240 fps (o "slow-mo" a la velocidad más alta)" → `camara_lenta_240`.
  - "Modo cámara lenta de 120 fps" → `camara_lenta_120`.
  - "Grabación normal (sin cámara lenta)" → `normal`.
  - Texto de ayuda: "en el iPhone, es el modo que elegiste en la app Cámara antes de grabar — no se puede saber mirando el archivo". El motor combina esto con los datos reales del archivo; si no coinciden, el golpe se marca con un error claro en vez de adivinar (ver más abajo).
- Selección múltiple de archivos (MP4, MOV). Validación previa en el navegador, por archivo:
  - más de 50 MB → no se sube, con instrucciones para recortar (decisión 016, tentativa);
  - duración mayor a ~8 s → aviso de que probablemente tenga varios golpes;
  - el aviso de "menos de 120 fps → solo preparación" del navegador usa el fps que declara el propio archivo, **sin corregir por cámara lenta todavía** (esa corrección la hace el motor, no el navegador): si el usuario ya eligió "cámara lenta" más arriba, no hace falta asustarlo con este aviso — se muestra solo cuando el modo elegido es "normal", o antes de que haya elegido el modo.
- La validación del navegador es una cortesía; la definitiva la hace el motor (Capítulo 4 §4.2.3). Si el modo declarado no coincide con el archivo (p. ej. "cámara lenta de 240" sobre un archivo que no es múltiplo entero de su propio fps), el golpe queda en error con un mensaje en lenguaje llano ("no pudimos confirmar la velocidad de este video; revisá el modo de captura o volvé a grabarlo") — nunca se procesa adivinando la escala temporal (R3).
- Panel lateral (o desplegable en móvil) con "cómo recortar" para iPhone y Android y "antes de grabar".

## 6. Contenido del reporte

### Vista simple
1. **Puntaje de rendimiento** con sus tres componentes (§7).
2. **Lo más importante:** máximo tres observaciones en lenguaje llano, cada una con su estado y un enlace a la evidencia.
3. **Tres momentos del golpe:** tres fotogramas reales del video, con el esqueleto, en el pico de cadera, de tronco y de brazo, y una frase ("Primero giró tu cadera, casi enseguida tu tronco…"). Selector de golpe; los golpes no ordenables llevan una marca y una explicación.
4. **Comparado con vos mismo:** tarjetas con dirección (mayor, igual, menor) frente a la sesión anterior comparable, con el número chico debajo.
5. Llamada a descargar el PDF o ver el detalle técnico.

### Vista detallada
- Nivel 1: las mismas observaciones, compactas.
- Desglose del puntaje: tabla con medición, referencia propia, puntaje y peso.
- Nivel 2: reproductor del video con esqueleto, sincronizado con las curvas de velocidad de giro (eje temporal único), marcas de los picos y tramos no auditables sombreados con su explicación. Gráfico de secuenciación (escalera cadera → tronco → brazo) con la evaluación del par cadera-tronco y el brazo "sin evaluar".
- Nivel 3: tabla de magnitudes (valor, confianza, estado, fundamento) y bloque de trazabilidad (motor, pose, filtro, frecuencia de corte, fps efectivos y, desde la decisión 020, cómo se obtuvieron: modo de captura declarado, factor de ralentización y origen).

### PDF
Página 1: datos de la sesión, resumen (puntaje + observaciones), secuenciación de un golpe y tabla por golpe. Página 2: métricas con confianza y fundamento, cómo leer los estados, trazabilidad y limitaciones.

## 7. Puntaje de rendimiento (propuesta, fórmula v1)

**Por qué existe:** la tesis plantea un reporte dual de rendimiento y de prevención (Capítulo 2 §2.3.3, Capítulo 3 §3.3.4.4), y a la vez se diferencia de las aplicaciones que dan "un puntaje basado en rendimiento" opaco (Capítulo 1 §1.3). Por eso el puntaje es **descomponible**: cada componente se ve, se mide y se explica.

**Componentes (0 a 100 cada uno), relativos al propio jugador:**
1. **Consistencia entre golpes:** qué tan parecidos son los golpes de la sesión entre sí (por ejemplo, dispersión de la separación cadera-hombro y del instante de los picos).
2. **Velocidad de giro del tronco:** pico de la sesión frente a la mejor sesión del jugador en el mismo gesto y encuadre.
3. **Separación cadera-hombro:** frente al rango habitual del jugador.

**Reglas:**
- Puntaje = promedio de los componentes auditables. Un componente no auditable se excluye y se informa.
- Con menos de dos componentes auditables, el puntaje es **no auditable**.
- Los componentes 2 y 3 necesitan al menos una sesión previa comparable. En la primera sesión de un gesto se muestra "Desde tu 2.ª sesión de este golpe" (sin número).
- No se compara con otros jugadores ni con profesionales (R5).
- Se rotula como índice descriptivo propio, no validado contra la velocidad de pelota.
- **La fórmula exacta (cómo se mapea cada componente a 0–100) se congela en una decisión de la Etapa 5 antes de calcularla sobre datos**, y su versión viaja en el reporte.

## 8. Responsive

- Puntos de corte: móvil (≤ 640 px, diseño de referencia 390 px), tableta (641–1024 px) y escritorio (≥ 1025 px, referencia 1440 px).
- **El celular es prioritario en Cargar y en el Reporte simple**: los videos se graban y se suben desde el teléfono.
- En móvil: navegación inferior de tres pestañas (Biblioteca, Cargar, Perfil), botón de acción fijo abajo en Cargar, grillas de tres columnas pasan a una columna, la tabla del nivel 3 pasa a tarjetas apiladas, el reproductor va arriba y las curvas debajo.
- Objetivos táctiles de 44 px como mínimo; contraste de texto 4,5:1.

## 9. Consecuencias para el modelo de datos (revisar antes de las migraciones 4.5.1)

El esquema del Capítulo 4 §4.4.6 no contempla todo lo que muestran las maquetas. Como mínimo:
- Entidad **sesión** (usuario, atleta, gesto, encuadre, lado de cámara, fecha, estado agregado) y `video.sesion_id`. El gesto, el encuadre y el lado de cámara pasan a la sesión.
- En usuarios: `rol` y `vista_por_defecto`.
- Por video (golpe): estado de procesamiento, ruta de la miniatura, ruta del video liviano con esqueleto y rutas de los tres fotogramas clave.
- Reporte a nivel de **sesión** (puntaje, componentes, versión de la fórmula, observaciones) además del resultado por golpe.
- Alertas: el campo `severidad` usa los cuatro estados de R3; "no ordenable" va como motivo, no como severidad.

## 10. Lo que el JSON del reporte (Etapa 5) tiene que traer

Todo lo que las pantallas muestran y nada que no muestren: datos de la sesión; puntaje y componentes con su medición y referencia; hasta tres observaciones (estado, título, texto llano, enlace a evidencia, magnitud que la disparó, fundamento); por golpe: instantes de pico de cadera, tronco y brazo, Δ, motivo si no es ordenable, rutas de los tres fotogramas clave; series de velocidad normalizadas para las curvas; tramos no auditables con su motivo; comparación con la sesión anterior comparable; tabla de magnitudes con valor, unidad, confianza, estado y fundamento; bloque de trazabilidad (incluye, por la decisión 020, el **modo de captura declarado**, el **factor de ralentización** y su origen, además de los fps efectivos).

## 11. Fuera del MVP

Planes y pagos, comparación con jugadores ATP/WTA, notificaciones por correo, panel multi-atleta del profesional (simulado como en el Capítulo 4 §4.3.3), exportación DICOM/HL7.
