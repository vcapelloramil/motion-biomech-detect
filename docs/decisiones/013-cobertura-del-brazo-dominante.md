# Decisión 013 — Cobertura del brazo dominante: limitación física conocida del material

**Fecha:** 26 de septiembre de 2026
**Estado:** vigente (Valentín: documentar la cobertura "tal como está", como limitación física conocida)
**Afecta a:** decisión 011 (orden del brazo) · Criterio 1 (cadena completa) · decisión 014 · Capítulos 6 y 7
· protocolo de grabación

---

## Contexto

En las dos sesiones de la Fase B la cámara quedó del **lado izquierdo** del jugador (no dominante) y el
jugador es diestro: el brazo que golpea es el **lejano**. Con la `z` relativa de los hombros, el lado
izquierdo es el más cercano en **74 de 84** clips de perfil y tres cuartos (saque 36/36, drive 24/24,
revés 14/24); los 10 clips restantes son todos revés, donde el giro del cuerpo expone el brazo derecho.

Herramienta: `python -m app.diagnosticos_e3 oclusion-lado`
(`docs/resultados/pose-oclusion-lado-dominante.json`). **Cobertura** = fracción de fotogramas con
confianza (`visibility`) ≥ 0,5, la definición del motor. Se mide en tres tramos: **reposo** (a más de
0,6 s del pico del torso, sin desenfoque posible), **ventana del gesto** (± 0,3 s) y clip completo.

## Qué se midió (lado dominante; mediana por grupo)

Cobertura del **codo** y de la **muñeca** dominantes:

| Sesión | Encuadre | Gesto | n | Codo: reposo | Codo: ventana | Muñeca: reposo | Muñeca: ventana |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | perfil | saque | 6 | 0,05 | **0,53** | 0,12 | 0,82 |
| 1 | perfil | drive | 6 | 0,04 | **0,03** | 0,09 | 0,47 |
| 1 | perfil | revés | 6 | 0,01 | 0,98 | 0,50 | 1,00 |
| 1 | tres cuartos | saque | 6 | 0,04 | **0,46** | 0,11 | 0,84 |
| 1 | tres cuartos | drive | 6 | 0,14 | **0,31** | 0,84 | 0,65 |
| 1 | tres cuartos | revés | 6 | 0,95 | 0,99 | 1,00 | 1,00 |
| 2 | perfil | saque | 6 | 0,08 | **0,38** | 0,15 | 0,91 |
| 2 | perfil | drive | 6 | 0,00 | **0,19** | 0,44 | 0,46 |
| 2 | perfil | revés | 6 | 0,02 | 0,87 | 0,75 | 1,00 |
| 2 | tres cuartos | saque | 18 | 0,79 | **0,30** | 0,96 | 0,44 |
| 2 | tres cuartos | drive | 6 | 0,84 | **0,46** | 0,99 | 0,48 |
| 2 | tres cuartos | revés | 6 | 1,00 | 0,98 | 1,00 | 0,99 |

Lado no dominante: 0,94–1,00 en todos los tramos y grupos. **Hombro y cadera: 1,00 en ambos lados, siempre**
(ojo: `visibility` satura en 1,0 para estos puntos; no prueba que estén bien ubicados).

## Lo que muestran los datos

1. **En perfil, oclusión geométrica del brazo dominante, en ambas sesiones.** En reposo el codo dominante
   tiene cobertura 0,00–0,08 (confianza 0,10–0,12) contra 1,00 del izquierdo, en el 100 % de los clips.
2. **La pérdida durante el golpe depende del gesto.** En el **saque** y el **drive** el codo dominante se
   pierde en la ventana (cobertura 0,03–0,53, es decir entre la mitad y casi todo el gesto), mientras que
   en el **revés** se ve bien (0,87–0,99) en ambos encuadres.
3. **No se explica solo por la posición de la cámara.** En la sesión 2 de tres cuartos el encuadre cambió y
   el codo se ve bien en reposo (saque 0,79; drive 0,84), pero **en la ventana del gesto vuelve a caer**
   (0,30 y 0,46); la muñeca también (0,96 → 0,44 y 0,99 → 0,48).

## Interpretación y lo que NO se afirma

La lectura de Valentín es que el límite es el **desenfoque durante el golpe**. Los datos son
**compatibles** con eso, pero **también con autooclusión** (el torso o la raqueta tapan el brazo al
rotar) y **no las separan**. **No se probó** grabar del lado dominante: se decidió no hacerlo, así que
"la cámara del lado dominante mejora la cobertura del golpe" queda **sin probar, no refutada**. El único
caso de "brazo que golpea de cara a la cámara" es el revés (cobertura ≈ 1,0), un gesto más lento que el
saque.

## Decisión

No se graba del lado derecho ni se hace un piloto. La cobertura del brazo dominante **se documenta tal
como está, como limitación conocida** de este material (una cámara, un lado, un jugador diestro).

## Consecuencias

- **Las mediciones del brazo en saque y drive descansan en una fracción del gesto** (codo: 30–50 % de los
  fotogramas de la ventana en el saque; 3–46 % en el drive), y falta justo alrededor del impacto, donde el
  brazo va más rápido. Muchos picos del brazo no serán auditables o se buscarán solo en lo visible.
- **El revés es el gesto con la cobertura del brazo más completa** (≥ 0,87), en ambos encuadres.
  Cobertura y orden son cosas distintas: en el revés de perfil el orden del brazo sigue siendo
  no concluyente (decisión 011).
- **Criterio 1 (cadena completa):** las repeticiones sin brazo auditable cuentan como no válidas y se
  informan (decisión 014: el denominador son todas las repeticiones).
- **No hay comparación equivalente para la extensión de codo** (decisión 011): la cobertura de la muñeca en
  el impacto sigue siendo baja.
- **Capítulos 6 y 7:** declarar como limitación: una sola cámara del lado no dominante, brazo dominante con
  cobertura de 30–50 % en el saque y el drive, causa (desenfoque o autooclusión) no separada.
- **Protocolo de grabación:** registrar en la ficha de cada toma el lado de la cámara respecto del lado
  dominante. No estaba anotado y hoy solo se infiere de la `z` relativa de los hombros.
