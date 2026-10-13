/**
 * Consistencia entre los golpes de una sesión (paso 3 del plan §8, `docs/ux/valor-sin-veredictos.md` §3.2).
 *
 * Los números los calcula el servidor (`GET /sesiones/{id}/consistencia`, `backend/app/consistencia.py`): el frontend no calcula nada
 * biomecánico. Acá solo están el tipo de la respuesta, la llamada y las FRASES, que son lógica pura y se prueban con `bun test`.
 *
 * Reglas del texto (decisiones 035 y 036): no se juzga. Se dice cuánto se parecen los golpes entre sí y, del orden, si fue el MISMO,
 * nunca cuál es el correcto. Vocabulario neutro ("aumentó / disminuyó"), sin "mejor" ni "peor".
 */

import { fmt } from "@/lib/formato";

export type Consistencia = {
  sesion_id: string;
  gesto: string;
  encuadre: string;
  fecha: string;
  version_regla: string;
  golpes: { total: number; medidos: number; no_medibles: number; en_analisis: number };
  separacion_cadera_hombro: {
    n: number;
    unidad: string;
    mediana: number | null;
    dispersion: number | null;
    minimo: number | null;
    maximo: number | null;
    valores: { video_id: string; valor: number }[];
  };
  orden: { medidos: number; ordenables: number; mismo_orden: number; orden_modal: string[] | null; suficiente: boolean };
  golpe_tipico: string | null;
  golpes_que_se_apartan: string[];
  versiones_motor: string[];
  mezcla_de_versiones: boolean;
  minimos: { dispersion: number; repetibilidad: number; se_apartan: number };
};

export function urlConsistencia(apiUrl: string | undefined, sesionId: string): string | null {
  if (!apiUrl || !apiUrl.trim()) return null;
  return `${apiUrl.trim().replace(/\/+$/, "")}/sesiones/${encodeURIComponent(sesionId)}/consistencia`;
}

// --- frases ----------------------------------------------------------------------------------------------------------------------

export type TarjetaConsistencia = {
  clave: "separacion" | "orden" | "golpes";
  titulo: string;
  /** El dato principal, corto. `null` = todavía no hay con qué decirlo. */
  valor: string | null;
  /** La frase que lo explica, con lo que falta si falta algo. */
  texto: string;
};

const plural = (n: number, uno: string, varios: string) => `${n} ${n === 1 ? uno : varios}`;

/** Las tres tarjetas de "Tus golpes entre sí". Siempre las tres: lo que no se puede decir, se dice por qué. */
export function tarjetasDeConsistencia(c: Consistencia): TarjetaConsistencia[] {
  const s = c.separacion_cadera_hombro;
  const o = c.orden;
  const g = c.golpes;

  let separacion: TarjetaConsistencia;
  if (s.n === 0 || s.mediana === null) {
    separacion = {
      clave: "separacion",
      titulo: "Separación cadera-hombro",
      valor: null,
      texto: "En esta sesión no se pudo medir la separación cadera-hombro con confianza.",
    };
  } else if (s.dispersion !== null) {
    separacion = {
      clave: "separacion",
      titulo: "Separación cadera-hombro",
      valor: `${fmt(s.mediana, 0)}° ± ${fmt(s.dispersion, 0)}°`,
      texto: `Mediana de ${plural(s.n, "golpe", "golpes")}: ${fmt(s.mediana, 0)}°. Entre golpes varió ±${fmt(s.dispersion, 0)}° (de ${fmt(s.minimo ?? s.mediana, 0)}° a ${fmt(s.maximo ?? s.mediana, 0)}°).`,
    };
  } else {
    separacion = {
      clave: "separacion",
      titulo: "Separación cadera-hombro",
      valor: `${fmt(s.mediana, 0)}°`,
      texto: `Mediana de ${plural(s.n, "golpe", "golpes")}: ${fmt(s.mediana, 0)}°. Con menos de ${c.minimos.dispersion} golpes medidos no se puede decir cuánto varía entre golpes.`,
    };
  }

  let orden: TarjetaConsistencia;
  if (o.medidos === 0) {
    orden = { clave: "orden", titulo: "Orden cadera-tronco", valor: null, texto: "Todavía no hay golpes medidos para comparar el orden." };
  } else if (o.ordenables === 0) {
    orden = {
      clave: "orden",
      titulo: "Orden cadera-tronco",
      valor: null,
      texto: "En ningún golpe se pudo establecer cuál llegó primero: a esta resolución la cadera y el tronco quedaron casi al mismo tiempo.",
    };
  } else if (o.suficiente) {
    orden = {
      clave: "orden",
      titulo: "Orden cadera-tronco",
      valor: `${o.mismo_orden} de ${o.ordenables}`,
      texto: `En ${o.mismo_orden} de ${plural(o.ordenables, "golpe", "golpes")} en que se pudo establecer, el orden entre tu cadera y tu tronco fue el mismo. Mide si se repite, no cuál es el correcto.`,
    };
  } else {
    orden = {
      clave: "orden",
      titulo: "Orden cadera-tronco",
      valor: null,
      texto: `Se pudo establecer el orden en ${plural(o.ordenables, "golpe", "golpes")}; con menos de ${c.minimos.repetibilidad} no se puede decir cuán seguido se repite.`,
    };
  }

  const resto: string[] = [];
  if (g.no_medibles > 0) resto.push(`${plural(g.no_medibles, "no se pudo medir", "no se pudieron medir")}`);
  if (g.en_analisis > 0) resto.push(`${plural(g.en_analisis, "sigue en análisis", "siguen en análisis")}`);
  const golpes: TarjetaConsistencia = {
    clave: "golpes",
    titulo: "Golpes medidos",
    valor: `${g.medidos} de ${g.total}`,
    texto: `Se midieron ${g.medidos} de ${plural(g.total, "golpe", "golpes")}${resto.length > 0 ? `; ${resto.join(" y ")}` : ""}.`,
  };

  return [separacion, orden, golpes];
}

/** El aviso de un golpe que se apartó de los demás. `numero` es la posición del golpe en la sesión (1, 2, 3…). */
export function fraseGolpeQueSeAparta(numero: number): string {
  return `El golpe ${numero} se pareció menos a los demás. Puede ser tu golpe o la medición: miralo en el video.`;
}

export const NOTA_MEZCLA_DE_VERSIONES =
  "Algunos golpes se calcularon con una versión anterior del motor: la comparación entre ellos mezcla versiones.";
