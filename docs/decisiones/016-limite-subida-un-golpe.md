# Decisión 016 — Límite de subida del MVP: un video por golpe, hasta 50 MB (TENTATIVA)

**Fecha:** 29 de septiembre de 2026
**Estado:** **TENTATIVA** — se confirma o se revierte con el criterio de verificación de más abajo, no antes.
**Afecta a:** Etapa 4.5 (esqueleto) · Etapa 8 (subida real desde el frontend) · protocolo de grabación ·
decisión 013 (protocolo, ficha de cada toma)

---

## El problema

El plan gratuito de Supabase Storage limita cada archivo subido a 50 MB (`docs/plan-desarrollo.md`, Etapa
4.5, con las fuentes verificadas el 29/9/2026). Medido sobre los clips reales de la Fase B: una repetición
recortada (un solo gesto) pesa 20–45 MB en la mayoría de los casos; un clip sin cortar con varias
repeticiones pesa 400–430 MB. El diseño del motor (apartado 4.3.3 de la tesis) asume que un video puede
contener varias repeticiones y que el sistema las segmenta; eso es incompatible con el límite gratuito.

## Decisión (Valentín, 29/9/2026)

**Para el MVP, se parte de un video por golpe** (una sola repetición), de **hasta 50 MB**. La pantalla de
carga rechaza los archivos más grandes con un mensaje que pide recortar a un solo golpe. **La subida por
partes (protocolo TUS, ya identificado como alternativa técnica) queda fuera del alcance del MVP.**

Si esto funciona bien, **el plan gratuito de Supabase alcanza para el MVP** y no se pasa a Pro (USD 25/mes)
por este motivo. Es una decisión que reduce alcance (el usuario recorta antes de subir, en vez de subir el
video completo del gesto) a cambio de no pagar y de no construir subida por partes antes de la entrega.

## Criterio de verificación — CUÁNDO se confirma o se revierte

**No se confirma con esta decisión ni con el razonamiento de arriba.** Se confirma cuando se pruebe el flujo
completo (subida → procesamiento → reporte) con clips reales de una repetición, en la Etapa 8 (interfaz
conectada) o antes, en el esqueleto de la Etapa 4.5 si se llega a probar la subida desde una pantalla.

- **Se da por buena** si los clips de una repetición entran cómodos en el límite, el recorte previo no
  genera fricción relevante en las pruebas de usabilidad de la Etapa 9 (apartado 4.6.6), y el reporte sale
  correcto sobre ese material.
- **Se reevalúa** si aparece cualquiera de estos problemas: clips de una repetición que no entran en 50 MB
  con cierta frecuencia (por ejemplo, saques largos o tomas con más preparación); las pruebas de usabilidad
  muestran que pedirle al usuario que recorte antes de subir es una fricción real, no cosmética; o el
  criterio 1 (repetibilidad) necesita comparar varias repeticiones de una sesión y el flujo de "una subida
  por golpe" lo vuelve incómodo para el usuario final (distinto del caso de investigación, donde igual se
  cortan a mano). Reevaluar significa volver a esta decisión, no cambiar el límite en silencio.

## Consecuencias

- **Protocolo de grabación:** se agrega la indicación de recortar a un solo golpe antes de considerar un
  clip como unidad de subida (`docs/protocolo-grabacion.md`, §7). No cambia cómo se graba (sigue grabándose
  la sesión completa con varias repeticiones y pausas, apartado 2.5/2.6 de la tesis); cambia qué se
  considera la unidad que el sistema recibe.
- **Pantalla de carga (Etapa 8):** debe validar el tamaño antes de subir (o al fallar la subida) y mostrar
  un mensaje que explique el motivo y pida recortar a un solo golpe — no un error genérico de "archivo
  demasiado grande". No implementado todavía.
- **No bloquea la Etapa 4.5:** el esqueleto puede probarse con cualquier clip corto de una repetición ya
  disponible en la Fase B.
