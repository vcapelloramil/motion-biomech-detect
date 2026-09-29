# Decisión 011 — Los valores de Fleisig para el brazo no son comparables con ω del vector hombro→codo

**Fecha:** 25 de septiembre de 2026
**Estado:** vigente. **Corrección de un error conceptual de referencia, no de calibración.**
**Afecta a:** decisión 008 (techo de plausibilidad del brazo) · Capítulo 3 (apartado 3.3.2.8, tabla de velocidades de Fleisig) · Capítulo 4 · bitácora

---

## El problema

El techo de plausibilidad del segmento `brazo` se anclaba a **2368 °/s** ("Hombro", Fleisig et
al., 2003; `_FLEISIG_MAX` en `engine/sequencing.py`, ×3 = 7104 °/s), y varias lecturas de este
trabajo ("el brazo da 1,7–2,6× Fleisig", "el brazo parece subestimado, ~0,55× Fleisig") comparaban
la velocidad del brazo con ese valor.

**Ese valor no es comparable con lo que calcula el motor.** Valentín lo verificó con dos
fuentes independientes (que no fueron consultadas por Claude):

- Fleisig et al. (2003), *Kinematics used by world class tennis players to produce high-velocity
  serves* — PubMed 14658245.
- *Biomechanics of the Tennis Serve: Implications for Strength Training* — academia.edu/22890061.

La rotación interna del hombro (~2400–2500 °/s) es un giro del húmero **sobre su propio eje
longitudinal**.

## Qué mide realmente ω sobre el vector hombro→codo

`velocidad_angular_segmento` (`engine/kinematics.py`) calcula `ω[i] = ∠(u[i-1], u[i]) · fps`,
con `u` = la dirección del vector unitario hombro→codo. Es la velocidad con la que cambia la
**orientación del segmento en el espacio** (el "balanceo" del brazo). Consecuencias, fijadas por
`tests/unit/test_omega_vector_vs_angulo.py` con geometrías de resultado conocido:

| Movimiento | ω del vector hombro→codo | ángulo del codo (3 puntos) |
| --- | --- | --- |
| Balanceo del brazo (el codo gira alrededor del hombro) | **la velocidad real** | — |
| Extensión de codo (el antebrazo gira, el brazo queda) | **0** | la velocidad real |
| Rotación axial pura (giro alrededor del eje del brazo) | **0** | **0** |

Un vector no cambia de dirección aunque haya rotación pura sobre sí mismo, así que **es
estructuralmente incapaz de medir la rotación interna del hombro**. Tampoco mide la extensión de
codo: esa es un cambio del ángulo *relativo* entre brazo y antebrazo, que solo captura el ángulo
de tres puntos.

## Qué valor de Fleisig se corresponde con qué magnitud

| Magnitud (Fleisig 2003, tabla de 3.3.2.8) | Valor | Qué es físicamente | ¿La mide el motor? |
| --- | --- | --- | --- |
| Rotación interna del hombro ("Hombro") | 2368 °/s | giro axial del húmero | **No** (ni vector ni ángulo) |
| Extensión de codo ("Codo") | 1510 °/s | cambio del ángulo relativo brazo-antebrazo | Sí, con `serie_angulo_articular("codo")`; **no** con el vector hombro→codo |
| Flexión de muñeca ("Muñeca") | 1950 °/s | ángulo relativo antebrazo-mano | No (sin punto de mano fiable) |
| Rotación del torso superior / de la pelvis | 870 / 440 °/s | giro del tronco / pelvis en torno al eje vertical | Sí (vectores de hombros y caderas en el plano transversal); *verificar contra el artículo* |
| Orientación del **brazo** en el espacio (lo que mide ω del vector) | — | balanceo del brazo | **No hay valor de Fleisig equivalente en la tabla** |

## Medición con los saques de la Fase B (E3 0.4.1, ventana anclada al torso)

Datos: `docs/resultados/e3-fleisig-brazo-saque.json`, `python -m app.diagnosticos_e3 fleisig-brazo`.
Pico mediano en la ventana (°/s):

| | ω del vector hombro→codo | ángulo del codo (extensión) |
| --- | --- | --- |
| Saque de perfil (6) | 1315 = 0,56× de 2368; 0,87× de 1510 | 1327 = **0,88×** de 1510 |
| Saque de tres cuartos (6) | 1379 = 0,58× de 2368; 0,91× de 1510 | 755 = **0,50×** de 1510 |

- La aparente "subestimación" (~0,55×) **era comparar contra la magnitud equivocada**: no
  constituye evidencia de nada. Contra 1510 el vector daría 0,87–0,91×, pero **eso tampoco es una
  comparación equivalente** (el vector no mide extensión de codo): sería una coincidencia numérica.
- La única comparación equivalente disponible es la del ángulo del codo contra 1510: 0,88× en
  perfil y 0,50× en tres cuartos, **con baja cobertura** (25–57 % de los fotogramas tienen los
  tres puntos; la muñeca se pierde justo en el impacto) → cotas inferiores poco confiables.
- Los picos de k=1 y k=4 coinciden (vector 1315 vs 1295; ángulo 1327 vs 1293): no es ruido.
- Una repetición (saque de perfil rep03) da 19 283 °/s: un error de detección, que cualquier
  techo razonable (7104 o 4530) rechaza igual.

## Decisión

1. **Se retira toda afirmación del tipo "el brazo da N× Fleisig"** (decisión 008, bitácora): el
   valor de referencia no corresponde a la magnitud.
2. **El techo del brazo deja de estar "anclado a Fleisig-hombro".** Ninguna cifra de la tabla
   equivale a la orientación del brazo en el espacio. El valor numérico queda por ahora en
   7104 °/s **como cota provisional para rechazar errores de detección, sin respaldo en la
   literatura**; el comentario de `_FLEISIG_MAX` lo indica. Reanclarlo a 1510 °/s (×3 = 4530) tendría
   el mismo efecto práctico sobre la Fase B (ningún pico válido supera 3000 °/s) pero repetiría el
   error conceptual con otro valor (el vector tampoco mide extensión de codo): solo sería
   aceptable rotulado como cota de orden de magnitud, no como comparación equivalente. **Pendiente de
   decisión de Valentín.**
3. **Alcance de la afirmación (ver la sección siguiente):** el "brazo" de la cadena
   `pelvis → torso → brazo` es un proxy de la **orientación espacial del segmento superior**
   (el balanceo del brazo), no la rotación interna del hombro. Vale para todo el sistema, no solo
   para el techo.

## Alcance: "orden del balanceo del brazo" no es "orden del pico de rotación interna"

**Qué mide el sistema.** El orden temporal de tres picos de velocidad angular de *orientación de
un eje*: (1) el eje de las caderas (giro de la pelvis en el plano transversal), (2) el eje de los
hombros (giro del torso superior) y (3) el eje hombro→codo, es decir el **balanceo del brazo**
(cómo cambia la dirección del brazo en el espacio: flexión, abducción, aducción horizontal).

**Qué describe la literatura (Fleisig et al., 2003, y la cadena cinética del saque).** Una secuencia
proximal→distal de picos de velocidad angular de la pelvis, del torso superior y, en el brazo, de
la extensión de codo, la **rotación interna del hombro** y la flexión de muñeca. El evento del
"brazo" en esa literatura es un giro **axial** del húmero.

**Son dos eventos distintos del gesto.** El balanceo del brazo (cambio de dirección del eje) y la
rotación interna (giro sobre el propio eje) son movimientos diferentes, pueden alcanzar su
velocidad máxima en instantes distintos y **no hay dato de referencia que los relacione**. En el
drive y el revés, además, el balanceo tiene picos en la preparación (caída de la raqueta) que no
corresponden al golpe. Con nuestros datos solo puede decirse, por ejemplo, que en el saque de tres
cuartos el pico del balanceo llega después del pico del torso en 6 de 6 repeticiones (mediana
~110 ms con el codo filtrado a 8 Hz; `docs/resultados/e3-corte-brazo-fase-b.json`); eso **no** dice
dónde cae respecto del pico de rotación interna.

| Afirmación | ¿Se sostiene? |
| --- | --- |
| "El sistema documenta el orden temporal de los picos de velocidad de pelvis, torso y **balanceo del brazo**" | **Sí**: es exactamente lo que mide. |
| "El sistema documenta el orden pelvis → torso → brazo **descripto en la literatura**" | **No, tal cual.** Pelvis y torso miden un giro axial del tronco, comparable en lo esencial con la literatura *(a verificar contra el artículo)*; el tercer eslabón mide otro evento. |
| Etiquetar el orden como "correcto" (escalera) o "incorrecto" (cruce) cuando interviene el brazo | **Sin fundamento bibliográfico** para el eslabón del brazo. El orden pelvis vs torso sí puede fundarse; torso vs balanceo del brazo, no. |
| Criterio 1: el orden observado es **repetible** (meta 8 de cada 10) | **Se mantiene** como propiedad de la medición (repetibilidad de lo observado), con el enunciado corregido a "pelvis, torso y balanceo del brazo". |
| Criterio 3: comparar al jugador **consigo mismo** entre sesiones | **Se mantiene**: no necesita referencia externa, y el error constante del proxy se cancela al comparar con el mismo encuadre. |

**Consecuencia para las reglas del proyecto.** R4 exige que toda alerta cite una fuente. Ninguna
etiqueta de "orden incorrecto" que dependa del brazo puede citar a Fleisig. Hasta que se decida
otra cosa, el orden que incluye al brazo debería documentarse como "orden observado del balanceo
del brazo", sin juicio de correcto/incorrecto *(propuesta; pendiente de decisión de Valentín)*.

**Terminología propuesta.** "Balanceo del brazo" (u "orientación del brazo") para lo que mide el
sistema; reservar "rotación interna" para lo que describe la literatura. El campo
`segmento: "brazo"` del contrato congelado puede mantenerse siempre que su definición quede
documentada.

**Qué haría falta para comparar con la literatura** (fuera del alcance del MVP): capturar rotación
axial —goniometría 3D, sensores inerciales, o puntos de mano y antebrazo lo bastante fiables para
inferir la orientación del antebrazo—. Puede declararse como limitación en los Capítulos 6 y 7.

**Lugares donde aparece la afirmación y hay que revisar la redacción** (no se editó ninguno en esta
sesión, salvo el comentario de `_FLEISIG_MAX`):

- `CLAUDE.md`: §1 ("el ORDEN de los picos (pelvis → torso → brazo)") y §3 ("Correcto = escalera
  ordenada… Incorrecto = cruce").
- `docs/tesis/capitulo-4-marco-tecnologico.md`: hipótesis I1 (~línea 263), Criterio 1 (~324) y la
  descripción del gráfico de secuenciación (~776).
- `docs/tesis/capitulo-3-marco-teorico.md`: tabla del apartado 3.3.2.8 y el tratamiento de la
  cadena cinética.
- `docs/arquitectura.md`, `docs/plan-desarrollo.md` (tareas 4.4–4.5, Anexo A: `orden_esperado`),
  `docs/contrato-reporte.ejemplo.json`.
- Interfaz: `frontend/src/routes/index.tsx`, `routes/reporte.tsx`,
  `components/reporte/grafico-secuenciacion.tsx`, `lib/reporte-mock.ts` (sujetos a las reglas R2 y R3).
- Código: docstring de `engine/segmentos_corporales.py`, `app/analizar.py`, `app/explorar_fase_b.py`,
  `backend/README.md`.

## Decisión de alcance: el orden del brazo en perfil es NO CONCLUYENTE (25/9/2026)

Decisión de Valentín, apoyada en `docs/resultados/e3-corte-brazo-fase-b.json` y
`e3-ventana-brazo-fase-b.json` (motor 0.4.1, 36 repeticiones):

- **Drive de perfil:** el pico del brazo llega 50–100 ms antes que el del torso, y acotar la
  ventana del brazo lo deja no auditable (1/6): no hay un pico posterior identificable.
- **Revés de perfil:** casi simultáneo con el torso (−12 a −21 ms) salvo dos picos 200–300 ms antes
  (probablemente preparación); con adelanto 0 los cuatro auditables pasan a +165 ms.
- **Saque de perfil:** depende del corte del codo (≤ 8 Hz el brazo llega después; ≥ 10 Hz, antes
  en 2 de 3) y de la ventana.

En perfil el orden torso/brazo se declara **no concluyente**. En el vocabulario de la regla R3
corresponde al estado **"no auditable"** (gris): el sistema no pudo medir con confianza suficiente
*(propuesta de mapeo; no implementada)*. Las afirmaciones que dependen del brazo se apoyan en el
encuadre de **tres cuartos**.

## Lectura metodológica: qué sostiene cada encuadre (citable en el Capítulo 6 y en las conclusiones)

Ancla de torso, E3 0.4.1, 36 repeticiones (6 por gesto y encuadre), un jugador, una sesión.
1 fotograma = 4,17 ms.

| Vínculo | Perfil | Tres cuartos |
| --- | --- | --- |
| **torso → balanceo del brazo** | brazo después del torso en **5 de 16**; drive antes (4/5), revés ~simultáneo, saque depende del corte y la ventana → **no concluyente** | brazo después del torso en **17 de 18**; estable con el corte del codo entre 6 y 15 Hz (a 20 Hz un caso de revés cambia: 16 de 18) y con la ventana → **robusto** |
| **pelvis vs torso** | pelvis primero en 3 de 15, **torso primero en 11 de 15** (saque 3/3 y drive 6/6, medianas −12 y −17 ms) → sesgo sistemático **opuesto al orden esperado**; no concluyente | pelvis primero en 9 de 18, torso primero en 7 de 18; mediana ±4 ms; |Δ| ≤ 3 fotogramas en 16 de 18 → **simultáneo dentro de la resolución**; no concluyente |

**Lectura.** En este conjunto, el encuadre de tres cuartos es el que permite establecer de forma
robusta el vínculo **torso → balanceo del brazo**, y el de perfil no. **Ningún encuadre resuelve el
orden entre pelvis y torso**: perfil da un sesgo sistemático con el torso primero y tres cuartos,
simultaneidad dentro de 1–3 fotogramas. **La cadena completa `pelvis → torso → brazo` no queda
establecida por ninguno de los dos; lo que tres cuartos sostiene es su segunda mitad.**

> **Corrección de la formulación inicial.** Se propuso citar que "perfil solo sostiene
> pelvis→torso". Los datos no lo respaldan: en perfil el orden pelvis→torso sale invertido de forma
> sistemática (saque y drive, 9 de 9) y en tres cuartos queda en empate técnico. Lo que perfil sí
> aporta es la **magnitud** de pelvis y torso (sin diferencia entre 0.4.0 y 0.4.1) y su cercanía
> temporal.

*Hipótesis, no probada aquí:* en perfil los ejes de caderas y hombros apuntan hacia la cámara y la
rotación ocurre en profundidad (`z`, la coordenada más ruidosa de MediaPipe); tres cuartos pone parte
de la rotación en el plano de la imagen (ya anticipado en la decisión 008, sección "guían el encuadre
de la Fase B").

*Propuesta de redacción para la tesis:* "En este conjunto de 36 repeticiones de un jugador, el
encuadre de tres cuartos permitió establecer de forma robusta que el pico del balanceo del brazo
sigue al del torso (17 de 18 repeticiones), y el de perfil no (5 de 16). Ninguno de los dos encuadres
resolvió el orden entre pelvis y torso: el de perfil mostró un sesgo sistemático con el torso primero
(11 de 15) y el de tres cuartos, simultaneidad dentro de 1–3 fotogramas (16 de 18 repeticiones)."
Debe acompañarse de las limitaciones: un jugador, una sesión, seis repeticiones por grupo, y que el
"brazo" es un proxy de orientación (sección anterior).

**Consecuencias.** (1) Recomendar tres cuartos en el protocolo para todo análisis que involucre al
brazo; perfil sirve para las magnitudes de pelvis y torso. (2) El Criterio 1 (repetibilidad del orden)
no se midió formalmente; la lectura exploratoria muestra que solo el saque de tres cuartos repite un
mismo orden completo en 5 de 6. (3) Vale para este jugador y esta sesión: la segunda sesión (Criterio 3)
puede confirmarlo o no.

## Trabajo futuro (NO implementado)

**Marcador de fase independiente** para separar el golpe de la preparación, por ejemplo el punto más
bajo de la muñeca como inicio del golpe hacia adelante, validado con fotogramas. Depende de la
cobertura de la muñeca (25–57 % de los fotogramas con los tres puntos en el saque), que es baja justo
en el impacto. Alternativa para el evento de rotación interna: goniometría 3D o sensores inerciales.

## PENDIENTE DE REDACCIÓN — Capítulo 3, apartado 3.3.2.8

Antes de la entrega hay que agregar una aclaración a la tabla de velocidades de Fleisig: el valor
de "Hombro (≈ 2368 °/s)" es rotación interna, un giro axial, y **no es comparable con un cálculo de
ángulo entre tres puntos ni con la orientación de un vector**; solo con mediciones que capturen
rotación axial (goniometría 3D completa, sensores inerciales). Los valores de "Codo" y "Muñeca" son
ángulos relativos entre segmentos, comparables con ángulos de tres puntos, no con la orientación de
un segmento aislado. El argumento de muestreo de esa tabla (los grados entre cuadros) sigue siendo
válido. No se editó el texto de la tesis en esta sesión.

## Consecuencias

- Todo "× Fleisig" del brazo en la bitácora y en la decisión 008 queda **sin valor**.
- Los umbrales del brazo no se recalibran por esto; el `MARGEN_PLAUSIBILIDAD` sigue como está.
- Si se quiere una comparación equivalente para la extensión de codo, hay que mejorar la cobertura de
  la muñeca (hoy 25–57 %) o medirla en fotogramas donde se vea.
