/**
 * Estado de un video (golpe) en lenguaje llano — pieza 7. Lógica pura, sin red ni DOM: se prueba con `bun test`
 * (frontend/tests/estado-video.test.ts).
 *
 * Reglas: R2 (vocabulario: se observa / se midió / no se pudo medir; nunca diagnosticar ni prescribir) y R3 (un dato
 * faltante nunca se rellena con una estimación).
 */

export type EstadoVideo = "pendiente" | "encolado" | "procesando" | "completado" | "parcial" | "fallido";
export type MotivoFallo = "modo_captura_incompatible" | "error_inesperado" | "archivo_convertido";

/** Tope de intentos de la API para un error inesperado (`KINETIQ_MAX_INTENTOS`, decisión 022). Solo para mostrar "intento N de 3". */
export const MAX_INTENTOS = 3;

export type FilaVideo = {
  id: string;
  sesion_id: string;
  estado: EstadoVideo;
  motivo_fallo: MotivoFallo | null;
  fps_real: number | string | null;
  intentos: number;
  creado_en: string;
  encolado_en?: string | null;
  inicio_procesamiento_en?: string | null;
  fin_procesamiento_en?: string | null;
  ruta_almacenamiento?: string;
};

const EN_CURSO: readonly EstadoVideo[] = ["pendiente", "encolado", "procesando"];

export function enCurso(estado: EstadoVideo): boolean {
  return EN_CURSO.includes(estado);
}

export function esTerminal(estado: EstadoVideo): boolean {
  return !enCurso(estado);
}

export function numero(v: number | string | null | undefined): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
}

// --- progreso --------------------------------------------------------------------------------------------------------

export const PASOS = [
  { id: "subido", etiqueta: "Video subido" },
  { id: "cola", etiqueta: "En cola" },
  { id: "analisis", etiqueta: "Analizando" },
  { id: "listo", etiqueta: "Listo" },
] as const;

/** Índice del paso en curso (0 a 3). Un fallo se queda en el paso donde estaba. */
export function pasoActual(estado: EstadoVideo): number {
  switch (estado) {
    case "pendiente":
      return 0;
    case "encolado":
      return 1;
    case "procesando":
      return 2;
    case "fallido":
      return 2;
    default:
      return 3;
  }
}

/**
 * Qué hace el motor, en el orden real del pipeline (CLAUDE.md §4). El servidor todavía no informa en qué etapa va, así que
 * la pantalla NO marca etapas como hechas: lo contrario sería inventar un avance (R3).
 */
export const ETAPAS = [
  { id: "E0", titulo: "Leyendo el video", detalle: "Se lee la frecuencia de captura real de cada fotograma." },
  { id: "E1", titulo: "Detectando tu cuerpo", detalle: "Se ubican los puntos del cuerpo en cada cuadro." },
  { id: "E1b", titulo: "Descartando puntos dudosos", detalle: "Lo que no se ve con confianza se marca como no auditable: nunca se inventa." },
  { id: "E3", titulo: "Limpiando la señal", detalle: "Se filtra el temblor sin correr los instantes de los picos." },
  { id: "E4", titulo: "Midiendo giros y orden de picos", detalle: "Se calcula cuándo alcanzan su velocidad máxima la cadera, el tronco y el brazo." },
  { id: "E5", titulo: "Armando tu reporte", detalle: "Se juntan los resultados con su confianza y su trazabilidad." },
] as const;

// --- tiempos ---------------------------------------------------------------------------------------------------------

export function formatearDuracion(segundos: number): string {
  const s = Math.max(0, Math.round(segundos));
  if (s < 60) return `${s} s`;
  const m = Math.floor(s / 60);
  const r = s % 60;
  return r === 0 ? `${m} min` : `${m} min ${r} s`;
}

/** Segundos entre dos instantes ISO; `null` si falta alguno o no se pueden leer. */
export function segundosEntre(desde: string | null | undefined, hasta: string | null | undefined): number | null {
  if (!desde || !hasta) return null;
  const a = Date.parse(desde);
  const b = Date.parse(hasta);
  if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) return null;
  return (b - a) / 1000;
}

/**
 * Latencia de punta a punta (Criterio 4): del encolado al fin del procesamiento. Si el video es anterior a la migración de
 * tiempos no hay `encolado_en` y se devuelve `null` (no se estima).
 */
export function latenciaDe(v: Pick<FilaVideo, "encolado_en" | "fin_procesamiento_en">): number | null {
  return segundosEntre(v.encolado_en, v.fin_procesamiento_en);
}

// --- fallos y resultados ---------------------------------------------------------------------------------------------

export type AccionFallo = "subir_otro" | "corregir_modo" | "reintentar" | "ninguna";

export type TextoFallo = { titulo: string; texto: string; accion: AccionFallo; contador?: string };

/** Mensaje para un video `fallido`, por `motivo_fallo` (decisiones 022 y 030). El texto en lenguaje llano lo pone el frontend. */
export function textoDeFallo(
  motivo: MotivoFallo | null,
  datos: { fps?: number | null; intentos?: number } = {},
): TextoFallo {
  const intentos = datos.intentos ?? 0;
  if (motivo === "archivo_convertido") {
    const n = datos.fps !== null && datos.fps !== undefined ? `llegó a ${Math.round(datos.fps)} fps` : "llegó con menos fps de los necesarios";
    return {
      titulo: "El teléfono convirtió el video",
      texto:
        `Tu teléfono convirtió el video al subirlo y ${n}, por debajo de los 120 que hacen falta. ` +
        "En el selector tocá Opciones → Formato: Actual, o subilo desde la app Archivos.",
      accion: "subir_otro",
    };
  }
  if (motivo === "modo_captura_incompatible") {
    return {
      titulo: "No pudimos confirmar la velocidad del video",
      texto:
        "La forma de grabación que indicaste no coincide con el archivo. Revisá cómo lo grabaste y volvé a intentar, " +
        "o volvé a grabarlo.",
      accion: "corregir_modo",
    };
  }
  // error_inesperado, o fallido sin motivo (anterior a la decisión 022)
  if (intentos >= MAX_INTENTOS) {
    return {
      titulo: "No pudimos procesar este video",
      texto: "Lo intentamos varias veces sin éxito. Conviene volver a subirlo.",
      accion: "subir_otro",
      contador: `Intento ${Math.min(intentos, MAX_INTENTOS)} de ${MAX_INTENTOS}`,
    };
  }
  return {
    titulo: "No pudimos procesar este video",
    texto: "Pasó algo de nuestro lado. Podés reintentar.",
    accion: "reintentar",
    contador: intentos > 0 ? `Intento ${intentos} de ${MAX_INTENTOS}` : undefined,
  };
}

export type ConteoObservaciones = {
  correcto: number;
  desvio_leve: number;
  alerta_de_carga: number;
  no_auditable: number;
  sin_evaluar: number;
};

export type ObservacionLeida = { severidad: string; texto: string; fundamento?: string | null; referencia?: string | null };

/** Cuenta las observaciones por severidad. Una severidad desconocida no se cuenta ni se reinterpreta. */
export function contarObservaciones(observaciones: readonly { severidad: string }[] | null | undefined): ConteoObservaciones {
  const c: ConteoObservaciones = { correcto: 0, desvio_leve: 0, alerta_de_carga: 0, no_auditable: 0, sin_evaluar: 0 };
  for (const o of observaciones ?? []) {
    if (o.severidad in c) c[o.severidad as keyof ConteoObservaciones] += 1;
  }
  return c;
}

/** `reportes_biomecanicos` llega como objeto (relación 1 a 1) o como lista según la consulta: se normaliza. */
export function reporteDe(video: { reportes_biomecanicos?: unknown }): { reporte: Record<string, unknown> | null } | null {
  const r = video.reportes_biomecanicos;
  const fila = Array.isArray(r) ? r[0] : r;
  if (!fila || typeof fila !== "object") return null;
  const rep = (fila as { reporte?: unknown }).reporte;
  return { reporte: rep && typeof rep === "object" ? (rep as Record<string, unknown>) : null };
}

export function observacionesDe(reporte: Record<string, unknown> | null): ObservacionLeida[] {
  const o = reporte?.observaciones;
  return Array.isArray(o) ? (o as ObservacionLeida[]) : [];
}

// --- sesiones --------------------------------------------------------------------------------------------------------

export type EstadoSesion = "en_curso" | "completada" | "parcial" | "fallida" | "vacia";

/** Estado agregado de una sesión a partir de los de sus videos (un golpe por video). */
export function estadoDeSesion(estados: readonly EstadoVideo[]): EstadoSesion {
  if (estados.length === 0) return "vacia";
  if (estados.some(enCurso)) return "en_curso";
  if (estados.every((e) => e === "fallido")) return "fallida";
  if (estados.every((e) => e === "completado")) return "completada";
  return "parcial";
}

export const GESTO_ETIQUETA: Record<string, string> = { saque: "Saque", drive: "Drive", reves: "Revés" };
export const ENCUADRE_ETIQUETA: Record<string, string> = { perfil: "perfil", tres_cuartos: "tres cuartos" };
