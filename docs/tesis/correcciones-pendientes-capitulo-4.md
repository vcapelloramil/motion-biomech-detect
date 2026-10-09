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
| 11 | Todo el capítulo donde figure "240 fps" como tasa de captura | 240 fps. | **240 fps nominales; ~200 reales** en el iPhone 15 Pro Max usado (Fotos ⓘ lo muestra); varía por video (~170 con poca luz). | 029 |

Fuera del Capítulo 4, pero para la redacción: las limitaciones que registran las decisiones 020 (modo de captura declarado) y 022 (reintento) van a los Capítulos 6 y 7.
