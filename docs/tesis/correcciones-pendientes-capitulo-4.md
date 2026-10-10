# Correcciones pendientes del Capítulo 4 (marco tecnológico)

Lista viva de lo que el Capítulo 4 (`docs/tesis/capitulo-4-marco-tecnologico.md`) dice y **ya no refleja lo construido o decidido**. No se edita el capítulo
todavía: se acumula acá y se redacta de una vez (misma práctica que la lista de pendientes de `CLAUDE.md` §5). Cada ítem cita la decisión que lo originó.

| # | Apartado | Qué dice hoy | Qué corresponde | Decisión |
| --- | --- | --- | --- | --- |
| 1 | §4.5.1 — diagrama de topología (línea ~665) y párrafo "Interfaz en Vercel" (~675) | El frontend se publica en **Vercel**, con vistas previas por rama. | Se publica en **Cloudflare** (Workers), donde el prototipo ya venía configurado. | 026 |
| 2 | Tablas de costos y del stack (~727, ~738) y diagramas de despliegue (~893, ~896) | Fila "Vercel — Hobby — USD 0". | Reemplazar por el hosting en Cloudflare (verificar cuotas del plan gratuito antes de escribir cifras). | 026 |
| 3 | §4.4.7 / stack | La interfaz se describe como producto del prototipo de Lovable. | El repositorio es la **única fuente**; Lovable se usó para el prototipo inicial y dejó de editar código el 7/10/2026. | 026 |
| 4 | §4.2.3 — flujo de datos (diagrama ~124 y secuencia ~168–169, texto ~192) | La API "genera la URL firmada de carga" y el cliente sube con ella. | El cliente sube **directo a Storage con su sesión** (RLS por carpeta); no hay URL firmada de carga. La lectura sí usa URL firmadas de vida corta. | 025 |
| 5 | §4.2.5 — tabla de operaciones (~219–227) | Siete operaciones por la API: alta de análisis, confirmación de carga, consulta de estado, obtención del reporte, listado, evolución y verificación. | La API expone **tres**: verificación de servicio, confirmación de carga y reintento. El alta, el estado, el reporte, el listado y la evolución son **lecturas/escrituras directas a Supabase con RLS**. | 025 |
| 6 | §4.2.4 — máquina de estados (~198–211) | Incluye `descartado` ("sin carga en 30 min") y `parcial` como estado final. | `descartado` no existe en el esquema; `fallido → encolado` está acotado por la decisión 022; el reintento desde `parcial` queda pendiente. | 022 |
| 7 | §4.4 y §4.5 — autenticación | Identidad verificada "en la API". | La API valida el JWT de Supabase contra sus claves públicas (JWKS) **y** chequea que el video sea del usuario (la API usa `service_role`, que ignora RLS). | 025 |
| 8 | §4.5.4 y tabla de planes (~697) | Servidor de cómputo "0,5 vCPU / 512 MB" para el MVP y "1–2 vCPU / 2 GB" como alternativa. | Free durante el desarrollo y las pruebas; **Standard (1 CPU / 2 GB)** para la defensa y cuando la espera o los cortes de Free molesten. Starter tiene la misma memoria que Free. | 017, 023 |
| 9 | §4.4.6 — esquema de datos | Siete tablas. | Nueve tablas, `sesiones` agregada, permisos por columna sobre `videos` y `sesiones`. | 018, 022 |
| 10 | RNF-01 y su plan de pruebas (tabla de requisitos no funcionales) | "Prueba con archivos de 30, 60, 120 y 240 fps y con video grabado en cámara lenta." | Agregar: archivo **convertido por el teléfono** al subirlo (100 fps o menos aunque se haya grabado a 240) y archivo con **fotogramas perdidos** (tasa real media ~199 contra 240 nominales). RNF-01 exige leer la tasa **real**: el corpus la asumió. | 029 |
| 11 | Todo el capítulo donde figure "240 fps" como tasa de captura | 240 fps. | **240 fps nominales; ~200 reales** en el iPhone 15 Pro Max usado (medido en 16 grabaciones: 199,9–201,0; ~170 en una con poca luz, según Fotos ⓘ). | 029, 030 |
| 12 | RNF-01 y 4.3.4 (Criterio 1, "120–240 fps") | El corpus propio "a 240 fps". | **El corpus propio es un remuestreo a ~120 fps con rampas de velocidad**: el procesamiento asumió 240 y por eso **no cumplía RNF-01** ("lee la tasa real del archivo y nunca la asume"). Muestreo efectivo: **120 fps (aptitud "reducido", en el borde inferior)**. | 030 |


## Anotaciones para el Capítulo 7 (resultados) y el Capítulo 6 (riesgos y limitaciones)

Registradas el 9/10/2026 con las decisiones 029 y 030. **No se redacta nada todavía**; se acumula acá.

1. **El corpus no cumplía RNF-01.** El procesamiento asumió 240 fps. La captura nominal fue 240, la **tasa real media del teléfono ~200 fps** (199,9–201,0 en 16 grabaciones; ~170 en otra con poca luz según Fotos),
   y el **muestreo de los archivos horneados con que se midió todo fue 120 fps** (1,67 fotogramas reales por fotograma horneado, ~7 % de fotogramas repetidos, rampas a velocidad normal en los extremos del archivo).
2. **Escala de velocidades y de milisegundos.** Las velocidades absolutas medidas con ese corpus están **sobreestimadas ×2,0** y los intervalos en ms **subestimados ×0,5** (cualquier cifra, techo de plausibilidad o Fleisig sobre estos datos).
   Los **ángulos no cambian** (Criterio 2 vale).
3. **Fragilidad del Criterio 1.** Pelvis y torso están a **0–3 fotogramas** en el 69 % de las repeticiones (mediana 2): en esas, el orden estimado es sensible a cualquier perturbación del tiempo (en la simulación
   cambió en el ~11–14 % de las corridas). **El único grupo que cumple** (`drive|perfil`, 1a = 0,83 frente a 0,80) **es frágil**: sigue cumpliendo en 10 de 12 y en 6 de 12 mundos perturbados según la tolerancia. Las conclusiones
   negativas son robustas (19 de 25 combinaciones no cumplen en ningún mundo). **Decirlo explícitamente.**
4. **La resolución temporal es un límite declarado:** a 120 fps un fotograma son 8,3 ms; con empates de 0–3 fotogramas el orden pelvis-torso es, en gran parte, **no resoluble** con este material (consistente con las salvedades de la decisión 015).
5. **La tasa real del iPhone varía por grabación y depende del formato de subida.** "Archivos" u "Opciones → Formato: Actual" conservan las marcas reales (~200 fps medios, 17 % de fotogramas perdidos); el formato por defecto de Fotos convierte a
   H.264 y baja a 100 fps o menos. **El sistema no puede deducir la tasa de la declaración del usuario:** la lee del archivo (RNF-01).
6. **Método:** emparejamiento por fecha de creación de los 16 originales con los horneados (16/16), alineamiento por contenido (15 pares, orden monótono 99,1–99,9 %), ubicación de 88 repeticiones (86 en la meseta).
   Reproducible con los scripts del repositorio y `docs/resultados/tasa-real-*.json`; los videos **no** están en el repositorio.
7. **Si se recalcula** (plan en `docs/plan-recalculo-corpus-tasa-real.md`): Criterios 1 y 3 con el eje de tiempo real, tolerancia en milisegundos fijada de antemano, informando lado a lado contra la medición original.

8. **Primera grabación propia por el flujo completo (9/10/2026): cadera y tronco a un fotograma.** Saque de perfil grabado a 240 fps nominales con el iPhone, subido con "Opciones → Formato: Actual" (`IMG_6376.mov`,
   2,5 s, 1920×1080): tasa real media **199,6 fps** (nominal 239,98; **16,8 %** de fotogramas perdidos). Con el tiempo reacomodado a una grilla uniforme de 240 Hz (**98 de 597 puntos interpolados, 16,4 %**), el pico de
   tronco quedó en 0,300 s y el de cadera en 0,304 s: **una separación de 4,2 ms, es decir, un fotograma de la grilla de 240 Hz (≈ 5 ms a la tasa real media de ~200 fps)**. Está dentro de la tolerancia de la decisión 014
   (τ = 1 fotograma): el orden **no es establecible** y el reporte lo informa como "simultaneidad al límite de resolución". **Dato para la autovalidación de la semana 4 (Criterio 1)**, con tres cuidados al citarlo:
   es **n = 1**, está **en el límite de resolución** y **no es evidencia a favor ni en contra** del orden "tronco primero" medido en el corpus. Sí ilustra el punto 3: la misma grabación, con el tiempo sin reacomodar
   (eje uniforme sobre fotogramas perdidos), daba la cadera 10 ms antes que el tronco (2 fotogramas), un orden aparente producido por el eje irregular.
9. **El conteo de fotogramas del contenedor puede no coincidir con el del decodificador.** En esa misma grabación, 501 paquetes visibles contra 499 fotogramas decodificados (los dos últimos no se entregan). El sistema
   no asigna tiempo "adivinando": alinea con las marcas de los fotogramas realmente decodificados y verifica que sean un subconjunto de las del contenedor. Va al plan de pruebas de RNF-01 junto con el archivo convertido.
10. **Latencia (Criterio 4), primer dato:** ~9 min de punta a punta en Render Free para un golpe de 2,5 s a 1080p (medido a mano); desde la migración `20261010000000` el servidor registra encolado, inicio y fin por video.
    Detalle y método en `docs/resultados/criterio4-latencia.md`. Se informa el valor medido, sin umbral.

Fuera del Capítulo 4, pero para la redacción: las limitaciones que registran las decisiones 020 (modo de captura declarado) y 022 (reintento) van a los Capítulos 6 y 7.
