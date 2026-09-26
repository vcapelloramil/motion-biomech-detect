# Registro de decisiones de arquitectura (ADR)

Cada decisión de arquitectura relevante se documenta acá, en su propio archivo numerado.
Alimenta directamente la redacción de los capítulos 6 (riesgos) y 7 (resultados) de la tesis.

## Convenciones

- Un archivo por decisión: `NNN-titulo-en-kebab-case.md`, numeración correlativa que no se
  reutiliza.
- Una decisión registrada no se borra ni se reescribe. Si más adelante se cambia de idea,
  se crea una decisión nueva que **supersede** a la anterior, y se marca la vieja como
  `Estado: reemplazada por 0NN`.
- Se registra la decisión cuando se toma, no al final de la etapa.

## Plantilla

```markdown
# Decisión NNN — Título

**Fecha:** DD de mes de AAAA
**Estado:** vigente | reemplazada por 0NN | descartada
**Afecta a:** etapas / documentos / capítulos

## El problema
Qué había que decidir y por qué no era obvio.

## Alternativas consideradas
Las opciones reales que estuvieron sobre la mesa, con su costo y su beneficio.

## Decisión
Qué se eligió.

## Consecuencias
Qué habilita, qué cierra, qué hay que recordar más adelante.
```

## Índice

| Nº | Título | Estado |
| --- | --- | --- |
| [001](001-admision-corpus.md) | Cómo se verifica un video antes de entrar al corpus | vigente |
| [002](002-config-ruta-corpus.md) | La ubicación del corpus se recibe por configuración | vigente |
| [003](003-estructura-monorepo.md) | Estructura del monorepo (apartado 4.3.5 de la tesis) | vigente |
| [004](004-ingesta-fps-y-verificacion.md) | Ingesta: dos verificaciones, factor externo y frecuencia efectiva | vigente |
| [005](005-percepcion-pose.md) | Percepción de pose: contrato intercambiable, MediaPipe por defecto | vigente |
| [006](006-velocidad-inferencia-vs-tesis.md) | La velocidad de inferencia real obliga a revisar 4.2.3 y 4.5.4 | vigente (pendiente de redacción) |
| [007](007-filtrado-de-senales.md) | Qué filtra el filtro (world landmarks) y el orden del pipeline | vigente |
| [008](008-cinematica-y-secuenciacion.md) | Cinemática y secuenciación (4.1–4.6) + hallazgos sobre corpus público | vigente (Etapa 4 abierta) |
| [009](009-inversion-de-profundidad.md) | Detector de inversión de profundidad (z) en la validación | vigente |
| [010](010-filtrado-por-segmentos.md) | E3 filtra por segmentos continuos (antes dejaba crudas las series con huecos) | vigente (motor 0.4.1; pendiente de redacción Cap. 4: justificación de hombro→codo) |
| [011](011-referencia-fleisig-del-brazo.md) | Los valores de Fleisig para el brazo no son comparables con ω del vector hombro→codo (error conceptual de referencia) | vigente (orden del brazo en perfil no concluyente; lectura por encuadre; pendiente de redacción Cap. 3 y 4, CLAUDE.md e interfaz) |
| [012](012-criterio-3-dos-sesiones-consecutivas.md) | Criterio 3: alcance con dos sesiones consecutivas (redefinición: consistencia, no sensibilidad a un cambio real) | vigente |
| [013](013-cobertura-del-brazo-dominante.md) | Cobertura del brazo dominante: limitación física conocida del material (cámara del lado no dominante; codo con 30–50 % en la ventana del saque y el drive) | vigente |
| [014](014-diseno-medicion-formal.md) | Diseño de la medición formal de los Criterios 1, 2 y 3 | **PROPUESTA** (a confirmar antes de medir) |
