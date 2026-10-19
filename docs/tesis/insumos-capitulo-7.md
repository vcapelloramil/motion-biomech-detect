# Insumos para el Capítulo 7 (resultados): el sistema y las mediciones al 19/10/2026

**Para quién es:** otro chat que redacta el capítulo y **no ve el repositorio**. Este documento es autocontenido: todas las cifras están acá, con su unidad, su fecha y el archivo de donde salen
(rutas relativas a la raíz del repositorio `motion-biomech-detect`; los videos y el corpus **no** están en el repositorio).

**Corte original:** 13/10/2026 (commit `60751d8`). **Actualizaciones:** 15/10 (pasos 5 y 6 y motor 0.5.5 publicados), 16/10 (decisión 038, etapa 1) y **19/10/2026 (esta versión; `origin/main` = `08ccec1`)**.
**§9 resume qué cambió desde el 13/10 y qué cifras se modificaron (antes → después); §10 resuelve o declara NO MEDIDO / NO CONSTA los pendientes del Capítulo 7.** Lo marcado con fecha del 15/10 en adelante es posterior al corte original.
Para el Capítulo 8 (aportes, recomendaciones, mejoras pendientes): `docs/tesis/insumos-capitulo-8.md`. Correcciones del Capítulo 4: `docs/tesis/correcciones-pendientes-capitulo-4.md`.
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
10. **Estado al 19/10:** los pasos 5 y 6, el correo propio y el respaldo con restauración están hechos y probados en lo que se pudo; la **detección automática del tipo de golpe y del encuadre no cumple el criterio pre-registrado** (§2.10); la espera en cola de una sesión de 6 golpes se **midió** (19,6 min; §10.8); el clip `IMG_6376`, subido como «perfil», es un **saque de tres cuartos** (§10.1). Falta: ensayo, limpieza y nueva subida con el motor congelado (24/10) y el PDF impreso en papel (§8).

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
10. **Publicado el 15/10/2026:** Perfil real (nombre, rol, jugadores, "Descargar mis datos"), **eliminar la cuenta** con sus archivos, **Evolución real** (la serie de sesiones del mismo jugador, gesto y encuadre) y el **PDF como documento A4**.

**Qué produce el reporte real hoy:** solo `sin_evaluar` ("Solo registrado"), `sin_diferencia_medible` y `no_auditable`. Los estados `correcto`, `desvio_leve` y `alerta_de_carga` siguen existiendo en el contrato pero, con el orden suspendido y sin umbrales con referencia, ningún reporte los emite (decisión 036).

### 1.3 Qué está en producción (y cuándo llegó)

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
| **Paso 5:** Perfil real, "Descargar mis datos", `DELETE /cuenta` (archivos de ambos buckets primero) | `main` (desde el 15/10) | `5b1dc01` · 13/10 03:50 | **Sí**, desde el 15/10; **"Eliminar mi cuenta" probado** con una cuenta de prueba |
| **Paso 6:** Evolución real (`GET /evolucion`, pantalla `/evolucion`) y PDF como documento A4 | `main` (desde el 15/10) | `0bbc1df` · 13/10 04:17 | **Sí**, desde el 15/10; Evolución y PDF probados en producción |
| Bitácora de cierre del día | `main` (desde el 15/10) | `60751d8` · 13/10 04:20 | — |

- Hasta el 14/10 `main` y `origin/main` estaban en `56a13c1` y la rama de respaldo no se desplegaba. **Desde el 15/10 `main` = `a377e71`.** Los pasos 5 y 6 **no agregan migraciones** (verificado: `supabase/` sin cambios).
- **Pruebas automáticas, corridas el 19/10/2026 sobre `08ccec1`:** servidor, suite rápida (`pytest -m "not slow"`) **620 passed** (106 deselected; incluye las pruebas contra el Supabase real); frontend, `bun test` **122 pass**. (El 13/10 la bitácora reportaba 589 y 106; 569 y 84 en `56a13c1`.)
- **Lo publicado después del 15/10** (motor 0.5.5, esquema de encuadre, instrucciones por dispositivo, navegación del celular): ver §9.1.
- **Probado en producción el 15/10/2026** (Valentín, con el frontend republicado): Perfil, Evolución y el PDF del golpe y de la sesión funcionan y se descargan; **"Eliminar mi cuenta" funcionó con una cuenta de prueba** y, verificado en la base,
  no quedaron filas ni archivos de esa cuenta en Postgres ni en Storage. Sin verificar todavía: Evolución con las sesiones del corpus subidas con el motor 0.5.5 (se vuelven a subir después del congelamiento del motor) y el PDF impreso en papel.

### 1.4 Versiones del motor y del contrato (RNF-02: el reporte lleva su versión)

| Motor | Qué cambia | Contrato |
| --- | --- | --- |
| 0.4.1 | Sello puesto en cuatro commits entre el 9 y el 12/10 (los reportes de esos días se distinguen por el contrato 1.0 a 1.2, no por el sello). Es el motor de las mediciones formales de los Criterios 1, 2 y 3. | 1.0–1.2 |
| 0.5.0 | Lee la tasa real de las marcas de tiempo; regularización a 240 Hz; tolerancia única 8,33 ms; artefactos. | 1.3 |
| 0.5.1 | Regla de cobertura: el pico de un segmento no se reporta si se midió menos del 75 % de la ventana. Magnitudes articulares. Video a 720 px. | 1.3 |
| 0.5.2 | Decisión 035: el saque no emite veredicto; contraste del encuadre declarado con el visto. | 1.3 |
| 0.5.3 | Decisión 036: ningún grupo emite veredicto. | 1.3 |
| 0.5.4 | Decisión 037: el empate es "golpe medido"; el pico que falta lleva su motivo. | 1.4 |
| 0.5.5 | Nota neutra cuando la cámara estuvo del lado de la mano dominante (lado todavía no validado; decisión 013). *(15/10/2026; en producción: `/health` = 0.5.5 verificado tres veces seguidas.)* | 1.4 |

---

## 2. Resultados medidos

Cada fila: número, unidad, fecha y archivo. El estado de cada uno está marcado aquí y consolidado en §3.

### 2.1 Tasa real de captura del iPhone — **FIRME**

El iPhone graba "a 240 fps" nominales; entrega ~200 fps reales, con fotogramas perdidos casi periódicos.

| Medida | Valor | Fecha | Archivo de origen |
| --- | --- | --- | --- |
| 16 originales HEVC del corpus: tasa real media por archivo | **199,92 a 200,96 fps** (mediana 200,62); nominal 239,98; **16,3 a 16,7 %** de fotogramas perdidos | 9/10/2026 | `docs/resultados/corpus-real-alineacion.json` (`reales`); decisión 030 |
| Un recorte de Archivos (huella de intervalos) | **198,87 fps** media; 17,13 % perdidos; 398 fotogramas visibles + 81 de pre-roll oculto; intervalos: 356 de 1 período y 41 de 3 | 9/10/2026 | `docs/resultados/tasa-real-iphone-huella.json`; decisión 029 |
| Saque subido por el flujo completo (`IMG_6376`; **declarado «perfil», es de tres cuartos**: §10.1) | 199,6 fps (16,8 % perdidos); 98 de 597 puntos interpolados (16,4 %) | 9/10/2026 | `docs/tesis/correcciones-pendientes-capitulo-4.md`, nota 8 |
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
| 1 | 9/10/2026 | `IMG_6376` (saque declarado «perfil»; **es de tres cuartos**, §10.1; 2,5 s) | Render **Free**, complexity 2 | 501 | **~9 min** | Manual (Valentín); las columnas de tiempo aún no existían |
| 2 | 12/10/2026 | `IMG_6395` (revés, tres cuartos, 3,0 s) | Render **Free** | 599 | **677,8 s** (cómputo 676,6 s) | Base: `encolado_en → fin_procesamiento_en` |
| 3 | 12/10/2026 noche | Recorte real de `IMG_6395` (3,1 s, 27 MB) | Render **Standard**, motor 0.5.0, con artefactos | 626 | **117,4 s** (cómputo 116,0 s) | Base, con la API de producción y un usuario de prueba (luego borrado) |
| 4 | 12/10/2026 noche | Saque de perfil desde el celular (~4,0 s) | Render **Standard**, motor 0.5.0, con artefactos | 805 | **148 s** (Valentín); **146,7 s** en el log | Log de Render (`procesar_video`) |

- **Free contra Standard, mismo tipo de archivo (filas 2 y 3):** 677,8 s contra 117,4 s = **5,8 veces más rápido**. Por fotograma: ~1,13 s contra ~0,19 s (derivado de las filas 2, 3 y 4: 676,6/599; 116,0/626; 146,7/805). **La latencia escala con los fotogramas.**
- Otros datos de Free (decisión 017/023): **414,1 s** y RSS pico **480,4 MB** para 360 fotogramas (2/10/2026). Referencia local (Docker, simulando el plan, 29/9): 512 MB/0,5 CPU 176–185 s; 1 GB/1 CPU 91,3 s; 2 GB/2 CPU 81,0 s (`e4.5-contenedor-tiempo-memoria.json`).
- **Artefactos** (fotogramas clave + video con esqueleto): +6,8 % de tiempo en la PC de desarrollo (9,1 s sobre 134 s); **10,2 s** en Render Standard (fila 4).
- **Procesamiento contra espera en cola:** desde el 13/10 se registran por separado (`inicio − encolado` = espera en la cola; `fin − inicio` = procesamiento, que es lo que mide el Criterio 4). Las filas 1 a 4 son de **un golpe a la vez**, sin cola. **La espera en cola de una sesión de varios golpes se midió el 19/10/2026 (§10.8):** sesión de 6 golpes del 24/9, **19,6 min** de punta a punta (procesamiento 193,5 s por golpe, mediana); la del 25/9, encolada detrás de la otra, **39,5 min**; el último de 12 golpes esperó 33,7 min. La estimación anterior (~12 min en Standard) era baja. En Free (estimación, 6 × 414 s) ~41 min: **no medido**.

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

### 2.10 Detección automática del tipo de golpe y del encuadre (decisión 038, etapa 1, 16/10/2026) — **FIRME (el resultado negativo) · PROVISORIO (la lectura)**

**Qué se hizo:** reglas simples sobre la pose (posición de "trofeo" para el saque; giro neto de hombros, distancia entre muñecas y lado del eje de los hombros para drive contra revés; el contraste D por tipo de golpe para el encuadre), fijadas **antes** de medir, con los cortes ajustados en una sesión y evaluados en la otra (24/9 ↔ 25/9) sobre las **76 repeticiones** del Paso B. Criterio pre-registrado: error ≤ 5 % entre los determinados y ≤ 20 % de "no determinado". Detalle y matrices: `docs/resultados/deteccion-038-etapa1.md`; arnés `backend/app/medicion_deteccion.py` (commit `fee1003`).

| Campo | Determinados | Error (Wilson 95 %) | No determinado | ¿Cumple? |
| --- | --- | --- | --- | --- |
| Tipo de golpe | 1 de 76 | 100 % (1 de 1) | **98,7 %** | **No** |
| Encuadre, con el tipo verdadero | 35 de 76 | 14,3 % (6,3–29,4 %) | 53,9 % | **No** |
| · saque / drive / revés | 18 / 13 / 4 | 0 % / 15,4 % / 75 % | 37,9 % / 45,8 % / 82,6 % | No |
| Encuadre, con el tipo detectado | 6 de 76 | 66,7 % (30–90 %) | 92,1 % | **No** |

**Lectura:** ningún campo cumple. La regla del saque se pre-registró para la preparación y en este jugador la muñeca no está sobre la nariz ahí (la altura llega en el contacto); el brazo dominante queda lejos de la cámara y falta el dato en 32 de 76 repeticiones. Drive contra revés:
dos candidatas separan una sesión pero ninguna la otra (un valor atípico por clase rompe los extremos). El contraste D del encuadre funciona para el saque, **no distingue el encuadre del drive y va invertido en el revés**, en línea con el hallazgo del Paso B de que el revés no sigue el patrón de los otros gestos.
Un análisis posterior **post hoc** (optimista, no cuenta) da ~10 % de error para saque contra resto y para drive contra revés: tampoco llega al 5 %.

**Límites:** un jugador diestro, un teléfono, dos sesiones consecutivas, cámara siempre a la izquierda, tres cuartos por delante, una sola técnica de revés (a una o dos manos: no registrado), etiquetas del mismo autor (cinco revés de perfil con la muñeca alta en el contacto sin revisar a mano). No se midió el lado de la cámara (el corpus es de una sola clase). **No generaliza a otros jugadores.** Lo que cambiaría la lectura: una sesión nueva con saque, drive y revés para validar reglas fijadas de antemano.

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
| 7 | Espera en cola de una sesión de 6 golpes (Standard) | 19,6 min y 39,5 min (§10.8) | **FIRME** como medición · **PROVISORIO** como estimador | n = 2 sesiones, motor 0.5.3, un usuario, cola de a un golpe; la segunda esperó detrás de la primera; golpes de 4,8–7,8 s. |
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
| 21 | Evolución real, Perfil real, eliminar cuenta, PDF A4 | funcionan (15/10) | **FIRME** en lo probado; **PROVISORIO** Evolución con datos finales | Publicados el 15/10 (`main` `a377e71`). Probados por Valentín en producción; eliminar cuenta, verificado en la base (0 filas y 0 archivos). Evolución se vuelve a mirar tras la nueva subida del corpus. |
| 22 | Correo propio (registro abierto, recuperar contraseña) | funciona (15/10) | **FIRME** en lo probado; **PROVISORIO** la entrega a otros proveedores | Lo probó Valentín con una cuenta de prueba; falta una prueba con otro proveedor y el límite de envíos por hora. |
| 23 | Costo marginal por análisis (USD) | — | **NO MEDIDO** | El Cap. 4 lo estimó en USD 0,13–0,25 con ocho minutos por video; hoy es USD 25/mes fijos de Render. |
| 24 | Detección automática de tipo de golpe y encuadre (038, etapa 1) | ningún campo cumple (tipo 98,7 % sin determinar; encuadre 14,3 % de error y 53,9 % sin determinar) | **FIRME** el resultado negativo · **PROVISORIO** la lectura | Reglas pre-registradas, partición por sesión, commit con árbol limpio; un jugador y dos sesiones. Lo cambiaría una sesión nueva de validación. |
| 25 | Origen y encuadre de los archivos subidos a mano | `IMG_6376` (declarado perfil) es un saque de tres cuartos; `IMG_6395` e `IMG_6380` coherentes; `IMG_6391` ya conocido | **FIRME** | Marca de captura del archivo y giro de hombros 52,9° (§10.1); dos de cinco archivos con el encuadre equivocado. |
| 26 | Pruebas de requisitos no funcionales | RNF-03: 17 passed (fase cero 0 ms contra +70,8 ms del filtro de una pasada); RNF-07: 28 passed; RNF-05 y Playwright: no existen | **FIRME** lo corrido · **NO REALIZADO** lo que falta | §10.4. |
| 27 | Cuotas de Cloudflare Workers (gratis) | 100 000 solicitudes por día, 10 ms de CPU por solicitud | **FIRME** (fuente oficial) · consumo real **NO MEDIDO** | §10.7. |

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

La lista viva de correcciones al capítulo, con la decisión que origina cada una, está en `docs/tesis/correcciones-pendientes-capitulo-4.md` (40 filas —las 12 originales, las 23 del 15/10 y 5 nuevas del 19/10— y 22 anotaciones para los capítulos 6 y 7). Resumen autocontenido:

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
| Objetivo específico 4 (análisis comparativo visual y contraste con modelos de referencia) | Comparar la ejecución del jugador con modelos de referencia para corregir errores y mejorar el rendimiento | **Comparación del jugador consigo mismo** (Evolución, vista de sesión); **sin modelos de referencia**, sin «corregir» ni «mejorar» (R2, R5; decisiones 035 y 036). Declarado por Valentín el 19/10/2026 | OE4 · CLAUDE.md R2, R5 · 036 |
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
8. **Latencia:** un golpe a la vez (y dos sesiones de 6 golpes encoladas por un solo usuario, §10.8), una instancia, n pequeño; sin carga concurrente de varios usuarios.
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

Orden vigente del plan (`docs/plan-mvp-punta-a-punta.md` §8): **pasos 1 a 7 hechos; resta el 8 (ensayo)**. Estado al 19/10: ver la columna «Estado»; el calendario de la bitácora del 16/10 (congelar el motor el 24/10; limpieza y nueva subida el 25–26/10; ensayo el 26–27/10; demo 28–30/10) **no tiene registros posteriores**.

| # | Qué | Estado |
| --- | --- | --- |
| 1 | ~~**Publicar los pasos 5 y 6**~~ **Hecho el 15/10/2026** (antes eran solo de `respaldo-13-10`): llevarlos a `main`, correr las pruebas, `git push origin main` (Render redeploya el servidor) y **republicar el frontend** (`bun run build` + `wrangler deploy`). Hacen falta las dos cosas: Evolución y Perfil llaman a `/evolucion` y `/cuenta`. | Pendiente de decisión de Valentín; **no se hizo** (`main` no se tocó) |
| 2 | **Probar en pantalla real:** (a) eliminar cuenta con una cuenta descartable (Storage queda sin la carpeta del usuario en los dos buckets y la cuenta ya no entra); (b) Evolución con las dos sesiones del corpus (los dos puntos, la variación, "se mantuvo" o "aumentó/disminuyó", el aviso de mezcla de versiones 0.5.3/0.5.4); (c) imprimir de verdad el PDF de un golpe y de una sesión (salto de página, imágenes, A4 vertical); (d) Perfil con una cuenta real; (e) Procesando en escritorio. | **Hecho en parte:** Perfil, Evolución, PDF (golpe y sesión), «Eliminar mi cuenta» y la navegación del celular **vistos por Valentín** (15 y 16/10). **Sin ver:** el PDF impreso en papel y Evolución con los datos finales |
| 3 | ~~Correo propio~~ **Resuelto el 15/10/2026** (Brevo; registro, confirmación y "Olvidé mi contraseña" probados). Falta probar con una dirección de otro proveedor y configurar el alias de contacto de Privacidad. | Hecho · parte pendiente |
| 4 | **Revisar el texto de `/privacidad`:** es una declaración de Valentín (no se usa para publicidad ni se vende; no hay borrado automático). | Pendiente |
| 5 | ~~Paso 7: respaldo de la base con restauración probada~~ **Hecho el 15/10/2026** en un Postgres local (16 de 16 comprobaciones; `docs/respaldo-y-restauracion.md`). Falta la copia fuera de la PC y la copia completa con `pg_dump`. | Hecho · parte pendiente |
| 6 | **Paso 8: ensayo de la demo** (un golpe por gesto subido; congelar). | Pendiente (0,5 sesión) |
| 7 | ~~Confirmar el lado de la cámara de las sesiones del corpus.~~ **Resuelto el 13/10/2026:** izquierda del jugador (no dominante) en todos los videos; las 7 sesiones subidas lo tienen declarado así y la mano dominante `derecha` (Anexo B, aviso 4). Las sesiones nuevas opcionales usan la izquierda. | Hecho |
| 8 | No cambiar el plan de Render ni reiniciar el servicio con un análisis en curso. | Regla |
| 9 | ~~**Decidir qué lado recomienda la aplicación:** el esquema de encuadre de Cargar (`frontend/src/components/esquema-encuadre.tsx`) dibuja la cámara del lado de la raqueta de un jugador diestro, y el corpus es del lado contrario. No cambia ningún cálculo (el lado declarado no entra en el motor), pero un usuario que siga el dibujo grabaría del otro lado y no sería comparable con el corpus.~~ **Resuelto el 15/10:** el esquema recomienda el lado **contrario** a la mano dominante (el validado), se aceptan los dos lados y el reporte agrega una nota neutra si es el de la mano dominante (motor 0.5.5). | Hecho |
| 10 | **Detección automática del tipo de golpe y del encuadre (038):** se intentó adelantarla antes de la demo (límite 23/10). **La etapa 1 no cumple** (§2.10): la etapa 2 no se propuso. La demo va con la carga declarada; la integración solo si valida antes del 23/10 | Etapa 1 hecha, negativa; resto condicionado |
| 11 | **Limpieza y nueva subida con el motor congelado (25–26/10):** borrar las 8 sesiones y subir los recortes; **corregir** la sesión `3a101dd3` (fecha 24/9 con un golpe del 25/9) y no volver a subir `IMG_6376` ni `IMG_6391` como «perfil» (§10.1) | Pendiente |

### 8.2 Antes de la defensa (**17/11/2026: fecha final de entrega de documentación y sistema para regularizar la materia**, según Valentín el 19/10; MVP completo: 2/11; no se informó otra fecha de defensa)

**Mediciones y software (en el orden de Valentín, 13/10, `plan-mvp-punta-a-punta.md` §9):**

1. Calibrar D para drive y revés con las poses del Paso B (0,5–1 sesión). *(Explorado el 16/10: no distingue el drive y va invertido en el revés; con datos nuevos, §10.9.)*
2. Criterio 3 con el tiempo real: métrica (ii) (0,5 sesión de análisis más cómputo).
3. `RESPALDO_POR_GRUPO` (columna b) con las cifras del Paso B (0,25).
4. Cintas de color: **solo si hay tiempo**, prueba tentativa, sin diseñar.
5. ~~Volcar los tiempos de cola y procesamiento de las sesiones del corpus y medir una sesión de 6 golpes en Standard.~~ **Hecho el 19/10/2026** (§10.8). Un tercer punto con el motor congelado es opcional.
6. Decidir qué hacer con el Criterio 5 (validación exploratoria con un entrenador o kinesiólogo, o "no evaluado, trabajo futuro") y con el umbral del Criterio 4 (se informa sin umbral).
7. Decidir si se re-mide el Criterio 2 con el motor 0.5.x (hoy 0.4.1; el cálculo angular no depende del tiempo, pero la cadena de procesamiento cambió).

**Redacción:**

8. **Capítulo 4:** aplicar las **40 filas** de `correcciones-pendientes-capitulo-4.md` (las 12 originales más las agregadas el 15 y el 19/10) y los pendientes de redacción de las decisiones 006, 010–015, 018–020; reemplazar el marcador `[INSERTAR RESULTADOS DE LA MEDICIÓN DE CADA CRITERIO]` del apartado 4.3.4; reemplazar la captura pendiente del panel de Vercel y de Supabase (4.5.4) por Cloudflare y Supabase.
9. **Capítulos 6 y 7** (limitaciones y resultados) con este documento y las anotaciones 1–22 de `correcciones-pendientes-capitulo-4.md`; **Capítulo 8** con `docs/tesis/insumos-capitulo-8.md`; **Capítulo 5** con los costos reales de §6 y §10.7–10.8.
10. Capturas y evidencia de cada etapa del flujo (plan §4, semana 4).

**Operación:** Render en **Standard "siempre para la defensa"** (decisión 023) y volver a Free después; anotar el vencimiento anual del dominio y decidir si se renueva; congelar la versión que se defiende (motor, contrato y commit) y citarla en el capítulo.

---

## 9. Delta desde el 13/10 (corte de esta versión: 19/10/2026)

**Cómo se verificó (19/10/2026):** `git log 60751d8..HEAD`; `/health` de producción tres veces seguidas; `pytest -m "not slow"` y `bun test` corridos de nuevo; `tools/respaldo/estado_de_la_base.py` y `tools/respaldo/tiempos_y_origen_de_las_subidas.py`
(solo lectura sobre la base y Storage); consulta de las páginas de límites de Cloudflare. **No hay commits ni registros posteriores al 16/10 02:56 (−03:00):** **Valentín confirmó el 19/10 que del 17 al 19/10 no hubo desarrollo:** el plan del 17/10 (reglas exploratorias nuevas, revisión de los cinco revés, protocolo de una jornada) **no se hizo** y sigue pendiente.

### 9.1 Commits (21 desde `60751d8`; dos del 13/10 por la tarde son documentos)

| Fecha (−03:00) | Commit | Qué | ¿Cambia producción? |
| --- | --- | --- | --- |
| 13/10 16:32 y 16:51 | `6836d1c`, `882e0ec` | Primera versión de este documento; lado de la cámara confirmado (izquierda, no dominante) y hallazgo del brazo reformulado | No (documentos) |
| 15/10 17:04 | `6d9b7d8` | Correcciones del Capítulo 4 al día (filas 13 a 35) y regla de registrarlas en el momento (CLAUDE.md §6) | No |
| 15/10 18:36 y 18:39 | `cbff5ec`, `d15ef26` | Perfil con «Tu actividad» real; esquema de encuadre con la cámara del lado contrario a la mano dominante, tres cuartos por delante, espejo para zurdos | Frontend |
| 15/10 18:40 y 18:43 | `3b4c71f`, `96498ea` | Correo propio funcionando (decisiones 034 y 027); propuesta de la decisión 038 y protocolo de la sesión del lado derecho | No |
| 15/10 18:47 | `6df3d9d` | **Motor 0.5.5:** el lado de la cámara es una recomendación (se aceptan los dos lados); nota neutra en el reporte si es el de la mano dominante | **Motor y frontend** |
| 15/10 18:58 | `a377e71` | Respaldo con restauración probada (paso 7), runbook de publicación y vuelta atrás. **`main` se publicó hasta este commit** (`56a13c1..a377e71`): lleva los pasos 5 y 6 | **Servidor y frontend** (con el frontend republicado por Valentín) |
| 15/10 19:54 | `201474f`, `8cb57ee` | Guion de la demo; decisión 038 aprobada con pre-registro; herramienta de estado de la base | No |
| 15/10 21:18 | `4f07ee7` | Instrucciones de carga por dispositivo (iPhone, Android, Computadora); Evolución sin gráfico vacío; la leyenda una sola vez | Frontend |
| 16/10 00:20 | `841b63b` | Bitácora de cierre de contexto | No |
| 16/10 00:36 | `9415814` | Navegación del celular (pestañas inferiores; inicial con menú «Salir»; sin sesión, Ingresar y Crear cuenta); esquema de Cargar sin pisar la línea y con raqueta en la mano dominante | Frontend (republicado y verificado por Valentín, con y sin sesión) |
| 16/10 00:44 a 02:56 | `fee1003` … `08ccec1` | **Decisión 038, etapa 1** (arnés de validación `medicion_deteccion.py`, resultados, análisis exploratorio) y bitácora | No (el arnés no lo importa el producto) |

### 9.2 Producción hoy (verificado el 19/10/2026)

| Qué | Valor |
| --- | --- |
| Servidor (Render Standard) | `GET /health` → `{"estado":"ok","version_motor":"0.5.5"}`, tres veces seguidas |
| Contrato del reporte | **1.4** (`VERSION_CONTRATO` en `backend/app/schemas/reporte.py`); sin cambio desde el 13/10 |
| Frontend (`kinetiqtennis.me`) | responde 200; republicado por Valentín el 16/10 (informe) |
| Código | `main` = `origin/main` = `08ccec1`. Último commit que toca el motor o el ensamblado del reporte: **`6df3d9d`** (15/10 18:47). `engine/` solo cambió en `version.py` desde `56a13c1` |
| Migraciones | **13 archivos en `supabase/migrations/`, ninguno nuevo desde el 13/10** (`git diff 60751d8..HEAD -- supabase` vacío) |
| Pruebas | servidor `pytest -m "not slow"` → **620 passed, 106 deselected** (190 s); frontend `bun test` → **122 pass**; `tsc` y `build` limpios (corridos el 16/10 sobre `9415814`; no se repitieron el 19/10) |
| Base (solo lectura) | **1 cuenta**, 1 jugador, **8 sesiones, 18 golpes, 17 reportes, 1 fallido**, ninguno en curso; **0 filas sin dueño**; Storage: `videos` 18 archivos (607 MB) y `artefactos` 47 (28 MB), **0 archivos de cuentas inexistentes** |

### 9.3 Qué cambió en el motor y en el frontend

- **Motor:** una sola versión nueva, **0.5.5** (15/10): `nota_lado_de_camara` en `ensamblar_reporte.py` agrega una observación neutra (`sin_evaluar`) si la cámara estuvo del lado de la mano dominante («este lado de cámara todavía no está validado…»); `procesar_video.py` lee
  `lado_camara` de la sesión solo para esa nota. **No cambia ningún número ni el contrato.** Ningún resultado de §2 se recalculó con la 0.5.5.
- **Frontend:** Perfil real y «Eliminar mi cuenta» (pasos 5 y 6, ya en `main`); Evolución real; PDF como documento A4; esquema de encuadre («Recomendado», espejo para zurdos, raqueta); instrucciones por dispositivo (Android «no probado en todos los modelos»;
  Computadora con LosslessCut para recortar sin recodificar); gráfico «Golpes con el mismo orden» oculto si ninguna sesión llega a 5 ordenables; navegación del celular (especificación §8). La ruta `/clinica` y `/performance` redirigen a la Biblioteca; **`reporte-mock.ts` (la maqueta con valores sin fuente) ya no existe**.
- **Datos de la base:** la sesión 8 (`3a101dd3`) se subió el 13/10 (golpe de la toma 02c); la cuenta de prueba, la del iPhone y la de rol entrenador se borraron con «Eliminar mi cuenta» (16/10).

### 9.4 Cifras del documento del 13/10 que cambiaron (antes → después)

| # | Dónde | Antes (13/10) | Ahora (19/10) | Por qué |
| --- | --- | --- | --- | --- |
| 1 | §1.3, pasos 5 y 6 | Solo en `respaldo-13-10`; «No» en producción | **En `main` desde el 15/10; probados por Valentín en producción** | Push `56a13c1..a377e71` |
| 2 | §1.3 y §1.4, producción | `56a13c1`, motor 0.5.4 | **`08ccec1`, motor 0.5.5** | `6df3d9d` |
| 3 | §1.3, pruebas | 589 servidor · 106 frontend (reportadas) | **620 · 122** (corridas el 19/10) | +23 del arnés de la 038, +respaldo, +esquema e instrucciones |
| 4 | §2.3, espera en cola de una sesión | Estimación: ~12 min por sesión de 6 golpes en Standard (~41 en Free); «NO MEDIDO» | **Medido: 19,6 min** (sesión del 24/9, 6 golpes) y **39,5 min** (la del 25/9, detrás de la otra); procesamiento por golpe 193,5 s y 246,5 s (mediana) | Tiempos de la base (§2.3, nueva tabla) |
| 5 | §2.1 y §2.3, `IMG_6376` | «Saque de perfil subido por el flujo completo» | **Declarado «perfil»; es un saque de tres cuartos** (marca de captura del archivo y giro de hombros 52,9°). Las tasas medidas no cambian | §10.1 |
| 6 | §8.1 punto 7 y Anexo B aviso 4, cartel de Cargar | El esquema dibujaba la cámara del lado de la raqueta | **Recomienda el lado contrario a la mano dominante** (el validado); se aceptan los dos lados | `d15ef26`, `6df3d9d` |
| 7 | §8.1 punto 2, pantallas | «Pendiente (ninguno verificado)» | Perfil, Evolución, PDF (golpe y sesión), «Eliminar mi cuenta» y navegación del celular **vistos por Valentín**; **sin ver:** el PDF impreso en papel | Informe de Valentín 15 y 16/10 |
| 8 | §6 y §8, correo | Brevo sin clave SMTP | **Funciona** (registro, confirmación y recuperar contraseña); sin probar con otro proveedor | decisión 034 |
| 9 | §2.8 / §3 fila 19, contraste D | Calibrado solo con el saque (28/28) | Igual para el producto; el 16/10 se **exploró** drive y revés (§2.10): D **no distingue el encuadre del drive y va invertido en el revés**; **no se calibró** | 038, etapa 1 |
| 10 | §3, sesiones subidas | «7 sesiones» (Anexo B aviso 4) | **8 sesiones, 1 cuenta** | Sesión `3a101dd3` |

**No cambió ninguna cifra de** §2.1 (tasas), §2.2 (corpus horneado), §2.4 y §2.5 (Pasos A y B), §2.6 (Criterios 1 a 3), §2.7 (brazo): **no se re-midió nada de eso** desde el 13/10; el único resultado de medición nuevo es el de la 038 (§2.10).

---

## 10. Pendientes del Capítulo 7: resueltos o declarados (corte 19/10/2026)

Cada punto lleva su estado. **RESUELTO** = hay evidencia en el repositorio o la obtuve hoy; **NO CONSTA** = el repositorio no lo dice (se le preguntó a Valentín); **NO MEDIDO / NO REALIZADO** = no se hizo. **Valentín contestó el 19/10 las cuatro preguntas abiertas** (motivo del cambio de alcance, texto del OE4, actividad del 17 al 19/10, fecha de defensa): sus respuestas están incorporadas abajo y marcadas «declaración de Valentín» (no constan en un documento del repositorio de esa fecha).

### 10.1 `IMG_6376` e `IMG_6395`: ¿qué encuadre y qué fecha? — **RESUELTO (con una corrección al documento del 13/10)**

Verificado el 19/10 sobre los archivos guardados en Storage (marca `com.apple.quicktime.creationdate` leída con `ffprobe`, sin descargar) y contra las fechas de los 16 originales de `docs/resultados/corpus-real-alineacion.json`:

| Archivo subido | Marca de captura del archivo | Original del corpus | Contenido del original en el corpus | Declarado al subir | Subida (−03:00) | Reporte |
| --- | --- | --- | --- | --- | --- | --- |
| `IMG_6376.mov` (501 fotogramas, 2,51 s, 20,6 MB) | **24/9/2026 14:58:43** | `IMG_6376.MOV` (sesión 1, toma 01; 15 176 fotogramas) | **Saque de tres cuartos** (6 repeticiones) | saque, **perfil**, fecha 24/9 | 9/10 20:19 | motor 0.4.1, `completado`; sesión `f1456994` |
| `IMG_6395.mov` (599 fotogramas, 3,0 s) | **25/9/2026 15:34:37** | `IMG_6395.MOV` (sesión 2; 17 703 fotogramas) | **Revés de tres cuartos** (6 repeticiones) | revés, tres cuartos, fecha 25/9 | 12/10 | motor 0.4.1, `completado`, 676,6 s en Free; sesión `0ee6f519` |
| `IMG_6395.mov` (604 fotogramas, cámara lenta mantenida) | ídem | ídem | ídem | ídem | 12/10 | **`fallido`** (`archivo_convertido`, 14,0 s): el caso RNF-01 |
| `IMG_6380.mov` (606 fotogramas) | 24/9/2026 15:09:58 | `IMG_6380.MOV` (sesión 1) | Revés de tres cuartos | revés, tres cuartos, 24/9 | 12/10 22:58 | motor 0.5.2; sesión `97ca033b` |
| `IMG_6391.mov` (805 fotogramas) | 25/9/2026 15:23:05 | `IMG_6391.mov` (sesión 2, toma 02) | **Saque de tres cuartos** (original incompleto, fuera del Paso B) | saque, **perfil** | 12/10 | motor 0.5.0; sesión `f8921845` (el caso de la decisión 035) |

- **Los cuatro son recortes de originales del corpus (24 y 25/9), no grabaciones nuevas**, subidos después (9, 12 y 13/10). Los recortes de las 18 repeticiones de Evolución (`recortar_evolucion.py`, `ffmpeg -c copy`) no conservan esa marca.
- **El encuadre de `IMG_6376`:** el contraste D del motor actual sobre el archivo subido da **52,9°** (pico del tronco en el fotograma 353 de la grilla de 240 Hz), **dentro del rango del saque de tres cuartos del corpus (50–83°) y fuera del de perfil (26–42°)**. Coincide con el catálogo del corpus. Salvedad: D se corrió el 19/10
  con el código actual sobre el archivo guardado (el reporte original es de la 0.4.1, que no tenía D) y alineando las marcas con las primeras 499 del archivo (501 paquetes visibles, 499 decodificados).
- **Consecuencia para el capítulo:** §2.1 (fila «`IMG_6376`») y §2.3 (fila 1 de latencia) lo llamaban «saque de perfil»: es lo que se **declaró**, no lo que es. Las tasas (199,6 fps, 16,8 % perdidos) y la latencia no dependen del encuadre y no cambian. Es **el mismo tipo de error que el de `IMG_6391`**
  (decisión 035): dos de los cinco archivos subidos a mano llevaban el encuadre equivocado. La nota 8 de `correcciones-pendientes-capitulo-4.md` («saque de perfil… cadera y tronco a un fotograma») queda corregida en ese archivo.
- **Un hallazgo más, en la base:** la sesión `3a101dd3` tiene **fecha 24/9/2026** pero contiene un golpe de la **toma 02c, grabada el 25/9** (`20260925_saque_trescuartos_toma02c_golpe1.mov`). Se subió con la fecha equivocada: en Evolución cuenta como una segunda sesión del 24/9. Se corrige en la limpieza del 25–26/10 (`docs/demo-guion.md` §C).

### 10.2 ¿Por qué no se probó la Vía A (YOLOv8-Pose/ONNX) antes de suspender el veredicto? — **RESUELTO como registro; NO PROBADA (NO MEDIDO)**

Lo que dice el repositorio, en orden:
1. **Decisión 005 (27/8):** YOLOv8-Pose entrega 17 puntos COCO en 2D, sin eje z; la Vía A (YOLOv8-Pose + modelo de elevación 2D→3D) queda **«diferida»**: se implementa «cuando el punto de decisión de la Etapa 4 diga que hace falta» (plan de repliegue, Capítulo 3 §3.3.2.9). MediaPipe entrega 3D directo; el Capítulo 4 (§4.4.3) justifica la elección por «maximizar aprendizaje por unidad de esfuerzo» y con una salvaguarda de reversibilidad
   (la interfaz `PoseBackend`; hay `FakeBackend` 2D y 3D en las pruebas). El Capítulo 3 (línea ~162) dice que el **Objetivo Específico 1 se formula sobre una arquitectura de dos etapas (percepción 2D + elevación 2D→3D)**: lo construido es otra (MediaPipe directo): **es un desvío a declarar**.
2. **Decisión 006 (27/8):** la Vía A sobre ONNX Runtime es la segunda palanca para **velocidad** (después de bajar `model_complexity`), no una prueba de exactitud.
3. **Decisión 015 (29/9), punto de decisión de la Etapa 4:** «sin repliegue de arquitectura» (Criterio 2 cumple por la media; Criterio 1 mixto). La condición para activar la Vía A no se dio.
4. **9/10:** regla de trabajo «sin investigaciones nuevas: se anota y se sigue» (CLAUDE.md §5).
5. **Decisiones 035 y 036 (12–13/10):** suspenden el veredicto **sin mencionar la Vía A** (no aparece en ninguna de las dos). **No hay una decisión escrita de no probarla**: lo que hay es que nunca se activó su condición y que el tiempo se destinó al flujo de punta a punta.
- **Lo que NO se sabe:** si otro estimador cambiaría la dependencia del orden con el encuadre (puede ser del estimador monocular o del movimiento). **NO MEDIDO.** Es trabajo futuro (§7.3 y Capítulo 8).

### 10.3 Motivo del cambio de alcance del 7/10 (autovalidación) — **RESUELTO (declaración de Valentín, 19/10/2026)**

El repositorio registra **el hecho y su efecto**, no la razón: `plan-mvp-punta-a-punta.md` §1 («cambio del 7/10: no habrá pruebas con otros usuarios; la validación la hace Valentín grabándose; el sistema igual tiene que funcionar para cualquier usuario nuevo… como si fuera público»), la decisión 023 («el cambio a Standard ya no depende de pruebas con usuarios») y CLAUDE.md §5.
**Motivo, según Valentín (19/10/2026): el plazo y no tener otros usuarios disponibles.** Es una declaración del autor; el repositorio solo trae el contexto de calendario (plan §1b del 9/10: ~40–50 % de llegar al 20/10 con trabajo todos los días) y no dice la causa. Consecuencias registradas: Criterios 4 (umbral) y 5 y la incertidumbre I4 quedan **no evaluados** (§2.6).

### 10.4 Pruebas de los requisitos no funcionales — **RESUELTO en parte; lo que falta se declara**

| RNF | Prueba prevista (Capítulo 4) | ¿Existe? | Resultado |
| --- | --- | --- | --- |
| **RNF-01** tasa real | Archivos de 30, 60, 120 y 240 fps y cámara lenta | **Parcial:** casos sintéticos de 60 (modo normal), 120 y 240 fps (`tests/integration/test_ingest_video.py`, `test_procesar_video_modo_normal_60fps.py`) y el archivo convertido (`test_archivo_convertido.py`, `test_tasa_del_archivo.py`); **no encontré un caso de 30 fps** | pasan dentro de las 620 |
| **RNF-02** versión en cada reporte | Inspección del registro persistido | Sí (`test_contrato_reporte.py`, `test_ensamblar_reporte.py`; la tabla `versiones_motor`) | Los 17 reportes de la base llevan su versión (0.4.1 ×2, 0.5.0, 0.5.2, 0.5.3 ×12, 0.5.4) |
| **RNF-03** fase cero | Señal sintética de orden de picos conocido | **Sí:** `tests/unit/test_dsp.py::test_fase_cero_conserva_el_instante_del_pico_y_la_unidireccional_no` y `test_dsp_segmentos.py` | **17 passed (19/10).** Señal con pico en la muestra 240 (1,000 s a 240 Hz), ruido de 40 y 70 Hz, Butterworth de 4.º orden con corte de 6 Hz: **fase cero → pico en 240 (corrimiento 0 ms)**; filtro **unidireccional → pico en 257 (+70,8 ms)**. Es decir: la prueba demuestra que el filtro de una sola pasada sí correría el orden aparente |
| **RNF-04** propagación de la marca de baja confianza | Propagación a lo largo del pipeline | Sí (`test_validation.py`, `test_pipeline_e3_huecos.py`, `test_dsp_segmentos.py`) | 27 passed (19/10) junto con `test_pose_base.py` |
| **RNF-05** procesamiento asincrónico | **Cerrar el navegador durante el procesamiento** | **No existe como está redactada.** Hay una prueba de que `POST /analisis/{id}/procesar` responde **202** y encola (`test_api_analisis.py`) y el cableado real (`test_api_analisis_e2e.py`, `TestClient`, ~100 s) | **NO REALIZADA** la prueba de cerrar el navegador. Evidencia indirecta: las 12 repeticiones de las dos sesiones se encolaron en ~6 min y se procesaron durante **~44 min** (§2.3); el estado se lee por polling, no hay conexión sostenida |
| **RNF-06** percepción reemplazable | Sustituir el backend de pose en pruebas de integración | **Parcial:** `FakeBackend` 2D y 3D (`test_pose_base.py`) y las pruebas del pipeline con él | Pasan; **no hay un segundo backend real** (Vía A no implementada) |
| **RNF-07** aislamiento por fila | Pruebas de políticas de seguridad a nivel de fila | **Sí, contra el Supabase real** (`test_rls_aislamiento.py`, 24 casos) y **en Storage** (`test_storage_aislamiento.py`, 4 casos) | **28 passed en 54,9 s (19/10/2026).** Crean dos usuarios de prueba y los borran; verificado después: 1 cuenta, 0 filas sin dueño, 0 archivos huérfanos |
| **RNF-08** máximo 3 observaciones | Validación de usabilidad | **No** | **NO EVALUADA** (sin usuarios, §10.3) |

- **Pruebas de extremo a extremo con Playwright: no existen.** Playwright no figura en `frontend/package.json` ni en ningún archivo de configuración; la integración continua es solo el keep-alive de Supabase; las pruebas del frontend son `bun test` (lógica pura, 122) sin navegador. Es lo que dice la corrección 31 del Capítulo 4.
- **Pruebas manuales por Valentín en producción (informe, sin capturas en el repositorio):** registro y confirmación, recuperar contraseña, carga desde el iPhone, Perfil, Evolución, PDF, «Eliminar mi cuenta» y navegación del celular.

### 10.5 ¿Hay una comparación contra un modelo de referencia (objetivo específico 4)? — **NO REALIZADA; reemplazada por la comparación del jugador consigo mismo (declaración de Valentín, 19/10/2026)**

**Texto del objetivo específico 4 (Valentín, 19/10/2026):** «Implementar una funcionalidad de análisis comparativo visual y un sistema que permita observar el contraste de la ejecución del jugador con modelos de referencia, permitiendo así corregir errores y mejorar el rendimiento deportivo.» **Valentín confirma que no se construyó la comparación contra un modelo de referencia: se reemplazó por la comparación del jugador consigo mismo.** El Capítulo 1 no está en el repositorio (los Capítulos 3 y 4 solo citan el OE1 y el OE5). **Es un objetivo cumplido solo en parte y el cambio debe declararse** (Capítulo 6 y conclusiones). Lo que hay, y lo que no:
- **No existe** una comparación del sistema contra un modelo, captura óptica, sensores o un jugador de referencia. Es una exclusión declarada: CLAUDE.md R5 («Fuera: comparativas con jugadores ATP/WTA») y §3 («comparar al jugador consigo mismo… no contra un promedio poblacional ni contra un modelo ideal»).
- **Referencias parciales que sí hay:** (a) el **Criterio 2** compara los ángulos de rodilla y codo contra goniometría manual (n = 18; §2.6); (b) el orden esperado de la literatura (cadera antes que tronco) se usa solo como «referencia» de un grupo, y la 036 lo suspendió; (c) los valores de Fleisig del brazo **no son comparables** con la ω del vector hombro→codo (decisión 011).
- **Falta una medición independiente de la pelvis** (cintas de color, registrada y sin diseñar; §7.3). **Lo que sí cubre parcialmente el objetivo:** (i) la comparación **visual** del jugador consigo mismo (Evolución, vista de sesión, tres fotogramas clave y video con esqueleto); (ii) el seguimiento entre sesiones del mismo encuadre. **Lo que no cubre:** el contraste con modelos de referencia, y «corregir errores y mejorar el rendimiento» (la regla R2 lo excluye: el sistema documenta y mide, no diagnostica ni prescribe; la 036 retiró el veredicto). Motivos documentados del reemplazo: R5 y CLAUDE.md §3 (no comparar contra jugadores profesionales ni un modelo ideal), y la dependencia del orden con el encuadre, que impide usar una referencia (§2.5).

### 10.6 Auditoría de fatiga, panel del profesional y umbrales poblacionales — **NO IMPLEMENTADOS (ni simulados)**

| Elemento (Capítulo 4, tabla de «simulado») | Estado al 19/10 | Evidencia |
| --- | --- | --- |
| Auditoría de fatiga intra-sesión (primer contra último bloque) | **No implementada ni simulada.** Lo que sí hay: consistencia entre golpes de una sesión (variación, golpe típico, golpes que se apartan) | `docs/tesis/correcciones-pendientes-capitulo-4.md` fila 23; `backend/app/consistencia.py` |
| Panel del profesional de la salud (multi-atleta) | **No implementado.** El rol «profesional de la salud» existe solo en el registro; `/clinica` redirige a la Biblioteca | `frontend/src/routes/clinica.tsx`; `docs/plan-mvp-punta-a-punta.md` §5 |
| Umbrales normativos poblacionales | **No implementados:** sin alertas con umbral (falta referencia, R4); no hay `engine/audit.py` | decisión 036; correcciones fila 13 |

### 10.7 Cuotas de Cloudflare Workers (plan gratuito) y costo de renovación del dominio — **RESUELTO (fuente oficial) · PARCIAL (dominio, fuente secundaria)**

- **Workers Free** (páginas `developers.cloudflare.com/workers/platform/limits/` y `/pricing/`, consultadas el 19/10/2026): **100 000 solicitudes por día** (se reinicia a las 00:00 UTC); **10 ms de CPU por solicitud HTTP**; 50 subsolicitudes por invocación; tamaño del Worker 64 MiB; 100 Workers por cuenta; 128 MB de memoria por isolate;
  hasta 20 000 archivos estáticos de 25 MiB cada uno; **«las solicitudes a assets estáticos son gratuitas e ilimitadas»**. El frontend se publica como Worker con renderizado en el servidor: cada página que se renderiza consume CPU del Worker. No se midió el consumo real de la aplicación (**NO MEDIDO**).
- **Renovación del dominio `.me` en Namecheap:** **≈ USD 19,18 por año** según una comparación de terceros (`domainoffer.net`, cifras de mayo de 2026); **no se pudo leer la página oficial de Namecheap** (respondió 403). **NO VERIFICADO en la fuente oficial.** La oferta del Student Pack es el primer año; **vence al año del registro** (octubre de 2026 + 1 año; fecha exacta no registrada en el repositorio); renovación automática apagada (decisión 034).

### 10.8 Espera en cola medida de una sesión de varios golpes y costo acumulado de Render — **RESUELTO (cola) · NO MEDIDO (costo)**

**Datos de la base** (`tools/respaldo/tiempos_y_origen_de_las_subidas.py`, 19/10/2026; Render Standard, motor 0.5.3; espera = `inicio − encolado`; procesamiento = `fin − inicio`; **cupo de análisis simultáneos = 1**). Los 12 golpes de las dos sesiones se encolaron el 13/10 entre 01:48 y 01:54 (−03:00), uno tras otro:

| Sesión | Golpes | Fotogramas por golpe (duración) | Procesamiento por golpe: mediana (mín–máx) | Espera en cola: mediana · máxima | Tiempo de pared (primer encolado → último fin) | s por fotograma (mediana) |
| --- | --- | --- | --- | --- | --- | --- |
| 24/9, saque de tres cuartos (`e46264bf`) | 6 | 966–1233 (4,8–6,2 s) | **193,5 s** (179,9–223,6) | 423,7 s · 867,9 s | **1177 s = 19,6 min** | 0,186 |
| 25/9, saque de tres cuartos (`e807c36e`) | 6 | 964–1566 (4,8–7,8 s) | **246,5 s** (181,1–279,7) | 1512,2 s · 2024,4 s | **2372 s = 39,5 min** (detrás de la otra sesión) | 0,180 |

- **La suma de los procesamientos (1170,9 + 1440,8 = 2611,7 s) coincide con el tiempo total desde el primer encolado hasta el último fin (43,7 min):** la cola trabaja sin huecos y **el último de 12 golpes esperó 33,7 min**.
- **La estimación del documento del 13/10 («~12 min por sesión de 6 golpes en Standard») era baja: el valor medido es 19,6 min,** porque los golpes de las sesiones del corpus son más largos (4,8–7,8 s) que los de 3–4 s con que se midieron los 117–147 s. **El costo por fotograma se mantiene (0,18–0,19 s)**: la latencia escala con los fotogramas.
- Otros tiempos de la base: golpes sueltos de 606 a 1121 fotogramas en 124,9 s a 209,4 s (Standard) y 676,6 s (Free, 599 fotogramas); el rechazo por archivo convertido, 14,0 s. Un golpe de la sesión del 9/10 (motor 0.4.1) no tiene tiempos (anterior a la migración).
- **Costo acumulado de Render: NO MEDIDO** (la facturación está en el panel de Render, al que no tengo acceso). **Cuenta aritmética, no una medición:** USD 25 por mes desde el 12/10; al 19/10 son 7 días ≈ **USD 5,6** si se prorratea por día (supuesto no verificado; no pude leer las condiciones de facturación en `render.com/pricing`).

### 10.9 Criterio 3 (métrica ii) con tiempo real; contraste D para drive y revés; Criterio 2 con el motor 0.5.x — **NO REALIZADOS (D: explorado)**

| Pendiente | Estado | Qué hay |
| --- | --- | --- |
| **Criterio 3, métrica (ii)** con el tiempo real | **NO REALIZADO** | Sigue siendo el punto 2 de «después de la demo» (`plan-mvp` §9). La métrica (i) no depende del tiempo y vale |
| **D para drive y revés** | **NO CALIBRADO; EXPLORADO el 16/10** | La etapa 1 de la 038 (§2.10) midió el giro de hombros por gesto y encuadre: **drive** perfil 27–72° y tres cuartos 33–72° (se solapan: D no lo distingue); **revés** perfil 26–86° y tres cuartos 9–64° (**invertido** respecto del saque). No hay umbrales validados |
| **Criterio 2 con el motor 0.5.x** | **NO REALIZADO** | Sigue medido con el motor 0.4.1; el cálculo angular no depende del tiempo, pero la cadena de procesamiento cambió. Decisión de Valentín pendiente |

### 10.10 Evolución vista en pantalla real con las sesiones del corpus — **RESUELTO (visto por Valentín) · PARCIAL (sin captura ni datos finales)**

- **Visto:** Valentín informó el 15/10 que Evolución funciona en producción con el frontend republicado; **no hay captura ni registro de qué números mostraba** en el repositorio. **Sin ver:** con las sesiones subidas con el motor congelado (se vuelven a subir el 25–26/10).
- **Lo que calcula hoy con los datos de la base** (misma función que `GET /evolucion`, `serie_de_evolucion`, saque · tres cuartos, lado izquierdo; 19/10/2026):

| Sesión | Fecha | Golpes (medidos · con orden distinguible) | Separación cadera-hombro máx.: mediana · dispersión · rango (°) | Versión del motor |
| --- | --- | --- | --- | --- |
| `e46264bf` | 24/9 | 6 · 1 (se apartan 2) | **32,05** · 1,11 · 28,5–32,9 | 0.5.3 |
| `3a101dd3` | 24/9 (**mal fechada**: es del 25/9) | 1 · 1 | 33,3 · — · 33,3 | 0.5.4 |
| `e807c36e` | 25/9 | 6 · 3 (se apartan 1) | **32,95** · 4,37 · 11,2–41,5 | 0.5.3 |

  **Variación habitual 2,74°; centro habitual 32,95°; cambio entre las dos últimas sesiones −0,35° («dentro de lo habitual»); mezcla de versiones 0.5.3 y 0.5.4: sí.** Con la fecha equivocada de `3a101dd3` la serie tiene 3 puntos donde debería tener 2; el «cambio» compara la sesión del 25/9 con un solo golpe.
  **Lectura honesta:** la separación cadera-hombro es estable entre las dos sesiones (≈ 32–33°); el orden tiene pocos golpes ordenables (1 de 6 y 3 de 6), por eso el gráfico «Golpes con el mismo orden» no se muestra.

### 10.11 Versión que se va a defender — **NO CONGELADA al 19/10**

- **Congelamiento previsto:** **24/10/2026** (`git tag motor-congelado-<versión>`; `engine/` y `ensamblar_reporte.py` sin cambios pendientes); **27/10 (D−1):** congelamiento total (no se publica nada); demo 28–30/10; MVP completo el 2/11; **17/11/2026 es la fecha final de entrega de la documentación y del sistema para regularizar la materia** (Valentín, 19/10/2026); no se informó otra fecha de defensa.
- **Hoy (candidata, no firme):** motor **0.5.5**, contrato **1.4**, `main` = `08ccec1` (último cambio del motor: `6df3d9d`). **No existe la etiqueta de congelamiento** (la última es `v0.5.0-etapa4`). Si la integración de la detección automática (038) no valida antes del 23/10, **la versión que se defiende es la que está en producción hoy**.

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
| Decisión 038, etapa 1 (detección automática) | `docs/decisiones/038-…`, `docs/resultados/deteccion-038-etapa1.md` (y `.json`, `-estadisticos.json`, `-exploratorio.json`), `backend/app/medicion_deteccion.py` |
| Tiempos de cola y origen de los archivos subidos | `tools/respaldo/tiempos_y_origen_de_las_subidas.py` (solo lectura); `tools/respaldo/estado_de_la_base.py` |
| Aportes, recomendaciones y mejoras (Capítulo 8) | `docs/tesis/insumos-capitulo-8.md` |

## Anexo B. Avisos: inconsistencias del repositorio a resolver antes de citar

1. **Dos p de Fisher distintos para el saque.** Paso A (corpus horneado, 120,2 fps): 0 de 9 contra 6 de 9, **p = 0,009**. Paso B (originales): 0 de 8 contra 7 de 7, **p = 0,0002**. Son dos mediciones; citar la del Paso B como definitiva y la del A como control.
2. **"El único grupo que cumple el Criterio 1".** La decisión 029 y la nota 3 de las correcciones dicen que es `drive|perfil` (1a 0,83), cifra que corresponde a τ = 3; la tabla formal (014) a τ = 1 da **tres grupos** y a τ = 2 y 3 **dos**. La decisión 031 lo corrigió. Citar siempre la tabla, con su τ y su motor.
3. **Fechas.** Las entradas de la bitácora rotuladas "2026-10-14" (tarde, mañana y madrugada) y las menciones "14/10" de `plan-mvp-punta-a-punta.md` (§8, filas 5 y 6: "Hecho el 14/10"), `brazo-por-golpe.md` ("Decisión (Valentín, 14/10/2026)") y `especificacion-frontend.md` ("decisión de Valentín, 14/10/2026", tres veces) corresponden a trabajo cuyos commits son del 13/10 (01:59 a 04:20, −03:00). En esta sesión se corrigió solo la entrada de cierre de la bitácora (su título y una mención dentro de ella); las demás quedan para que Valentín decida.
4. **Lado de la cámara: RESUELTO el 13/10/2026.** Valentín confirmó que en todos sus videos la cámara estuvo **a su izquierda (lado no dominante; es diestro)**, como decía la decisión 013 (medido con la `z`
   relativa de los hombros en 74 de 84 clips). Verificado en la base: las **7 sesiones** subidas hasta el 13/10 (24 y 25/9; **8 al 19/10**) tienen `lado_camara = izquierda` y el atleta `mano_dominante = derecha`. Se corrigieron los documentos
   que decían "del lado de la raqueta" o "del lado del brazo dominante" (`protocolo-grabacion.md`, `protocolo-sesiones-evolucion.md`, `protocolo-saques-tres-cuartos.md`, y la "Implicancia" de
   `brazo-por-golpe.md`, ya reformulada). ~~Queda un cartel de la aplicación que dibuja la cámara del lado de la raqueta~~ **Resuelto el 15/10/2026:** el esquema de Cargar recomienda el lado contrario a la mano dominante (§8.1, punto 9).
5. **"Oclusión real" frente a "causa no separada".** `brazo-por-golpe.md` concluye "oclusión real, no una regla demasiado estricta" (lo que descarta es que la regla del 75 % sea el motivo); la decisión 013 dejaba abiertas el desenfoque y la autooclusión. Tras confirmar el lado de la cámara (13/10), la lectura vigente es que el brazo dominante queda del lado lejano y el torso lo tapa en el armado; el capítulo debe decir qué se afirma: **el estimador no ve el codo en el armado del golpe**, y que la explicación por el lado de grabación es la que mejor encaja, **sin haberla contrastado** grabando del lado de la raqueta.
6. **D calibrado con 22 saques y verificado con 28.** El umbral de ~46° sale de 22 saques; las 28 repeticiones válidas del saque son la verificación de consistencia. Es la misma muestra.
7. **La decisión 037 dice "Decide Valentín" sobre el brazo; ya decidió** (queda "no medido", sin máximo parcial). El texto de la 037 no se actualizó.
8. **"76 repeticiones válidas" frente a 75.** El Paso B midió 76 repeticiones y 75 son válidas para el par cadera-tronco (una de saque de perfil de la sesión 1 no lo es); `brazo-por-golpe.md` llama "válidas" a las 76.
9. **Tasa equivalente del corpus:** 120,1 fps (mediana de los pares del JSON) y 120,2 fps (valor usado en el Paso A y en los documentos); diferencia sin consecuencias, pero conviene citar una.
10. **Fecha del Paso B.** Los documentos lo fechan "13/10/2026"; el commit `7c9535c` es del 12/10 21:39 (−03:00) y el JSON de la sesión 2 se generó el 13/10 02:51 UTC (12/10 23:51 −03:00).
11. **`IMG_6376` figura como «saque de perfil» en varios documentos** (`criterio4-latencia.md` fila 1, la nota 8 de `correcciones-pendientes-capitulo-4.md`, la bitácora del 9/10 y el documento del 13/10 de este material). Es lo que se **declaró** al subirlo: el original es un **saque de tres cuartos** (§10.1). Citar siempre «declarado perfil; es tres cuartos».
12. **Sesión `3a101dd3` mal fechada:** fecha 24/9/2026 con un golpe de la toma 02c, grabada el 25/9 (§10.1). Afecta a Evolución (§10.10).
