/**
 * Los textos de Evolución en el lenguaje simple de la decisión 039 (segunda ronda): «En una frase» (una sola idea, SIN números), «Qué vimos»
 * (los datos, con su ⓘ) y un texto aparte cuando hay menos de dos sesiones comparables. Reglas fijas sobre la serie que calcula el servidor
 * (`/evolucion`), sin IA generativa; los mismos tests de palabras prohibidas y de jerga que el reporte (tests/textos-evolucion.test.ts).
 *
 * La comparación es solo entre sesiones del mismo jugador, golpe y encuadre. El lado de la cámara todavía no forma parte de la clave de la
 * serie: si las sesiones se grabaron desde lados distintos, un aviso lo dice (decisión 013).
 */

import { etiquetasDeSesiones, type SerieDeEvolucion } from "@/lib/evolucion";
import { fmt } from "@/lib/formato";
import { VERSION_TEXTOS, type Item } from "@/lib/textos-reporte";

export type TextosEvolucion = {
  version: string;
  /** Debajo del título de la pantalla. */
  cabecera: string;
  enUnaFrase: string;
  vimos: { medido: Item[]; noMedido: Item[] };
  /** Menos de dos sesiones comparables: qué hace falta para comparar. `null` si hay dos o más. */
  pocasSesiones: string | null;
  avisos: string[];
  graficos: {
    tituloLinea: string;
    unidadLinea: string;
    notaLinea: string;
    textoBanda: string | null;
    tituloBarras: string;
    notaBarras: string;
    sinBarras: string;
  };
  detalle: { columnas: string[]; filas: string[][]; nota: string };
};

/** Lo que dice la pantalla bajo el título (existe aunque todavía no haya serie). */
export const CABECERA_EVOLUCION =
  "Solo se comparan sesiones tuyas del mismo golpe y encuadre, grabadas desde el mismo lugar. No hay comparación con otros jugadores: un cambio es solo lo que cambió, no un juicio sobre tu técnica.";

const grados = (x: number) => `${fmt(x, 0)}°`;
const golpes = (n: number) => `${n} ${n === 1 ? "golpe" : "golpes"}`;

export function textosDeEvolucion(serie: SerieDeEvolucion): TextosEvolucion {
  const ses = serie.sesiones;
  const n = ses.length;
  const ultima = ses[n - 1];
  const anterior = ses[n - 2];
  const c = serie.cambio_separacion;
  const hab = serie.variacion_habitual;
  const conSeparacion = ses.filter((s) => s.separacion_cadera_hombro.mediana !== null);

  // --- En una frase: una idea, sin números ---
  let enUnaFrase: string;
  if (n === 0) enUnaFrase = "Todavía no hay sesiones de este golpe y encuadre para comparar.";
  else if (n === 1) enUnaFrase = "Tenés una sola sesión de este golpe y encuadre: es tu punto de partida.";
  else if (!c) enUnaFrase = "Todavía no hay dos sesiones con la torsión medida para poder compararlas.";
  else if (c.delta === 0 || c.dentro_de_lo_habitual === true) enUnaFrase = "Tu torsión se mantuvo de una sesión a la otra.";
  else if (hab === null) enUnaFrase = "Tu torsión cambió de una sesión a la otra, pero hay pocos golpes para saber si es más de lo que variás normalmente.";
  else enUnaFrase = c.delta > 0 ? "Te enroscaste más que en tu sesión anterior." : "Te enroscaste menos que en tu sesión anterior.";

  // --- Qué vimos ---
  const medido: Item[] = [];
  const noMedido: Item[] = [];
  const etiquetas = etiquetasDeSesiones(ses);
  const cuando = ultima ? ` (${etiquetas[n - 1]})` : "";

  if (conSeparacion.length === 0) {
    noMedido.push({ titulo: "La torsión cadera-hombro:", texto: "todavía no hay una sesión con esta medición con confianza suficiente." });
  } else if (!c) {
    const m = conSeparacion[conSeparacion.length - 1].separacion_cadera_hombro.mediana as number;
    medido.push({
      texto: `Tu punto de partida: el valor típico de tu torsión fue de ${grados(m)}. La comparación empieza con tu segunda sesión de este golpe y encuadre.`,
      ayuda: "valor_tipico",
    });
  } else if (hab === null) {
    medido.push({
      texto: `El valor típico de tu torsión pasó de ${grados(c.anterior)} a ${grados(c.actual)} (cambió ${grados(Math.abs(c.delta))}). Con menos de 4 golpes medidos por sesión no se puede decir si es más que lo que variás entre golpes.`,
      ayuda: "valor_tipico",
    });
  } else if (c.delta === 0 || c.dentro_de_lo_habitual) {
    medido.push({
      texto: `El valor típico de tu torsión fue de ${grados(c.actual)} en tu última sesión y de ${grados(c.anterior)} en la anterior: se mantuvo, dentro de lo que variás entre golpes (±${grados(hab)}).`,
      ayuda: "variacion_tipica",
    });
  } else {
    medido.push({
      texto: `El valor típico de tu torsión ${c.delta > 0 ? "aumentó" : "disminuyó"} ${grados(Math.abs(c.delta))}: de ${grados(c.anterior)} a ${grados(c.actual)}, más que lo que variás entre golpes de una sesión (±${grados(hab)}). Es lo que cambió, no un juicio sobre tu técnica.`,
      ayuda: "variacion_tipica",
    });
  }

  if (ultima) {
    const o = ultima.orden;
    const antes = anterior && anterior.orden.suficiente ? ` Antes: ${anterior.orden.mismo_orden} de ${anterior.orden.ordenables}.` : "";
    if (o.medidos === 0) {
      noMedido.push({ titulo: "El orden entre cadera y tronco:", texto: "todavía no hay golpes medidos para compararlo." });
    } else if (!o.suficiente) {
      medido.push({
        texto:
          o.ordenables === 0
            ? `En tu última sesión${cuando} no se pudo ver qué giró primero, la cadera o el tronco: giraron casi a la vez.`
            : `En tu última sesión${cuando} se pudo ver el orden en ${golpes(o.ordenables)}; hacen falta 5 o más para decir cuán seguido se repite.`,
        ayuda: "orden_repeticion",
      });
    } else {
      medido.push({
        texto: `En tu última sesión${cuando} el orden entre cadera y tronco fue el mismo en ${o.mismo_orden} de ${o.ordenables} golpes en que se pudo ver.${antes} Solo cuenta si se repite.`,
        ayuda: "orden_repeticion",
      });
    }
    medido.push({
      texto: `En tu última sesión se midieron ${ultima.golpes.medidos} de ${golpes(ultima.golpes.total)}${anterior ? ` (antes: ${anterior.golpes.medidos} de ${anterior.golpes.total})` : ""}.`,
    });
  }
  if (n >= 2) medido.push({ texto: `Comparamos ${n} sesiones tuyas del mismo golpe y encuadre.`, ayuda: "sesiones_comparadas" });

  // --- Menos de dos sesiones comparables ---
  const pocasSesiones =
    n >= 2
      ? null
      : n === 1
        ? "Para comparar hacen falta al menos dos sesiones tuyas del mismo golpe y encuadre, grabadas desde el mismo lugar. Tenés una: cuando cargues la segunda, acá vas a ver qué cambió."
        : "Para comparar hacen falta al menos dos sesiones tuyas del mismo golpe y encuadre, grabadas desde el mismo lugar. Todavía no hay ninguna.";

  // --- Lo que hace dudosa la comparación ---
  const avisos: string[] = [];
  if (serie.lados_de_camara.length > 1) {
    avisos.push(
      "Estas sesiones se cargaron con la cámara de lados distintos del jugador: la comparación puede no ser válida. Para compararte, grabá siempre desde el mismo lugar.",
    );
  }
  if (serie.mezcla_de_versiones) avisos.push("Algunos golpes se calcularon con una versión anterior del motor: la comparación entre ellos mezcla versiones.");
  if (ses.some((s) => s.golpes_que_se_apartan > 0)) {
    avisos.push("En alguna sesión hubo golpes que se parecieron menos a los demás; entran igual en el valor típico, que no se mueve por un golpe suelto.");
  }

  return {
    version: VERSION_TEXTOS,
    cabecera: CABECERA_EVOLUCION,
    enUnaFrase,
    vimos: { medido, noMedido },
    pocasSesiones,
    avisos,
    graficos: {
      tituloLinea: "Cuánto te enroscaste (torsión cadera-hombro)",
      unidadLinea: "grados · valor típico por sesión",
      notaLinea:
        "Cada punto es el valor típico de los golpes medidos de la sesión; la línea vertical, cuánto variaron entre sí. Con pocos golpes esa variación es una estimación gruesa: no la compares de una sesión a otra. Una sesión sin dato queda como hueco: no se completa con una estimación.",
      textoBanda: hab !== null && serie.centro_habitual !== null ? `tu variación habitual ±${grados(hab)}` : null,
      tituloBarras: "Golpes con el mismo orden de cadera y tronco",
      notaBarras:
        "De los golpes en que se pudo ver qué giró primero, cuántos tuvieron el mismo orden. Solo cuenta si se repite. Con menos de 5 golpes no se dice.",
      sinBarras:
        "No hay gráfico del orden: ninguna sesión llega a 5 golpes en los que se pueda ver qué giró primero. Con la cámara en tres cuartos es lo habitual, porque la cadera y el tronco giran casi a la vez. Los golpes medidos se ven en el gráfico de arriba.",
    },
    detalle: {
      columnas: ["Sesión", "Golpes medidos", "Torsión (valor típico)", "Variación típica", "Orden visto", "Cámara a la"],
      filas: ses.map((s, i) => [
        etiquetas[i],
        `${s.golpes.medidos} de ${s.golpes.total}`,
        s.separacion_cadera_hombro.mediana !== null ? grados(s.separacion_cadera_hombro.mediana) : "—",
        s.separacion_cadera_hombro.dispersion !== null ? `±${grados(s.separacion_cadera_hombro.dispersion)}` : "—",
        s.orden.ordenables > 0 ? `${s.orden.ordenables} de ${s.orden.medidos}` : "ninguno",
        s.lado_camara ?? "—",
      ]),
      nota: "«Orden visto» son los golpes en que se pudo ver qué giró primero. La variación se da desde 4 golpes por sesión y, con pocos golpes, es una estimación gruesa: no conviene compararla entre sesiones.",
    },
  };
}
