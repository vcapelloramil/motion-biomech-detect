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
  /** Inicio de la ventana analizada, en segundos desde el inicio del VIDEO. Los instantes de los picos se cuentan desde acá. */
  desde_s?: number | null;
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

const coma = (x: number, dec = 1) => x.toFixed(dec).replace(/\.0+$/, "").replace(".", ",");

/** "1 fotograma ≈ 5 ms a 200 fps reales": la resolución del ARCHIVO, no la de la grilla de 240 Hz a la que se regulariza (12/10). */
export function resolucionTexto(fpsReal: number | null): string | null {
  if (fpsReal === null || !(fpsReal > 0)) return null;
  return `1 fotograma ≈ ${coma(1000 / fpsReal)} ms a ${Math.round(fpsReal)} fps reales`;
}

/** La frase bajo el gráfico de secuenciación: qué se observó, en el vocabulario de R2 (se observa, no se pudo medir).
 *  `fps` es la tasa REAL media del archivo; `toleranciaMs`, la tolerancia con que el motor decidió "ordenable" (reporte v1.3). */
export function fraseDeSecuencia(rep: RepeticionLeida | null, fps: number | null, toleranciaMs: number | null = null): FraseSecuencia {
  if (!rep) return { tipo: "sin_dato", texto: "No se pudo medir el orden de este golpe." };
  if (rep.auditable && rep.orden_observado && rep.orden_observado.length === 3) {
    const [a, b, c] = rep.orden_observado.map((s) => NOMBRE_SEGMENTO[s]);
    return {
      tipo: "orden",
      texto: `Se observa que primero alcanzó su velocidad máxima tu ${a}, después tu ${b} y por último tu ${c}.`,
    };
  }
  // Cadera y tronco medidos y ordenables, brazo sin medir (le faltó parte del movimiento): se informa lo que se midió.
  if (rep.auditable && rep.orden_observado && rep.orden_observado.length === 2) {
    const [a, b] = rep.orden_observado.map((s) => NOMBRE_SEGMENTO[s]);
    return {
      tipo: "orden",
      texto: `Se observa que primero alcanzó su velocidad máxima tu ${a} y después tu ${b}. El brazo no se pudo medir en este golpe.`,
    };
  }
  if (rep.motivo_no_auditable && SIMULTANEIDAD.test(rep.motivo_no_auditable)) {
    const resolucion = resolucionTexto(fps);
    const tolerancia = toleranciaMs !== null ? ` (a menos de ${coma(toleranciaMs)} ms uno del otro)` : "";
    return {
      tipo: "simultaneo",
      texto:
        `Tu cadera y tu tronco alcanzaron su velocidad máxima casi al mismo tiempo${tolerancia}. ` +
        `A esta resolución${resolucion ? ` (${resolucion})` : ""} no se puede saber cuál fue primero, así que no lo evaluamos.`,
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
  /** Con qué tolerancia el motor decidió "ordenable" (contrato 1.3; null en un reporte anterior). */
  tolerancia_orden_ms: number | null;
  puntos_interpolados: number | null;
  puntos_de_la_grilla: number | null;
  hueco_maximo_ms: number | null;
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
    tolerancia_orden_ms: num(t.tolerancia_orden_ms),
    puntos_interpolados: reg ? num(reg.puntos_interpolados) : null,
    puntos_de_la_grilla: reg ? num(reg.puntos_de_la_grilla) : null,
    hueco_maximo_ms: reg ? num(reg.hueco_maximo_ms) : null,
  };
}

// --- magnitudes articulares como dato (plan §8, punto 3) ----------------------------------------------------------------

/** Error medido contra goniometría manual ciega (decisión 015, Criterio 2). Es lo que se muestra junto al valor (R4). */
export const ERROR_VALIDADO = {
  rodilla: { media: 8.5, p95: 19.2 },
  codo: { media: 12.5, p95: 36.4 },
} as const;

export type MagnitudLeida = {
  nombre: string;
  etiqueta: string;
  valor: number | null;
  unidad: string;
  confianza: number;
  auditable: boolean;
  /** Qué tan confiable es este valor y por qué, en una línea (sin literatura: es la validación propia del proyecto). */
  nota: string;
};

const LADO_FEM: Record<string, string> = { izq: "izquierda", der: "derecha" };
const LADO_MASC: Record<string, string> = { izq: "izquierdo", der: "derecho" };

/** Las magnitudes que NO son velocidades pico: separación cadera-hombro y ángulos de rodilla y codo. Ninguna lleva estado de juicio. */
export function magnitudesDe(reporte: Json | null): MagnitudLeida[] {
  const m = reporte?.metricas;
  if (!Array.isArray(m)) return [];
  const salida: MagnitudLeida[] = [];
  for (const x of m as Json[]) {
    const nombre = typeof x.nombre === "string" ? x.nombre : "";
    const base = {
      nombre,
      valor: num(x.valor),
      unidad: typeof x.unidad === "string" ? x.unidad : "grados",
      confianza: num(x.confianza) ?? 0,
      auditable: x.auditable === true,
    };
    if (nombre === "separacion_cadera_hombro_max") {
      salida.push({
        ...base,
        etiqueta: "Separación cadera-hombro máxima",
        nota: base.auditable
          ? "Ángulo entre el eje de las caderas y el de los hombros, el máximo del golpe. Medido en 3D; su repetibilidad entre sesiones se midió, sin goniometría."
          : "No se midió en una parte suficiente de la ventana del golpe.",
      });
      continue;
    }
    const a = /^angulo_(rodilla|codo)(?:_(izq|der))?_en_pico_tronco$/.exec(nombre);
    if (a) {
      const parte = a[1] as "rodilla" | "codo";
      const lado = a[2] ? ` ${(parte === "rodilla" ? LADO_FEM : LADO_MASC)[a[2]]}` : "";
      const e = ERROR_VALIDADO[parte];
      salida.push({
        ...base,
        etiqueta: `Ángulo ${parte === "rodilla" ? "de la rodilla" : "del codo"}${lado} en el pico del tronco`,
        nota: base.auditable
          ? `En el plano de la imagen. Error medido contra goniometría manual: ${String(e.media).replace(".", ",")}° de media y hasta ` +
            `${String(e.p95).replace(".", ",")}° en el 95 % de los casos.` +
            (parte === "codo" ? " El codo del brazo dominante suele tener poca cobertura." : "")
          : "No se informa: alguna de las tres articulaciones no se detectó con confianza suficiente (0,6) en ese fotograma.",
      });
    }
  }
  return salida;
}

// --- artefactos (contrato 1.3): rutas en Storage, nunca URLs ------------------------------------------------------------

export type FotogramaClaveLeido = { segmento: Segmento; instante_s: number; ruta: string };
export type OverlayLeido = { ruta: string; desde_s: number; hasta_s: number; factor_lento: number | null };
export type ArtefactosLeidos = { fotogramas: FotogramaClaveLeido[]; overlay: OverlayLeido | null };

/** Lo que el motor generó. Ausente = "no generado" (no "cero"): la pantalla no muestra la sección, sin inventar nada. */
export function artefactosDe(reporte: Json | null): ArtefactosLeidos {
  const a = (reporte?.artefactos ?? {}) as Json;
  const orden: Segmento[] = ["pelvis", "torso", "brazo"];
  const crudos = Array.isArray(a.fotogramas_clave) ? (a.fotogramas_clave as Json[]) : [];
  const fotogramas = orden.flatMap((s) =>
    crudos
      .filter((f) => f.segmento === s && typeof f.ruta === "string" && f.ruta.length > 0 && num(f.instante_s) !== null)
      .map((f) => ({ segmento: s, instante_s: f.instante_s as number, ruta: f.ruta as string })),
  );
  const info = (a.overlay_info ?? null) as Json | null;
  const overlay =
    typeof a.overlay_ruta === "string" && a.overlay_ruta.length > 0
      ? {
          ruta: a.overlay_ruta,
          desde_s: num(info?.desde_s) ?? 0,
          hasta_s: num(info?.hasta_s) ?? 0,
          factor_lento: num(info?.factor_lento),
        }
      : null;
  return { fotogramas, overlay };
}

// --- detalle: fundamentos sin repetir ------------------------------------------------------------------------------------

export type FundamentoObservacion = {
  severidad: string;
  texto: string;
  /** null si ya se mostró idéntico en una observación anterior (la línea de instantes se repetía en las tarjetas). */
  fundamento: string | null;
  referencia: string | null;
};

/** Para el nivel 3: cada observación con su fundamento y su fuente, y cada línea de fundamento una sola vez. */
export function fundamentosSinRepetir(observaciones: readonly ObservacionLeida[]): FundamentoObservacion[] {
  const vistos = new Set<string>();
  return observaciones.map((o) => {
    const f = o.fundamento ?? null;
    const dup = f !== null && vistos.has(f);
    if (f !== null) vistos.add(f);
    return { severidad: o.severidad, texto: o.texto, fundamento: dup ? null : f, referencia: o.referencia ?? null };
  });
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
