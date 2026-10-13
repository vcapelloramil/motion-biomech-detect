# Evolución de la demo: dos sesiones reales del corpus (13/10/2026) y, como opcional, sesiones nuevas

**Decisión de Valentín (13/10):** no depender de grabar. **La Evolución de la demo se arma con los originales del iPhone del corpus** (sesiones del 24/9 y del 25/9, saque en tres cuartos), recortados
sin recodificar. Las sesiones nuevas (con o sin cintas de color) quedan como **opcionales**; su protocolo está más abajo.

## A. Los recortes del corpus (hechos y verificados)

**Qué hay:** 18 recortes de golpes del **saque en tres cuartos**, en `C:\Users\valen\Desktop\corpus-originales-reales\recortes-evolucion\` (fuera del repositorio; los videos no se versionan). El detalle por
archivo está en `recortes.json` de esa carpeta. Reproducible: `python -m app.recortar_evolucion` (`backend/app/recortar_evolucion.py`).

**Cómo se hicieron:** `ffmpeg -c copy` desde el original, con las mismas ventanas del Paso B (`docs/resultados/corpus-real-alineacion.json`) y 0,3 s de margen; el corte arranca en el fotograma clave anterior
(~1 s). Se quitó el audio.

**Qué se verificó, por cada uno de los 18 (aritmética entera sobre las marcas de tiempo):**

| Comprobación | Resultado |
| --- | --- |
| Cada fotograma del recorte existe en el original **con la misma marca de tiempo** (salvo una constante) | 18 de 18 |
| **Ningún fotograma de la ventana falta**, y la ventana del Paso B queda completa | 18 de 18 |
| Tasa real medida del recorte | **199,3 a 201,1 fps** (la del original: ~200 fps) |
| Decodifica sin errores | 18 de 18 |
| Pesa menos de 50 MiB (el tope de Cargar) | 18 de 18 (el más grande, 49,2 MB) |
| El motor lo lee como captura real (`escala_temporal_conocida`, origen "marcas de tiempo", no "archivo convertido") | probado con 2 recortes (el motor completo no se corrió: ~5 min de pose por golpe en esta PC) |

**Sesiones y qué subir:**

| Sesión | Fecha a poner en Cargar | Archivos | Golpes |
| --- | --- | --- | --- |
| **1** | **24/09/2026** | `20260924_saque_trescuartos_toma01_golpe1.mov` … `golpe6.mov` | 6 |
| **2** | **25/09/2026** | `20260925_saque_trescuartos_toma02b_golpe1.mov` … `golpe6.mov` | 6 |
| 2 (opcional, +6) | 25/09/2026 | `20260925_saque_trescuartos_toma02c_golpe1.mov` … `golpe6.mov` | 6 |

**Cómo cargarlas** (cuando esté el paso 2, ya hecho): en Cargar, **una sesión por día**, *Golpe* = saque, *Encuadre* = **tres cuartos**, *Lado de la cámara* = **a la izquierda del jugador** (el lado no dominante: el jugador es diestro y la cámara
estuvo a su izquierda en todos los videos del corpus; confirmado por Valentín el 13/10/2026; las dos sesiones ya subidas lo tienen declarado así), *¿Cómo lo grabaste?* = **cámara lenta 240**, y **la fecha real** (24 y 25 de septiembre). Los archivos se eligen **desde la computadora**: no
hace falta "Formato: Actual" ni tocar nada en Fotos, porque el navegador sube el archivo tal cual.

**Qué esperar:** los mismos golpes que midió el Paso B (el mismo motor sobre la misma señal): sirve de control cruzado "producción contra Paso B". En el Paso B estas tomas dieron cadera primero o dentro de la
tolerancia; **el orden no se evalúa** (decisiones 035 y 036). Lo que Evolución muestra es la **separación cadera-hombro** por sesión y la variación entre golpes.

**Límites a declarar:** son las mismas dos sesiones con las que se validó el Criterio 3 (no una validación independiente) y un solo jugador. Para la demo alcanza: lo que se muestra es el sistema funcionando
sobre datos reales con trazabilidad, no una prueba nueva.

---

## B. Sesiones nuevas (opcional)

### Protocolo

**Para qué:** que Evolución muestre, en la demo (28–30/10), **datos reales de un mismo jugador en dos días distintos**, sin inventar nada (`docs/ux/valor-sin-veredictos.md` §3.3). Es el paso 6 del
orden vigente (`docs/plan-mvp-punta-a-punta.md` §8). Complementa a `docs/protocolo-grabacion.md` (lo que dice de la "comparación en el tiempo" rige acá) y no lo reemplaza.

**Quién:** Valentín (el mismo jugador del corpus). **Costo:** ~1 hora de grabación por sesión y ~30 minutos de recorte y carga.

## Qué grabar

| | Valor | Por qué |
| --- | --- | --- |
| **Gesto** | **Saque** | Es el único con D calibrado (el aviso de "el video parece de otro encuadre" funciona para el saque) y el gesto con respaldo bibliográfico de la tesis |
| **Encuadre** | **Tres cuartos** (cámara a ~45° por detrás, **del lado izquierdo del jugador**, el no dominante: el mismo de todo el corpus) | En el corpus la separación cadera-hombro es mayor en tres cuartos (30–33°) que en perfil (24–26°) y la variación habitual dentro de una sesión es de ~3°: un cambio real es más fácil de ver sobre ese ruido |
| **Sesiones** | **2 mínimo, 3 ideal**, en **días distintos** | Con 2 hay un cambio; con 3 aparece la banda propia ("tu variación habitual") |
| **Golpes por sesión** | **8 grabados**, subir **todos los que estén completos** (mínimo 6) | Con 4 golpes medidos hay dispersión; con 5 ordenables, repetibilidad del orden. Con 3 no hay ninguna de las dos |
| **Cada video** | **un solo golpe, 3 a 4 s** (≈ 1 s antes del inicio del movimiento y ≈ 1 s después del impacto), **menos de 50 MB** | Es lo que acepta Cargar; el recorte validado de 3,1 s (626 fotogramas) procesó en 117 s |
| **Duración de cada sesión** | ~20 min: **5 saques de calentamiento sin grabar**, después 8 grabados con **1 minuto de descanso** entre ellos, a ritmo de entrenamiento | Evita que el cansancio o el cambio de luz se confundan con un cambio entre sesiones |

## Lo que tiene que ser **igual** en las dos sesiones

Evolución solo compara sesiones del mismo gesto y encuadre, y el sesgo del instrumento solo se cancela si **la geometría no cambia**:

1. **Mismo lugar, misma marca en el piso**: dos cruces de cinta (dónde se para el jugador y dónde va el trípode). **Sacar una foto de las marcas** y usarla el segundo día.
2. **Misma altura del celular** (~1 m, a la cadera), **misma distancia** (4 a 5 m) y **mismo lado** de la cámara respecto del jugador (anotar derecha o izquierda).
3. **Misma configuración:** 1080p a 240 fps, horizontal, el mismo celular, el mismo modo.
4. **Misma luz y misma hora**, de día y sin contraluz; ropa ajustada de color contrastante con el fondo, la misma raqueta y el mismo calzado.
5. **Anotar** altura, distancia y condición de luz (la planilla de `docs/protocolo-grabacion.md`), y **la fecha real** de cada grabación.

## Cómo elegir los golpes (para no sesgar la muestra)

- **Se descartan solo por razones técnicas:** el cuerpo sale del cuadro, el celular se movió, algo tapa al jugador, el video se cortó.
- **Nunca por cómo salió el golpe.** Si se eligieran "los buenos", Evolución mostraría una mejora que es de la selección y no del jugador.

## Cómo subirlos (cuando esté lista la carga con varios golpes)

1. En Fotos: recortar cada saque y **sacar la cámara lenta** (barra de rayitas, todo el tramo a velocidad normal).
2. Subir con **Opciones → Formato: Actual** o desde la app Archivos.
3. En Cargar: **una sesión por día**, gesto *saque*, encuadre *tres cuartos*, lado de la cámara **izquierda** (siempre el mismo del corpus: con otro lado la comparación con las sesiones del 24 y 25/9 deja de ser válida y la Evolución lo avisa), *"¿Cómo lo grabaste?" = cámara lenta 240*, y **en la fecha, la fecha real de la grabación** (se puede
   editar; Evolución ordena por esa fecha).
4. Guardar los **originales sin modificar** aparte (Archivos o iCloud).

## Cuándo

**Grabar no depende de la aplicación**: solo la carga necesita "varios golpes" (paso 2 del orden). Se puede grabar y recortar antes, y subir cuando esté la carga. Lo único que importa es que **sean dos
días distintos** y que los dos días se cumplan los puntos de "tiene que ser igual". Con la carga de hoy (un golpe por sesión) cada golpe quedaría como una sesión aparte y Evolución no serviría.

## Opcional: una tercera sesión con un cambio **intencional y declarado**

Si se quiere ver que Evolución detecta un cambio y no solo "se mantuvo": una sesión de 8 saques en la que Valentín **cambia a propósito una cosa** (por ejemplo, saca sin rotar los hombros tanto), con la misma
geometría. En la demo se **rotula como "cambio intencional"**: es una prueba de sensibilidad del sistema, no un resultado del jugador. **No se simula un cambio sobre los datos.**

## Qué se espera ver (sin prometerlo)

- **Dos sesiones sin cambio intencional:** lo esperable es "se mantuvo" (en el Criterio 3, la separación fue consistente entre sesiones en la mayoría de los grupos: Δ ≤ σ_w ≈ 3°). **Es un resultado válido**
  de la demo: demuestra que el sistema no inventa cambios.
- **Un cambio de más de ~3°** entre sesiones se mostrará como "cambió más que tu variación habitual", sin decir que es mejor o peor.
