/**
 * Vista simple del reporte (pieza 8): del JSON del contrato v1.2 a lo que muestra la pantalla. Lógica pura, sin red ni DOM;
 * se prueba con `bun test` (frontend/tests/reporte-simple.test.ts).
 *
 * El frontend NO calcula nada biomecánico (especificación §1): ordena y redacta lo que ya midió y validó el motor.
 */

import type { ObservacionLeida } from "@/lib/estado-video";

export type Segmento = "pelvis" | "torso" | "brazo";

export const NOMBRE_SEGMENTO: Record<Segmento, string> = { pelvis: "cadera", torso: "tronco", brazo: "brazo" };

/** Colores de segmento de la especificación §2 (en gráficos). */
export const COLOR_SEGMENTO: Record<Segmento, string> = { pelvis: "#a78bfa", torso: "#22d3ee", brazo: "#f1f5f9" };

export type PicoLeido = { segmento: Segmento; instante_s: number; velocidad: number; confianza: number; unidad: string };

export type RepeticionLeida = {
  indice: number;
  auditable: boolean;
  orden_observado: Segmento[] | null;
  correcto: boolean | null;
  motivo_no_auditable: string | null;
  picos: PicoLeido[];
};

// --- observaciones ---------------------------------------------------------------------------------------------------

/** Orden de importancia (R3: lo que más pide atención primero; "sin evaluar" es un dato, no un juicio). */
const PRIORIDAD = ["alerta_de_carga", "desvio_leve", "correcto", "no_auditable", "sin_evaluar"] as const;

/** Nivel 1 (CLAUDE.md §3): máximo TRES observaciones, visibles sin desplazamiento. El resto queda en el detalle. */
export const MAX_OBSERVACIONES = 3;

export function masImportantes(
  observaciones: readonly ObservacionLeida[],
  max: number = MAX_OBSERVACIONES,
): { visibles: ObservacionLeida[]; ocultas: ObservacionLeida[] } {
  const rango = (s: string) => {
    const i = (PRIORIDAD as readonly string[]).indexOf(s);
    return i < 0 ? PRIORIDAD.length : i;
  };
  // sort estable: dentro de una misma severidad se conserva el orden en que las escribió el motor
  const ordenadas = observaciones
    .map((o, i) => ({ o, i }))
    .sort((a, b) => rango(a.o.severidad) - rango(b.o.severidad) || a.i - b.i)
    .map((x) => x.o);
  return { visibles: ordenadas.slice(0, max), ocultas: ordenadas.slice(max) };
}

// --- secuencia -------------------------------------------------------------------------------------------------------

export type FraseSecuencia = {
  tipo: "orden" | "simultaneo" | "sin_dato";
  texto: string;
};

const SIMULTANEIDAD = /simultaneidad/i;

/** La frase bajo el gráfico de secuenciación: qué se observó, en el vocabulario de R2 (se observa, no se pudo medir). */
export function fraseDeSecuencia(rep: RepeticionLeida | null, fps: number | null): FraseSecuencia {
  if (!rep) return { tipo: "sin_dato", texto: "No se pudo medir el orden de este golpe." };
  if (rep.auditable && rep.orden_observado && rep.orden_observado.length === 3) {
    const [a, b, c] = rep.orden_observado.map((s) => NOMBRE_SEGMENTO[s]);
    return {
      tipo: "orden",
      texto: `Se observa que primero alcanzó su velocidad máxima tu ${a}, después tu ${b} y por último tu ${c}.`,
    };
  }
  if (rep.motivo_no_auditable && SIMULTANEIDAD.test(rep.motivo_no_auditable)) {
    const tasa = fps !== null ? `A ${Math.round(fps)} fps ` : "A esta frecuencia ";
    return {
      tipo: "simultaneo",
      texto:
        "Tu cadera y tu tronco alcanzaron su velocidad máxima casi al mismo tiempo. " +
        `${tasa}no se puede saber cuál fue primero, así que no lo evaluamos.`,
    };
  }
  return { tipo: "sin_dato", texto: "No se pudo medir el orden de este golpe con confianza suficiente." };
}

/** Los picos medidos, en el orden de las filas del gráfico (cadera, tronco, brazo). */
export function picosOrdenados(rep: RepeticionLeida | null): PicoLeido[] {
  const orden: Segmento[] = ["pelvis", "torso", "brazo"];
  return orden.flatMap((s) => (rep?.picos ?? []).filter((p) => p.segmento === s && Number.isFinite(p.instante_s)));
}

// --- lectura defensiva del JSON ----------------------------------------------------------------------------------------

type Json = Record<string, unknown>;

export function repeticionesDe(reporte: Json | null): RepeticionLeida[] {
  const sec = reporte?.secuenciacion as Json | undefined;
  const reps = sec?.repeticiones;
  return Array.isArray(reps) ? (reps as RepeticionLeida[]) : [];
}

export type DatosTrazabilidad = {
  fps_real: number | null;
  fps_nominal: number | null;
  fotogramas_perdidos_pct: number | null;
  puntos_interpolados_pct: number | null;
  /** Tasa de la grilla uniforme a la que se regularizó el tiempo (un fotograma = 1 / fps_grilla): la resolución real del orden. */
  fps_grilla: number | null;
  escala_conocida: boolean;
  version_motor: string | null;
  backend_pose: string | null;
  modo_captura: string | null;
};

function num(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

export function trazabilidadDe(reporte: Json | null): DatosTrazabilidad {
  const t = (reporte?.trazabilidad ?? {}) as Json;
  const reg = (t.regularizacion ?? null) as Json | null;
  return {
    fps_real: num(t.fps_real),
    fps_nominal: num(t.fps_nominal),
    fotogramas_perdidos_pct: num(t.fotogramas_perdidos_pct),
    puntos_interpolados_pct: reg ? num(reg.puntos_interpolados_pct) : null,
    fps_grilla: reg ? num(reg.fps_grilla) : null,
    escala_conocida: t.escala_temporal_conocida === true,
    version_motor: typeof t.version_motor === "string" ? t.version_motor : null,
    backend_pose: typeof t.backend_pose === "string" ? t.backend_pose : null,
    modo_captura: typeof t.modo_captura === "string" ? t.modo_captura : null,
  };
}

export type TramoNoAuditable = { desde_s: number; hasta_s: number; motivo: string };

export function tramosNoAuditablesDe(reporte: Json | null): TramoNoAuditable[] {
  const c = reporte?.cobertura as Json | undefined;
  const t = c?.tramos_no_auditables;
  return Array.isArray(t) ? (t as TramoNoAuditable[]) : [];
}

export function coberturaDe(reporte: Json | null): number | null {
  return num((reporte?.cobertura as Json | undefined)?.auditable_pct);
}
