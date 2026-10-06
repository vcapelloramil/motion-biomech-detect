# Decisión 022 — Reintento `fallido → encolado` y permisos por columna sobre `videos` y `sesiones`

**Fecha:** 6 de octubre de 2026
**Estado:** vigente — diseño aprobado por Valentín el 6/10; en implementación (ver "Avance" al final)
**Afecta a:** `supabase/migrations/20261006130000_columnas_protegidas_videos_sesiones.sql` y una migración de
reintento (paso b) · `backend/app/routers/analisis.py` · `backend/app/procesar_video.py` ·
`docs/ux/especificacion-frontend.md` §5 · decisión 018 (RLS) · decisión 020 (modo de captura) · Capítulo 4
§4.2.4 (máquina de estados: `fallido → encolado`, "reintento manual")

---

## El problema

El pendiente 2 de la nota de traspaso pedía el reintento `fallido → encolado`. Al leer el código para
diseñarlo aparecieron cinco hallazgos que condicionan el diseño:

1. **El endpoint no valida el estado previo.** `POST /analisis/{id}/procesar` pone `encolado` sin mirar de
   dónde viene: un doble clic lanza dos procesamientos del mismo video, y un `POST` sobre un video
   `completado` lo reprocesa.
2. **`procesar_video` no borra el reporte previo** (la nota de traspaso decía que sí; era incorrecto,
   verificado leyendo el código: no hay `delete` ni `upsert`). Con `reportes_biomecanicos.video_id unique`, un
   segundo análisis falla en el `insert` y el `except` marca `fallido` a un video que ya tenía un reporte
   válido.
3. **Un fallo inesperado no deja motivo.** El `except` escribe `fallido` sin `motivo_fallo`; si el video traía
   uno de una corrida anterior, queda el viejo.
4. **El usuario podía forjar estados.** `authenticated` tenía `INSERT` y `UPDATE` sobre todas las columnas de
   `videos` (RLS limita qué filas, no qué columnas). Comprobado contra el proyecto real el 6/10 antes de
   aplicar la migración: 20 de 23 casos de `tests/integration/test_columnas_protegidas.py` fallaban, es decir,
   un usuario podía cambiar su propio `estado`, `motivo_fallo`, `fps_real`, etc. La máquina de estados del
   reintento no vale nada si quien la consulta puede falsificarla.
5. **`parcial` no entra en el caso.** Declarar "normal" un clip de iPhone en cámara lenta (30 fps) deja el
   video `parcial` por R1, no `fallido`; la tesis (§4.2.4) dibuja `parcial` como estado final.

## Alternativas consideradas

- **Reintentar siempre desde `fallido`, sin más condiciones.** Simple, pero un `modo_captura_incompatible` con
  la declaración sin cambiar vuelve a fallar igual: cómputo y confusión para el usuario. Descartada.
- **Operación nueva `POST /analisis/{id}/reintentar`.** La superficie de la API se mantiene mínima (§4.2.5) y la
  tesis ya dibuja `fallido → encolado` como "reintento manual" del mismo flujo. Descartada: se reutiliza el
  endpoint, con validación por estado de origen.
- **Función RPC en la base para el cambio de estado atómico.** Hace falta atomicidad, pero se logra con un
  *compare-and-swap* (`update ... where id = X and estado = <el leído>`) y la lógica de decisión como función
  pura en Python, probable sin red. Descartada la RPC: menos superficie en la base.
- **Dejar editar `sesiones.modo_captura` siempre.** Los reportes congelan el modo con el que se calcularon
  (decisión 020); cambiar la declaración con golpes ya analizados deja escalas mezcladas en una sesión.
  Descartada: un trigger lo impide (ver abajo).
- **Habilitar ya el reintento desde `parcial`.** Es probablemente el error más común del usuario real, pero
  `parcial` hoy mezcla dos causas (R1: fps insuficientes, sin reporte; y reporte con tramos no auditables) y
  no tiene código de motivo. Queda **pendiente** como paso siguiente, con su propio diseño.

## Decisión

**Principio:** se reintenta solo desde `fallido`, y solo si hay algo distinto que probar.

| Estado actual | ¿Se encola? |
| --- | --- |
| `pendiente` | Sí (confirmación de carga, como hoy) |
| `fallido` + `modo_captura_incompatible` | Solo si `sesiones.modo_captura` ≠ el modo con el que falló |
| `fallido` + `error_inesperado` | Sí, hasta un tope de intentos (parámetro, valor inicial 3) |
| `encolado` / `procesando` | **409**: el doble clic no encola dos veces |
| `completado` / `parcial` | **409**: nunca se reanaliza |

**Base de datos.**
1. *(paso a, primer commit, separado)* Permisos por columna: `authenticated` pierde `INSERT`/`UPDATE` de tabla
   sobre `videos` y `UPDATE` de tabla sobre `sesiones`; se otorgan solo las columnas legítimas — `videos`
   INSERT: `id, sesion_id, usuario_id, ruta_almacenamiento`; `videos` UPDATE: ninguna (ningún flujo actual
   modifica un golpe ya creado); `sesiones` UPDATE: todo menos `id, usuario_id, creado_en`. Criterio verificado
   contra el esquema, la especificación de frontend y lo que escribe cada cliente (el frontend todavía no
   escribe contra Supabase). *Ampliación respecto de lo aprobado en el diseño:* se restringe también el
   `INSERT` de `videos`, porque dar de alta un golpe ya `completado` es la misma falsificación que
   actualizarlo después.
2. *(paso b)* `videos.motivo_fallo` suma `error_inesperado`; `videos.modo_captura_intentado` (el modo con el
   que se intentó) y `videos.intentos` (entero, default 0); **trigger en `sesiones`** que rechaza cambiar
   `modo_captura` si algún video de la sesión está `encolado`, `procesando`, `completado` o `parcial`. Así los
   golpes ya analizados nunca quedan "desactualizados": el modo solo se corrige si todos los golpes fallaron o
   están pendientes; si no, se crea otra sesión. Va en la base porque el usuario edita `sesiones` directo con
   RLS.
3. El esquema de `reportes_biomecanicos` no cambia; `procesar_video` borra el reporte previo del video antes de
   insertar (solo puede existir uno si venimos de un `fallido` tardío).

**API.** Mismo endpoint. Función pura `decidir_reintento(estado, motivo, modo_intentado, modo_actual,
intentos)` + *compare-and-swap* al encolar (0 filas actualizadas → 409). Respuestas `202` / `404` / `409` con
`{codigo, estado_actual}`; códigos `estado_no_reintentable`, `declaracion_sin_cambios`, `intentos_agotados`
(los textos en lenguaje llano los pone el frontend, R2). Al encolar se limpian `motivo_fallo`, `fps_real` y
`apto_fase_rapida` y se suma 1 a `intentos`. `procesar_video` escribe `modo_captura_intentado` al empezar y
`error_inesperado` en el `except`.

**Frontend (especificación; la implementación queda atada a la tarea 7.4, autenticación de usuario: el token
compartido de hoy no puede vivir en el navegador).** Golpe `modo_captura_incompatible`: mensaje llano y botón
"Corregir el modo y reintentar" (abre "¿Cómo lo grabaste?", guarda y recién entonces reintenta; si el trigger
rechaza el cambio: "esta sesión ya tiene golpes analizados con otro modo; creá una sesión nueva para este
video"). Golpe `error_inesperado`: "Reintentar" con el contador de intentos. Botón deshabilitado en `encolado`
y `procesando` (la guarda real es el 409). **Prevención del error más común (`parcial` por R1):** el aviso de
"menos de 120 fps, solo preparación" pregunta explícitamente "¿Lo grabaste en cámara lenta?" y ofrece cambiar
"¿Cómo lo grabaste?" antes de subir.

## Consecuencias

- Cuatro defensas contra reanalizar lo que no falló por la declaración: la tabla de estados (409 en
  `completado`/`parcial`), el compare-and-swap (dos pedidos simultáneos encolan uno solo), la declaración sin
  cambios (409, sin gastar cómputo) y el trigger (los golpes ya analizados no necesitan reanálisis).
- Un video que falló por el modo de captura de una sesión con otros golpes ya analizados no se arregla
  cambiando el modo: hay que moverlo a una sesión nueva o volver a subirlo. `videos` no es actualizable por
  el usuario, así que "mover" hoy es volver a subirlo; si aparece la necesidad real se agrega esa columna con
  su propia migración.
- **Pendiente anotado:** reintento desde `parcial` (declaró "normal" un slow-mo), con código de motivo propio
  para distinguir la causa R1 de los tramos no auditables.
- **No revisado en esta decisión:** `sesiones.gesto`, `encuadre` y `lado_camara` también son editables con
  golpes ya analizados y cambiarlos invalidaría los reportes igual que `modo_captura`; y `usuarios` conserva
  `UPDATE` de tabla para `authenticated`. Quedan para una revisión aparte, no se mezclan acá.
- Un video `procesando` huérfano tras un reinicio del proceso sigue sin resolverse: es la tarea 6.5, no este
  reintento.

## Avance

- **Paso (a):** migración `20261006130000` y `tests/integration/test_columnas_protegidas.py` escritas y
  commiteadas; prueba en rojo contra el proyecto real antes de aplicar (20 fallan, 3 pasan: los dos controles
  positivos y `usuario_id`, que ya frenaba RLS). **Pendiente de aplicar por Valentín.**
