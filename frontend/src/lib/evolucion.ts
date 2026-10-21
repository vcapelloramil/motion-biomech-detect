/**
 * Evolución (paso 6 del plan §8, `docs/ux/valor-sin-veredictos.md` §3.3): un jugador frente a sí mismo, solo entre sesiones del mismo
 * golpe y encuadre. Los números los calcula el servidor (`GET /evolucion`, `backend/app/consistencia.py::serie_de_evolucion`); acá están el
 * tipo y las FRASES (lógica pura, `bun test`). La llamada está en `evolucion-api.ts`.
 *
 * Reglas del texto (decisiones 035 y 036): no se juzga. "Aumentó / disminuyó / se mantuvo", nunca "mejoró / empeoró"; sin color de estado;
 * el cambio se compara con la variación habitual del propio jugador. Una sesión sin dato es un hueco, no se interpola.
 */

import { fmt } from "@/lib/formato";

export type ResumenDeSesion = {
  sesion_id: string;
  fecha: string;
  lado_camara: string | null;
  golpes: { total: number; medidos: number; no_medibles: number; en_analisis: number; con_orden_distinguible: number };
  separacion_cadera_hombro: {
    n: number;
    mediana: number | null;
    dispersion: number | null;
    minimo: number | null;
    maximo: number | null;
  };
  orden: { medidos: number; ordenables: number; mismo_orden: number; suficiente: boolean };
  versiones_motor: string[];
  golpes_que_se_apartan: number;
};

export type SerieDeEvolucion = {
  atleta_id: string;
  gesto: string;
  encuadre: string;
  version_regla: string;
  sesiones: ResumenDeSesion[];
  variacion_habitual: number | null;
  centro_habitual: number | null;
  cambio_separacion: { anterior: number; actual: number; delta: number; dentro_de_lo_habitual: boolean | null } | null;
  lados_de_camara: string[];
  versiones_motor: string[];
  mezcla_de_versiones: boolean;
};

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

/** "2026-09-24" → "24 sep" (sin pasar por Date: una fecha sin hora no tiene que correrse por la zona horaria). */
export function etiquetaDeFecha(fecha: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(fecha);
  if (!m) return fecha;
  return `${Number(m[3])} ${MESES[Number(m[2]) - 1] ?? m[2]}`;
}

/**
 * Una etiqueta por sesión. Si dos sesiones son del mismo día se distinguen por su orden de carga («24 sep · 1.ª» y «24 sep · 2.ª»): la fecha
 * de una sesión es la de la grabación y no trae hora. Las sesiones llegan ordenadas por fecha y orden de carga (servidor).
 */
export function etiquetasDeSesiones(sesiones: readonly { fecha: string }[]): string[] {
  const total = new Map<string, number>();
  for (const s of sesiones) total.set(s.fecha, (total.get(s.fecha) ?? 0) + 1);
  const visto = new Map<string, number>();
  return sesiones.map((s) => {
    const base = etiquetaDeFecha(s.fecha);
    if ((total.get(s.fecha) ?? 0) < 2) return base;
    const k = (visto.get(s.fecha) ?? 0) + 1;
    visto.set(s.fecha, k);
    return `${base} · ${k}.ª`;
  });
}

export type TarjetaDeEvolucion = {
  clave: "separacion" | "orden" | "golpes" | "sesiones";
  titulo: string;
  valor: string | null;
  /** Dirección del cambio contra la sesión anterior (solo informativa, sin color de estado). */
  direccion: "sube" | "baja" | "igual" | null;
  texto: string;
};

const grados = (x: number) => `${fmt(x, 0)}°`;

/** Las cuatro tarjetas de arriba. Siempre las cuatro: lo que no se puede decir, se dice por qué. */
export function tarjetasDeEvolucion(serie: SerieDeEvolucion): TarjetaDeEvolucion[] {
  const ses = serie.sesiones;
  const ultima = ses[ses.length - 1];
  const anterior = ses[ses.length - 2];

  // --- separación ---------------------------------------------------------------------------------------------------------------
  const conSeparacion = ses.filter((s) => s.separacion_cadera_hombro.mediana !== null);
  let separacion: TarjetaDeEvolucion;
  const c = serie.cambio_separacion;
  if (conSeparacion.length === 0) {
    separacion = {
      clave: "separacion",
      titulo: "Separación cadera-hombro",
      valor: null,
      direccion: null,
      texto: "Todavía no hay una sesión con la separación medida con confianza.",
    };
  } else if (!c) {
    const m = conSeparacion[conSeparacion.length - 1].separacion_cadera_hombro.mediana as number;
    separacion = {
      clave: "separacion",
      titulo: "Separación cadera-hombro",
      valor: grados(m),
      direccion: null,
      texto: `Tu punto de partida: ${grados(m)}. La comparación empieza con tu segunda sesión de este golpe y encuadre.`,
    };
  } else {
    const dir = c.delta === 0 || c.dentro_de_lo_habitual === true ? "igual" : c.delta > 0 ? "sube" : "baja";
    const hab = serie.variacion_habitual;
    let texto: string;
    if (hab === null) {
      texto = `Cambió ${grados(Math.abs(c.delta))} (de ${grados(c.anterior)} a ${grados(c.actual)}). Con menos de 4 golpes medidos por sesión no se puede decir si es más que tu variación habitual.`;
    } else if (c.dentro_de_lo_habitual) {
      texto = `Se mantuvo: ${grados(c.actual)} frente a ${grados(c.anterior)} la sesión anterior, dentro de lo que variás entre golpes (±${grados(hab)}).`;
    } else {
      texto = `${c.delta > 0 ? "Aumentó" : "Disminuyó"} ${grados(Math.abs(c.delta))}: de ${grados(c.anterior)} a ${grados(c.actual)}, más que lo que variás entre golpes de una sesión (±${grados(hab)}). No es mejor ni peor: es lo que cambió.`;
    }
    separacion = { clave: "separacion", titulo: "Separación cadera-hombro", valor: grados(c.actual), direccion: dir, texto };
  }

  // --- orden ----------------------------------------------------------------------------------------------------------------------
  const frase = (s: ResumenDeSesion) => `${s.orden.mismo_orden} de ${s.orden.ordenables}`;
  let orden: TarjetaDeEvolucion;
  if (!ultima || ultima.orden.medidos === 0) {
    orden = { clave: "orden", titulo: "Mismo orden entre golpes", valor: null, direccion: null, texto: "Todavía no hay golpes medidos para comparar el orden." };
  } else if (!ultima.orden.suficiente) {
    orden = {
      clave: "orden",
      titulo: "Mismo orden entre golpes",
      valor: null,
      direccion: null,
      texto:
        ultima.orden.ordenables === 0
          ? "En la última sesión no se distingue cuál llegó primero, la cadera o el tronco: a esta resolución quedaron casi al mismo tiempo."
          : `En la última sesión se distingue el orden en ${ultima.orden.ordenables} golpes; con menos de 5 no se puede decir cuán seguido se repite.`,
    };
  } else {
    const antes = anterior && anterior.orden.suficiente ? ` Antes: ${frase(anterior)}.` : "";
    orden = {
      clave: "orden",
      titulo: "Mismo orden entre golpes",
      valor: frase(ultima),
      direccion: null,
      texto: `En la última sesión, el orden entre cadera y tronco fue el mismo en ${frase(ultima)} golpes en que se distingue.${antes} Mide si se repite, no cuál es el correcto.`,
    };
  }

  // --- golpes medidos -------------------------------------------------------------------------------------------------------------
  const golpes: TarjetaDeEvolucion = ultima
    ? {
        clave: "golpes",
        titulo: "Golpes medidos",
        valor: `${ultima.golpes.medidos} de ${ultima.golpes.total}`,
        direccion: null,
        texto: `En la última sesión se midieron ${ultima.golpes.medidos} de ${ultima.golpes.total} golpes.${anterior ? ` Antes: ${anterior.golpes.medidos} de ${anterior.golpes.total}.` : ""}`,
      }
    : { clave: "golpes", titulo: "Golpes medidos", valor: null, direccion: null, texto: "Todavía no hay sesiones de este golpe y encuadre." };

  const sesiones: TarjetaDeEvolucion = {
    clave: "sesiones",
    titulo: "Sesiones comparadas",
    valor: String(ses.length),
    direccion: null,
    texto: "Del mismo jugador, golpe y encuadre. Solo se compara con tus propias sesiones.",
  };

  return [separacion, orden, golpes, sesiones];
}

/** Lo que hace dudosa la comparación, dicho antes de los gráficos. */
export function avisosDeEvolucion(serie: SerieDeEvolucion): string[] {
  const avisos: string[] = [];
  if (serie.lados_de_camara.length > 1) {
    avisos.push(
      "Estas sesiones se cargaron con la cámara de lados distintos del jugador: la comparación puede no ser válida. Para compararte, grabá siempre desde el mismo lugar.",
    );
  }
  if (serie.mezcla_de_versiones) {
    avisos.push("Algunos golpes se calcularon con una versión anterior del motor: la comparación entre ellos mezcla versiones.");
  }
  if (serie.sesiones.some((s) => s.golpes_que_se_apartan > 0)) {
    avisos.push("En alguna sesión hubo golpes que se parecieron menos a los demás; entran igual en la mediana, que no se mueve por un golpe suelto.");
  }
  return avisos;
}
