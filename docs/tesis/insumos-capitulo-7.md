# Insumos para el Capítulo 7 (resultados): el sistema y las mediciones al 13/10/2026

**Para quién es:** otro chat que redacta el capítulo y **no ve el repositorio**. Este documento es autocontenido: todas las cifras están acá, con su unidad, su fecha y el archivo de donde salen
(rutas relativas a la raíz del repositorio `motion-biomech-detect`; los videos y el corpus **no** están en el repositorio).

**Corte:** 13/10/2026, commit `60751d8` de la rama `respaldo-13-10` (04:20 hora local, −03:00). Producción es `origin/main` = `56a13c1` (13/10, 03:04).
**Quién escribe:** Claude Code, a pedido de Valentín Capello Ramil (autor). Nada de este documento es redacción de tesis: es material para redactarla.

---

## 0. Cómo leer este documento

- **Estados:** **FIRME** (medido con un procedimiento versionado y reproducible, sin depender de algo pendiente) · **PROVISORIO** (medido, pero con una limitación que puede cambiar la conclusión; se dice cuál) ·
  **PENDIENTE** (falta hacerlo o falta verlo funcionando) · **NO MEDIDO** (no hay dato en el repositorio; no se estima).
- **Fechas:** son las del commit o las del archivo, en hora local (−03:00). La bitácora del repositorio rotula `14/10` a trabajo cuyos commits son del 13/10 (01:59 a 04:20): acá prevalece la fecha del commit.
- **Un jugador, un lado.** Todo el corpus propio es de un solo jugador (el autor, diestro), un iPhone 15 Pro Max, dos sesiones consecutivas (24 y 25/9/2026), y **en todos los videos la cámara estuvo a la
  izquierda del jugador, el lado no dominante** (confirmado por Valentín el 13/10/2026; verificado en la base). **Todos los resultados de orden se midieron con la cámara de ese lado.** Esto condiciona todo lo que
  sigue y se repite en §7.
- **Vocabulario del producto (regla R2 del proyecto):** el sistema *documenta y mide*; no predice, no diagnostica, no previene. La etiqueta de una alerta es "alerta de carga". Conviene mantenerlo en el capítulo.
- **Texto de la hipótesis:** el apartado 1.4 de la tesis (donde está enunciada) **no está en el repositorio**. Lo que sí está es cómo la citan los Capítulos 3 y 4 (§5). Habría que cotejar la redacción literal contra el Capítulo 1.

### Glosario mínimo

| Término | Significado en este documento |
| --- | --- |
| **Gesto · encuadre · grupo** | Saque / drive / revés · perfil (cámara a ~90° del golpe) / tres cuartos (cámara en diagonal por detrás, ~45°) · gesto × encuadre (6 grupos). |
| **Repetición** | Un golpe. La unidad de análisis de los criterios. |
| **Δ** | `t_tronco − t_cadera`, en ms (instantes de los picos de velocidad angular). **Positivo = la cadera llegó primero** (orden esperado en la literatura). |
| **Ordenable** | Dos picos son ordenables si `abs(Δ) > 1/120 s = 8,33 ms` (estricta; decisión 032). Con `abs(Δ) ≤ 8,33 ms` el orden "no se puede establecer a esta resolución" (se dice "dentro de la tolerancia"). |
| **1a · 1b · 1c** (Criterio 1) | 1a = ordenables / todas las repeticiones del grupo; 1b = entre las ordenables, fracción con el orden modal; **el criterio se cumple si 1a ≥ 0,8 y 1b ≥ 0,8**; 1c = coincidencia con el orden esperado (se informa aparte, sin umbral). |
| **tp · pt** | Orden modal observado: tronco primero · cadera ("pelvis") primero. |
| **Corpus horneado** | Los archivos de cámara lenta con que se hizo toda la medición original (marcas de tiempo reescritas a 30 fps). Su muestreo efectivo resultó ser ~120 fps (§2.2). |
| **Originales** | Los HEVC del iPhone con las marcas de tiempo reales (~200 fps medios). Base del Paso B. |
| **Regularización** | Interpolación de las poses a una grilla uniforme de 240 Hz usando las marcas reales; los puntos interpolados se cuentan y se informan. |
| **Golpe medido** | Los picos de cadera y de tronco se midieron con confianza ≥ 0,5, aunque empaten (decisión 037). |

### Resumen en diez líneas

1. El sistema **funciona de punta a punta en producción** (celular → Cloudflare → Supabase → Render Standard → reporte): 117–147 s por golpe de 3–4 s en Render Standard; 678 s en el plan gratuito (§1, §2.3).
2. **Corrección de escala del corpus:** el iPhone captura a ~200 fps reales (no 240) y el corpus con que se midió todo era un remuestreo a ~120 fps. Hubo que recalcular (§2.1, §2.2).
3. **Con los originales (Paso B, 76 repeticiones), el orden cadera→tronco depende del encuadre** en el saque (0 de 8 contra 7 de 7 con la cadera primero, Fisher p = 0,0002) y en el drive (1 de 8 contra 3 de 3, p = 0,024); el revés no sigue el patrón (§2.5).
4. **Los dos grupos que cumplen el Criterio 1 (saque y drive de perfil, 1a = 0,83) son justamente los sospechosos** de sesgo del encuadre; en la réplica ninguno cumple (§2.5).
5. Por eso desde el 13/10 **ningún grupo emite veredicto del orden** (decisiones 035 y 036): el sistema mide y registra; no juzga (§4).
6. **El pico del brazo no se pudo medir en el 68 % de las repeticiones (52 de 76)**; 18 de 18 en el saque de tres cuartos. Con la cámara del lado no dominante el brazo que golpea queda del lado lejano y el torso lo
   tapa en el armado: es una condición del lado de grabación (§2.7).
7. Error angular contra goniometría manual: rodilla 8,5° y codo 12,5° de media (meta < 20,6°); el p95 del codo (36,4°) supera la meta y el codo dominante tiene n = 2 (§2.6).
8. Consistencia entre sesiones (Criterio 3): 9 de 11 combinaciones (82 %) por la regla original, 10 de 11 por la lectura calibrada; la métrica de instante está pendiente de recalcularse con el tiempo real (§2.6).
9. El valor que queda es **medición trazable + seguimiento del jugador consigo mismo en el mismo encuadre**, no un juicio del orden (§5).
10. Falta, antes de la demo (28–30/10): probar en pantalla real los pasos 5 y 6 (solo en la rama de respaldo), el correo propio, el respaldo con restauración y el ensayo (§8).

---

## 1. El sistema construido y funcionando hoy

### 1.1 Arquitectura desplegada

```
Navegador (iPhone o PC)
   │ HTTPS
   ▼
Cloudflare Workers  ── https://kinetiqtennis.me (dominio propio, DNS en Cloudflare; el subdominio workers.dev sigue activo)
   │ frontend React 19 + TanStack Start + Tailwind 4 (el repositorio es la única fuente; Lovable dejó de editar el 7/10/2026)
   │
   ├── Supabase Auth ........ registro, ingreso, JWT
   ├── Supabase Postgres .... 9 tablas con RLS; el cliente lee y escribe con su propia sesión
   └── Supabase Storage ..... bucket `videos` (privado, 50 MB, mp4/mov) y bucket `artefactos` (privado, jpeg/mp4); carpeta por usuario
   │
   │ POST /analisis/{video_id}/procesar  (JWT verificado por JWKS + el video debe ser del usuario) → 202
   ▼
Render (contenedor Docker, plan Standard: 1 CPU, 2 GB) ── API FastAPI + motor Python en el mismo proceso
   │ cola de a un análisis (cupo configurable); recuperación al arrancar
   │ MediaPipe Pose en CPU (sin GPU), Butterworth de fase cero, ffmpeg para los artefactos
   ▼
Supabase (con service_role): reporte JSON (contrato 1.4), estados, tiempos de cola y procesamiento, fotogramas y video con esqueleto
```

| Componente | Qué es | Plan / costo real hoy | Fuente |
| --- | --- | --- | --- |
| Frontend | Cloudflare Workers (TanStack Start, React 19, Tailwind 4, shadcn/ui) | Plan gratuito; **cuotas NO VERIFICADAS** (corrección 2 del Cap. 4) | decisión 026; `frontend/wrangler.jsonc` |
| Dominio | `kinetiqtennis.me`, registrado en Namecheap por el GitHub Student Developer Pack; DNS en Cloudflare; renovación automática apagada; **vence al año** | Sin costo el primer año; **costo de renovación NO VERIFICADO** | decisión 034 |
| Datos, identidad, archivos | Supabase Cloud (Postgres + Auth + Storage) | Free (500 MB de base, 1 GB de almacenamiento; **sin respaldos**) | decisiones 018, 021, 025 |
| Motor + API | Render, contenedor Docker, `render.yaml` (`plan: standard`) | **USD 25/mes** (1 CPU, 2 GB) desde el 12/10/2026; antes plan Free (0,1 CPU, 512 MB) | decisiones 017, 019, 023; `render.yaml` |
| Pose | MediaPipe Pose (33 puntos, 3D directo), `model_complexity=2`, `static_image_mode=True`, CPU | — | decisión 005 |
| Correo de confirmación | SMTP propio con el dominio (Brevo). **Estado: funciona desde el 15/10/2026** (registro, confirmación y recuperar contraseña probados con una cuenta de prueba) | Plan gratuito de Brevo; costo **NO VERIFICADO** | decisiones 027 y 034 |
| Integración continua | GitHub (repositorio privado) | Free | `.github/` |

**Reglas de arquitectura que rigen (CLAUDE.md §4):** el frontend no calcula nada biomecánico (solo representa lo que evalúa el motor); el motor no importa bibliotecas web; el filtrado es de **fase cero** (adelante y atrás) y va antes de calcular velocidades.
**Pipeline del motor:** E0 ingesta (lee las marcas de tiempo reales) → E1 pose → E1b validación por confianza → regularización a 240 Hz → E3 filtrado (Butterworth 4.º orden, corte por clip con análisis residual de Winter) → E4 cinemática, picos y secuenciación (ventana de ±300 ms anclada al pico del torso) → ensamblado del reporte (contrato 1.4) → artefactos (tres fotogramas clave y un video con esqueleto).

### 1.2 Qué hace, de punta a punta

1. **Registro** con rol (jugador, entrenador, profesional de la salud) y consentimiento (Ley 25.326); la cuenta se activa al confirmar el correo (decisión 027), con SMTP propio (Brevo) funcionando desde el 15/10/2026.
2. **Ingreso** y "Olvidé mi contraseña" (`/recuperar`, `/restablecer`; probado con una cuenta de prueba el 15/10/2026).
3. **Cargar:** una sesión de hasta 12 golpes (se recomienda un mínimo de 6), 50 MB por archivo, mp4/mov; el usuario declara gesto, encuadre, lado de la cámara y cómo grabó. El navegador sube **directo a Storage** con su sesión (RLS por carpeta). Instrucción previa: en el iPhone, *Opciones → Formato: Actual* o subir desde Archivos (§2.1).
4. **API:** valida el JWT y que el video sea del usuario, responde 202 y procesa en segundo plano, de a un golpe por vez.
5. **Motor:** lee la tasa **real** del archivo (nunca la asume; pisos de aptitud 114 y 57 fps, con 5 % de tolerancia), extrae la pose, regulariza el tiempo, filtra, mide y arma el reporte. Si el usuario declaró cámara lenta y el archivo llegó en tiempo real con la grilla por debajo de 114 fps (la firma de una conversión hecha por el teléfono), el análisis falla con un motivo propio (`archivo_convertido`) y el mensaje explica el camino que funciona; si declaró grabación normal, queda `parcial` (solo la fase de preparación, regla R1).
6. **Procesando:** estado por polling, con la espera en cola y el procesamiento por separado; reintento de un golpe fallido.
7. **Reporte de un golpe:** "Tres momentos" (fotogramas reales con esqueleto en el pico de cadera, tronco y brazo), observaciones **sin veredicto**, magnitudes con su confianza (separación cadera-hombro máxima; ángulos de rodilla y codo en el pico del tronco), trazabilidad (versión del motor, tasa, regularización, tolerancia) y limitaciones.
8. **Vista de sesión:** consistencia entre golpes (separación mediana y dispersión, "mismo orden en N de M", golpes medidos, golpe típico, golpes que se apartan), calculada al leerla (no se guarda).
9. **Biblioteca** (miniatura real, "N golpes medidos · K con orden distinguible · M no medibles"), **eliminar un golpe o una sesión** (borra los archivos de ambos buckets y las filas), **PDF** por impresión del navegador.
10. **Solo en la rama de respaldo (no en producción):** Perfil real (nombre, rol, jugadores, "Descargar mis datos"), **eliminar la cuenta** con sus archivos, **Evolución real** (la serie de sesiones del mismo jugador, gesto y encuadre) y el **PDF como documento A4**.

**Qué produce el reporte real hoy:** solo `sin_evaluar` ("Solo registrado"), `sin_diferencia_medible` y `no_auditable`. Los estados `correcto`, `desvio_leve` y `alerta_de_carga` siguen existiendo en el contrato pero, con el orden suspendido y sin umbrales con referencia, ningún reporte los emite (decisión 036).

### 1.3 Qué está en producción y qué solo en `respaldo-13-10`

| Capacidad | Dónde | Commit · fecha (−03:00) | En producción |
| --- | --- | --- | --- |
| Motor Etapas 0–4 (pipeline, Criterios 1–3 medidos) | `main` | tag `v0.5.0-etapa4` · 29/9/2026 | Sí |
| Contenedor en Render (Free), API semilla, medición real | `main` | 1–2/10/2026 (decisiones 017, 019) | Sí (hoy Standard) |
| Carga directa, JWKS, Cloudflare, Lovable fuera | `main` | 7/10/2026 (decisiones 025, 026) | Sí |
| Render **Standard**; motor 0.5.0, contrato 1.3, tolerancia única 8,33 ms, fotogramas clave y video | `main` | `e35fc6f` 12/10 15:33 · `875b2cf` 12/10 14:42 | Sí |
| Motor 0.5.1 (cobertura del 75 %, magnitudes, video 720 px) | `main` | `01e8ad4` · 12/10 18:00 | Sí (Render "Live" con motor 0.5.1; verificado ese día con un usuario de prueba, luego borrado) |
| Motor 0.5.2 (saque sin veredicto; contraste del encuadre) | `main` | `1975738` · 12/10 22:04 | Sí |
| Motor 0.5.3 (ningún grupo emite veredicto) | `main` | `c2d35d8` · 13/10 00:32 | Sí |
| Higiene de contenido; varios golpes por sesión (hasta 12) | `main` | `c55139e` 13/10 00:37 · `c9f0334` 13/10 01:25 | Sí |
| Vista de sesión, consistencia, eliminar golpe/sesión, miniatura, tiempos, recuperación al arrancar | `main` | `93a15aa` · 13/10 01:59 | Sí |
| **Motor 0.5.4, contrato 1.4, decisión 037**, PDF por impresión, hallazgos de producción | `main` | `56a13c1` · 13/10 03:04 | **Sí** (`/health` = 0.5.4, verificado 3 veces seguidas; frontend republicado por Valentín, según la bitácora) |
| **Paso 5:** Perfil real, "Descargar mis datos", `DELETE /cuenta` (archivos de ambos buckets primero) | solo `respaldo-13-10` | `5b1dc01` · 13/10 03:50 | **No** |
| **Paso 6:** Evolución real (`GET /evolucion`, pantalla `/evolucion`) y PDF como documento A4 | solo `respaldo-13-10` | `0bbc1df` · 13/10 04:17 | **No** |
| Bitácora de cierre del día | solo `respaldo-13-10` | `60751d8` · 13/10 04:20 | — |

- `main` y `origin/main` quedan en `56a13c1`: Render no tiene nada nuevo que desplegar (la rama de respaldo no se despliega). Los pasos 5 y 6 **no agregan migraciones** ni tocan el motor.
- **Pruebas automáticas (reportadas en la bitácora al cierre, sin volver a correrlas para este documento):** servidor, suite rápida **589 passed** (569 en `56a13c1`); frontend, `bun test` **106 pass** (84 en `56a13c1`), `tsc` y `build` limpios.
- **Nada de los pasos 5 y 6 está verificado en pantalla real:** los gráficos de Evolución solo se miraron con una serie sintética; el PDF solo se renderizó a 210 mm con datos sintéticos; la cascada de eliminar cuenta está razonada del esquema, no ejecutada.

### 1.4 Versiones del motor y del contrato (RNF-02: el reporte lleva su versión)

| Motor | Qué cambia | Contrato |
| --- | --- | --- |
| 0.4.1 | Sello puesto en cuatro commits entre el 9 y el 12/10 (los reportes de esos días se distinguen por el contrato 1.0 a 1.2, no por el sello). Es el motor de las mediciones formales de los Criterios 1, 2 y 3. | 1.0–1.2 |
| 0.5.0 | Lee la tasa real de las marcas de tiempo; regularización a 240 Hz; tolerancia única 8,33 ms; artefactos. | 1.3 |
| 0.5.1 | Regla de cobertura: el pico de un segmento no se reporta si se midió menos del 75 % de la ventana. Magnitudes articulares. Video a 720 px. | 1.3 |
| 0.5.2 | Decisión 035: el saque no emite veredicto; contraste del encuadre declarado con el visto. | 1.3 |
| 0.5.3 | Decisión 036: ningún grupo emite veredicto. | 1.3 |
| 0.5.4 | Decisión 037: el empate es "golpe medido"; el pico que falta lleva su motivo. | 1.4 |
| 0.5.5 | Nota neutra cuando la cámara estuvo del lado de la mano dominante (lado todavía no validado; decisión 013). *(15/10/2026; solo en `respaldo-13-10` hasta publicar.)* | 1.4 |

---

## 2. Resultados medidos

Cada fila: número, unidad, fecha y archivo. El estado de cada uno está marcado aquí y consolidado en §3.

### 2.1 Tasa real de captura del iPhone — **FIRME**

El iPhone graba "a 240 fps" nominales; entrega ~200 fps reales, con fotogramas perdidos casi periódicos.

| Medida | Valor | Fecha | Archivo de origen |
| --- | --- | --- | --- |
| 16 originales HEVC del corpus: tasa real media por archivo | **199,92 a 200,96 fps** (mediana 200,62); nominal 239,98; **16,3 a 16,7 %** de fotogramas perdidos | 9/10/2026 | `docs/resultados/corpus-real-alineacion.json` (`reales`); decisión 030 |
| Un recorte de Archivos (huella de intervalos) | **198,87 fps** media; 17,13 % perdidos; 398 fotogramas visibles + 81 de pre-roll oculto; intervalos: 356 de 1 período y 41 de 3 | 9/10/2026 | `docs/resultados/tasa-real-iphone-huella.json`; decisión 029 |
| Saque de perfil subido por el flujo completo (`IMG_6376`) | 199,6 fps (16,8 % perdidos); 98 de 597 puntos interpolados (16,4 %) | 9/10/2026 | `docs/tesis/correcciones-pendientes-capitulo-4.md`, nota 8 |
| Revés de tres cuartos subido por el flujo (`IMG_6395`, 3,0 s) | 199,9 fps (16,7 % perdidos y 16,7 % interpolados) | 12/10/2026 | ídem, nota 11 |
| Saque de perfil desde el celular, 805 fotogramas | 200,8 fps; 16,3 % interpolados | 12/10/2026 | `docs/resultados/criterio4-latencia.md`, fila 4 |
| 18 recortes del corpus para Evolución | 199,3 a 201,1 fps | 13/10/2026 | `docs/protocolo-sesiones-evolucion.md` §A |
| Una grabación con poca luz | "~170 fps" **según Fotos ⓘ; NO MEDIDO en el archivo** | 9/10/2026 | decisión 029 |

**Qué hace el teléfono según el camino de subida** (decisiones 028 y 029; medido con `inspeccionar_subidas`):

| Camino | Lo que llega | Estado |
| --- | --- | --- |
| Selector de Fotos, formato por defecto ("más compatible"), recorte de 2 s | **H.264, 100 fps**, 201 fotogramas (no es analizable: < 114 fps) | medido 7/10 |
| Mismo recorte desde Archivos u *Opciones → Formato: Actual* | HEVC original, marcas reales, 198,9 fps medios | medido 9/10 |
| Cámara lenta sin recortar, formato por defecto | H.264, 60 nominales → **42,7 fps reales**; rechazado | medido 9/10 |
| Recorte con la cámara lenta mantenida (12 s), aun con "Actual" | Llega a **~50 fps**; rechazado por el sistema (`archivo_convertido`) en 15 y 18 s, dos veces | 12/10 |

Los cuatro selectores de la página de prueba entregaron **el mismo archivo** (difieren en 15 bytes de metadatos): el atributo `accept` no cambia nada. Un video vertical llegaba acostado (rotación −90° que OpenCV no aplicaba); corregido.

### 2.2 El corpus horneado es un remuestreo a ~120 fps — **FIRME**

Alineando por contenido (miniaturas de 64×36) los originales contra los archivos horneados, en 15 pares completos:

| Medida | Valor | Archivo |
| --- | --- | --- |
| Fotogramas reales por fotograma horneado, en la meseta | **1,665 a 1,675** (mediana 1,67), idéntico en los 15 pares | `corpus-real-alineacion.json` (`resumen`) |
| Muestreo equivalente | **mediana 120,1 fps** (rango 119,8 a 120,3 entre pares); el Paso A usó 120,2 | ídem |
| Rampas a velocidad normal en los extremos | 6,6–6,7 reales por horneado al principio y al final del archivo | decisión 030 |
| Fotogramas horneados repetidos | 5,7 a 11,4 % | decisión 030 |
| Repeticiones ubicadas / enteras en la meseta | 88 / **86** (98 %); 2 empiezan en una rampa | `corpus-real-alineacion.json` |
| Emparejamiento original↔horneado por fecha de creación | 16 de 16 | decisión 030 |

**Consecuencia, aplicada a todo lo medido con el corpus horneado:** velocidades absolutas **×2,0 sobreestimadas**, intervalos en ms **×0,5 subestimados**, resolución temporal **8,3 ms por fotograma** (no 4,2), aptitud R1 "reducido" en el borde inferior (no "completo"). **Los ángulos no cambian** (no dependen del tiempo).
`IMG_6391` (saque de tres cuartos, toma 02) está **incompleto** en el original (2503 fotogramas contra ~15 221 esperados); sus 6 repeticiones quedan afuera del recálculo.

### 2.3 Latencia (Criterio 4), memoria y velocidad de inferencia

**Latencia de punta a punta** (`docs/resultados/criterio4-latencia.md`). El Criterio 4 se define por lo que declaren los usuarios: **no hay umbral**; se informa el valor medido.

| # | Fecha | Golpe | Entorno | Fotogramas | Latencia | Cómo se obtuvo |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 9/10/2026 | `IMG_6376` (saque, perfil, 2,5 s) | Render **Free**, complexity 2 | 501 | **~9 min** | Manual (Valentín); las columnas de tiempo aún no existían |
| 2 | 12/10/2026 | `IMG_6395` (revés, tres cuartos, 3,0 s) | Render **Free** | 599 | **677,8 s** (cómputo 676,6 s) | Base: `encolado_en → fin_procesamiento_en` |
| 3 | 12/10/2026 noche | Recorte real de `IMG_6395` (3,1 s, 27 MB) | Render **Standard**, motor 0.5.0, con artefactos | 626 | **117,4 s** (cómputo 116,0 s) | Base, con la API de producción y un usuario de prueba (luego borrado) |
| 4 | 12/10/2026 noche | Saque de perfil desde el celular (~4,0 s) | Render **Standard**, motor 0.5.0, con artefactos | 805 | **148 s** (Valentín); **146,7 s** en el log | Log de Render (`procesar_video`) |

- **Free contra Standard, mismo tipo de archivo (filas 2 y 3):** 677,8 s contra 117,4 s = **5,8 veces más rápido**. Por fotograma: ~1,13 s contra ~0,19 s (derivado de las filas 2, 3 y 4: 676,6/599; 116,0/626; 146,7/805). **La latencia escala con los fotogramas.**
- Otros datos de Free (decisión 017/023): **414,1 s** y RSS pico **480,4 MB** para 360 fotogramas (2/10/2026). Referencia local (Docker, simulando el plan, 29/9): 512 MB/0,5 CPU 176–185 s; 1 GB/1 CPU 91,3 s; 2 GB/2 CPU 81,0 s (`e4.5-contenedor-tiempo-memoria.json`).
- **Artefactos** (fotogramas clave + video con esqueleto): +6,8 % de tiempo en la PC de desarrollo (9,1 s sobre 134 s); **10,2 s** en Render Standard (fila 4).
- **Procesamiento contra espera en cola:** desde el 13/10 se registran por separado (`inicio − encolado` = espera en la cola; `fin − inicio` = procesamiento, que es lo que mide el Criterio 4). Las filas 1 a 4 son de **un golpe a la vez**, sin cola. **La espera en cola medida para una sesión de varios golpes: NO MEDIDO** (el archivo no tiene filas 5 en adelante; los tiempos de los golpes de las dos sesiones del corpus ya subidas a producción (6 por sesión, según el protocolo) están en la base y no se volcaron). Lo que hay es una estimación: una sesión de 6 golpes en Standard ~12 min; en Free ~41 min (6 × 414 s).

**Memoria pico (RSS):**

| Entorno | RSS pico | Fotogramas | Fecha | Fuente |
| --- | --- | --- | --- | --- |
| Render **Standard**, con artefactos (n = 1) | **748,4 MB** | 805 | 12/10/2026 | `criterio4-latencia.md`, fila 4 |
| Render Free (n = 1) | 480,4 MB (sobre 512: margen de **32 MB**) | 360 | 2/10/2026 | decisiones 017 y 023 |
| Docker local, 512 MB / 0,5 CPU (3 corridas) | 426,4 a 426,9 MB | 360 | 29/9/2026 | `e4.5-contenedor-tiempo-memoria.json` |
| PC de desarrollo (Windows) | ~460 MB | 626 | 12/10/2026 | decisión 033 |

El mismo proceso ocupa más en Linux/Render (748 MB) que en Windows (460 MB): **la causa no se investigó**. En Free ese golpe de 805 fotogramas no habría entrado. Margen en Standard: ~1,3 GB.

**Velocidad de inferencia de la pose** (`docs/resultados/e2-velocidad-inferencia.json`, 27/8/2026, motor 0.2.0): **3,57 fps** medios (280 ms por fotograma; p50 236,5 ms; p95 321,8 ms), MediaPipe `model_complexity=2`, 1080p, 80 fotogramas, CPU de una PC con Windows. El Capítulo 4 estimaba ~25 fps (decisión 006): **casi 7 veces menos**.

### 2.4 Paso A del recálculo (12/10/2026) — **FIRME como control; superado por el Paso B como medición**

Las poses ya extraídas del corpus horneado, con el tiempo real (120,2 fps), la ventana de ±300 ms en tiempo real y la tolerancia en ms de la decisión 032. Motor 0.5.0, commit `3d88f89`, árbol limpio; 84 repeticiones; los resultados se informan **lado a lado con la medición original**, como se fijó antes de mirar (plan de recálculo §3).
Archivos: `docs/resultados/paso-a-sesion-2.json` (medición), `paso-a-sesion-1.json` (réplica exploratoria), `paso-a-resumen.md`.

**Criterio 1, sesión 2 (conjunto de medición), tolerancia 8,33 ms** — ordenables · 1a · 1b · orden:

| Grupo | n | Original (240 fps asumidos) | Paso A (120,2 fps) | Cumple (orig. → A) |
| --- | --- | --- | --- | --- |
| Saque · perfil | 6 | 6 · 1,00 · 1,00 · tp | 5 · 0,83 · 1,00 · tp | sí → **sí** |
| Saque · tres cuartos | 18 | 9 · 0,50 · 1,00 · pt | 8 · 0,44 · 0,62 · pt | no → no |
| Drive · perfil | 6 | 6 · 1,00 · 1,00 · tp | 3 · 0,50 · 1,00 · tp | sí → **no** |
| Drive · tres cuartos | 6 | 0 · 0,00 | 0 · 0,00 | no → no |
| Revés · perfil | 5 | 4 · 0,67 · 0,75 · pt | 3 · 0,60 · 0,67 · pt | no → no |
| Revés · tres cuartos | 6 | 6 · 1,00 · 0,83 · tp | 3 · 0,50 · 1,00 · tp | sí → **no** |

- **Réplica (sesión 1):** el saque de perfil cumple (4 ordenables de 5, 1a 0,80, 1b 1,00, tp); ninguno de los otros cinco.
- **No se puede atribuir todo el cambio al reloj:** al corregir los fps cambian también la ventana (±36 fotogramas en vez de ±72), la separación mínima entre picos y los umbrales en °/s.
- **Controles exploratorios (no pre-registrados):** el "tronco primero" **no** se explica por el reloj, ni por el filtro (cortes fijos de 4 a 12 Hz; en saque de tres cuartos sí cambia con el corte), ni por la definición (giro axial da el mismo sentido y, en el saque de perfil, una diferencia mayor: mediana −129 ms contra −62 ms). Lo que sí se sostuvo es que **depende del encuadre**.
- **Saque, ordenables a 8,33 ms (dos sesiones):** perfil 0 cadera primero / 9 tronco primero / 1 dentro; tres cuartos 6 / 3 / 15; Fisher exacto **p = 0,009** (exploratorio). Todos los gestos juntos: p = 0,23.
- **En tres cuartos el instrumento estaba en su límite:** en 34 de 48 repeticiones la cadera y el tronco quedan a 8,33 ms o menos.

### 2.5 Paso B del recálculo (12–13/10/2026) — la medición definitiva — **FIRME (conteos) · PROVISORIO (lectura)**

**Qué es:** los 6 grupos medidos sobre los **originales** del iPhone (~200 fps reales con sus marcas de tiempo), regularizados a la grilla de 240 Hz (≈ 16–17 % de puntos interpolados, contados y declarados), con la **misma constante de "ordenable"** que usa el producto (8,33 ms, estricta).
**Procedimiento:** `backend/app/medicion_paso_b.py`; commit `7c9535c`, árbol limpio, motor 0.5.1; corrida de 131,9 min; generado el 13/10/2026 02:51 UTC (= 12/10 23:51 −03:00).
**Archivos:** `docs/resultados/paso-b-sesion-2.json` (medición) y `paso-b-sesion-1.json` (réplica exploratoria, no independiente), `paso-b-resumen.md`, `paso-b-saque.md`.
**Universo:** 13 originales; **76 repeticiones medidas** (35 de la sesión 1 + 41 de la sesión 2); **75 válidas** (1 repetición de saque de perfil de la sesión 1 no es válida). Excluidas por diseño: las 2 que empiezan en una rampa de velocidad y las 6 de `IMG_6391` (original incompleto).
Las cifras de las tablas fueron **recalculadas desde los JSON** al preparar este documento y coinciden con `paso-b-resumen.md`.

**Tabla por gesto y encuadre** (Δ = tronco − cadera; "dentro" = |Δ| ≤ 8,33 ms; dos sesiones sumadas):

| Gesto | Encuadre | Medidas | Válidas | Cadera primero | Tronco primero | Dentro | Mediana de Δ s1 · s2 (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Saque | perfil | 11 | 10 | **0** | **8** | 2 | −18,7 · **−162,5** |
| Saque | tres cuartos | 18 | 18 | **7** | **0** | 11 | +4,2 · +10,4 |
| Drive | perfil | 12 | 12 | 1 | **7** | 4 | −2,1 · −20,8 |
| Drive | tres cuartos | 12 | 12 | 3 | 0 | 9 | +6,2 · 0,0 |
| Revés | perfil | 11 | 11 | 3 | 3 | 5 | +4,2 · −4,2 |
| Revés | tres cuartos | 12 | 12 | 0 | **5** | 7 | −8,3 · −10,4 |
| **Total** | | **76** | **75** | 14 | 23 | 38 | |

**¿Depende del encuadre? Por gesto** (solo repeticiones ordenables; prueba exacta de Fisher, bilateral, **exploratoria**):

| Gesto | Perfil: cadera / tronco primero | Tres cuartos: cadera / tronco primero | p |
| --- | --- | --- | --- |
| Saque | 0 / 8 | 7 / 0 | **0,0002** |
| Drive | 1 / 7 | 3 / 0 | **0,024** |
| Revés | 3 / 3 | 0 / 5 | 0,18 |

- **Saque y drive: sí, y en el mismo sentido** (perfil: el tronco llega primero; tres cuartos: la cadera llega primero o queda dentro de la tolerancia). Un movimiento físico no puede depender de la cámara: **al menos uno de los dos encuadres mide mal**, y con estos datos no se puede decir cuál (elegir el que coincide con lo esperado sería elegir por el resultado).
- **Revés: no sigue el patrón.** En tres cuartos el tronco llega primero en las 5 repeticiones ordenables; en perfil 3 contra 3, y ese grupo es sensible al método (con giro axial el orden modal pasa a cadera primero: 3 repeticiones). El "tronco primero" del revés es del gesto o es otro sesgo del estimador: **no se puede decidir**.
- **El saque de perfil de la sesión 2** tiene Δ de mediana **−162,5 ms** (−250 a −4 ms), muy por encima de la resolución, y es donde la señal de la cadera está menos acoplada a la del tronco (correlación de ω 0,55 contra 0,82 en tres cuartos); en la sesión 1 es −18,7 ms con correlación 0,92: el sentido es el mismo, la magnitud no.

**Criterio 1 con los originales** (par cadera-tronco, tolerancia primaria 8,33 ms) — ordenables / n · 1a · 1b · orden modal:

| Grupo | Sesión 2 (medición) | Sesión 1 (réplica) |
| --- | --- | --- |
| Saque · perfil | 5/6 · **0,83** · 1,00 · tp · **cumple** | 3/5 · 0,60 · 1,00 · tp · no |
| Saque · tres cuartos | 6/12 · 0,50 · 1,00 · pt · no | 1/6 · 0,17 · 1,00 · pt · no |
| Drive · perfil | 5/6 · **0,83** · 1,00 · tp · **cumple** | 3/6 · 0,50 · 0,67 · tp · no |
| Drive · tres cuartos | 1/6 · 0,17 · 1,00 · pt · no | 2/6 · 0,33 · 1,00 · pt · no |
| Revés · perfil | 4/5 · 0,80 · 0,50 · tp · no | 2/6 · 0,33 · 0,50 · tp · no |
| Revés · tres cuartos | 3/6 · 0,50 · 1,00 · tp · no | 2/6 · 0,33 · 1,00 · tp · no |

- **Cumplen, en la sesión de medición, solo el saque de perfil y el drive de perfil**, ambos con el tronco primero. **En la réplica no cumple ningún grupo.**
- **Ningún grupo de tres cuartos cumple:** la causa es la resolución (más de la mitad queda dentro de 8,33 ms), no la inconsistencia (1b = 1,00 en saque y drive).
- **Sensibilidad a la tolerancia** (declarada de antemano, sesión 2): a 4,17 ms cumplen también el revés de tres cuartos (1,00) y la toma 02b del saque de tres cuartos (0,83); a 12,5 y a 16,7 ms **solo cumple el saque de perfil** (1a 0,83). Es decir: el único grupo que cumple en todas las tolerancias es el que más depende del encuadre.
- **Cambio contra el Paso A:** con los originales el drive de perfil pasa de 1a 0,50 a 0,83 (resolución de 5 ms en lugar de 8,3): algunos empates se resuelven y otros no.
- **Los grupos que cumplen el Criterio 1 son justamente los sospechosos:** la repetibilidad no distingue un movimiento real de un sesgo fijo del encuadre.

**Lo que no se puede decir:** cuál encuadre mide bien (no hay una medición independiente de la pelvis); que el jugador "llegue tarde con la cadera".

### 2.6 Criterios 1 a 5 del apartado 4.3.4 — consolidado

| Criterio | Meta (Cap. 4) | Resultado | Estado |
| --- | --- | --- | --- |
| **1. Ordenamiento de picos** | Pelvis, torso y brazo distinguibles y ordenables de forma repetible en ≥ 8 de cada 10 repeticiones válidas | **Medición original** (decisión 014, motor 0.4.1, corpus horneado, sesión 2, τ = 1): cumplen saque de perfil (1a 1,00 · 1b 1,00), drive de perfil (1,00 · 1,00) y revés de tres cuartos (1,00 · 0,83); no cumplen saque de tres cuartos (0,50 · 1,00), drive de tres cuartos (0,00) y revés de perfil (0,67 · 0,75). A τ = 2 y 3 cumplen dos. **Superada** por el recálculo con tiempo real (§2.4–§2.5): con los originales, **2 de 6 en la sesión de medición, 0 de 6 en la réplica**. | **FIRME** la medición con los originales (Paso B); la original queda como registro |
| **2. Error angular en articulaciones proximales** | < 20,6° (estimación visual humana; Krosshaug et al., 2007) contra goniometría manual | **Plano de la imagen (2D, primario), n = 18 por articulación:** rodilla media **8,5°** (mediana 5,9°; p95 19,2°; sesgo −1,5°); codo media **12,5°** (mediana 10,5°; p95 **36,4°**; sesgo +2,1°). **Cumple por la media** en ambas. Error intra-observador **4,1°**. Secundario 3D (no validado por esta vía): rodilla 15,4° de media, codo 18,0°. **Codo dominante: n = 2, errores 11,9° y 42,5° (media 27,2°)**. | **FIRME** (media agregada, 2D); **PROVISORIO** (codo dominante); motor 0.4.1, no re-medido con 0.5.x |
| **3. Repetibilidad consigo mismo** (redefinida, decisión 012) | Variabilidad entre sesiones ≤ intra-sesión (≥ 75 % de combinaciones consistentes) | **9 de 11 (82 %)** con la regla original (Δ ≤ σ_w); **10 de 11 (91 %)** con la lectura calibrada (p de permutación > 0,05). 12 combinaciones, una excluida (revés de perfil, métrica ii: censura de la ventana). Tabla abajo. | **PROVISORIO**: métrica (i) sí; métrica (ii) por recalcular con tiempo real; n = 6 por sesión |
| **4. Latencia** | La definen los usuarios (sin umbral) | 117,4 a 146,7 s por golpe de 3–4 s en Standard; 677,8 s en Free (§2.3). Umbral: **no definido**. | **PROVISORIO** (n = 2 en Standard, un golpe a la vez) |
| **5. Utilidad percibida** | Los usuarios señalan un uso concreto no cubierto | **NO EVALUADO** (el alcance cambió el 7/10: autovalidación, sin pruebas con otros usuarios). Opciones del plan: validación exploratoria con un entrenador o kinesiólogo, o "no evaluado, trabajo futuro". | **PENDIENTE** |

**Criterio 3, detalle** (`docs/resultados/criterio3.json`; motor 0.4.1, commit `6773ffd`, 29/9/2026; sesiones 24 y 25/9; n = 6 por grupo y sesión; saque de tres cuartos solo con la toma 02/01):
σ_w = desvío robusto intra-sesión; Δ = |mediana s1 − mediana s2|; consistente si Δ ≤ σ_w.

| Grupo | (i) Separación cadera-hombro máx.: medianas s1 · s2 (°) | σ_w (°) | Δ (°) | p perm. | (ii) Instante del pico del torso desde la máx. separación: medianas s1 · s2 (ms) | σ_w (ms) | Δ (ms) | p perm. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Drive · perfil | 30,6 · 24,6 | 3,14 | **6,03 (no)** | **0,044** | −166,7 · −10,4 | 37,1 | **156,3 (no)** | **0,050** |
| Drive · tres cuartos | 28,9 · 28,0 | 2,84 | 0,93 | 0,78 | −179,2 · −179,2 | 26,3 | 0,0 | 1,00 |
| Revés · perfil | 28,1 · 26,7 | 2,84 | 1,38 | 0,58 | **no auditable** (censura: 5 de 12 en el borde de la ventana; bruto Δ 6,25 ms, p 0,87) | — | — | — |
| Revés · tres cuartos | 40,4 · 43,2 | 2,85 | 2,75 | 0,074 | −245,8 · −227,1 | 26,3 | 18,8 | 0,49 |
| Saque · perfil | 25,7 · 23,9 | 2,96 | 1,86 | 0,59 | −54,2 · −93,8 | 40,2 | 39,6 | 0,066 |
| Saque · tres cuartos | 30,1 · 32,8 | 2,98 | 2,71 | 0,17 | −39,6 · −47,9 | 13,9 | 8,3 | 0,43 |

- **Un solo grupo con señal de diferencia entre sesiones en las dos métricas: drive de perfil** (sin corrección por las 6 comparaciones). La diferencia de tamaño del torso en píxeles entre sesiones fue 1,1 %: no es un cambio de encuadre grueso.
- **Calibración del umbral:** con n = 6 y ningún cambio real, la regla Δ ≤ σ_w da "consistente" solo el 75,6 % de las veces por azar (simulación, decisión 014): el umbral del 75 % coincide con lo esperado por azar. Por eso se informa también la lectura calibrada.
- **La métrica (ii) depende del tiempo** y se midió con el corpus horneado (intervalos ×0,5): hay que recalcularla con el tiempo real (pendiente). La métrica (i) no depende del tiempo.
- **Qué no se afirma** (decisión 012): que el sistema detecte un cambio real de técnica.

### 2.7 El pico del brazo, golpe por golpe — **FIRME (conteo y visibilidad) · PROVISORIO (causa física)**

Las 76 repeticiones del Paso B medidas con el motor actual (regla de cobertura del 75 %) y sin ella (motor 0.5.0). Archivos: `docs/resultados/brazo-por-golpe-13-10.json`, `codo-ventana-saque-trescuartos.json`, `brazo-por-golpe.md` (13/10/2026).

| Grupo | Repeticiones | Sin pico del brazo, motor actual (≥ 0.5.1) | Sin pico del brazo, motor 0.5.0 |
| --- | --- | --- | --- |
| **Todo el corpus** | 76 | **52 (68 %)** | **7 (9 %)** |
| Saque · tres cuartos | 18 | **18** | 2 |
| Saque · perfil | 11 | 9 | 1 |
| Drive · perfil | 12 | 12 | 2 |
| Drive · tres cuartos | 12 | 12 | 1 |
| Revés · perfil | 11 | 1 | 1 |
| Revés · tres cuartos | 12 | 0 | 0 |

- **Saque de tres cuartos, ventana de ±0,3 s alrededor del pico del tronco (145 fotogramas), mediana de las 18 repeticiones:** confianza del hombro dominante ≥ 0,5 el **100 %** de la ventana; del **codo** dominante el **41 %**; **0 %** en la primera mitad (el armado del golpe; en la repetición mirada fotograma a fotograma la confianza cruda va de 0,00 a 0,27) y **82 %** en la segunda; muñeca 57 %.
- **No es un caso de borde:** en las 52 repeticiones que pierden el brazo, la cobertura medida va del 6 al 59 % y **ninguna** queda entre el 60 y el 75 %. Bajar el piso no recuperaría ni una repetición.
- **El motor anterior (0.5.0) reportaba un pico del brazo en 69 de 76** repeticiones, pero era el máximo de la fase posterior al pico del tronco, la única en que el codo se veía: un máximo parcial presentado como del golpe completo. La regla de cobertura lo retiró.
- **Decisión de Valentín:** el brazo queda "**no medido**" con su motivo en palabras simples, **sin máximo parcial** (un dato que parece el pico del brazo y no lo es sería un dato equivocado presentado como bueno).
- **Lado de grabación.** **La cámara estuvo siempre a la izquierda del jugador, el lado no dominante** (jugador diestro; confirmado por Valentín el 13/10/2026; decisión 013): el brazo dominante queda del lado
  **lejano** a la cámara y **el torso lo tapa en el armado del golpe**. Es una condición del **lado de grabación**, no solo del encuadre: en el revés, donde el giro del cuerpo expone el brazo dominante a la
  cámara, el codo se ve (cobertura ≈ 1,0; 1 de 11 y 0 de 12 sin pico). Es la lectura que mejor explica los datos —el codo no se ve justo en el armado, la fase más lenta, mientras el hombro se ve siempre—; la
  decisión 013 dejaba abiertas el desenfoque y la autooclusión, y **no se contrastó grabando del lado de la raqueta** (trabajo futuro, §7.3).
- **Hallazgo redactado para el capítulo** (versión del 13/10 de `brazo-por-golpe.md`): con la cámara del lado no dominante, "el pico de velocidad angular del brazo dominante no se pudo medir en el 68 % de los
  golpes (52 de 76): 18 de 18 en el saque de tres cuartos, 12 de 12 en el drive de perfil y en el de tres cuartos, 9 de 11 en el saque de perfil y 1 de 11 y 0 de 12 en el revés"; el brazo que golpea queda del
  lado lejano y el torso lo tapa en el armado: **una condición del lado de grabación, no solo del encuadre**.

### 2.8 Detección del encuadre (D, decisión 035) — **PROVISORIO**

El encuadre lo declara el usuario y de él depende qué grupo se aplica; en la prueba de producción del 12/10 un saque de tres cuartos (`IMG_6391`) se subió como perfil. D contrasta lo declarado con lo visto: el **giro de la línea de hombros** en la preparación (de 0,8 a 0,3 s antes del pico del tronco).

| Medida | Valor | Fuente |
| --- | --- | --- |
| Giro de hombros, saque de perfil | **26–42°** (mediana 35°), 22 saques | `paso-b-saque.md`; `engine/encuadre.py` |
| Giro de hombros, saque de tres cuartos | **50–83°** (mediana 56°) | ídem |
| Umbrales en producción | perfil ≤ 42°, tres cuartos ≥ 50°, entre los dos no se afirma nada | `engine/encuadre.py` |
| El golpe del celular que parecía contradecir al Paso B | giro 59° (dentro de tres cuartos); archivo del 25/9 15:23:05 = hora de `IMG_6391`; Δ reproducido = +12,5 ms | `paso-b-saque.md` §2 |
| Verificación sobre el corpus | las **28 repeticiones válidas del saque** se clasifican en el encuadre con que se grabaron: **0 avisos falsos, 0 sin afirmar** | decisión 035 |
| La apertura de hombros / largo del tronco (primera idea) | **no sirve**: medianas 0,23 (perfil) y 0,15 (tres cuartos), con el golpe nuevo en 0,11 | `paso-b-saque.md` |

**Por qué PROVISORIO:** el umbral se calibró con los mismos saques sobre los que se verificó (consistencia, no validación independiente); un jugador; **solo con la cámara a la izquierda del jugador** (el cálculo toma
el valor absoluto del giro, así que no distingue el signo, pero no se verificó con la cámara del otro lado); **solo calibrado para el saque** (drive y revés, pendiente); detecta una discrepancia **gruesa**, no mide el ángulo de la cámara; pide ≥ 0,8 s de preparación antes del pico. **No bloquea la carga**: avisa y retira el veredicto.

### 2.9 Recortes del corpus para la Evolución de la demo — **FIRME (los recortes) · PENDIENTE (verlos en pantalla)**

**Decisión de Valentín (13/10):** no depender de grabar; la Evolución de la demo se arma con los originales del corpus (saque en tres cuartos, 24/9 y 25/9), recortados sin recodificar (`ffmpeg -c copy`).

| Qué | Valor |
| --- | --- |
| Recortes | **18**: 6 de `IMG_6376` (24/9, toma 01), 6 de `IMG_6392` (25/9, toma 02b) y 6 de `IMG_6393` (25/9, toma 02c) |
| Verificación, 18 de 18 | cada fotograma existe en el original con la misma marca de tiempo; ninguno de la ventana falta; decodifica sin errores; pesa menos de 50 MiB (máximo **49,2 MB**) |
| Tasa real de los recortes | **199,3 a 201,1 fps** |
| El motor los lee como captura real | probado con 2 recortes (el motor completo no se corrió sobre los 18 en esa PC) |
| Subidas a producción y procesadas | las dos sesiones (24/9 y 25/9; 6 golpes cada una según el protocolo) con el motor 0.5.3, según la bitácora |
| Reproducible | `backend/app/recortar_evolucion.py`; carpeta **fuera del repositorio** |

**Límites a declarar:** son las mismas dos sesiones con las que se validó el Criterio 3 (no es una validación independiente) y un solo jugador. Alcanza para mostrar el sistema funcionando sobre datos reales con trazabilidad, no para probar nada nuevo.
**Pendiente:** ver la pantalla de Evolución con esas dos sesiones (hoy solo se miró con una serie sintética) y comparar producción contra Paso B (control cruzado previsto en `docs/protocolo-sesiones-evolucion.md`).

---

## 3. Estado de cada resultado

| # | Resultado | Cifra principal | Estado | Por qué · qué lo cambiaría |
| --- | --- | --- | --- | --- |
| 1 | Tasa real del iPhone | 199,92–200,96 fps (16 originales) | **FIRME** | Marcas de tiempo de los archivos, reproducible. Un teléfono, un modo. La grabación "~170 fps" viene de Fotos ⓘ: **NO MEDIDO** en archivo. |
| 2 | Corpus horneado = ~120 fps con rampas | 120,1 fps (mediana) | **FIRME** | Alineación por contenido de 15 pares; 98 % de repeticiones en la meseta. |
| 3 | Camino de subida del iPhone | 100 fps por defecto; ~200 con "Actual" | **FIRME** | Medido con `inspeccionar_subidas` en 4 selectores y 3 formatos. Un modelo de teléfono. |
| 4 | Velocidad de inferencia | 3,57 fps | **PROVISORIO** | Una corrida, 80 fotogramas, motor 0.2.0, otra máquina. Superada en la práctica por las mediciones en contenedor. |
| 5 | Latencia en Free | 677,8 s (3,0 s de video) | **FIRME** como medición; **PROVISORIO** como estimador | n = 1 por tipo de archivo. |
| 6 | Latencia en Standard | 117,4 s y 146,7 s | **PROVISORIO** | n = 2, un golpe a la vez, un usuario, una instancia. |
| 7 | Espera en cola de una sesión | — | **NO MEDIDO** | El registro existe desde el 13/10; los datos de las dos sesiones del corpus ya subidas están en la base sin volcar. |
| 8 | Memoria pico en Standard | 748,4 MB | **PROVISORIO** | n = 1, medido en el log de Render; la diferencia con Windows no se investigó. |
| 9 | Paso A | 1 grupo cumple (saque de perfil) | **FIRME** (control) | Superado como medición por el Paso B; sirve de lado a lado con la original. |
| 10 | Paso B: conteos por gesto y encuadre | 76 repeticiones; 14 / 23 / 38 | **FIRME** | Pre-registrado, commit con árbol limpio, recalculado desde los JSON. |
| 11 | Dependencia del encuadre (Fisher) | saque p = 0,0002; drive p = 0,024; revés 0,18 | **FIRME** como hecho descriptivo · **PROVISORIO** como inferencia | Exploratoria: un jugador, repeticiones de una toma no independientes, sin corrección por comparaciones. **La causa: PENDIENTE** (hace falta una medición independiente de la pelvis). |
| 12 | Criterio 1 con los originales | 2/6 (medición), 0/6 (réplica) | **FIRME** la medición · **PROVISORIO** la lectura | El grupo que cumple es el sospechoso de sesgo; la repetibilidad no es exactitud. |
| 13 | Criterio 2 | rodilla 8,5° · codo 12,5° | **FIRME** (agregado 2D) · **PROVISORIO** (codo dominante) | n = 18, solo fotogramas con confianza ≥ 0,6 (región auditable), un observador; codo dominante n = 2; **no re-medido con motor ≥ 0.5.0**. |
| 14 | Criterio 3, métrica (i) | 9/11 (82 %) · 10/11 (91 %) | **PROVISORIO** | No depende del tiempo, pero n = 6, un jugador y un par de sesiones consecutivas. |
| 15 | Criterio 3, métrica (ii) | — | **PENDIENTE** | Hay que recalcularla con el tiempo real; revés de perfil, no auditable (censura de ventana). |
| 16 | Criterio 4 | 117–147 s · 678 s | **PROVISORIO** | Sin umbral; ver 5, 6 y 7. |
| 17 | Criterio 5 / I4 | — | **PENDIENTE** (no evaluado) | Sin pruebas con otros usuarios. |
| 18 | Brazo no medible | 52 de 76 (68 %) | **FIRME** (conteo y visibilidad del codo) · **PROVISORIO** (causa) | La atribución al lado de grabación (brazo lejano tapado por el torso) es la lectura que mejor explica los datos, pero no se contrastó grabando del lado de la raqueta (013). |
| 19 | Detección de encuadre D | 28/28, 0 falsos | **PROVISORIO** | Misma muestra para calibrar y verificar; solo saque; drive y revés pendientes. |
| 20 | Recortes de Evolución | 18/18 verificados | **FIRME** | Aritmética entera sobre las marcas de tiempo. |
| 21 | Evolución real, Perfil real, eliminar cuenta, PDF A4 | — | **PENDIENTE** | Solo en `respaldo-13-10`; sin verlos en pantalla real. |
| 22 | Correo propio (registro abierto, recuperar contraseña) | funciona (15/10) | **FIRME** en lo probado; **PROVISORIO** la entrega a otros proveedores | Lo probó Valentín con una cuenta de prueba; falta una prueba con otro proveedor y el límite de envíos por hora. |
| 23 | Costo marginal por análisis (USD) | — | **NO MEDIDO** | El Cap. 4 lo estimó en USD 0,13–0,25 con ocho minutos por video; hoy es USD 25/mes fijos de Render. |

---

## 4. Hallazgos no previstos en los Capítulos 1 a 4

Cada fila: qué se esperaba, qué se encontró, la decisión que lo documenta y dónde impacta. (Hay hallazgos anteriores a la 028 que el capítulo también puede necesitar: 011 el "brazo" es un proxy de orientación y no una rotación interna, sin comparación con Fleisig; 013 cobertura del brazo dominante; 014–015 salvedades del punto de decisión de la Etapa 4; 020 la declaración del modo de captura puede producir un error silencioso; 022 reintento y columnas protegidas.)

| # | Decisión (fecha) | Se esperaba | Se encontró | Impacta en |
| --- | --- | --- | --- | --- |
| 1 | **028** (7/10) | Que un recorte de Fotos conserva los fotogramas capturados | Llega a **100 fps** (H.264), no a 240; los 4 selectores entregan el mismo archivo; un saque de ~2 s entra en 201 fotogramas. Por ese camino un golpe a 240 fps **no es analizable**. | Cap. 4 (flujo de datos, RNF-01), Cap. 6 |
| 2 | **029** (9/10) | 240 fps de captura | **~200 fps reales** medios, irregulares (fotogramas perdidos casi periódicos, 16–17 %); el formato "Actual" los conserva y el por defecto no; el contenedor declara 479 fotogramas y 169,28 fps contando 81 de pre-roll (E0 lo leía mal); "escala conocida" del catálogo sin base. Pisos de aptitud con 5 % de tolerancia (114 y 57 fps). | Cap. 4 (RNF-01 y su plan de pruebas), Cap. 6, Cap. 7 |
| 3 | **030** (9/10) | Que el corpus fuera de 240 fps (y, por la 029, de ×1,2 de error) | **Es un remuestreo a ~120 fps con rampas**: velocidades ×2, ms ×0,5, resolución 8,3 ms; el corpus no cumplía RNF-01 ("lee la tasa real y nunca la asume"). La 029 había estimado ×1,2 y la 028 había afirmado que no había rampas: ambas **corregidas** por esta. | Cap. 4, Cap. 6, Cap. 7 (todo lo medido con el corpus) |
| 4 | **031** (9/10) | Veredicto del orden en los gestos con referencia | El único grupo con referencia (saque) y con Criterio 1 cumplido (perfil) daba "tronco primero" en 6 de 6: **todo saque de perfil saldría "desvío leve"**. Quedó "bloqueante de la demo" hasta validar. También corrigió la frase "el único grupo que cumple es drive, perfil" de la 029. | Cap. 7 |
| 5 | **032** (12/10) | Una sola regla de "ordenable" | El producto usaba 4,17 ms (un fotograma de la grilla) y la medición 8,33 ms: eran dos reglas. Unificada en 8,33 ms estricta; un revés de 8,3 ms dejó de ser ordenable. El motor había cambiado cuatro veces con el mismo sello 0.4.1. | Cap. 4 (RNF-02), Cap. 7 |
| 6 | **033** (12/10) | Reproductor sincronizado (tabla 4.7) y retención con video con esqueleto | Se entregó el video con esqueleto en cámara lenta fija y tres fotogramas clave; a 360 px "se veía mal" → 720 px, CRF 20 (~1,6 MB por 12 s). Memoria en Linux 748 MB. | Cap. 4 (4.3.3, 4.5.3) |
| 7 | **034** (12–13/10) | Dominio opcional ≈ USD 1,20 | Un Worker solo acepta un dominio propio si la zona DNS está **activa en Cloudflare**; el Student Pack deja un repositorio de GitHub Pages residual (se eliminó); Brevo autentica el dominio y la clave SMTP se generó después (resuelto el 15/10). | Cap. 4 (4.5), Cap. 5 |
| 8 | **035** (12–13/10) | Que el orden medido sea una propiedad del gesto | **Depende del encuadre en el saque**: perfil 0 cadera primero / 8 tronco primero; tres cuartos 7 / 0; p = 0,0002. El golpe de prueba "contradictorio" era un saque de tres cuartos declarado perfil. Se suspende el veredicto y se agrega D. | Cap. 7, Cap. 6 |
| 9 | **036** (13/10) | Veredicto en al menos algunos gestos | El patrón se repite en el **drive** (1/7 contra 3/0; p = 0,024) y el **revés** no es confiable con una sola cámara. **Ningún grupo emite veredicto.** Los grupos que cumplen el Criterio 1 son los sospechosos. | Cap. 4 (4.3.3 "auditoría de secuenciación"), Cap. 7, Cap. 6 |
| 10 | **037** (13/10) | "No auditable" para todo lo que no se ordena | Un empate a la resolución **es un golpe medido** ("sin diferencia medible"); "no auditable" queda para datos no confiables (R3). Un pico que falta lleva su motivo. | Cap. 4 (R3), Cap. 7 |
| 11 | bitácora del 13/10 y `brazo-por-golpe.md` | Pico del brazo medible en el saque y el drive | **68 % sin pico del brazo** (18 de 18 en saque de tres cuartos): el brazo dominante queda del lado lejano a la cámara y el torso lo tapa en el armado (condición del lado de grabación). El motor 0.5.0 mostraba un máximo parcial como si fuera del golpe. | Cap. 7, Cap. 6 |
| 12 | decisión 006 (27/8) | ~25 fps de inferencia (Cap. 4 §4.2.3 y §4.5.4) | **3,57 fps** medidos; el procesamiento asincrónico se vuelve más necesario. | Cap. 4 |

---

## 5. Estado de la hipótesis

**Cómo la citan los capítulos del repositorio** (el texto del apartado 1.4 no está acá): el Capítulo 3 (§3.3.2.9) dice que la hipótesis "habla de precisión suficiente para detectar la desincronización, no de si es 2D o 3D"; el Capítulo 4 (§4.5.2) agrega que la ejecución sobre dispositivos convencionales, sin GPU, es suficiente, y que un sistema que necesitara GPU "habría refutado su propia premisa". El Capítulo 4 (§4.3.2) la desglosa en cinco incertidumbres I1 a I5.

| Componente | Veredicto sugerido | Evidencia | Límite |
| --- | --- | --- | --- |
| **Ejecución en hardware convencional, sin GPU** | **Se confirma** | Corre en CPU: 117–147 s por golpe de 3–4 s en 1 CPU / 2 GB (USD 25/mes) | n = 2 en Standard; un golpe a la vez |
| **I2 · error angular < 20,6° en articulaciones proximales** | **Se confirma parcialmente** | Media rodilla 8,5° y codo 12,5° (2D, n = 18 por articulación) | p95 del codo 36,4° supera la meta; el codo dominante (n = 2) dio 27,2°; solo fotogramas con confianza ≥ 0,6; un observador; motor 0.4.1 |
| **I1 · orden repetible de los picos con una sola cámara, 120–240 fps** | **Se confirma parcialmente la repetibilidad; no se confirma el orden como medida** | 2 de 6 grupos cumplen el Criterio 1 en la medición (1a 0,83) y 0 de 6 en la réplica; el instante de cada pico se mide con ~5 ms de resolución | En tres cuartos más de la mitad de las repeticiones queda dentro de la tolerancia; **el orden de saque y drive cambia con el encuadre**, así que la repetibilidad que se observa puede ser la de un sesgo fijo |
| **I1 · cadena completa pelvis → torso → brazo** | **No se confirma** | El pico del brazo no se pudo medir en 52 de 76 repeticiones (68 %); 18 de 18 en saque de tres cuartos | Cámara del lado no dominante (brazo dominante lejano, tapado por el torso en el armado); no se probó el otro lado |
| **I3 · comparar al jugador consigo mismo** | **Se confirma parcialmente** | 9 de 11 combinaciones (82 %) por la regla original y 10 de 11 (91 %) por la calibrada; σ intra-sesión de la separación cadera-hombro ≈ 2,8–3,1° | Métrica (ii) por recalcular; n = 6 por sesión; **un jugador y dos sesiones consecutivas**; un cambio real de técnica no se indujo ni se detectó |
| **Núcleo: detectar la desincronización de la cadena cinética con una cámara** | **No se confirma con este material** (el sistema deja de emitir el juicio) | El orden cadera → tronco depende del encuadre y no se puede decir cuál mide bien | Sin referencia independiente de la pelvis; un jugador; el resultado no refuta el orden esperado de la literatura: **delimita lo que este instrumento puede afirmar** |
| **I5 · latencia tolerable** | **Medida, sin umbral** | Ver §2.3 | El umbral lo debían definir los usuarios |
| **I4 · utilidad percibida** | **No evaluada** | — | Sin pruebas con otros usuarios |

**Lectura para el capítulo, sin exagerar ni minimizar:**

- Lo que **sí** se construyó y se midió: un sistema que, desde un celular y sin GPU, entrega por golpe **mediciones trazables** (ángulos con su error, separación cadera-hombro, instantes de los picos con su resolución y su confianza), dice **cuándo no puede medir y por qué**, y permite comparar al jugador **consigo mismo**.
- Lo que **no** se pudo sostener: que, con una sola cámara y este material, el **orden** cadera → tronco sea una medida confiable del movimiento. Es un resultado negativo con valor propio: los dos grupos que "pasan" el criterio de repetibilidad son los que cambian con el encuadre, y el sistema lo detectó y se retiró del juicio (R3: un dato equivocado presentado como bueno es peor que un dato faltante).
- Lo que **no** se debe afirmar: que el jugador tenga la cadera "tardía"; que el encuadre de tres cuartos sea el correcto (coincide con la literatura, pero elegirlo así sería elegir por el resultado); que el sistema detecta cambios reales de técnica; que los resultados generalicen más allá de un jugador diestro, un iPhone y un lugar.

**El valor del sistema sin veredictos** (`docs/ux/valor-sin-veredictos.md`, decisión 036): **medición + seguimiento del jugador consigo mismo en el mismo encuadre.** El argumento: el sesgo del estimador es **fijo por encuadre** (la misma cámara, desde el mismo lugar, le hace el mismo error a la misma persona), así que **al compararse contra uno mismo en el mismo encuadre, el sesgo se cancela**. Lo que queda es: (a) medir con trazabilidad (dato, confianza y error); (b) cuánto varía el jugador entre golpes de una sesión; (c) cuánto cambia de una sesión a otra, **contra su propia variación**. Vocabulario neutro (aumentó / disminuyó / se mantuvo; "no es mejor ni peor"), sin color de estado.
**Declarar con honestidad:** que el sesgo sea efectivamente constante entre sesiones es un **argumento, no una medición** (no hay referencia independiente); lo medido es que la separación cadera-hombro varía poco entre sesiones consecutivas del mismo encuadre (Criterio 3, métrica i) y que una diferencia de ~6° (drive de perfil) sí supera la variación habitual.

---

## 6. Desvíos respecto de lo planificado en el Capítulo 4

La lista viva de correcciones al capítulo, con la decisión que origina cada una, está en `docs/tesis/correcciones-pendientes-capitulo-4.md` (12 correcciones y 18 anotaciones para los capítulos 6 y 7). Resumen autocontenido:

| Tema | El Capítulo 4 decía | Lo construido o medido | Decisión · corrección n.º |
| --- | --- | --- | --- |
| Hosting del frontend | Vercel Hobby (USD 0), vistas previas por rama | **Cloudflare Workers** (donde el prototipo ya venía configurado), dominio propio | 026, 034 · 1 y 2 |
| Origen del frontend | Generado y mantenido con Lovable | Lovable para el prototipo inicial; **el repositorio es la única fuente desde el 7/10/2026** | 026 · 3 |
| Flujo de carga | La API genera la URL firmada de carga; el cliente sube con ella | El cliente sube **directo a Storage** con su sesión (RLS por carpeta); la lectura usa URL firmadas de 1 h | 025 · 4 |
| Superficie de la API | 7 operaciones | **3 según la corrección 5** (verificación de servicio, confirmación de carga y reintento: en el código, `GET /health` y `POST /analisis/{id}/procesar`, que cubre las dos últimas); el alta, el estado, el reporte y el listado son lecturas y escrituras directas a Supabase con RLS. Se agregó `GET /sesiones/{id}/consistencia` (en producción) y, solo en la rama de respaldo, `GET /evolucion` y `DELETE /cuenta` | 025 · 5 |
| Autenticación | Identidad verificada "en la API" | JWT de Supabase validado por **JWKS** y propiedad del video chequeada (la API usa `service_role`, que ignora RLS) | 025 · 7 |
| Estados de procesamiento | Incluye `descartado` y `parcial` final | `descartado` no existe; `fallido → encolado` acotado; reintento desde `parcial` pendiente | 022 · 6 |
| Esquema de datos | 7 tablas | **9 tablas**, `sesiones` agregada, permisos por columna | 018, 022 · 9 |
| Servidor de cómputo | 0,5 vCPU / 512 MB mínimo; 1–2 vCPU / 2 GB recomendado; "contenedor nivel inicial USD 7–25" | **Free medido: 0,1 CPU, 512 MB → no alcanza** (32 MB de margen; 11 min por golpe); Starter tiene la misma memoria; **Standard (1 CPU / 2 GB, USD 25/mes) desde el 12/10**; Free otra vez después de la defensa | 017, 023 · 8 |
| Tiempo por análisis | "ocho minutos por video"; costo marginal USD 0,13–0,25 | **117–147 s en Standard** (golpes de 3–4 s); 678 s en Free. Costo marginal por análisis: **NO MEDIDO** | 023 |
| Velocidad de inferencia | ~25 fps (§4.2.3 y §4.5.4) | **3,57 fps** en CPU (`model_complexity=2`) | 006 |
| Dominio | Opcional, ≈ USD 1,20 | `kinetiqtennis.me` por el Student Pack; renovación **NO VERIFICADA**; DNS en Cloudflare | 034 |
| Correo | No previsto como componente | SMTP propio con el dominio (el correo integrado de Supabase entrega 2 por hora y solo al equipo del proyecto): **componente agregado; funciona desde el 15/10/2026** | 027, 034 |
| Tasa de captura | "240 fps" en todo el capítulo; RNF-01 prueba con 30, 60, 120 y 240 fps | **240 nominales, ~200 reales**; el corpus propio es ~120 fps; agregar a RNF-01 el archivo convertido y el de fotogramas perdidos | 029, 030 · 10, 11, 12 |
| Estimación de pose | YOLOv8-Pose + elevación 3D como vía A; MediaPipe como vía B | **MediaPipe** por defecto, 3D directo, sin etapa de elevación (descartada); YOLOv8-Pose/ONNX previsto como alternativa, **no implementado** (según el contexto del proyecto, el objetivo específico 1 de la tesis nombra YOLOv8-Pose vía ONNX: cotejar su redacción) | 005 |
| Auditoría de secuenciación | "Comparación del orden observado contra el esperado y generación de alertas" | **Sin veredicto en ningún grupo**; solo registro (`sin_evaluar`), `sin_diferencia_medible` y `no_auditable`; sin alertas con umbral (falta referencia) | 031, 035, 036, 037 |
| Reproductor sincronizado | Video, esqueleto y curvas en el mismo eje | **Video con esqueleto en cámara lenta fija + 3 fotogramas clave**; sin reproductor sincronizado (tarea diferida) | 033 · 14 |
| Exportación del reporte | PDF con sello de versión | **Impresión del navegador** ("Guardar como PDF"); documento A4 con vista de impresión propia solo en la rama de respaldo; no se genera en el servidor ni se guarda | plan §8 |
| Política de retención | Original 7 días y luego solo el video con esqueleto | **No implementada** (tarea 7.6 diferida); el bucket `artefactos` aparte la deja lista; el usuario puede eliminar un golpe, una sesión o la cuenta (cuenta: solo en respaldo) | 033 |
| Segmentación de golpes | Marcado manual asistido dentro de un video | Una subida = un golpe (límite de 50 MB); la sesión agrupa golpes | 016 |
| Validación con usuarios (I4, Criterio 4 y 5) | Pruebas de usabilidad con usuarios | **Autovalidación**: grabaciones propias, sin otros usuarios (cambio de alcance del 7/10) | plan MVP §4 |
| Corpus de evaluación | Grabaciones propias a 240 fps | Mismas grabaciones, con la tasa corregida; **un jugador** | 029, 030 |

**Costos reales hoy (13/10/2026):** Render Standard **USD 25/mes** (el único costo recurrente); Supabase Free, Cloudflare (Workers y DNS) y GitHub en planes gratuitos; dominio sin costo el primer año; correo propio funcionando desde el 15/10 (Brevo, 300 correos por día según fuente secundaria; costo no verificado). **Costo acumulado de Render desde el 12/10: NO MEDIDO** (se factura por plan y tiempo; verificar en el panel).

---

## 7. Limitaciones, amenazas a la validez y trabajo futuro

### 7.1 Limitaciones (declarar en el Capítulo 6 y recordar en el 7)

1. **Un solo jugador** (el autor, diestro), un iPhone 15 Pro Max, un lugar, dos sesiones consecutivas (24 y 25/9/2026). Nada generaliza más allá de eso.
   **Todos los resultados de orden se midieron con la cámara del lado no dominante** (a la izquierda del jugador, en todos los videos; confirmado el 13/10/2026): el orden cadera-tronco, la separación, los
   ángulos, los Criterios 1 y 3, los Pasos A y B y la calibración del contraste de encuadre valen **para ese lado**. No se sabe qué darían con la cámara del lado de la raqueta.
2. **n pequeño:** 6 repeticiones por grupo y sesión (12 el saque de tres cuartos en la sesión 2). Las repeticiones de una misma toma **no son independientes**. Los p de Fisher son **exploratorios**, sin corrección por comparaciones (6 grupos × varias métricas).
3. **Sin medición independiente de la pelvis:** no hay referencia (marcadores, sensores inerciales, segunda cámara). El sistema dice qué mide en cada encuadre, no cuál es verdad.
4. **Resolución temporal:** ~5 ms por fotograma real a ~200 fps; tolerancia de "ordenable" 8,33 ms; **16–17 % de los puntos de la grilla de 240 Hz son interpolados** (un instante que cae en uno es una reconstrucción, con error acotado por el hueco, ≤ 6 ms). En tres cuartos más de la mitad de las repeticiones queda dentro de la tolerancia.
5. **Una cámara, un lado y 2D:** la pose es monocular (la profundidad la infiere el estimador); el brazo que golpea es el lejano a la cámara y el torso lo tapa en el armado; el codo dominante se ve entre el 0 y el
   82 % de la ventana según la fase. En consecuencia, **el codo que se mide es, en la mayoría de los fotogramas, el no dominante** (16 de las 18 mediciones del Criterio 2).
6. **Criterio 2:** plano de la imagen (2D), 18 fotogramas, solo donde el sistema es confiable (≥ 0,6: "vale para la región auditable"), un observador (error intra-observador 4,1°), codo dominante con n = 2; medido con motor 0.4.1.
7. **Ventana de ±300 ms anclada al torso:** puede **censurar** la métrica (ii) del Criterio 3 (revés de perfil: 5 de 12 en el borde exacto; excluido a mano) y condiciona qué picos se encuentran.
8. **Latencia:** un golpe a la vez, un usuario, una instancia, n pequeño; sin carga concurrente; la espera en cola no está medida.
9. **Sin pruebas con otros usuarios:** utilidad (I4, Criterio 5) y umbral de latencia no evaluados.

### 7.2 Amenazas a la validez

| Tipo | Amenaza | Qué se hizo |
| --- | --- | --- |
| **Interna (circularidad)** | **Las mismas dos sesiones** sirvieron para explorar, fijar umbrales, calibrar D (umbral de ~46° con 22 saques; verificación con 28) y medir los Criterios 1 y 3. La sesión 1 es "réplica exploratoria", no independiente. | Se rotularon así; la sesión 2 es el conjunto de medición; los criterios se **congelaron antes de medir** (decisión 014); el Paso A se pre-registró. **No hay una muestra independiente.** |
| **Interna (decisiones posteriores a ver datos)** | Override manual del revés de perfil (ii); suspensiones 035 y 036; unificación de tolerancia (032); controles del Paso A no pre-registrados. | Todo documentado con su fecha y motivo; los controles se informan todos, también los que no apoyan la hipótesis. |
| **Interna (selección)** | 8 repeticiones fuera del Paso B (2 en rampa, 6 de `IMG_6391` incompleto); el saque de tres cuartos pesa 18 de 76. | Declaradas; las 6 de `IMG_6391` se perdieron por un original incompleto. |
| **De constructo** | El "orden" es el de los picos de la velocidad angular **total** del vector (no el giro axial); el "brazo" es el vector hombro→codo, un proxy de orientación (no rotación interna; no comparable con Fleisig, decisión 011); el estimador devuelve profundidad inferida. | Control con giro axial y cortes fijos en el Paso A y B; el brazo se informa como dato, sin evaluar. |
| **Externa** | Un jugador, un teléfono, una iluminación, un solo lado de cámara (el no dominante), gestos de entrenamiento (no de partido). | R5: alcance declarado; el lado se registra en cada sesión (`lado_camara`) y la Evolución avisa si cambia. |
| **De conclusión** | n = 6, p exploratorios, regla del 75 % que coincide con el azar con n = 6. | Lectura calibrada (permutación) y todos los resultados informados. |
| **Instrumento** | La tasa real varía por grabación; el teléfono puede convertir el archivo; el formato "Actual" es necesario. | El motor lee la tasa del archivo, regulariza, cuenta lo interpolado y rechaza lo convertido. |

### 7.3 Trabajo futuro

- **Multivista:** grabar el mismo golpe a la vez desde perfil y desde tres cuartos (la prueba más limpia de la dependencia del encuadre). **Descartada por ahora: no hay un segundo teléfono.**
- **Cintas de color:** una medición independiente de la pelvis con un solo teléfono (cuatro colores en cresta ilíaca y acromion), que permitiría levantar la suspensión del veredicto grupo por grupo. **Registrada, sin diseñar** (cuántas repeticiones, criterio de acuerdo y qué levanta la suspensión se define si se decide hacerla).
- **Validación contra una referencia independiente** (marcadores, sensores inerciales o captura óptica) y **más de un jugador**, en más de un día y con niveles distintos.
- **Grabar del lado de la raqueta** (cámara a la derecha de un jugador diestro) en saque y drive, para medir el brazo dominante y contrastar la explicación del lado de grabación (decisión 013). **Salvedad:** cambia
  la comparabilidad con el corpus; esas sesiones serían un corpus aparte. Las sesiones nuevas opcionales para Evolución usan el mismo lado del corpus (izquierda).
- **Calibrar D para drive y revés** con las poses del Paso B; **Criterio 3 con el tiempo real**; revisar la columna (b) de `RESPALDO_POR_GRUPO` con las cifras del Paso B (el drive de perfil pasaría a cumplir con 1a 0,83; no cambia ningún veredicto porque la suspensión gana).
- **Ventana específica por gesto**, pre-registrada, para no censurar la métrica (ii).
- **Marca por pico del instante medido o reconstruido** y suma de la incertidumbre del hueco a la decisión de "ordenable".
- **Alertas con umbral con referencia bibliográfica** (E5.1), solo donde haya fuente; **YOLOv8-Pose/ONNX** y elevación 3D como vías alternativas; PDF generado en el servidor, retención de 7 días y reproductor sincronizado; validación de utilidad con entrenadores y kinesiólogos (I4, Criterio 5).

---

## 8. Qué falta antes de la demo (28–30/10) y antes de la defensa

### 8.1 Antes de la demo a los profesores (28–30/10/2026, decisión de Valentín)

Orden vigente del plan (`docs/plan-mvp-punta-a-punta.md` §8): pasos 1 a 6 hechos; restan el 7 y el 8. Núcleo restante ≈ 1,25 sesiones más las pruebas.

| # | Qué | Estado |
| --- | --- | --- |
| 1 | **Publicar los pasos 5 y 6** (hoy solo en `respaldo-13-10`): llevarlos a `main`, correr las pruebas, `git push origin main` (Render redeploya el servidor) y **republicar el frontend** (`bun run build` + `wrangler deploy`). Hacen falta las dos cosas: Evolución y Perfil llaman a `/evolucion` y `/cuenta`. | Pendiente de decisión de Valentín; **no se hizo** (`main` no se tocó) |
| 2 | **Probar en pantalla real:** (a) eliminar cuenta con una cuenta descartable (Storage queda sin la carpeta del usuario en los dos buckets y la cuenta ya no entra); (b) Evolución con las dos sesiones del corpus (los dos puntos, la variación, "se mantuvo" o "aumentó/disminuyó", el aviso de mezcla de versiones 0.5.3/0.5.4); (c) imprimir de verdad el PDF de un golpe y de una sesión (salto de página, imágenes, A4 vertical); (d) Perfil con una cuenta real; (e) Procesando en escritorio. | Pendiente (ninguno verificado) |
| 3 | ~~Correo propio~~ **Resuelto el 15/10/2026** (Brevo; registro, confirmación y "Olvidé mi contraseña" probados). Falta probar con una dirección de otro proveedor y configurar el alias de contacto de Privacidad. | Hecho · parte pendiente |
| 4 | **Revisar el texto de `/privacidad`:** es una declaración de Valentín (no se usa para publicidad ni se vende; no hay borrado automático). | Pendiente |
| 5 | **Paso 7: respaldo de la base con restauración probada de punta a punta** (Supabase Free no respalda; los datos del respaldo no van al repositorio). | Pendiente (0,75 sesión) |
| 6 | **Paso 8: ensayo de la demo** (un golpe por gesto subido; congelar). | Pendiente (0,5 sesión) |
| 7 | ~~Confirmar el lado de la cámara de las sesiones del corpus.~~ **Resuelto el 13/10/2026:** izquierda del jugador (no dominante) en todos los videos; las 7 sesiones subidas lo tienen declarado así y la mano dominante `derecha` (Anexo B, aviso 4). Las sesiones nuevas opcionales usan la izquierda. | Hecho |
| 8 | No cambiar el plan de Render ni reiniciar el servicio con un análisis en curso. | Regla |
| 9 | **Decidir qué lado recomienda la aplicación:** el esquema de encuadre de Cargar (`frontend/src/components/esquema-encuadre.tsx`) dibuja la cámara del lado de la raqueta de un jugador diestro, y el corpus es del lado contrario. No cambia ningún cálculo (el lado declarado no entra en el motor), pero un usuario que siga el dibujo grabaría del otro lado y no sería comparable con el corpus. | Pendiente (decisión de Valentín) |

### 8.2 Antes de la defensa (entrega final: 17/11/2026; MVP completo: 2/11; la fecha de defensa **no consta en el repositorio**)

**Mediciones y software (en el orden de Valentín, 13/10, `plan-mvp-punta-a-punta.md` §9):**

1. Calibrar D para drive y revés con las poses del Paso B (0,5–1 sesión).
2. Criterio 3 con el tiempo real: métrica (ii) (0,5 sesión de análisis más cómputo).
3. `RESPALDO_POR_GRUPO` (columna b) con las cifras del Paso B (0,25).
4. Cintas de color: **solo si hay tiempo**, prueba tentativa, sin diseñar.
5. Volcar los tiempos de cola y procesamiento de las sesiones del corpus y medir una sesión de 6 golpes en Standard (cierra el Criterio 4 con la espera en cola).
6. Decidir qué hacer con el Criterio 5 (validación exploratoria con un entrenador o kinesiólogo, o "no evaluado, trabajo futuro") y con el umbral del Criterio 4 (se informa sin umbral).
7. Decidir si se re-mide el Criterio 2 con el motor 0.5.x (hoy 0.4.1; el cálculo angular no depende del tiempo, pero la cadena de procesamiento cambió).

**Redacción:**

8. **Capítulo 4:** aplicar las 12 correcciones y los pendientes de redacción de las decisiones 006, 010–015, 018–020; reemplazar el marcador `[INSERTAR RESULTADOS DE LA MEDICIÓN DE CADA CRITERIO]` del apartado 4.3.4; reemplazar la captura pendiente del panel de Vercel y de Supabase (4.5.4) por Cloudflare y Supabase.
9. **Capítulos 6 y 7** (limitaciones y resultados) con este documento y las anotaciones 1–18 de `correcciones-pendientes-capitulo-4.md`; **Capítulo 5** con los costos reales de §6.
10. Capturas y evidencia de cada etapa del flujo (plan §4, semana 4).

**Operación:** Render en **Standard "siempre para la defensa"** (decisión 023) y volver a Free después; anotar el vencimiento anual del dominio y decidir si se renueva; congelar la versión que se defiende (motor, contrato y commit) y citarla en el capítulo.

---

## Anexo A. Dónde está cada cosa (por si el autor quiere cotejar)

| Tema | Archivo |
| --- | --- |
| Estado y cierre del 13/10 | `docs/bitacora.md` (primera entrada) |
| Resultados y cómo reproducirlos | `docs/resultados/README.md` |
| Paso A · Paso B · saque | `docs/resultados/paso-a-resumen.md`, `paso-b-resumen.md`, `paso-b-saque.md`, `paso-b-sesion-{1,2}.json` |
| Criterios 1, 2, 3 | `docs/resultados/criterio1-resumen.md`, `criterio2.json`, `criterio3.json` y `docs/decisiones/014-…`, `015-…` |
| Latencia y memoria | `docs/resultados/criterio4-latencia.md`, `e4.5-contenedor-tiempo-memoria.json`, `e2-velocidad-inferencia.json` |
| Tasa real y corpus | `docs/resultados/tasa-real-iphone-huella.json`, `corpus-real-alineacion.json`, `tasa-real-sensibilidad.json` |
| Brazo | `docs/resultados/brazo-por-golpe.md` y `-13-10.json`, decisión 013 |
| Decisiones 028 a 037 | `docs/decisiones/028-…` a `037-…` |
| Correcciones del Cap. 4 y anotaciones para el 6 y el 7 | `docs/tesis/correcciones-pendientes-capitulo-4.md` |
| Valor sin veredictos | `docs/ux/valor-sin-veredictos.md` |
| Plan y orden hasta la demo y después | `docs/plan-mvp-punta-a-punta.md` §8 y §9 |

## Anexo B. Avisos: inconsistencias del repositorio a resolver antes de citar

1. **Dos p de Fisher distintos para el saque.** Paso A (corpus horneado, 120,2 fps): 0 de 9 contra 6 de 9, **p = 0,009**. Paso B (originales): 0 de 8 contra 7 de 7, **p = 0,0002**. Son dos mediciones; citar la del Paso B como definitiva y la del A como control.
2. **"El único grupo que cumple el Criterio 1".** La decisión 029 y la nota 3 de las correcciones dicen que es `drive|perfil` (1a 0,83), cifra que corresponde a τ = 3; la tabla formal (014) a τ = 1 da **tres grupos** y a τ = 2 y 3 **dos**. La decisión 031 lo corrigió. Citar siempre la tabla, con su τ y su motor.
3. **Fechas.** Las entradas de la bitácora rotuladas "2026-10-14" (tarde, mañana y madrugada) y las menciones "14/10" de `plan-mvp-punta-a-punta.md` (§8, filas 5 y 6: "Hecho el 14/10"), `brazo-por-golpe.md` ("Decisión (Valentín, 14/10/2026)") y `especificacion-frontend.md` ("decisión de Valentín, 14/10/2026", tres veces) corresponden a trabajo cuyos commits son del 13/10 (01:59 a 04:20, −03:00). En esta sesión se corrigió solo la entrada de cierre de la bitácora (su título y una mención dentro de ella); las demás quedan para que Valentín decida.
4. **Lado de la cámara: RESUELTO el 13/10/2026.** Valentín confirmó que en todos sus videos la cámara estuvo **a su izquierda (lado no dominante; es diestro)**, como decía la decisión 013 (medido con la `z`
   relativa de los hombros en 74 de 84 clips). Verificado en la base: las **7 sesiones** subidas (24 y 25/9) tienen `lado_camara = izquierda` y el atleta `mano_dominante = derecha`. Se corrigieron los documentos
   que decían "del lado de la raqueta" o "del lado del brazo dominante" (`protocolo-grabacion.md`, `protocolo-sesiones-evolucion.md`, `protocolo-saques-tres-cuartos.md`, y la "Implicancia" de
   `brazo-por-golpe.md`, ya reformulada). **Queda un cartel de la aplicación que dibuja la cámara del lado de la raqueta** (esquema de encuadre en Cargar): ver §8.1, punto 9.
5. **"Oclusión real" frente a "causa no separada".** `brazo-por-golpe.md` concluye "oclusión real, no una regla demasiado estricta" (lo que descarta es que la regla del 75 % sea el motivo); la decisión 013 dejaba abiertas el desenfoque y la autooclusión. Tras confirmar el lado de la cámara (13/10), la lectura vigente es que el brazo dominante queda del lado lejano y el torso lo tapa en el armado; el capítulo debe decir qué se afirma: **el estimador no ve el codo en el armado del golpe**, y que la explicación por el lado de grabación es la que mejor encaja, **sin haberla contrastado** grabando del lado de la raqueta.
6. **D calibrado con 22 saques y verificado con 28.** El umbral de ~46° sale de 22 saques; las 28 repeticiones válidas del saque son la verificación de consistencia. Es la misma muestra.
7. **La decisión 037 dice "Decide Valentín" sobre el brazo; ya decidió** (queda "no medido", sin máximo parcial). El texto de la 037 no se actualizó.
8. **"76 repeticiones válidas" frente a 75.** El Paso B midió 76 repeticiones y 75 son válidas para el par cadera-tronco (una de saque de perfil de la sesión 1 no lo es); `brazo-por-golpe.md` llama "válidas" a las 76.
9. **Tasa equivalente del corpus:** 120,1 fps (mediana de los pares del JSON) y 120,2 fps (valor usado en el Paso A y en los documentos); diferencia sin consecuencias, pero conviene citar una.
10. **Fecha del Paso B.** Los documentos lo fechan "13/10/2026"; el commit `7c9535c` es del 12/10 21:39 (−03:00) y el JSON de la sesión 2 se generó el 13/10 02:51 UTC (12/10 23:51 −03:00).
