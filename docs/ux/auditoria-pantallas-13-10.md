# Auditoría pantalla por pantalla — maquetas contra producción (13/10/2026)

**Para qué:** antes de gastar las sesiones que quedan hasta la demo (28–30/10), saber qué hay hoy en cada pantalla, qué de la maqueta **ya no aplica** tras las decisiones 031–036 (ningún grupo emite
veredicto; sin puntaje 0–100) y qué es imprescindible. **No se programó nada** en este punto.

**Cómo se auditó (y qué no se pudo ver):**

- **Con el navegador, en `kinetiqtennis.me`:** Landing, Ingreso, Registro y `/reporte` (que sin sesión redirige a Ingreso). La landing de producción coincide palabra por palabra con `frontend/src/routes/index.tsx`.
- **Pantallas con sesión (Biblioteca, Cargar, Procesando, Reporte, Perfil): leídas del código de `frontend/src/routes/*` en `main`**, no vistas en producción. No inicié sesión ni creé una cuenta de prueba
  en producción (el registro depende del SMTP, que sigue sin resolver, y crear cuentas ahí no es algo que deba hacer yo). **No verifiqué qué commit del frontend está desplegado**: la landing coincide con `main`,
  pero Valentín tenía pendiente republicar los cambios del 12/10. Conviene que mire estas pantallas él una vez con una cuenta suya.
- **Referencia:** `docs/ux/maquetas/capturas/*.png` y `html/*.html`, `docs/ux/especificacion-frontend.md` (v1, 1/10) y `docs/plan-mvp-punta-a-punta.md` §8.

**Qué ya no aplica, en general** (se repite en la tabla): (1) **el puntaje de rendimiento 0–100 y sus tres componentes** (la maqueta lo pone en Biblioteca, ReporteSimple, Evolución, PDF y Landing); (2) **"Correcto" y
"Desvío leve" como resultado del orden cadera → tronco** (los seis grupos suspendidos: decisiones 035 y 036); (3) **"Cuatro estados, siempre con nombre"**: el reporte real hoy solo produce **"Solo registrado"** y
**"No auditable"**; (4) **"rango habitual" y flechas verdes/ámbar** como juicio sobre la separación cadera-hombro (es un dato; el color no puede decir "mejor" o "peor"); (5) **planes y precios** en Perfil
(fuera del MVP, especificación §11).

---

## 1. La tabla

Esfuerzo en **sesiones de ~medio día** (la unidad del plan §8); son estimaciones mías, sin medir. **IMP** = imprescindible para la demo.

| # | Pantalla | Qué muestra la maqueta | Qué hay hoy | Qué ya no aplica (031–036) | Esfuerzo | IMP |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Landing** (`Main`) | Hero "Tu técnica, documentada cuadro a cuadro" con una tarjeta de un golpe y "CORRECTO · cadera antes que tronco en 4 de 6"; tres pasos; "lo que mide / lo que no hace"; **cuatro estados**; "para quién" (jugador, entrenador, kinesiólogo); CTA | **Diseño viejo (Lovable)**, real y publicada. Tarjeta del hero con "✓ Coincide / Orden esperado"; paso 4 "**Veredicto** en tres observaciones"; promete "comparación del jugador consigo mismo entre sesiones" (no existe todavía); **tres enlaces a "Ver un reporte de ejemplo" que, sin sesión, mandan a Ingreso** (verificado) | La tarjeta "Coincide" y "Veredicto" (contradicen la 035/036); "puntaje que podés desarmar"; "cuatro estados siempre con nombre" | **0,5** corregir el texto y el CTA; **+1** si se hace el diseño nuevo | **Sí** (el texto); el diseño nuevo, no |
| 2 | **Registro** | Rol, consentimiento (Ley 25.326), aviso de spam, reenvío | **Real y funcional** (rol, consentimiento, "revisá spam", reenviar, mensaje "Confirmá tu correo"); formulario simple, sin el diseño nuevo | Nada | **0,5** diseño; **depende de Valentín:** SMTP (Brevo o Resend) y la prueba con correo real | **Sí** (funcional). El diseño, no |
| 3 | **Ingreso / Recuperar / Restablecer** (sin maqueta propia) | — | **Real** (ingreso, "¿Olvidaste tu contraseña?", `/recuperar`, `/restablecer`); falta probarlo con correo propio | Nada | 0 (la prueba es de Valentín) | **Sí** |
| 4 | **Biblioteca** | Tarjetas por sesión con miniatura real, estado, **puntaje**, conteo "1 correcto · 1 desvío leve · 1 no auditable", filtros, "Ver mi evolución" | **Real**: lista de sesiones, buscador, filtros, estado, conteo por estado; sin miniatura (panel neutro); **el enlace de la tarjeta abre solo el primer golpe**; sin puntaje; sin acceso a Evolución | Puntaje; el conteo "N correctos / N desvíos" (hoy sería "N solo registrado"); el color verde/ámbar de las tarjetas | **0,5** (conteo "N golpes medidos · M no medibles", enlace a la vista de sesión y a Evolución); miniatura **0,25** (el fotograma clave ya existe) | **Sí** (0,5); miniatura, no |
| 5 | **Cargar** / `CargarMovil` | Atleta, golpe, encuadre, lado de la cámara, **varios videos a la vez** con estado por archivo (Listo / No se va a subir / Solo preparación), "cómo recortar", "antes de grabar", "tu privacidad", barra fija "Analizar 3 golpes" | **Real, un golpe por sesión** (el selector de archivos no es múltiple): atleta, golpe, encuadre, lado, "¿Cómo lo grabaste?", instrucción de recorte con "Formato: Actual", límite de 50 MB, aviso de fps. **Falta:** varios videos, lista por archivo, barra fija en el celular, "tu privacidad" | Nada; al revés: **el encuadre pasa a ser la decisión central** (el sesgo es fijo por encuadre) y la pantalla tiene que decirlo | **2** (plan §8 #4; recortable a "hasta 3 golpes": 1,5) | **Sí**: sin varios golpes no hay consistencia entre golpes ni Evolución |
| 6 | **Procesando** | Estados de la máquina, progreso por etapa en texto llano y etiqueta técnica en chico, "podés cerrar la página" | **Real**: estados, etapas, motivo de fallo en lenguaje llano, reintento / "Subir otro archivo" / "Corregir y reintentar" | Nada | **0,25** (que muestre "golpe 2 de 6" cuando haya varios) | **Sí** (ya está) |
| 7 | **Reporte simple** / `ReporteMovil` | "Saque · 6 golpes"; interruptor Simple/Detallado; **PDF**; **puntaje 74/100 con tres componentes**; tres observaciones con CORRECTO / DESVÍO LEVE / NO AUDITABLE; tres momentos con **selector de golpe**; frase de secuencia; "comparado con vos mismo" (↓ Menor, = Igual, ↑ Más); CTA al PDF | **Real, de un solo golpe** ("· 1 golpe"): tres observaciones (hoy "Solo registrado" o "No auditable"), gráfico de picos con eje temporal, frase de secuencia, **tres fotogramas reales con esqueleto y video con esqueleto**, detalle técnico plegado (trazabilidad, picos, magnitudes articulares, tramos no auditables). **Falta:** vista de sesión de varios golpes, selector de golpe, "consigo mismo", PDF, interruptor | **Todo el bloque del puntaje**; "CORRECTO … es el orden que describe la literatura"; "DESVÍO LEVE" en la separación con "31° contra 37°" (es un dato, sin juicio); flechas de color en "comparado con vos mismo" | **1,5** (plan §8 #5: agregador y vista de sesión) sobre #5 | **Sí**: es el producto |
| 8 | **Reporte detallado** | Nivel 1 compacto, desglose del puntaje, reproductor sincronizado con curvas, escalera de secuenciación, tabla de magnitudes, trazabilidad | **No es una pantalla aparte**: el "detalle técnico" plegado del reporte simple ya trae trazabilidad, picos, magnitudes con confianza y tramos no auditables. **No hay** interruptor, vista por rol ni reproductor sincronizado (el componente existe solo en la maqueta falsa de `/reporte`) | Desglose del puntaje | **0,5** (interruptor que abre el detalle y vista por defecto según el rol; plan §8 #6 decía 1); reproductor sincronizado **2** (plan §8 #16, "si queda margen") | **Parcial**: el detalle ya está; el interruptor no |
| 9 | **PDF** (`ReportePDF1`, `ReportePDF2`) | A4: datos, resumen con puntaje, secuenciación, tabla por golpe; métricas con confianza, cómo leer los estados, trazabilidad, limitaciones | **Falta** (`pdf_ruta` es `null`) | El puntaje en la página 1; "cómo leer los estados" debe explicar solo los que el reporte usa | **1** (plan §8 #7, versión barata: impresión del detalle) | **Sí** (tabla 4.7 de la tesis; "no se recorta") |
| 10 | **Evolución** | "Vos, frente a vos mismo": puntaje con "+3", separación cadera-hombro con **rango habitual**, "cadera antes que tronco: Estable", barras de golpes con cadera antes que tronco por sesión, **huecos "sin dato"** | **No hay pantalla**: existe un componente (`evolucion-atleta.tsx`) con datos de ejemplo de abril y mayo que **ninguna ruta monta** y ningún enlace lleva ahí | Puntaje; "cadera antes que tronco" **como serie de calidad** (es el orden suspendido); "Mejoró / Bajó" con color; **mantener**: los huecos "sin dato", "solo se comparan sesiones del mismo encuadre" | **1** para una versión real mínima (ver `valor-sin-veredictos.md`); el plan §8 #13 solo la marcaba "Datos de ejemplo" (0,25) y #15 la hacía depender del puntaje (2) | **Sí, mínima**: es el seguimiento consigo mismo, el valor que quedó |
| 11 | **Perfil** | Rol, vista por defecto, mano dominante, privacidad, descargar y eliminar mis datos | **Maqueta con datos inventados** ("Marco Rivera", "23 sesiones", "1 alerta de carga", **planes y precios**, "Gestionar pago") con la marca "Datos de ejemplo". Nada se lee ni se guarda | Planes, precios y pago; los contadores "alerta de carga" y "42°" | **1,5** (plan §8 #10: rol, vista, mano dominante, descargar) + **1** eliminar cuenta y datos (#11) | **Sí**: acceso y supresión (Ley 25.326); el resto, recortable |
| 12 | **`/reporte` sin id** (no tiene maqueta) | — | **Reporte falso con valores inventados** detrás del login: "5 de 6 saques correctos", "Veredicto", "Coincide con el orden esperado". Es a donde apuntan los tres "Ver un reporte de ejemplo" | **Todo**: contradice las decisiones 031–036 | **0,25** retirarlo y redirigir el CTA | **Sí** (retirar) |
| 13 | **Tecnología** (no tiene maqueta) | — | Real; explica el pipeline | Revisar que no nombre "veredicto" (lo leí por arriba: no lo hace) | 0 | No |

---

## 2. Hallazgos que conviene mirar antes de la tabla

1. **La landing de producción hoy promete lo que las decisiones 035 y 036 retiraron** ("Veredicto en tres observaciones", tarjeta "✓ Coincide / Orden esperado"). Es lo primero que ven los profesores y se
   corrige con texto, sin diseño nuevo.
2. **"Ver un reporte de ejemplo" no funciona para un visitante**: `/reporte` pide sesión y redirige a Ingreso (lo verifiqué en producción). Y detrás del login hay un reporte inventado con veredictos. Las dos
   cosas se arreglan retirando esa ruta (fila 12).
3. **Evolución no existe como pantalla** aunque la especificación y la maqueta la ubican como parte del producto, y es justo la que carga el valor que queda (fila 10).
4. **Perfil sigue siendo la maqueta de Lovable** (otra persona, planes, pagos): para una demo "como público" hay que reemplazarla o, como mínimo, que no muestre nada inventado.
5. **El reporte real es un reporte de un golpe**: todo lo que la maqueta muestra de "6 golpes" (selector, consistencia, comparado) depende de Cargar con varios golpes (fila 5), que es el cuello de botella.
6. **Evolución real necesita datos reales:** al menos **2 sesiones del mismo gesto y encuadre subidas por el camino real** (2 × ~6 golpes por cada gesto que se quiera mostrar). Eso lo tiene que grabar Valentín.
   Los clips recortados del corpus son la conversión a ~120 fps con rampas (decisión 030) y no sirven. **Los originales del iPhone del Paso B** (`corpus-originales-reales`, ~200 fps con marcas reales) sí
   serían material real, pero habría que recortar cada golpe sin reencodear y que quede por debajo de 50 MB: **no lo probé**; es una opción más barata que grabar de nuevo.

---

## 3. Orden propuesto y recortes

**Criterio:** primero lo que hoy **contradice el producto** (barato y visible), después la **cadena que carga el valor** (varios golpes → vista de sesión → Evolución), después lo que **cierra "como público"**
(PDF, Perfil, eliminar), y al final lo que es solo diseño.

| Paso | Qué | Sesiones | Depende de |
| --- | --- | --- | --- |
| 1 | **Higiene de contenido** (filas 1, 4 y 12): landing sin veredicto ni puntaje, retirar `/reporte` falso y su CTA, conteo de la Biblioteca "medidos / no medibles", etiqueta única | 0,75 | — |
| 2 | **Cargar con varios golpes** (fila 5) + Procesando "golpe 2 de 6" (fila 6) | 2,25 | — |
| 3 | **Vista de sesión y consistencia entre golpes** (fila 7) | 1,5 | 2 |
| 4 | **Evolución mínima real** (fila 10) | 1 | 3 y **sesiones grabadas por Valentín** |
| 5 | **PDF barato** (fila 9) y **interruptor Simple/Detallado** (fila 8) | 1,5 | 3 |
| 6 | **Perfil real mínimo + eliminar cuenta y datos** (fila 11) | 2,5 | — |
| 7 | **Respaldo y recuperación al arranque** (plan §8 #12) | 1,25 | — |
| 8 | **Ensayo de la demo** (plan §8 #14) | 0,5 | todo |
| | **Núcleo** | **≈ 11,25** | |
| 9 | Diseño nuevo de Landing, Registro e Ingreso (filas 1–2) | 1–2 | — |
| 10 | Miniatura real en Biblioteca (fila 4); reproductor sincronizado (fila 8) | 0,25 + 2 | — |

Ritmo observado 1,5 sesiones por día: el núcleo cierra en ~8 días hábiles desde el 14/10 (~22–23/10); con el ritmo pesimista de 1 por día, ~25–26/10. **Es el mismo margen corto que ya tenía el plan; el
cambio es que el puntaje (2 sesiones del plan #15) sale y Evolución entra con 1.**

**Recortes si el 24/10 el núcleo no está al 80 %**, en este orden (lo primero cae primero):

1. Pasos 9 y 10 (todo lo de diseño y el reproductor).
2. El interruptor Simple/Detallado del paso 5 (queda el detalle técnico plegado, que ya existe).
3. "Descargar mis datos" del paso 6 (queda eliminar).
4. En el paso 2, de "varios golpes" a "hasta 3 golpes por sesión" (−0,75).

**No se recortan:** paso 1, paso 2–3 (sin varios golpes no hay producto), PDF, eliminar cuenta, ensayo.

**Se elimina del plan:** el puntaje de rendimiento (§8 #15, 2 sesiones) y "Evolución con la marca 'Datos de ejemplo'" (#13): una pantalla de ejemplo con datos inventados ya no tiene lugar al lado de
un producto cuyo punto es no inventar.

**Lo que necesito de Valentín para este orden:** (a) **dos sesiones de un gesto y un encuadre subidas por el camino real** (idealmente saque y drive en el mismo encuadre, ~6 golpes cada una), grabadas de nuevo
o recortadas de los originales del Paso B, para que Evolución muestre algo real antes del 28/10; (b) la prueba de registro con correo real (SMTP); (c) que mire él una vez las pantallas con sesión en producción.
