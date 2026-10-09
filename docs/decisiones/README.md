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
| [008](008-cinematica-y-secuenciacion.md) | Cinemática y secuenciación (4.1–4.6) + hallazgos sobre corpus público | vigente (Etapa 4 cerrada, ver decisión 015) |
| [009](009-inversion-de-profundidad.md) | Detector de inversión de profundidad (z) en la validación | vigente |
| [010](010-filtrado-por-segmentos.md) | E3 filtra por segmentos continuos (antes dejaba crudas las series con huecos) | vigente (motor 0.4.1; pendiente de redacción Cap. 4: justificación de hombro→codo) |
| [011](011-referencia-fleisig-del-brazo.md) | Los valores de Fleisig para el brazo no son comparables con ω del vector hombro→codo (error conceptual de referencia) | vigente (orden del brazo en perfil no concluyente; lectura por encuadre; pendiente de redacción Cap. 3 y 4, CLAUDE.md e interfaz) |
| [012](012-criterio-3-dos-sesiones-consecutivas.md) | Criterio 3: alcance con dos sesiones consecutivas (redefinición: consistencia, no sensibilidad a un cambio real) | vigente |
| [013](013-cobertura-del-brazo-dominante.md) | Cobertura del brazo dominante: limitación física conocida del material (cámara del lado no dominante; codo con 30–50 % en la ventana del saque y el drive) | vigente |
| [014](014-diseno-medicion-formal.md) | Diseño de la medición formal de los Criterios 1, 2 y 3 | vigente (congelada; los tres criterios medidos) |
| [015](015-cierre-etapa-4.md) | Cierre de la Etapa 4: sin repliegue, cinco salvedades documentadas | vigente |
| [016](016-limite-subida-un-golpe.md) | Límite de subida del MVP: un video por golpe, hasta 50 MB | **TENTATIVA** (se confirma probando el flujo completo) |
| [017](017-plan-contenedor-motor.md) | Plan de contenedor para el motor: Render Starter (USD 7/mes) alcanza, medido con Docker real | vigente (hallazgo de `model_complexity` pendiente de decisión) |
| [018](018-esquema-datos-etapa-4.5.md) | Esquema de datos de la Etapa 4.5: sesión como grupo de golpes | vigente |
| [019](019-semilla-api-despliegue-render.md) | Semilla de la API (FastAPI) para desplegar y medir el plan gratuito de Render | vigente |
| [020](020-bug-fps-efectivos-procesar-video.md) | Bug real de fps, corregido con una declaración de modo de captura del usuario | vigente (implementada y aplicada; control contra historial diferido) |
| [021](021-keepalive-supabase-funcion-anon.md) | Keep-alive de Supabase: función `keepalive()` ejecutable por `anon` (excepción acotada a "nada a anon") | vigente |
| [022](022-reintento-fallido-y-columnas-protegidas.md) | Reintento `fallido → encolado` y permisos por columna sobre `videos` y `sesiones` | vigente (en implementación; ver "Avance") |
| [023](023-instancia-render-pruebas-con-usuarios.md) | Instancia de Render: Free primero, Standard (1 CPU, 2 GB) cuando la espera o los cortes molesten y siempre para la defensa; Starter descartado | vigente (actualizada el 7/10; el cambio lo hace Valentín) |
| [024](024-contrato-del-reporte-v1.md) | Contrato del reporte v1.0: el único cambio antes de generar JSON reales | vigente (implementado) |
| [025](025-carga-directa-estado-directo-y-autenticacion-api.md) | Carga directa a Storage, estado por lectura directa y autenticación de la API con JWKS (desvío de §4.2.3 y §4.2.5) | vigente (Capítulo 4 por corregir) |
| [026](026-hosting-cloudflare-y-frontend-en-el-repo.md) | El frontend se publica en Cloudflare y el repositorio es la única fuente del código | vigente (Capítulo 4 por corregir) |
| [027](027-correo-de-confirmacion-smtp.md) | Correo de confirmación de registro: SMTP propio | vigente (A en curso con el Student Pack; B de respaldo) |
| [028](028-llegada-del-golpe-a-240fps-casos-a-b-c.md) | Cómo llega un golpe grabado a 240 fps (casos a, b y c) y qué hace E0 con ellos | vigente; la prueba del iPhone mostró que el camino por defecto de Fotos llega a 100 fps; **el formato "Actual" sí conserva la captura** (ver 029) |
| [030](030-el-corpus-horneado-es-120-fps-con-rampas.md) | El corpus horneado no es de 240 fps: es un remuestreo a ~120 fps con rampas de velocidad (corrige la magnitud de la 029) | vigente en lo medido; recálculo a aprobar |
| [029](029-tasa-real-de-captura-varia-y-se-lee-del-archivo.md) | La tasa real de captura no es la nominal y varía por video: el motor la lee del archivo (RNF-01) | vigente en lo medido; propuesta de producto a aprobar; sin recalcular el corpus; **actualizada el 9/10: tolerancia del 5 % sobre los pisos de R1 (114 y 57 fps)** |
| [031](031-veredicto-del-orden-por-gesto-y-encuadre.md) | El veredicto del orden cadera → tronco solo existe con referencia y Criterio 1 cumplido; el resto se documenta "sin evaluar" (contrato v1.2) | vigente; se revisa con el recálculo (Paso A) |
