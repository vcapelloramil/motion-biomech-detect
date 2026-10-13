# El pico del brazo, golpe por golpe (13/10/2026)

**Pregunta de Valentín (hallazgo c):** en la sesión del corpus subida a producción, "no se pudo medir el pico del brazo" en todos los golpes. ¿Es oclusión real en tres cuartos o la regla de cobertura
(2c, motor 0.5.1) es demasiado estricta? ¿Cuántos golpes del corpus pierden el brazo con el motor actual y con el anterior?

**Cómo se midió:** las poses del Paso B (originales a tasa real, regularizados a 240 Hz; `backend/.cache/corpus-real-pose-b`, 76 repeticiones válidas), medidas dos veces con la misma ventana anclada al
tronco: con la regla actual (se exige que se haya medido el **75 %** de la ventana, motor ≥ 0.5.1) y sin esa exigencia (motor 0.5.0). Datos: `brazo-por-golpe-13-10.json`. El diagnóstico de la
visibilidad del codo: `codo-ventana-saque-trescuartos.json` (18 repeticiones del saque en tres cuartos).

## Resultado

| Grupo | Repeticiones | Sin pico del brazo, motor actual (≥ 0.5.1) | Sin pico del brazo, motor anterior (0.5.0) |
| --- | --- | --- | --- |
| **Todo el corpus** | 76 | **52 (68 %)** | **7 (9 %)** |
| Saque · tres cuartos | 18 | **18** | 2 |
| Saque · perfil | 11 | 9 | 1 |
| Drive · perfil | 12 | 12 | 2 |
| Drive · tres cuartos | 12 | 12 | 1 |
| Revés · perfil | 11 | 1 | 1 |
| Revés · tres cuartos | 12 | 0 | 0 |

**La sesión del 24/9 (saque en tres cuartos, las 6 repeticiones):** con el motor actual **las 6** pierden el brazo (se midió entre el **38 y el 50 %** de la ventana, mínimo exigido 75 %); con el anterior,
las 6 lo tenían. En todo el saque en tres cuartos (24/9 y 25/9, 18 repeticiones) lo tienen **16 de 18** con el anterior (las otras 2, por una serie demasiado corta o sin picos) y **0 de 18** con el actual.

## Por qué: es oclusión real, no una regla demasiado estricta

En las 18 repeticiones del saque en tres cuartos, en la ventana de ±0,3 s alrededor del pico del tronco (145 fotogramas):

| Medida (mediana de las 18) | Valor |
| --- | --- |
| Confianza del hombro dominante ≥ 0,5 | **100 %** de la ventana |
| Confianza del **codo** dominante ≥ 0,5 | **41 %** de la ventana |
| … en la **primera mitad** (los 0,3 s antes del pico del tronco: el armado del golpe) | **0 %** (confianza cruda 0,0–0,27; mediana 0,06) |
| … en la **segunda mitad** (del pico del tronco en adelante) | **82 %** (confianza 0,91) |
| Muñeca dominante ≥ 0,5 | 57 % |

- El estimador (MediaPipe) **reporta el codo como no visible** durante todo el armado del golpe: su "visibilidad" cruda es casi 0 y no es un efecto del filtro ni de nuestra regla. Con la cámara en
  tres cuartos, el brazo que saca queda detrás del cuerpo y de la cabeza en esa fase.
- **No es un caso de borde:** en las 52 repeticiones que pierden el brazo, la cobertura medida va del 6 al 59 % y **ninguna** queda entre el 60 y el 75 %. Bajar el piso (a 60 %, por ejemplo) no
  recuperaría ni un golpe; solo con un piso < 40 % se "recuperaría", y sería el máximo de la mitad de la ventana.
- La regla 2c hace lo que se diseñó (12/10): sin ella el "pico del brazo" es el máximo de la **segunda mitad** de la ventana, es decir de la fase que sigue al pico del tronco, sin saber qué pasó antes.
  Por eso el motor anterior "encontraba" el pico en 69 de 76 repeticiones: era un máximo parcial presentado como si fuera el de todo el movimiento (R3).

## Qué cambia en el producto (decisión 037)

- El pico que falta **ya no desaparece**: "Tres momentos" muestra la tarjeta **"Pico del brazo: no medido"** con el motivo en palabras simples ("el sistema no pudo seguir el brazo que golpea con confianza
  durante el 43 % del golpe… suele pasar cuando el cuerpo tapa el brazo desde donde estaba la cámara") y la observación del brazo lo trae como fundamento.
- El golpe sigue **medido** si cadera y tronco tienen pico (el brazo no decide el estado).

## Decisión que queda para Valentín

1. **Dejarlo como está** (recomendado): en saque y drive con esta cámara el brazo no se mide, y se dice por qué. Es un resultado del instrumento para el Capítulo 7.
2. **Mostrar el máximo de la parte visible como dato parcial**, con la rotulación "máximo de la parte del golpe en que el brazo se veía (desde el pico del tronco en adelante)", en el detalle técnico y
   nunca en "Tres momentos" ni en el orden. Costo: ~0,5 sesión. Riesgo: un dato que parece el pico del brazo y no lo es; por eso no lo hice sin tu OK.
3. **Cambiar el encuadre de grabación del saque** (cámara del lado contrario al brazo que saca, o más a la altura del hombro) para que el codo se vea en el armado: es un cambio de protocolo, no de código,
   y no sirve para el corpus ya grabado.
