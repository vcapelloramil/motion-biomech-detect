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
3. **Alcance:** el "brazo" de la cadena `pelvis → torso → brazo` es un proxy —la orientación del
   brazo—, no la rotación interna del hombro. Con este vector no se puede contrastar el momento del
   pico de rotación interna que describe la literatura.

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
