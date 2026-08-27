import type { Estado } from "@/components/estado";

/**
 * Payload simulado del motor.
 *
 * Seccion 4 del CLAUDE.md: "El frontend NO calcula nada biomecanico. Solo
 * representa datos ya evaluados por el motor." Este modulo emula exactamente
 * la estructura que va a devolver la API: valores ya filtrados, ya auditados y
 * con su confianza. Cuando exista el backend, se reemplaza por un fetch y
 * ningun componente de presentacion cambia.
 */

export const MOTOR = {
  version: "v0.1.0",
  backendPose: "MediaPipe Pose",
  filtro: "Butterworth 4º orden, fase cero (bidireccional)",
  corteHz: 8,
  fpsVideo: 240,
  sello: "v0.1.0 · MediaPipe Pose · Butterworth 4º orden fase cero",
} as const;

export type SegmentoId = "pelvis" | "torso" | "brazo";

export interface Segmento {
  id: SegmentoId;
  label: string;
  /** Token de color de la paleta existente. Tres series distinguibles sin agregar hues nuevos. */
  color: string;
  /** Instante del pico de velocidad, en segundos desde el inicio del gesto. */
  pico: number;
  /** Velocidad angular normalizada del pico (0-1). El valor absoluto vive en el nivel 3. */
  amplitud: number;
  /** Confianza media de los landmarks que componen el segmento (0-1). */
  confianza: number;
}

export interface Caso {
  id: "correcto" | "alterado";
  repeticion: string;
  segmentos: Segmento[];
  /** Instante del impacto, en segundos. */
  impacto: number;
  /** Duracion del eje temporal del grafico, en segundos. */
  duracion: number;
  estado: Estado;
  ordenObservado: SegmentoId[];
  veredicto: string;
  alerta: {
    titulo: string;
    magnitud: string;
    referencia: string;
  } | null;
}

/** Orden esperado de la cadena cinetica: proximal a distal. */
export const ORDEN_ESPERADO: SegmentoId[] = ["pelvis", "torso", "brazo"];

export const ETIQUETAS: Record<SegmentoId, string> = {
  pelvis: "Pelvis",
  torso: "Torso",
  brazo: "Brazo",
};

const COLORES: Record<SegmentoId, string> = {
  pelvis: "var(--neon)",
  torso: "var(--clinic)",
  brazo: "var(--foreground)",
};

function seg(id: SegmentoId, pico: number, amplitud: number, confianza: number): Segmento {
  return { id, label: ETIQUETAS[id], color: COLORES[id], pico, amplitud, confianza };
}

export const CASOS: Record<Caso["id"], Caso> = {
  correcto: {
    id: "correcto",
    repeticion: "Saque 3 de 6",
    segmentos: [
      seg("pelvis", 0.42, 0.58, 0.94),
      seg("torso", 0.51, 0.76, 0.91),
      seg("brazo", 0.58, 1, 0.87),
    ],
    impacto: 0.62,
    duracion: 0.7,
    estado: "correcto",
    ordenObservado: ["pelvis", "torso", "brazo"],
    veredicto: "El orden observado coincide con el orden esperado.",
    alerta: null,
  },
  alterado: {
    id: "alterado",
    repeticion: "Saque 5 de 6",
    segmentos: [
      seg("pelvis", 0.45, 0.54, 0.93),
      seg("torso", 0.38, 0.81, 0.9),
      seg("brazo", 0.57, 0.94, 0.86),
    ],
    impacto: 0.62,
    duracion: 0.7,
    estado: "alerta",
    ordenObservado: ["torso", "pelvis", "brazo"],
    veredicto: "El torso alcanzó su pico 70 ms antes que la pelvis: la secuencia se invirtió.",
    alerta: {
      titulo: "Alerta de carga · secuencia invertida",
      magnitud: "Torso 0,38 s · Pelvis 0,45 s · desfase −70 ms respecto del orden esperado",
      referencia: "Elliott (2006); Kibler (1995)",
    },
  },
};

/**
 * Curva de velocidad por segmento, tal como la devolveria el motor despues del
 * filtrado: una muestra cada ~10 ms.
 */
export function serieVelocidad(s: Segmento, duracion: number, muestras = 71) {
  const sigma = 0.085;
  return Array.from({ length: muestras }, (_, i) => {
    const t = (i / (muestras - 1)) * duracion;
    const v = s.amplitud * Math.exp(-((t - s.pico) ** 2) / (2 * sigma ** 2));
    return { t, v };
  });
}

/** Tramo del gesto que el motor no pudo medir con confianza suficiente. */
export const TRAMO_NO_AUDITABLE = { desde: 0.55, hasta: 0.7 };

export interface Metrica {
  nombre: string;
  valor: string | null;
  unidad: string;
  estado: Estado;
  confianza: number | null;
  referencia: string;
  detalle: string;
}

export const METRICAS: Metrica[] = [
  {
    nombre: "Separación cadera-hombro máxima",
    valor: "42",
    unidad: "°",
    estado: "correcto",
    confianza: 0.94,
    referencia: "Fleisig et al. (2003)",
    detalle:
      "Ángulo entre el eje de la pelvis y el eje de los hombros en el instante de máxima disociación.",
  },
  {
    nombre: "Flexión de rodilla en la carga",
    valor: "118",
    unidad: "°",
    estado: "correcto",
    confianza: 0.91,
    referencia: "Elliott (2006)",
    detalle: "Ángulo de la rodilla de la pierna de apoyo en el punto más bajo de la fase de carga.",
  },
  {
    nombre: "Extensión de codo en el impacto",
    valor: null,
    unidad: "°",
    estado: "no-auditable",
    confianza: null,
    referencia: "—",
    detalle:
      "La confianza de los landmarks de codo y muñeca cayó por debajo del umbral durante el tramo del impacto. No se rellena con una estimación.",
  },
  {
    nombre: "Ángulo de tronco en la aceleración",
    valor: "27",
    unidad: "°",
    estado: "desvio",
    confianza: 0.88,
    referencia: "Kibler (1995)",
    detalle:
      "Inclinación lateral del tronco respecto de la vertical durante la fase de aceleración.",
  },
];

export interface Confianza {
  articulacion: string;
  valor: number;
  cuadrosDescartados: number;
}

export const CONFIANZA_POR_ARTICULACION: Confianza[] = [
  { articulacion: "Cadera derecha", valor: 0.96, cuadrosDescartados: 2 },
  { articulacion: "Cadera izquierda", valor: 0.95, cuadrosDescartados: 3 },
  { articulacion: "Hombro derecho", valor: 0.92, cuadrosDescartados: 7 },
  { articulacion: "Hombro izquierdo", valor: 0.93, cuadrosDescartados: 5 },
  { articulacion: "Codo derecho", valor: 0.61, cuadrosDescartados: 48 },
  { articulacion: "Muñeca derecha", valor: 0.54, cuadrosDescartados: 63 },
  { articulacion: "Rodilla derecha", valor: 0.9, cuadrosDescartados: 8 },
  { articulacion: "Rodilla izquierda", valor: 0.89, cuadrosDescartados: 9 },
];

/**
 * R4 — toda alerta responde dos preguntas: que magnitud la disparo y que fuente
 * la respalda. Confirmar cada entrada contra la bibliografia del Capitulo 2
 * antes de la entrega.
 */
export const REFERENCIAS = [
  {
    clave: "Elliott (2006)",
    cita: "Elliott, B. (2006). Biomechanics and tennis. British Journal of Sports Medicine, 40(5), 392-396.",
    usoEn: "Orden proximal-distal de los picos de velocidad; flexión de rodilla en la carga.",
  },
  {
    clave: "Kibler (1995)",
    cita: "Kibler, W. B. (1995). Biomechanical analysis of the shoulder during tennis activities. Clinics in Sports Medicine, 14(1), 79-85.",
    usoEn: "Disociación cadera-hombro y ángulo de tronco como descriptores de la cadena cinética.",
  },
  {
    clave: "Fleisig et al. (2003)",
    cita: "Fleisig, G., Nicholls, R., Elliott, B., & Escamilla, R. (2003). Kinematics used by world class tennis players to produce high-velocity serves. Sports Biomechanics, 2(1), 51-64.",
    usoEn: "Rango de referencia de la separación cadera-hombro en el saque.",
  },
  {
    clave: "Bahr (2016)",
    cita: "Bahr, R. (2016). Why screening tests to predict injury do not work - and probably never will. British Journal of Sports Medicine, 50(13), 776-780.",
    usoEn:
      "Fundamento del alcance del sistema: ninguna alerta de esta pantalla afirma nada sobre lesiones futuras.",
  },
  {
    clave: "Winter (2009)",
    cita: "Winter, D. A. (2009). Biomechanics and Motor Control of Human Movement (4th ed.). Wiley.",
    usoEn: "Filtrado Butterworth de fase cero y selección de la frecuencia de corte.",
  },
];
