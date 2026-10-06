# CLAUDE.md — Proyecto KinetiQ

Contexto permanente del proyecto. Leer antes de proponer o hacer cualquier cambio.

---

## 1. Qué es este proyecto

Sistema de análisis biomecánico preventivo para tenis mediante visión artificial y análisis
de la cadena cinética. Proyecto Final de Ingeniería en Informática, Universidad del Salvador.
Autor: Valentín Capello Ramil. Nombre de producto: **KinetiQ**.

El sistema procesa de forma asincrónica videos pregrabados (mp4/mov) de jugadores de tenis,
extrae puntos articulares con estimación de pose, y **documenta** el orden temporal en que
cada segmento del cuerpo alcanza su velocidad máxima durante saque, drive y revés.

**Qué mide realmente el sistema:** el ORDEN de los picos de velocidad (pelvis → torso → brazo),
más ángulos articulares y separación cadera-hombro.

**Qué NO mide:** velocidad de la pelota, precisión de tiro, ubicación en cancha, porcentaje de
transferencia de energía, ni nada que requiera rastrear la pelota o la cancha.

---

## 2. Reglas duras — NO NEGOCIABLES

Estas cinco reglas derivan de los capítulos ya entregados de la tesis. Violarlas invalida
el trabajo académico, no solo el código.

### R1 — Mínimo 120 fps
El teorema de Nyquist-Shannon impone que, para medir el gesto rápido, el video debe estar
grabado a **120 fps como mínimo** (240 recomendado). A 30 fps el hombro rota casi 80° entre
fotogramas: la información no está "borrosa", está perdida y ningún filtro la recupera.

- Nunca escribir "30 fps recomendado" ni similar en ninguna pantalla.
- La pantalla de carga debe validar los FPS reales del archivo y advertir de forma visible.
- Videos por debajo de 120 fps solo habilitan el análisis de la fase de preparación.

### R2 — El sistema documenta, no predice ni diagnostica
No existe evidencia que permita predecir lesiones a partir del movimiento (Bahr, 2016).

**Verbos prohibidos en toda la interfaz, textos y reportes:** predecir, diagnosticar, prevenir.
**Términos prohibidos:** nombres de patologías ("epicondilitis", "tendinitis"), "riesgo de
lesión", "bandera roja" como etiqueta visible.
**Verbos correctos:** se observa, se documenta, se midió, no se pudo medir.
**Etiqueta correcta para una alerta:** "alerta de carga".

Tampoco se prescribe tratamiento. Nunca escribir cosas como "reducí la intensidad X días"
o "consultá por tal lesión". El sistema muestra el dato; la conclusión es del profesional.
Razón legal: si el software dirige la atención médica sube de Clase I a Clase II ante ANMAT.

### R3 — Cuatro estados, no tres
El semáforo tiene cuatro estados y el cuarto es el más importante:

| Estado | Color | Significado |
|---|---|---|
| Correcto | verde | Dentro del rango de referencia |
| Desvío leve | ámbar | Se aparta, sin alcanzar criterio de alerta |
| Alerta de carga | rojo | Patrón asociado en la literatura con mayor carga articular |
| **No auditable** | **gris** | **El sistema no pudo medir con confianza suficiente** |

Un dato equivocado presentado como bueno es peor que un dato faltante. Nunca rellenar huecos
con estimaciones silenciosas. Ningún estado se comunica solo por color: siempre ícono + texto.

### R4 — Trazabilidad
Toda alerta debe poder responder dos preguntas: qué magnitud concreta la disparó y qué fuente
la respalda. Todo reporte lleva sello de versión del motor, backend de pose y parámetros de
filtrado. Nunca inventar números sin unidad, sin confianza y sin origen.

### R5 — Alcance declarado
**Dentro:** saque, drive, revés. Un jugador por video. Videos de entrenamiento.
**Fuera:** voleas, dejadas, aproximación; partidos completos; múltiples jugadores; análisis en
tiempo real; rastreo de pelota o cancha; comparativas con jugadores ATP/WTA; exportación a
formatos médicos (DICOM/HL7).

---

## 3. Jerarquía de la interfaz

Tres niveles con revelación progresiva. Cada nivel es completo en sí mismo.

1. **Veredicto** — máximo TRES observaciones accionables, lenguaje llano, sin jerga, visible
   sin desplazamiento. Es lo que pidió el 60% de los encuestados.
2. **Evidencia** — video con esqueleto superpuesto sincronizado, gráfico de secuenciación,
   curvas por segmento. Cada observación del nivel 1 enlaza al instante exacto del video.
3. **Dato y fundamento** — valores numéricos, confianza, parámetros de filtrado, versión del
   motor, referencia bibliográfica de cada umbral.

**El gráfico de secuenciación es el elemento central del producto:** un eje temporal único con
los instantes en que pelvis, torso y brazo alcanzan su velocidad máxima. Correcto = escalera
ordenada de izquierda a derecha. Incorrecto = cruce.

**Comparar al jugador consigo mismo** es la base del reporte clínico, no compararlo contra un
promedio poblacional ni contra un "modelo ideal".

---

## 4. Arquitectura

```
Usuario → Frontend (React/TanStack) → API (FastAPI) → Motor Python → Supabase
```

Pipeline del motor:
```
E0 Ingesta (OpenCV, FPS reales)
E1 Pose (MediaPipe por defecto / YOLOv8-Pose+ONNX alternativo)
E1b Validación por confianza
E2 Elevación 2D→3D (opcional)
E3 Filtrado Butterworth de FASE CERO (bidireccional, nunca unidireccional)
E4 Ángulos, velocidades, orden de picos
E5 Auditoría y alertas
```

**Reglas de arquitectura:**
- El frontend NO calcula nada biomecánico. Solo representa datos ya evaluados por el motor.
- El motor no importa bibliotecas web. Recibe rutas de archivo, devuelve estructuras de datos.
- El filtrado va DESPUÉS de la elevación 3D y ANTES de calcular velocidades.
- El filtro debe ser de fase cero (aplicación hacia adelante y hacia atrás). Un filtro
  unidireccional corre los picos en el tiempo y destruye justamente lo que medimos.
- La etapa de pose es intercambiable detrás de una interfaz común (plan de repliegue).

---

## 5. Estado actual

**Fecha de referencia: 7/10/2026.**

- Capítulos 1, 2 y 3 de la tesis entregados. Capítulo 4: fecha objetivo 25/8/2026 (ya pasada); el texto
  vigente quedó escrito antes de que existiera motor funcional ("no existe código productivo" en su propia
  sección de limitaciones) y tiene varias secciones que ya no reflejan lo construido — lista de pendientes
  de redacción acumulados en las decisiones 006, 010, 011, 012, 013, 014, 015, 018, 019 y 020 (esta última con las limitaciones del
  modo de captura declarado a incluir en los Capítulos 6 y 7). Repasar esa lista
  antes de dar el capítulo por actualizado (incluye el esquema de datos del apartado 4.4.6, que pasó de
  siete a nueve tablas).
- **Motor: Etapas 0 a 4 del plan cerradas** (`v0.5.0-etapa4`, en `main`). Versión `0.4.1` (no desactualizada:
  ningún cambio en `engine/` desde ese bump, ver el propio `engine/version.py`). Pipeline completo de punta a
  punta (ingesta → pose → filtrado de fase cero → cinemática → secuenciación) sobre corpus público y sobre la
  Fase B propia (dos sesiones, 110 clips, un jugador). Criterios 1, 2 y 3 del apartado 4.3.4 medidos
  formalmente; decisión 015 (sin repliegue de arquitectura, cinco salvedades documentadas sobre el orden por
  encuadre y gesto).
- **Etapa 4.5 (esqueleto en la nube) cerrada.** Supabase conectado: esquema de nueve tablas con RLS completo
  (decisión 018), bucket de Storage privado, el motor corre dentro de un contenedor que baja un clip de
  Storage, procesa y escribe el resultado en la base (`backend/app/procesar_video.py`), y ese contenedor está
  desplegado de verdad en Render (plan Free primero; Standard —1 CPU, 2 GB— cuando la espera o los cortes molesten y siempre para la defensa,
  decisión 023; Starter descartado: misma memoria que Free). Semilla de la API de la Etapa 6 ya escrita (decisión 019): `GET /health` y
  `POST /analisis/{video_id}/procesar`, sobre la estructura `backend/app/{main.py, security.py, routers/,
  workers/}` prevista desde la decisión 003.
- Frontend: prototipo navegable generado con Lovable (TanStack Start, React 19, Tailwind 4,
  shadcn/ui, configurado para Cloudflare Workers). **Desde el 7/10/2026 el repositorio es la única fuente del código:
  Lovable ya no edita (decisión 026).**
  Diseño visual bueno; contenido y semántica todavía requieren corrección según las reglas de la sección 2,
  y ahora además según las salvedades de la decisión 015 (p. ej. no etiquetar "correcto/incorrecto" donde
  no corresponde). Especificación completa en `docs/ux/especificacion-frontend.md` (1/10/2026).

**Estado al 7/10/2026 (detalle en `docs/bitacora.md`):** keep-alive de Supabase hecho (decisión 021); reintento `fallido → encolado` y
permisos por columna hechos (decisión 022); **contrato del reporte v1.0 hecho (decisión 024)**. Quedan decididos, sin implementar:
carga directa a Storage y autenticación de la API por JWKS (025), frontend en Cloudflare (026), correo de confirmación (027, **pendiente de
elegir** dominio propio + Brevo o Gmail dedicado). Control contra historial, diferido.

**Prioridad inmediata:** el plan de punta a punta, `docs/plan-mvp-punta-a-punta.md` (aprobado el 7/10): Etapa 5 mínima (ensamblador del
reporte), login (7.4) y la interfaz conectada (Cargar, Procesando, Reporte simple) para probarlo desde el celular hacia el 20/10. La
validación es **autovalidación** (grabaciones propias, sin otros usuarios); el sistema igual tiene que funcionar para cualquier usuario
nuevo. Correcciones pendientes del Capítulo 4: `docs/tesis/correcciones-pendientes-capitulo-4.md`.

### Despliegue objetivo (Capítulo 4, apartado 4.5)

**"No se requiere despliegue público: alcanza con el servidor de desarrollo local" ya NO vale** (era la
prioridad de cuando el prototipo era solo de interfaz, sin motor). El MVP se despliega en la nube:

- **Frontend:** **Cloudflare** (Workers), donde ya venía configurado; no Vercel (decisión 026; corrección del Capítulo 4 pendiente).
- **Datos, identidad y archivos:** Supabase Cloud (PostgreSQL, Auth, Storage).
- **Motor:** contenedor persistente de bajo costo (candidatos evaluados en el plan: Render, Railway,
  Fly.io — decisión con datos reales de tiempo y memoria medidos en contenedor, no solo de folleto).

**Calendario:** MVP completo el **2/11/2026**; entrega final el **17/11/2026**. Si el ritmo de trabajo lo
permite, se prioriza terminar antes de esas fechas, no llegar justo a ellas.

---

## 6. Criterios de trabajo

- **MVP primero.** Ante dos soluciones, elegir la más simple que valide la hipótesis. No
  introducir infraestructura que el volumen actual no justifica (colas persistentes,
  observabilidad avanzada, microservicios).
- **Explicar el código.** El autor tiene experiencia limitada en Python y frameworks web:
  al proponer cambios, explicar qué hace cada parte y por qué.
- **Cambios acotados.** Preferir ediciones puntuales sobre regeneraciones amplias.
- **Ante la duda sobre alcance o vocabulario, preguntar.** Un texto que suena bien pero
  contradice la sección 2 cuesta más de lo que ahorra.
