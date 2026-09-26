# Decisión 012 — Criterio 3: alcance con dos sesiones consecutivas (redefinición)

**Fecha:** 26 de septiembre de 2026
**Estado:** vigente (redefinición de Valentín)
**Afecta a:** Criterio 3 (tesis, Capítulo 4, tabla de criterios) · plan de desarrollo (0.5, Fase B) ·
`CLAUDE.md` §3 · Capítulos 6 y 7 · decisión 014 (diseño de la medición formal)

---

## El problema

**Criterio 3 original** (Capítulo 4): *Repetibilidad de la comparación consigo mismo*. Meta:
"variabilidad del sistema menor que la variabilidad intra-sujeto". Método: "sesiones repetidas;
análisis de dispersión". Si no se cumple: "descartar la comparación consigo mismo como base clínica".

**Plan de la Fase B** (Etapa 0, tarea 0.5): dos sesiones separadas por al menos una semana, con el
mismo encuadre.

**Lo que hay:** las sesiones 1 y 2 son de fechas consecutivas (24 y 25 de septiembre de 2026), con
48 repeticiones propias cada una, un solo jugador y **ningún evento entre medio** (entrenamiento,
fatiga, ajuste consciente de técnica) que pudiera producir una diferencia real.

## Decisión (Valentín, 26/9/2026)

1. **No se espera una semana más.** El problema no es la cantidad de días: es que no hubo ningún
   evento intermedio capaz de producir un cambio real, y una semana sin eso tampoco lo resolvería.
   Se usan las sesiones 1 y 2 tal como están.
2. **Criterio 3 redefinido:** *mide la repetibilidad del método aplicado por el mismo jugador en dos
   sesiones distintas, con la variación natural entre ellas (día, vestimenta, estado del cuerpo), y
   sin ninguna intervención deliberada de por medio.*

## Qué demuestra y qué NO demuestra

- **Demuestra** la **consistencia** del sistema entre tomas del mismo jugador en sesiones distintas.
- **No permite afirmar que el sistema detectaría un cambio real de técnica.** Esa pregunta queda
  **fuera de alcance con este diseño**, sin importar cuántos días separen las sesiones, salvo que en
  el medio ocurriera algo que produjera ese cambio.

## Consecuencias que conviene tener presentes

- **El Criterio 3 redefinido no restablece al original.** La condición de fracaso del original
  ("descartar la comparación consigo mismo como base clínica") depende de la *sensibilidad* a un
  cambio real, que este diseño no puede evaluar. Cumplir el criterio redefinido no valida la
  afirmación de `CLAUDE.md` §3 ("comparar al jugador consigo mismo es la base del reporte clínico"):
  esa afirmación queda **sin validación de sensibilidad** y se sostiene solo como diseño, con la
  consistencia entre tomas como evidencia parcial. *Propuesta de redacción para la tesis:* nombrar
  el resultado "consistencia entre sesiones" y no "repetibilidad de la comparación consigo mismo", y
  declarar la limitación en los Capítulos 6 y 7.
- **El espaciado se aparta del plan** (una semana). Queda registrado como desvío deliberado, con la
  razón dada arriba.

## Límites propios de este material (a declarar junto con el criterio)

- **El encuadre no es idéntico entre sesiones.** El argumento del plan ("el error constante de la
  cámara se cancela al comparar mediciones del mismo jugador con el mismo encuadre") no está
  garantizado: la visibilidad en reposo del brazo dominante en el saque y el drive de tres cuartos
  cambió mucho entre sesiones (confianza del codo 0,03–0,27 en la sesión 1 y 0,59–0,92 en la 2,
  `docs/resultados/pose-oclusion-lado-dominante.json`), y el saque de tres cuartos de la sesión 2
  tiene **tres tomas** (`02`, `02b`, `02c`). Antes de interpretar una diferencia entre sesiones hay que
  documentar la equivalencia de encuadre (tamaño del jugador en cuadro, posición, ángulo estimado).
- **Un solo jugador y sesiones consecutivas.** La variación natural entre dos días seguidos puede ser
  menor que entre sesiones más espaciadas; el criterio no lo distingue.

## Operacionalización

Qué métricas se comparan y con qué regla se decide "consistente" se fija en la decisión 014 (diseño de
la medición formal), **antes** de mirar los datos de la sesión 2.
