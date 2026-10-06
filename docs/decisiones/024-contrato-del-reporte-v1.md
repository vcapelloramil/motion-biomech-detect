# Decisión 024 — Contrato del reporte v1.0: el único cambio antes de generar JSON reales

**Fecha:** 7 de octubre de 2026
**Estado:** vigente — implementado en `backend/app/schemas/reporte.py` y `docs/contrato-reporte.ejemplo.json`
(18 pruebas en `tests/unit/test_contrato_reporte.py`)
**Afecta a:** Etapa 5 (ensamblado del reporte, tarea 5.4) · API · frontend (Reporte simple) · decisiones 018, 020 y 004 ·
Anexo A de `docs/plan-desarrollo.md` (queda **superado**: la fuente del contrato es ahora `reporte.py` + el ejemplo JSON)

---

## El problema

El contrato se congeló en la Etapa 0, antes de que existiera el motor, y quedó desalineado con lo que se decidió después.
Había dos cambios pendientes desde la decisión 018 y la 020 ("antes de generar cualquier JSON real"), y el plan de punta a punta
(`docs/plan-mvp-punta-a-punta.md`) agrega dos más. Se hacen **juntos, en un solo paso**, para tocar el contrato una sola vez y
subir su versión, porque un reporte guardado tiene que seguir siendo interpretable aunque el motor evolucione (RNF-02, apartado 4.2.5).

## Qué cambia (contrato 0 → v1.0)

| Campo | Antes | Ahora | Motivo |
| --- | --- | --- | --- |
| `version_contrato` | no existía | obligatorio, `"1.0"` | RNF-02: cada reporte guardado declara con qué versión se escribió. |
| `Severidad` | `correcto`, `atencion`, `no_auditable` | `correcto`, `desvio_leve`, `alerta_de_carga`, `no_auditable` | Los cuatro estados de R3; igual a `alertas.severidad` de la base (decisión 018). `atencion` desaparece (se renombra a `desvio_leve`). |
| `trazabilidad.modo_captura`, `factor_ralentizacion`, `origen_factor` | no existían | obligatorios, vocabularios cerrados; `factor_ralentizacion` ≥ 1 | Decisión 020 (R4): lo declarado, el factor y su origen. Con esto la cuenta de `fps_real` se rehace desde el JSON. |
| `secuenciacion.resumen.dispersion_instante_pico_torso_ms` | obligatorio, ≥ 0 | opcional (`None`) | Con un video = un golpe no hay dispersión que calcular, y un 0 sería un dato inventado (R3). |
| `artefactos.overlay_url`, `pdf_url` | obligatorios, URL | **`overlay_ruta`, `pdf_ruta`**: opcionales, **ruta en Storage** | No existen en la primera entrega (video con esqueleto y PDF diferidos). Se guarda la **ruta**, no la URL: una URL firmada vence y el reporte se guarda (decisión 025: el cliente firma al leer). |
| `artefactos.fotogramas_clave` | no existía | lista de `{segmento, instante_s, ruta}` | Los tres momentos del golpe de la vista simple (spec §6), con las columnas `videos.ruta_fotograma_*` ya existentes. |

**Refinamiento sobre lo aprobado:** el plan proponía hacer `overlay_url` y `pdf_url` opcionales. Se los renombró a `*_ruta` además de hacerlos
opcionales, porque guardar una URL firmada en un JSON persistente deja un enlace muerto a los pocos minutos. Es un cambio de nombre en dos campos que
ningún código consumía todavía.

## Qué NO cambia, a propósito

- **Sin puntaje de rendimiento ni sus componentes.** El spec §10 los pide, pero se difieren (Valentín, 7/10): en una primera sesión saldrían "no auditable" o
  "desde tu 2.ª sesión". Si se incorporan, es un cambio de contrato (v1.1) con la fórmula congelada en una decisión de la Etapa 5.
- **`comparacion_propia` sigue opcional** (`None` sin sesión previa).
- `extra="forbid"` y las reglas de rango (confianza en [0, 1], porcentajes en [0, 100]) siguen igual.
- `Pico.confianza` sigue **obligatorio**: el motor todavía no la calcula por pico, y el ensamblador (tarea 5.4) tiene que calcularla (confianza media de los
  landmarks del segmento en el instante del pico). No se hace opcional para no habilitar un reporte con números sin confianza (R4).

## Alternativas consideradas

- **Dos cambios separados** (severidad ahora, artefactos después): dos subidas de versión y dos rondas de coordinación con la interfaz. Descartada.
- **Seguir con `*_url`** y firmar en el servidor al guardar: el enlace caduca dentro del JSON. Descartada.
- **Hacer `confianza` opcional por pico** para poder generar el primer JSON ya: abre la puerta a un número sin confianza. Descartada: se calcula.

## Consecuencias

- Las siguientes piezas se construyen contra v1.0: el ensamblador (`engine/`, tarea 5.4), la columna `jsonb` de `reportes_biomecanicos` (el reporte
  se guarda validado por este contrato) y el Reporte simple del frontend.
- El Anexo A de `docs/plan-desarrollo.md` queda como historia de la Etapa 0, no como especificación.
- Un cambio posterior a este contrato sube `version_contrato` y se registra en una decisión nueva que supersede a esta.
- Hay dos pruebas que mantienen alineados el contrato y la base: los vocabularios de `severidad` y de `modo_captura` se comparan contra las migraciones SQL.
