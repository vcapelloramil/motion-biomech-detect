# Capítulo 3 — Marco Teórico y Estado del Arte

> Archivo de referencia para uso interno de desarrollo. Reproduce el contenido del
> Capítulo 3 de la tesis "Sistema de análisis biomecánico preventivo para el tenis
> mediante visión artificial y análisis de la cadena cinética" (Valentín Capello Ramil,
> Universidad del Salvador, 2026), tal como fue entregado. Se conserva íntegro porque
> varias decisiones de las Etapas 2 y 4 del plan de desarrollo dependen directamente de
> argumentos específicos de este capítulo.

---

## 3.1. Estado del Arte

El relevamiento se organizó en tres capas: revisiones sistemáticas y análisis en la
intersección de visión por computadora, biomecánica deportiva y medicina del deporte;
trabajos de validación que contrastan técnicas sin marcadores contra sistemas
optoelectrónicos de referencia (Vicon, Qualisys, OptiTrack); y el estado de la industria,
incluidos distintos productos descontinuados.

### 3.1.1. Investigaciones Nacionales en Biomecánica y Visión Artificial

No se identificó ninguna línea de investigación argentina publicada y consolidada que
integre estimación de pose por aprendizaje profundo con análisis de la cadena cinética en
tenis. Existen tres núcleos que no dialogan entre sí: un núcleo informático orientado a
dominios ajenos al deportivo, un núcleo de kinesiología y fisiatría predominantemente
clínico y observacional, y el núcleo del tenis como práctica, con una población no
instrumentada. La brecha nacional no es de capacidad técnica ni de conocimiento clínico:
es de integración.

**Consecuencia para el desarrollo:** el proyecto carece de umbrales normativos para
población amateur argentina; los umbrales del motor de reglas se importan de literatura
internacional de poblaciones de élite (Brecha 7).

### 3.1.2. Investigaciones Internacionales

#### 3.1.2.1. Validación del mocap sin marcadores

**Nakano et al. (2020):** evaluó captura 3D sin marcadores mediante OpenPose y cinco
cámaras contra un sistema optoelectrónico. Aproximadamente el 47 % de los errores fue
inferior a 20 mm y el 80 % inferior a 30 mm, pero un 10 % superó los 40 mm; la causa de
esos errores mayores fue pérdida de seguimiento, no imprecisión distribuida. Suavizaron
sus datos con un filtro Butterworth de cuarto orden y retardo cero, con corte determinado
por análisis residual (Winter).

**Needham et al. (2021), Universidad de Bath:** comparando OpenPose, AlphaPose y
DeepLabCut contra captura optoelectrónica, hallaron diferencias sistemáticas en cadera y
rodilla de 30 a 50 mm, atribuidas a etiquetado erróneo en el entrenamiento; en el tobillo
los errores fueron de 1 a 15 mm. **Distinción central:** el error aleatorio se atenúa con
filtrado, el sistemático es un sesgo que se propaga a toda magnitud derivada. Un sesgo
constante afecta la magnitud absoluta de un ángulo, no el tiempo de un pico de velocidad.

**Mathis et al. (2020):** los algoritmos de pose fueron optimizados para métricas de
visión por computadora (mAP, PCK) que responden "¿está el punto donde debería?", no
"¿es un centro articular anatómicamente reproducible?".

**OpenCap (Uhlrich et al., 2023):** plataforma web de código abierto que calcula
cinemática y dinámica a partir de dos o más smartphones, con errores cinemáticos
articulares de 4,1° (RMSE < 6°) a menos del 1 % del costo de un laboratorio de USD
150.000. Requiere dos o más iPhones calibrados; no dispone de motor de reglas de tenis ni
evalúa secuenciación de cadena cinética en gestos de raqueta.

**Theia3D (Kanko et al., 2021):** sistema multicámara de gama alta, diferencias de
centros articulares de 4,7 ± 1,2 cm en miembro inferior y 5,7 ± 1,5 cm en superior, con
concordancia angular RMSD de 11–14°.

**Pagnon et al. (2022):** respaldan el patrón de Needham et al. respecto a errores de
centros articulares; reportan errores en el rango de movimiento de 2,8° a 14,1° con dos
cámaras y OpenPose. Con Pose2Sim (8 cámaras) redujeron los errores a un promedio de
2,3°–4,3°.

**Tabla de expectativa cuantitativa (aporte al apartado 2.4):**

| Magnitud | Rango esperable | Fuente | Implicancia |
| --- | --- | --- | --- |
| Centro articular, tobillo | 1–15 mm | Needham (2021); Pagnon (2022) | Referencia distal confiable |
| Centro articular, cadera/rodilla | 30–50 mm, sistemático | Needham (2021); Pagnon (2022) | Sesgo no filtrable; afecta magnitud, no timing |
| Ángulo, multicámara calibrada | ~4,1° (RMSE < 6°) | Uhlrich (2023) | Piso optimista |
| Ángulo, gestos balísticos | RMSD 11–14° | Theia3D | Techo realista para tenis |
| Rango de movimiento, 2 cámaras | 2,8°–14,1° | Pagnon (2022); D'Antonio | Banda operativa esperable |

**Umbral de precisión angular adoptado:** del orden de 10–15° para ángulos absolutos, con
requisito más estricto sobre el orden temporal de los picos. Prometer 5° con una sola
cámara no sería defendible.

#### 3.1.2.2. La estimación de pose aplicada al deporte: evidencia agregada

**Aulton et al. (2025):** primera revisión sistemática de estimación de pose por
aprendizaje profundo desde las ciencias del deporte, PRISMA sobre 50 artículos. Hallazgos
centrales:

- La gestión de riesgo clínico no aparece como dominio de aplicación propio; la
  prevención de lesiones se menciona como beneficio secundario.
- 21 de 50 estudios entrenaron y validaron sobre datos privados.
- Solo 12 de 50 estudios validaron sobre participantes reales (déficit de validación
  ecológica). **La grabación de campo con dispositivos móviles es la contribución
  metodológica diferencial del proyecto frente al 76 % de la literatura.**
- Ausencia total de estudios longitudinales.
- OpenPose fue el algoritmo más usado (14 estudios); 20 trabajos en 2D y 27 en 3D. La
  mayoría de los enfoques 3D emplea un modelo adicional para convertir 2D en 3D —enfoque
  que paga error de reconstrucción pero es el más adecuado para una sola cámara; seis de
  siete trabajos suplementarios usaron cámara única.

#### 3.1.2.3. Antecedentes específicos en tenis

**Universidad de Bath (Journal of Sports Sciences, 2025):** 16 tenistas ejecutando saque,
drive y revés, capturados con HRNet y OpenPose contra marcadores y fuerzas de reacción.
Sesgos pequeños (≤ 4 %) para trabajo mecánico externo, pero con **artefactos de alta
frecuencia** en la cinemática sin marcadores —validación empírica directa de la necesidad
de la etapa de procesamiento de señales.

**Kovacs y Ellenbecker (2011):** modelo de análisis del saque de ocho etapas en tres
fases (preparación, aceleración, finalización). Base del motor de reglas.

#### 3.1.2.4. Epidemiología y modelado del riesgo de lesiones en tenis

**Abrams, Renstrom y Safran (2012):** el tenis impone cargas elevadas al hombro y codo
cientos de veces por partido; las lesiones agudas afectan el miembro inferior, las
crónicas el superior. La cadena cinética enlaza los segmentos del miembro superior,
inferior y core.

**Revisión sistemática (37 estudios, PROSPERO, 2011–2025):** incidencia de 1,25 a 56,6
lesiones por 1000 horas en adultos; predominio de miembro inferior (48–56 %), seguido de
afectación lumbar (12–39 %) y sobreuso de hombro. Las modificaciones en el timing de la
técnica redujeron el torque del hombro (cadena: timing medible → modificable → torque
reducido → riesgo reducido).

**Limitación declarada:** la evidencia proviene de poblaciones de élite o subélite; la
población destinataria es amateur.

### 3.1.3. Productos Similares y Herramientas Comerciales

- **Sistemas de laboratorio** (Vicon, Qualisys, OptiTrack): patrón oro, requieren
  infraestructura especializada.
- **Grado investigación** (OpenCap, Theia3D, Pose2Sim): todas requieren múltiples cámaras.
- **Infraestructura fija** (Hawk-Eye, PlaySight): producen estadística de juego, no
  cinemática articular.
- **SwingVision:** competidor comercial más directo. Usa cámara de iPhone/iPad,
  suscripción USD 179,99 anuales. Cuatro asimetrías con el proyecto: (1) rastrea pelota y
  ubicación, no ángulos ni secuenciación; (2) sin dimensión clínica; (3) tecnología
  patentada y opaca; (4) dependencia de Apple y precio elevado.
- **Sensores inerciales (2013–2021):** Babolat Play, Zepp, Sony Smart Tennis Sensor,
  Babolat POP, HEAD, Qlipp. Todos discontinuados en una ventana de 18 meses entre 2020 y
  2021.

**Nicho identificado:** la intersección de "monocular", "cadena cinética" y "salida
clínica trazable" está desocupada.

### 3.1.4. Brechas Identificadas (justificación del MVP)

| Brecha | Objetivo | Evidencia | Riesgo si no se atiende |
| --- | --- | --- | --- |
| 1. Dominio clínico | OE5 | Aulton (2025); matriz | Se vuelve un SwingVision peor |
| 2. Opacidad / trazabilidad | OE3, OE5 | SwingVision; Theia3D | Sin adopción clínica |
| 3. Datos privados | Ap. 2.5 | Aulton: 21/50 privados | Irrelevancia académica |
| 4. Validación ecológica | Ap. 2.5 | Aulton: 12/50 en vivo | Solo funciona en dataset |
| 5. Longitudinal | Cap. 6 | Aulton (2025) | Sobrepromesa refutable |
| 6. Monocular↔cinemática | OE1, OE2 | Uhlrich; Needham | Es la hipótesis del proyecto |
| 7. Nacional/normas | Ap. 1.3, Cap. 6 | Ap. 3.1.1 | Umbrales no validados localmente |

**Corrección técnica relevada:** YOLOv8-Pose no es un modelo 3D. La documentación de
Ultralytics confirma que se entrena sobre COCO-Pose con 17 puntos en tripletas (x, y,
visibilidad), sin eje Z. El Objetivo Específico 1 se formula sobre una arquitectura de dos
etapas (percepción 2D + elevación 2D→3D), práctica dominante según Aulton et al. Ver
desarrollo completo en el apartado 4.4.3 del Capítulo 4.

---

## 3.2. Sondeo Exploratorio de Demanda (Encuesta)

Cuestionario anónimo (Google Forms, español e inglés), difundido en comunidades de tenis
online. Muestreo por conveniencia y autoselección, **no representativo**.

**Perfil:** mayormente jugadores de nivel intermedio de club, algunos avanzados, un
principiante, un entrenador.

**Hallazgos clave:**

- **~60 % de los participantes** reportó haber tenido alguna lesión o molestia
  relacionada con el tenis; la zona más mencionada fue el hombro, coincidiendo con el
  patrón epidemiológico del apartado 3.1.2.4.
- La evaluación técnica actual es indirecta y subjetiva ("por cómo sale la pelota", "por
  sensación", "por lo que dice el entrenador"); solo una minoría se graba.
- Interés alto entre jugadores intermedios y principiantes (4 o 5 sobre 5); **los
  jugadores más avanzados fueron los más escépticos** — el público más receptivo es el
  intermedio.
- **Formato de salida preferido, por amplio margen: "un resumen simple con 2 o 3 cosas a
  corregir"**, seguido de "un reporte para mostrarle al entrenador o kinesiólogo". Los
  números y gráficos detallados recibieron bastante menos interés. **Esta es la base
  directa de la jerarquía de tres niveles del apartado 4.6.2 del Capítulo 4.**
- Fuerte preferencia por modelos gratuitos o de bajo costo; confirma que la barrera de
  precio de SwingVision (USD 179,99/año) es real para este público.
- Un participante que usó SwingVision lo dejó por no querer pagar la suscripción.
- Objeción de fondo de un jugador avanzado: la técnica y la lesión dependen de la
  biología de cada jugador y del contexto, "un problema de sistemas biológicos al que se
  le aplica una solución de ingeniería" — reproduce la crítica de Bahr (2016).

---

## 3.3. Marco Teórico

Organizado en dos variables: **Variable 1** (3.3.1–3.3.2, visión artificial e IA — cómo el
software convierte un video en coordenadas del cuerpo) y **Variable 2** (3.3.3, biomecánica
y cadena cinética — sentido físico y clínico de esas coordenadas); el punto 3.3.4 explica
la relación entre ambas.

### 3.3.1. Inteligencia Artificial y Visión por Computadora

**3.3.1.1. De la escena real a la imagen.** La cámara pierde el eje de profundidad al
proyectar una escena 3D sobre una imagen 2D ("ambigüedad de profundidad", apartado 1.2).
**Dato crítico:** el sistema debe leer la cantidad real de FPS con que se grabó el video,
no asumirla. Un error de FPS no genera ruido: genera un reporte internamente coherente y
completamente falso (todas las velocidades salen multiplicadas o divididas por el mismo
factor, sin que ningún filtro posterior lo detecte).

**3.3.1.2. De reglas hechas a mano a modelos que aprenden.** Las posturas deportivas son
demasiado variadas para reglas escritas a mano (Aulton et al., 2025); el aprendizaje
profundo es el único enfoque manejable para gestos tan complejos.

**3.3.1.3. Tres formas de encontrar los puntos del cuerpo.** Mapas de calor (HRNet):
precisos pero pesados. Regresión directa (BlazePose): apunta a la velocidad. Clasificación
(RTMPose): buena precisión y rapidez incluso en baja calidad — en Rode et al. (2025) fue
el modelo 2D más preciso (9,3° de error en flexión de rodilla, 100 % de detección).

**3.3.1.4. Tenis como caso favorable.** Un solo jugador ejecutando un gesto, pocos
jugadores en cuadro: escenario favorable. Contra: auto-oclusión y velocidades muy altas
que producen desenfoque de movimiento.

**3.3.1.5. Por qué no alcanza con las métricas del área informática.** Las métricas mAP,
PCK, MPJPE responden "¿el punto está donde debería?", no "¿corresponde al centro de la
articulación?". **Principio de diseño:** el sistema se mide con grados de error angular,
orden de picos de velocidad y falsas alarmas — no con métricas de visión por computadora.

### 3.3.2. Modelos de Estimación de Pose 3D

**3.3.2.1. Dificultades para estimar 3D con una sola cámara.** Infinitas posiciones del
cuerpo producen la misma imagen 2D; el modelo "adivina" la profundidad usando lo aprendido
de sus datos de entrenamiento. Cuando el gesto se aleja de lo visto en entrenamiento, la
adivinanza empeora sin avisar. **Un dato equivocado que se hace pasar por bueno es peor que
un dato faltante** — de ahí la necesidad de marcar como "no confiable" todo dato bajo
cierto puntaje de certeza.

**3.3.2.2. Los tipos de métodos para estimar 3D.** Basados en modelo (pesados, fuera de
alcance), directos (MediaPipe, una sola pasada), de elevación (2D cuadro a cuadro → 3D
aprovechando la secuencia temporal). Los de elevación dependen de la calidad de la etapa
2D anterior, que trae temblor de cuadro a cuadro (lo que corrige la Etapa 2.1 del diseño).

**3.3.2.3. YOLOv8-Pose, COCO-Pose y ONNX.** Detección de una sola pasada, muy rápida.
**17 puntos, dos coordenadas más visibilidad (x, y, visibilidad). No hay tercera
dimensión. Es un modelo 2D.**

**3.3.2.4. La segunda etapa: pasar de 2D a 3D.** VideoPose3D (Pavllo et al., 2019): separa
el "ver" del "reconstruir" — la primera etapa se puede reemplazar sin tocar la segunda.
MotionBERT (Zhu et al., 2023): entrenado con esqueletos 2D dañados, tolera oclusión y
ruido. PoseFormerV2 (2023): reduce el temblor de la etapa 2D. MotionAGFormer (2024):
liviano y eficiente.

**3.3.2.5. MediaPipe: la alternativa de una sola etapa.** 33 puntos en 3D directo,
incluyendo cara, manos y pies. Entrenado sobre todo con yoga y gimnasia, distintas del
tenis. En Rode et al. (2025) fue el mejor de los modelos 3D directos: 146 mm de error,
17,2° en rodilla, 98,8 % de detección.

**3.3.2.6. ONNX.** Formato abierto, corre en hardware variado sin cambios; no ata al
programa de entrenamiento; permite comprimir el modelo.

**3.3.2.7. La estructura completa del sistema (seis etapas):**

| Etapa | Qué hace | Entra | Sale | Herramienta |
| --- | --- | --- | --- | --- |
| E0 — Ingesta | Abre el video y lee los FPS reales | MP4/MOV | Fotogramas + FPS | OpenCV |
| E1 — Detección 2D | Ubica el cuerpo en cada cuadro | Fotograma | 17 puntos (x, y, confianza) | YOLOv8-Pose (ONNX) / MediaPipe |
| E1b — Validación | Marca los puntos poco confiables | Puntos 2D | Puntos 2D + marca de confianza | Lógica propia |
| E2 — Elevación a 3D | Reconstruye la profundidad usando el tiempo | Ventana de cuadros 2D | Puntos en 3D | VideoPose3D / MotionAGFormer |
| E3 — Filtrado | Saca el temblor antes de calcular velocidades | Series 3D crudas | Series 3D limpias | Filtro Butterworth |
| E4 — Cálculo | Ángulos, velocidades, secuencia, alertas | Series 3D limpias | Resultados + alertas | Geometría + reglas |

**3.3.2.8. Cuánto error es razonable esperar (Rode et al., 2025, 11 modelos vs. Vicon de
27 cámaras):**

| Medida | En 2D | En 3D |
| --- | --- | --- |
| Error de posición de los puntos | 72–122 mm | 146–249 mm |
| Error en el ángulo de rodilla | 9,3°–21,9° | 14,1°–25,8° |
| Error en el ángulo de codo | 21,5°–28,9° | 16,3°–26,0° |
| Velocidad de procesamiento | 25–200 fps | 117–9.341 fps (elevación) |

**Cinco conclusiones:** (1) el error de profundidad es el más grande y no es defecto
corregible; (2) pasar a 3D empeora la rodilla y mejora el codo, porque el codo se mueve
fuera del plano de la cámara — justifica mantener 3D para hombro/codo; (3) 5° de error es
imposible; comparado contra la estimación "a ojo" de un humano (error promedio 20,6°,
Krosshaug et al., 2007), la mayoría de estos modelos ya le gana; (4) la cadera es lo más
confiable, muñecas y tobillos lo menos — la precisión debe medirse articulación por
articulación, no con un número único; (5) la elevación mejora incluso la parte 2D.

**3.3.2.9. Plan de repliegue.** Si la elevación resulta demasiado lenta, o el error de
profundidad no mejora las articulaciones de interés, el sistema puede volver a análisis 2D
con encuadre controlado, sin que la hipótesis del apartado 1.4 se caiga —esa hipótesis
habla de "precisión suficiente para detectar la desincronización", no de si es 2D o 3D.

### 3.3.3. Biomecánica Deportiva y la Cadena Cinética en el Tenis

**3.3.3.1. Definición.** La energía se transmite desde las partes más cercanas al suelo
hacia las más lejanas, en orden: suelo → piernas y caderas → tronco → brazo, muñeca,
raqueta. Kibler: piernas y tronco generan 51–55 % de la energía que llega a la mano.

**3.3.3.2. El orden de la cadena y la separación cadera-hombro.** Cada parte debe empezar
a acelerar justo cuando la anterior llega a su velocidad máxima — **esto es exactamente lo
que el sistema mide**, no un valor absoluto sino el orden. La separación cadera-hombro
(desfase entre giro de cadera y de tronco) es una de las medidas más confiables por
involucrar solo articulaciones proximales.

**3.3.3.3. La cuenta de la compensación.** Si el tronco aporta 20 % menos de energía, el
hombro debe girar 33–34 % más rápido para el mismo golpe. Esas fallas de secuencia
aparecen en el 50–67 % de los deportistas con lesión de hombro. **El déficit es invisible a
simple vista** (la pelota puede entrar igual) — esa invisibilidad es la razón de ser del
sistema. La poca flexión de rodilla implica 23–27 % más carga en hombro y codo, y
coincide con lo que la visión artificial mide mejor.

**3.3.3.4. De los puntos a los ángulos.** Ángulo entre tres puntos (producto escalar):
funciona bien para codo y rodilla (bisagra en un sentido). **No alcanza para el hombro**,
que gira en tres sentidos — con los 17 puntos de COCO (sin marcadores en la mano) la
rotación del hombro no se puede medir directamente. Razón adicional para considerar los 33
puntos de MediaPipe.

### 3.3.4. Relación de Variables: cómo se conectan la IA y la Biomecánica

**3.3.4.1. El recorrido del dato.** Escena real (pierde profundidad) → imagen (detección
2D suma temblor + desvío fijo) → puntos 2D (elevación suma error, sobre todo en
profundidad) → puntos 3D (los cálculos agrandan o cancelan el error) → resultados finales.

**3.3.4.2. Qué errores se agrandan y cuáles se cancelan — el aporte teórico central:**

| Cálculo biomecánico | Afecta desvío fijo | Afecta escala | Afecta temblor | Afecta FPS mal leído | Confiabilidad | ¿MVP? |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Ángulo respecto de la vertical | Mucho | Poco | Medio | No | Baja | No |
| 2. Ángulo entre tres puntos | Medio | No | Medio | No | Media-alta | Sí |
| 3. Cadera-hombro | Poco | No | Medio | No | Alta | Sí, prioridad |
| 4. Velocidad de un segmento | Poco | Mucho | Mucho | Mucho | Media (con filtro) | Sí |
| 5. Aceleración | Poco | Mucho | Muchísimo | Muchísimo | Baja | No |
| **6. Orden de los picos de velocidad** | **No** | **No** | **Medio** | **Mucho** | **Alta** | **Sí — el núcleo** |
| 7. Comparar contra umbral fijo | Mucho | Mucho | Medio | Medio | Baja | Condicionado |

**El cálculo 6 es el decisivo:** no le afecta el desvío fijo (aunque la cadera esté mal
ubicada por 30–50 mm de forma constante, eso corre la curva pero no cambia el momento del
pico) ni la escala (un error píxeles→metros agranda o achica la curva pero no mueve el
pico en el tiempo). Solo le afecta el temblor y un FPS mal leído — ambos ya resueltos por
el filtro Butterworth y la lectura real de FPS. **Esto es lo que el proyecto necesita
medir, y resulta ser inmune al peor error de la cámara.**

**3.3.4.3. El punto donde se unen las dos variables.** Martin et al. (2014): los
lesionados tenían el giro del tronco más tarde y más carga articular. Cadena de
razonamiento: video → puntos 2D (con error) → puntos 3D → filtrado → orden de la cadena
(inmune al error) → giro tardío del tronco (Martin) → más carga → riesgo modificable →
alerta.

**3.3.4.5. Umbral fijo o comparación con uno mismo.** Tres caminos: (a) umbral fijo
importado — simple pero de dudosa validez para amateurs; (b) **comparar al jugador contra
sí mismo** — si el error de cámara es constante para un mismo jugador y encuadre, se
cancela al comparar; opción más robusta; (c) comparar contra modelo ideal — premisa
discutible de que existe "una técnica correcta única". **Recomendación: (b) como base del
reporte clínico, (a) solo con respaldo bibliográfico, (c) para performance.**

---

## 3.4. Marco Conceptual

Tres límites duros que no se resuelven con más desarrollo: el 3.4.1 es un límite lógico
(qué se puede afirmar sin mentir), el 3.4.2 un límite físico (qué información se pierde si
no se captura en el momento), el 3.4.3 un límite legal (qué funciones no se pueden vender
sin registro).

### 3.4.1. Gobernanza Clínica y Gestión de Riesgos Físicos

**3.4.1.1. Gobernanza clínica (Scally y Donaldson, 1998).** La auditoría clínica —revisar
sistemáticamente la práctica contra un estándar— es la definición que mejor encaja con
este proyecto.

**3.4.1.2. "Bandera roja".** El término ya tiene significado médico establecido (señales
que hacen sospechar patología grave y obligan a derivar). **Se adopta "alerta de carga"
como etiqueta visible en la interfaz**, reservando "bandera roja" para documentación
interna.

**3.4.1.3. Por qué no se pueden predecir las lesiones.** Bahr (2016): para que un test de
predicción sea válido hacen falta tres pasos —estudio longitudinal grande, confirmación en
varios grupos, experimento controlado que demuestre beneficio de intervenir sobre "alto
riesgo" vs. todos. **El proyecto no cumple ninguno, ni podría en un trabajo de grado.**

**3.4.1.4. La cuenta que explica por qué fallan estos tests.** Con un test del 80 % de
acierto sobre 1000 jugadores: si la lesión es común (20 %), la mitad de las alarmas son
falsas; si es específica (5 %), 4 de cada 5 alarmas son falsas. **Tres consecuencias de
diseño:** (1) reportar el acierto sobre la prevalencia real, no sobre un conjunto
balanceado; (2) **hablar de "documentar", no de "predecir"** — el Objetivo Específico 5 se
reformula como "documentar de forma verificable los patrones que la literatura asocia con
más carga en las articulaciones"; (3) comparar al jugador consigo mismo esquiva el problema
de predicción y pasa a ser seguimiento.

**3.4.1.5. El marco legal: el software como producto médico.** IMDRF define Software como
Producto Médico (SaMD). En Argentina, ANMAT (Disposición 9688/2019) exige registro para
software autónomo que sea producto médico.

**Criterios para quedar afuera de la categoría (deben cumplirse los cuatro):**

| # | Criterio | ¿Lo cumple el sistema? |
| --- | --- | --- |
| 1 | No procesa señal de un aparato de medición | Depende de si el celular cuenta como tal |
| 2 | Muestra/analiza información médica del paciente | Se cumple en parte |
| 3 | Solo apoya la decisión, no la dirige ni diagnostica | Se cumple |
| 4 | No reemplaza el criterio profesional; permite revisar el fundamento | Se cumple — la transparencia deja de ser un lujo y pasa a ser requisito |

**Tabla de nivel de riesgo:**

| Situación de salud | Diagnosticar/tratar | Dirigir la atención | Informar la atención |
| --- | --- | --- | --- |
| Crítica | IV | III | II |
| Seria | III | II | I |
| No seria | II | I | I |

**Una lesión de tenis por desgaste no es situación crítica. Si el sistema informa (no
dirige, no diagnostica), queda en Clase I** —la de menor riesgo. La versión más honesta del
sistema es la que lo ubica en la categoría legal más baja.

**3.4.1.6. Dónde está la línea.** Lo que define si el sistema es producto médico no es la
tecnología, es **lo que se declara que hace** — incluso la publicidad cuenta como
declaración de finalidad.

**3.4.1.7. Transparencia y datos personales.** Cada reporte debe anotar con qué versión
del sistema se generó. El sistema maneja datos sensibles bajo la Ley 25.326. Procesar el
video en el dispositivo y subir solo los números simplifica el encuadre legal.

### 3.4.2. Procesamiento Digital de Señales (DSP) en Análisis de Movimiento

**3.4.2.1. La señal del movimiento y su ruido.** El movimiento real es de baja frecuencia,
el ruido de la cámara es de alta frecuencia — un filtro pasa-bajos conserva uno y elimina
el otro.

**3.4.2.2. El teorema del muestreo — el hallazgo más duro del capítulo.** Nyquist-Shannon:
para capturar un movimiento hay que filmarlo a más del doble de la velocidad de lo más
rápido que se quiere ver. **Si se filma más lento, la información rápida queda
irrecuperablemente mezclada con la lenta — ningún filtro posterior la separa.** Debe
resolverse en el momento de filmar.

**Velocidades del saque (Fleisig et al., 2003) y grados de giro entre cuadros según fps:**

| Parte del cuerpo (pico) | A 30 fps | A 60 fps | A 120 fps | A 240 fps |
| --- | --- | --- | --- | --- |
| Tronco (280°/s) | 9,3° | 4,7° | 2,3° | 1,2° |
| Pelvis (440°/s) | 14,7° | 7,3° | 3,7° | 1,8° |
| Torso (870°/s) | 29,0° | 14,5° | 7,3° | 3,6° |
| Codo (1510°/s) | 50,3° | 25,2° | 12,6° | 6,3° |
| Muñeca (1950°/s) | 65,0° | 32,5° | 16,3° | 8,1° |
| Hombro (≈2368°/s) | 78,9° | 39,5° | 19,7° | 9,9° |

**A 30 fps el hombro gira casi 80° entre cuadros: el sistema no lo mide mal, no lo ve.**
Los estudios de biomecánica del tenis nunca filman a 30 fps.

**Requisito adoptado: mínimo 120 fps para cualquier análisis de las partes rápidas del
gesto.** Videos más lentos solo sirven para la fase de preparación, marcados como "no
confiables" para la fase rápida.

**3.4.2.3. Por qué se elige el filtro Butterworth.** No deforma las frecuencias que deja
pasar. Cuarto orden, **fase cero es fundamental**: un filtro común corre la señal en el
tiempo de forma distinta según el contenido frecuencial de cada segmento, cambiando el
orden aparente de los picos —justo lo que se quiere detectar. Solución: aplicar el filtro
dos veces (adelante y atrás) para que los corrimientos se cancelen. En código: usar
`filtfilt`, nunca `lfilter`.

**3.4.2.4. Cómo se elige el punto de corte.** Análisis residual de Winter: se prueba el
filtro con distintos cortes, se mide cuánto se aleja del original, y se identifica el
punto donde el filtro pasa de sacar ruido a sacar movimiento real.

**3.4.2.5. Hasta dónde llega el filtro.** Se rompe en tres casos presentes en el tenis: el
impacto (ocupa todas las frecuencias, filtrarlo lo borra), errores gruesos de detección
(un dato disparatado se desparrama sobre los cuadros vecinos, el filtro no lo elimina), y
el movimiento demasiado rápido para la frecuencia de captura.

**3.4.2.6. En qué momento aplicar el filtro.** Filtrar de más los datos 2D antes de la
elevación sería contraproducente (algunos modelos de elevación fueron entrenados con señal
ruidosa a propósito). **Orden correcto:** detección 2D → sacar datos disparatados →
elevación a 3D → filtro → cálculos.

### 3.4.3. Viabilidad y Producto Mínimo Viable (MVP) en Health-Tech

**3.4.3.1. Qué es realmente un MVP.** No es "una versión recortada del producto", es una
herramienta para probar una idea con el mínimo esfuerzo. Dudas más grandes: ¿se puede
ordenar los picos con la velocidad de filmación disponible? ¿a alguien le sirve el
resultado?

**3.4.3.2. Criterios de éxito del MVP:**

| # | Qué se evalúa | Meta | Si no se cumple |
| --- | --- | --- | --- |
| 1 | ¿Se pueden ordenar los picos de velocidad en la fase rápida? | Pelvis, torso y brazo distinguibles y ordenables de forma repetible | Falla el núcleo → replegarse a la fase de preparación |
| 2 | Error en ángulos cercanos al centro | Menor que mirar a ojo (20,6°) | Replegarse a 2D con encuadre controlado |
| 3 | ¿Resultados parecidos al comparar al jugador consigo mismo? | El sistema varía menos que el propio jugador | La comparación con uno mismo no sirve |
| 4 | Tiempo de procesamiento | El que pida el entrenador y los encuestados | Reducir alcance o procesar más tarde |
| 5 | ¿Le sirve a los usuarios? | Uso concreto hoy no cubierto | Cambiar el producto, no la tecnología |

**3.4.3.6. Cierre.** Afirmación verificable que el sistema sostiene: un sistema de una sola
cámara puede establecer el orden de la cadena cinética con más confiabilidad que un ser
humano a simple vista, y documentarlo a un profesional de forma verificable.

---

## Nota de uso para el desarrollo

Los apartados con relevancia directa por etapa del plan:

- **Etapa 1 (Ingesta):** 3.3.1.1, 3.4.2.2 — lectura de FPS reales, mínimo 120 fps.
- **Etapa 2 (Pose):** 3.3.2.3 a 3.3.2.9 — por qué YOLOv8-Pose es 2D, comparación con
  MediaPipe, tabla de error esperable por articulación.
- **Etapa 3 (DSP):** 3.4.2.1 a 3.4.2.6 — Butterworth de fase cero, `filtfilt` vs
  `lfilter`, orden del pipeline.
- **Etapa 4 (Secuenciación):** 3.3.3, 3.3.4.1 a 3.3.4.5 — por qué el orden de picos es la
  magnitud más confiable; es el argumento a validar empíricamente en el punto de decisión.
- **Etapa 5 (Auditoría):** 3.4.1.2 a 3.4.1.4 — vocabulario permitido, formulación como
  "documentar" y no "predecir".
- **Interfaz (Etapa 8):** 3.2 — formato de salida preferido por los encuestados.
