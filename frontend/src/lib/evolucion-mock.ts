/**
 * Serie historica del atleta, tal como la devolveria la API.
 * Vive fuera del componente por la misma razon que reporte-mock.ts: el frontend
 * representa datos ya evaluados por el motor, no los calcula.
 */
export interface SesionEvolucion {
  fecha: string;
  /** Separacion cadera-hombro maxima, en grados. */
  separacion: number | null;
  /** Desfase temporal entre el pico de pelvis y el de torso, en milisegundos. */
  desfase: number | null;
}

export const EVOLUCION: SesionEvolucion[] = [
  { fecha: "12 Abr", separacion: 36, desfase: 95 },
  { fecha: "19 Abr", separacion: 38, desfase: 88 },
  { fecha: "26 Abr", separacion: 39, desfase: 84 },
  { fecha: "01 May", separacion: 41, desfase: null },
  { fecha: "08 May", separacion: 41, desfase: 76 },
  { fecha: "12 May", separacion: 42, desfase: 72 },
];
