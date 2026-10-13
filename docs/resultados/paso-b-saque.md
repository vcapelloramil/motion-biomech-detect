# Paso B — el saque con los originales a tasa real, y la "contradicción" del golpe del celular (13/10/2026)

**Qué es:** el saque (perfil y tres cuartos, dos sesiones) medido sobre los **originales** del iPhone (~200 fps reales, marcas de tiempo reales), regularizados a la grilla de 240 Hz con los puntos interpolados contados,
con la **misma constante de "ordenable"** que el producto (1/120 s = 8,33 ms, estricta; decisión 032). Arnés: `backend/app/medicion_paso_b.py`; commit `33dd7d9`, árbol limpio, motor 0.5.1. Resultados:
`paso-b-sesion-1.json` y `paso-b-sesion-2.json`. **Falta** drive y revés (siguen en la cola, ~2 h 10 min). Excluidas: las dos repeticiones que empiezan en la rampa y las 6 de `IMG_6391` (original incompleto).

## 1. Resultado del saque (29 repeticiones medidas, 28 válidas)

Δ = t_tronco − t_cadera; negativo = el tronco llegó primero. "Dentro" = |Δ| ≤ 8,33 ms (no ordenable).

| Grupo | Repeticiones válidas | Cadera primero | Tronco primero | Dentro de la tolerancia | Mediana de Δ |
| --- | --- | --- | --- | --- | --- |
| **Saque · perfil** (sesión 1 + 2) | 10 | **0** | **8** | 2 | −18,7 ms (s1) · −162,5 ms (s2) |
| **Saque · tres cuartos** (sesión 1 + 2) | 18 | **7** | **0** | 11 | +4,2 ms (s1) · +10,4 ms (s2) |

Criterio 1 con los originales (par cadera-tronco, tolerancia primaria):

| Grupo · sesión | 1a (ordenables / todas) | 1b (mismo orden entre las ordenables) | Orden modal | ¿Cumple? |
| --- | --- | --- | --- | --- |
| Perfil · sesión 2 (medición) | 5 / 6 = 0,83 | 1,00 | tronco primero | **sí** |
| Perfil · sesión 1 (réplica) | 3 / 5 = 0,60 | 1,00 | tronco primero | no |
| Tres cuartos · sesión 2 | 6 / 12 = 0,50 | 1,00 | cadera primero | no |
| Tres cuartos · sesión 1 | 1 / 6 = 0,17 | 1,00 | cadera primero | no |

**Lectura.**
- **El "tronco primero" del perfil se reproduce con los originales** (8 de 8 ordenables, ninguna con la cadera primero): **no viene del corpus convertido**; el Paso A y el B coinciden.
- **En tres cuartos ocurre lo contrario y con la misma consistencia:** 7 de 7 ordenables con la cadera primero. Pero **11 de 18 quedan dentro de la tolerancia** (el instrumento no puede ordenarlas), por eso 1a es bajo.
- **El orden depende del encuadre:** 0 de 8 contra 7 de 7 (prueba exacta de Fisher, p = 0,0002; **exploratoria**: un jugador, repeticiones de una misma toma no independientes).
- **Qué NO se puede decir:** cuál de los dos encuadres mide bien. Si se eligiera el que coincide con lo esperado (tres cuartos) sería elegir por el resultado. Hace falta una medición independiente de la pelvis
  (cintas de color en el mismo video: `docs/protocolo-saques-tres-cuartos.md`).

## 2. La "contradicción" del golpe del celular

**Lo observado:** el golpe subido a producción como "saque de perfil" (reporte `cbaf328d`, motor 0.5.0) dio la cadera 13 ms antes que el tronco ("correcto"), contra el tronco primero del perfil del Paso B.

**Causas propuestas y cómo se comprobaron sin grabar de nuevo:**

| # | Causa posible | Cómo se comprobó | Resultado |
| --- | --- | --- | --- |
| 1 | **El encuadre declarado no es el del video** | Metadatos del archivo (`com.apple.quicktime.creationdate`) y giro de la línea de hombros en la preparación (mundo 3D, mediana de 0,8 a 0,3 s antes del pico del tronco) comparado con el corpus | **Es la causa.** El archivo se grabó el **25/9/2026 15:23:05**: es exactamente la hora de **`IMG_6391`, el saque de TRES CUARTOS (toma 02)**; el giro de hombros del golpe es **59°**, dentro del de tres cuartos del corpus (**50–83°, mediana 56°**) y fuera del de perfil (**26–42°, mediana 35°**) |
| 2 | La versión del motor (0.5.0 en producción, 0.5.1 después) | Reprocesar el mismo video con el camino del Paso B | **Descartada**: reproduce Δ = **+12,5 ms** (cadera 1,658 s, tronco 1,671 s) |
| 3 | La ventana o el pico elegido | Cortes fijos de 4, 6, 8, 10 y 12 Hz y giro axial sobre el mismo video | **Descartada**: Δ de +16,7, +12,5, +4,2, +4,2, +4,2 ms y +16,7 ms con el giro axial; nunca tronco primero |
| 4 | Día o montaje distinto | Fecha de captura del archivo | **Descartada**: es de la misma sesión (25/9) que el corpus |
| 5 | El azar de una repetición (n pequeño) | Cuenta | **Compatible pero innecesaria**: con 0 de 8 en perfil un golpe en contra no sería imposible (cota superior exacta del 95 %: ~37 %), pero la causa 1 ya lo explica |
| 6 | Criterio de selección de repeticiones del corpus | Revisión de qué entra | **No aplica**: `IMG_6391` quedó afuera del Paso B por incompleto, así que ese golpe **no estaba** en la medición |

**Consecuencias:**
- **No hay contradicción: el golpe del celular es un saque de tres cuartos y se comporta como el resto del grupo** (cadera primero o dentro de la tolerancia).
- **Pero deja un problema de producto real:** el sistema **aplicó el veredicto del grupo `saque|perfil`** ("correcto") a un video de tres cuartos porque el encuadre es lo que declara el usuario. Con el giro de
  hombros **hay una forma barata de comprobar el encuadre declarado** (en el corpus los dos grupos no se solapan: 42° contra 50°). Es una propuesta (decisión 035, parte D), no está implementada.
- **La apertura de hombros / largo del tronco** (primera idea) **no sirve**: medianas de 0,23 (perfil) y 0,15 (tres cuartos), con el golpe nuevo en 0,11.

## 3. Limitaciones

- Un jugador, dos sesiones, 28 repeticiones válidas; las de una misma toma no son independientes.
- El umbral entre encuadres (≈ 46°) sale de 22 repeticiones del propio corpus: sirve para **detectar una discrepancia gruesa**, no para medir el ángulo de la cámara.
- Corpus a 200 fps reales: en tres cuartos más de la mitad de las repeticiones queda al límite de la resolución (5 ms por fotograma) y no se ordena.
- Falta drive y revés; no hay medición independiente de la pelvis.
