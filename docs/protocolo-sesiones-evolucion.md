# Protocolo: dos sesiones reales para la pantalla Evolución (13/10/2026)

**Para qué:** que Evolución muestre, en la demo (28–30/10), **datos reales de un mismo jugador en dos días distintos**, sin inventar nada (`docs/ux/valor-sin-veredictos.md` §3.3). Es el paso 6 del
orden vigente (`docs/plan-mvp-punta-a-punta.md` §8). Complementa a `docs/protocolo-grabacion.md` (lo que dice de la "comparación en el tiempo" rige acá) y no lo reemplaza.

**Quién:** Valentín (el mismo jugador del corpus). **Costo:** ~1 hora de grabación por sesión y ~30 minutos de recorte y carga.

## Qué grabar

| | Valor | Por qué |
| --- | --- | --- |
| **Gesto** | **Saque** | Es el único con D calibrado (el aviso de "el video parece de otro encuadre" funciona para el saque) y el gesto con respaldo bibliográfico de la tesis |
| **Encuadre** | **Tres cuartos** (cámara a ~45° por detrás del lado de la raqueta) | En el corpus la separación cadera-hombro es mayor en tres cuartos (30–33°) que en perfil (24–26°) y la variación habitual dentro de una sesión es de ~3°: un cambio real es más fácil de ver sobre ese ruido |
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
3. En Cargar: **una sesión por día**, gesto *saque*, encuadre *tres cuartos*, el lado de la cámara, *"¿Cómo lo grabaste?" = cámara lenta 240*, y **en la fecha, la fecha real de la grabación** (se puede
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
