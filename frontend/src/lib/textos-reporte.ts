/**
 * Los textos del reporte (decisión 039): lo que ve el jugador en el golpe, en la sesión y en el PDF.
 *
 * Reglas fijas sobre los datos que el reporte YA tiene guardados: plantillas con huecos, sin IA generativa. Lógica pura, sin red ni DOM:
 * la pantalla y el PDF llaman a las mismas funciones, así que dicen lo mismo. Se prueba con `bun test` (tests/textos-reporte.test.ts),
 * incluida una prueba de palabras prohibidas sobre todas las salidas.
 *
 * Versionados (R4): si se cambia una frase o una regla, sube `VERSION_TEXTOS` y la bitácora dice qué cambió.
 *
 * Lo que estos textos NO hacen (decisión 039): no dicen qué valor es bueno o malo, no prescriben técnica ni tratamiento, no hablan de
 * riesgo de lesión, no comparan con profesionales ni prometen mejoras. Solo observan, explican cómo medir mejor, cómo usar los datos,
 * dan contexto de la literatura en un recuadro aparte y arman preguntas para el entrenador.
 */

import type { Consistencia } from "@/lib/consistencia";
import { UMBRAL_CONFIANZA_PICO } from "@/lib/estado-video";
import { esLadoDeLaMano, ladoRecomendado } from "@/lib/esquema-encuadre";
import { fmt } from "@/lib/formato";
import {
  ERROR_VALIDADO,
  artefactosDe,
  coberturaDe,
  picosNoMedidosDe,
  repeticionesDe,
  trazabilidadDe,
  tramosNoAuditablesDe,
  type RepeticionLeida,
} from "@/lib/reporte-simple";

export const VERSION_TEXTOS = "2";

type Json = Record<string, unknown>;

// --- glosario: lo que dice el ⓘ ---------------------------------------------------------------------------------------------

export type ClaveAyuda =
  | "torsion"
  | "giro_rapido"
  | "a_la_vez"
  | "angulo_rodilla"
  | "angulo_codo"
  | "valor_tipico"
  | "variacion_tipica"
  | "golpe_tipico"
  | "se_aparta"
  | "confianza"
  | "brazo_tapado"
  | "orden_repeticion"
  | "sesiones_comparadas";

export const GLOSARIO: Record<ClaveAyuda, { termino: string; corto: string }> = {
  torsion: {
    termino: "Torsión cadera-hombro",
    corto:
      "Es el ángulo entre la línea de tus caderas y la de tus hombros, en su máximo. 0° sería caderas y hombros alineados; cuanto mayor es el número, más enroscado estaba el tronco respecto de la cadera.",
  },
  giro_rapido: {
    termino: "Giro más rápido",
    corto:
      "Es el instante en que esa parte del cuerpo giró con más velocidad durante el golpe. La cadera se sigue con la línea de las caderas y el tronco con la de los hombros.",
  },
  a_la_vez: {
    termino: "Casi a la vez",
    corto:
      "El video se graba a unos 200 fotogramas por segundo: cada uno dura unos 5 ms (milésimas de segundo). Con menos de 8 ms de diferencia no se puede saber cuál de las dos partes llegó primero.",
  },
  angulo_rodilla: {
    termino: "Ángulo de la rodilla",
    corto:
      "Es el ángulo entre el muslo y la pantorrilla, visto en la imagen. 180° es la pierna totalmente estirada; cuanto más bajo es el número, más flexionada está la rodilla.",
  },
  angulo_codo: {
    termino: "Ángulo del codo",
    corto:
      "Es el ángulo entre el brazo y el antebrazo, visto en la imagen. 180° es el brazo totalmente estirado; cuanto más bajo es el número, más doblado está el codo.",
  },
  valor_tipico: {
    termino: "Valor típico",
    corto:
      "Es la mediana: el valor del medio al ordenar los golpes de menor a mayor. No se deja arrastrar por un golpe muy distinto de los demás.",
  },
  variacion_tipica: {
    termino: "Variación típica",
    corto:
      "Cuánto se aleja, en general, un golpe del valor típico. Está calculada de modo que un golpe muy distinto no la agrande. Se da desde 4 golpes.",
  },
  golpe_tipico: {
    termino: "Golpe típico",
    corto: "El golpe de la sesión más cercano al valor típico de la torsión. Es el más representativo; no es un golpe ejemplar ni un juicio sobre tu técnica.",
  },
  se_aparta: {
    termino: "Un golpe que se aparta",
    corto: "Su torsión quedó a más de 3 variaciones típicas del valor típico de la sesión. Puede ser tu golpe o la medición: conviene mirarlo en el video.",
  },
  confianza: {
    termino: "Confianza",
    corto: "Va de 0 a 1 y es la seguridad con que el sistema ubicó las articulaciones que definen esa medición. Cerca de 1 es mucha seguridad.",
  },
  orden_repeticion: {
    termino: "Mismo orden entre golpes",
    corto:
      "De los golpes en que se pudo distinguir qué giró primero, cuántos tuvieron el mismo orden. Solo cuenta si se repite; no dice cuál orden conviene. Se informa desde 5 golpes en que se pudo distinguir.",
  },
  sesiones_comparadas: {
    termino: "Sesiones comparadas",
    corto:
      "Solo se comparan sesiones tuyas del mismo golpe y encuadre, y conviene que estén grabadas desde el mismo lugar: el mismo movimiento puede dar números distintos desde otro punto de vista.",
  },
  brazo_tapado: {
    termino: "Brazo no medido",
    corto:
      "Con la cámara del lado contrario a la mano con que golpeás, el cuerpo tapa el brazo mientras armás el golpe y el sistema no puede seguirlo.",
  },
};

// --- tipos de salida ---------------------------------------------------------------------------------------------------------

export type Item = {
  titulo?: string;
  texto: string;
  ayuda?: ClaveAyuda;
  /** A dónde lleva el enlace de la frase (la pantalla lo dibuja; el PDF solo imprime el texto). */
  enlace?: "sesion" | "evolucion";
  /** Un golpe puntual de la sesión (para enlazar a su reporte). */
  golpeId?: string;
};

export type FilaDetalle = { dato: string; valor: string; significa: string };
export type GrupoDetalle = { titulo: string; filas: FilaDetalle[] };

export type Literatura = { titulo: string; aclaracion: string; texto: string };

export type Profesional = { preguntas: string[]; confianza: Item[]; aviso: string };

export type FotosTexto = {
  /** Cadera y tronco en el mismo fotograma (diferencia dentro de la tolerancia): se muestra una sola foto. */
  fotoUnica: boolean;
  /** Pie de la foto única, o `null` si no corresponde. */
  etiquetaFotoUnica: string | null;
  queMirarFoto: string;
  /** Qué es el video y qué mirar; `null` si el reporte no tiene video con esqueleto. */
  video: string | null;
  queMirarVideo: string | null;
};

export type TextosGolpe = {
  version: string;
  enUnaFrase: string;
  vimos: { medido: Item[]; noMedido: Item[] };
  fotos: FotosTexto;
  hacer: { medir: Item[]; usar: Item[]; literatura: Literatura };
  profesional: Profesional;
  detalle: GrupoDetalle[];
};

export type TextosSesion = {
  version: string;
  enUnaFrase: string;
  vimos: { medido: Item[]; noMedido: Item[]; seAparta: Item[] };
  /** Pie del golpe típico y qué mirar. `null` si no hay golpe típico. */
  tipico: { numero: number; texto: string; queMirar: string } | null;
  hacer: { medir: Item[]; usar: Item[]; literatura: Literatura };
  profesional: Profesional;
  detalle: {
    columnas: string[];
    filas: string[][];
    nota: string;
    terminos: { termino: string; significa: string }[];
    versiones: string;
  };
};

// --- fijos -----------------------------------------------------------------------------------------------------------------

/** El aviso (decisión 039, punto 5). Es la única frase que nombra lo que KinetiQ NO hace: la prueba de palabras prohibidas la exime. */
export const AVISO =
  "KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.";

/** Recuadro de literatura: solo la cadena cinética del saque, con la única cita cuyo alcance el proyecto da por sostenido. Una secuencia
 *  específica (orden de picos, valores) NO se escribe hasta verificar el pasaje (decisión 039). */
export const LITERATURA_SAQUE =
  "La literatura describe el saque como una cadena que transmite energía desde las piernas, a través de la cadera y el tronco, hacia el brazo y la raqueta (Kovacs y Ellenbecker, 2011). La forma exacta varía de un jugador a otro.";
export const LITERATURA_SIN_REFERENCIA = "Para este golpe todavía no hay una referencia incorporada al proyecto.";
const ACLARACION_LITERATURA = "Contexto general: no es una comparación con tus datos.";

/** La cámara del lado de la mano dominante: el brazo queda más a la vista, pero ese lado todavía no está validado (decisión 013). */
const NOTA_LADO_DE_LA_MANO = (que: string) =>
  `Grabaste con la cámara del lado de tu mano dominante: el brazo con el que golpeás queda más a la vista, pero ese lado todavía no está validado en KinetiQ, así que cadera y tronco de ${que} no se pueden comparar con los de sesiones grabadas desde el otro lado.`;

const MODOS_LLANOS: Record<string, string> = { camara_lenta_240: "cámara lenta de 240 fps", camara_lenta_120: "cámara lenta de 120 fps" };

/**
 * El ángulo de la rodilla o del codo dicho en palabras, sin veredicto (decisión 039, segunda ronda): 180° es totalmente estirada.
 * Los cortes son redondos y aproximados, con el error medido contra goniometría a la vista (8,5° y 12,5° de media).
 */
export function posturaDe(parte: "rodilla" | "codo", valor: number): string {
  const estirada = parte === "rodilla" ? "estirada" : "estirado";
  const flexionada = parte === "rodilla" ? "flexionada" : "flexionado";
  if (valor >= 178) return `totalmente ${estirada}`;
  if (valor >= 170) return `casi ${estirada}`;
  if (valor >= 140) return `algo ${flexionada}`;
  if (valor >= 100) return flexionada;
  return `muy ${flexionada}`;
}

const SUJETO_ARTICULACION = (parte: "rodilla" | "codo", lado: "izq" | "der" | null) => {
  const l = lado ? ` ${(parte === "rodilla" ? LADO_FEM : LADO_MASC)[lado]}` : "";
  return parte === "rodilla" ? `la pierna${l}` : `el brazo${l}`;
};

const REFERENCIA_RODILLA = "180° es la pierna totalmente estirada";
const REFERENCIA_CODO = "180° es el brazo totalmente estirado";

const GESTOS: Record<string, { uno: string; varios: string; verbo: string }> = {
  saque: { uno: "saque", varios: "saques", verbo: "sacar" },
  drive: { uno: "drive", varios: "drives", verbo: "pegar" },
  reves: { uno: "revés", varios: "reveses", verbo: "pegar" },
};
const gestoDe = (g: string) => GESTOS[g] ?? { uno: "golpe", varios: "golpes", verbo: "pegar" };

const ENCUADRES: Record<string, string> = { perfil: "perfil", tres_cuartos: "tres cuartos" };

// --- lectura defensiva ---------------------------------------------------------------------------------------------------------

function num(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

type MetricaLeida = { nombre: string; valor: number | null; auditable: boolean; confianza: number };

function metricasDe(reporte: Json | null): MetricaLeida[] {
  const m = reporte?.metricas;
  if (!Array.isArray(m)) return [];
  return (m as Json[]).map((x) => ({
    nombre: typeof x.nombre === "string" ? x.nombre : "",
    valor: num(x.valor),
    auditable: x.auditable === true,
    confianza: num(x.confianza) ?? 0,
  }));
}

/** La torsión cadera-hombro máxima en grados, o `null` si no se midió con confianza. */
export function torsionDe(reporte: Json | null): number | null {
  const m = metricasDe(reporte).find((x) => x.nombre === "separacion_cadera_hombro_max");
  return m && m.auditable && m.valor !== null ? m.valor : null;
}

export type ArticularLeida = { nombre: string; parte: "rodilla" | "codo"; lado: "izq" | "der" | null; valor: number | null; confianza: number; auditable: boolean };

export function articularesDe(reporte: Json | null): ArticularLeida[] {
  const salida: ArticularLeida[] = [];
  for (const m of metricasDe(reporte)) {
    const a = /^angulo_(rodilla|codo)(?:_(izq|der))?_en_pico_tronco$/.exec(m.nombre);
    if (!a) continue;
    salida.push({
      nombre: m.nombre,
      parte: a[1] as "rodilla" | "codo",
      lado: (a[2] as "izq" | "der" | undefined) ?? null,
      valor: m.auditable ? m.valor : null,
      confianza: m.confianza,
      auditable: m.auditable && m.valor !== null,
    });
  }
  return salida;
}

export type OrdenDelGolpe =
  | { tipo: "sin_medir" }
  | { tipo: "a_la_vez"; ms: number }
  | { tipo: "cadera_primero" | "tronco_primero"; ms: number };

/** Qué llegó primero a su giro más rápido, cadera o tronco: solo con los dos picos medidos con confianza (decisión 037). */
export function ordenDelGolpe(reporte: Json | null): OrdenDelGolpe {
  const tolMs = trazabilidadDe(reporte).tolerancia_orden_ms ?? 1000 / 120;
  for (const r of repeticionesDe(reporte)) {
    const p = r.picos?.find((x) => x.segmento === "pelvis");
    const t = r.picos?.find((x) => x.segmento === "torso");
    if (!p || !t || p.confianza < UMBRAL_CONFIANZA_PICO || t.confianza < UMBRAL_CONFIANZA_PICO) continue;
    if (!Number.isFinite(p.instante_s) || !Number.isFinite(t.instante_s)) continue;
    const d = (t.instante_s - p.instante_s) * 1000;
    if (Math.abs(d) <= tolMs + 1e-6) return { tipo: "a_la_vez", ms: Math.abs(d) };
    return d > 0 ? { tipo: "cadera_primero", ms: d } : { tipo: "tronco_primero", ms: -d };
  }
  return { tipo: "sin_medir" };
}

/** ¿Se midió el pico del brazo que golpea en la primera repetición? */
export function brazoMedido(reporte: Json | null): boolean {
  const r = repeticionesDe(reporte)[0];
  return !!r?.picos?.some((p) => p.segmento === "brazo");
}

// --- palabras ------------------------------------------------------------------------------------------------------------------

const ms0 = (x: number) => (x < 0.5 ? "menos de 1" : fmt(x, 0));
const milesimas = (x: number) => (Math.round(x) === 1 ? "1 milésima de segundo" : `${ms0(x)} milésimas de segundo`);

function lista(ns: number[]): string {
  const t = ns.map(String);
  if (t.length <= 1) return t.join("");
  return `${t.slice(0, -1).join(", ")} y ${t[t.length - 1]}`;
}

/** "el 6", "el 2 y el 6". */
function listaConEl(ns: number[]): string {
  const t = ns.map((n) => `el ${n}`);
  if (t.length <= 1) return t.join("");
  return `${t.slice(0, -1).join(", ")} y ${t[t.length - 1]}`;
}

const LADO_FEM: Record<string, string> = { izq: "izquierda", der: "derecha" };
const LADO_MASC: Record<string, string> = { izq: "izquierdo", der: "derecho" };

function articulacionTexto(a: Pick<ArticularLeida, "parte" | "lado">): string {
  const lado = a.lado ? ` ${(a.parte === "rodilla" ? LADO_FEM : LADO_MASC)[a.lado]}` : "";
  return `${a.parte === "rodilla" ? "rodilla" : "codo"}${lado}`;
}

/** "codo_der" → "codo derecho": sin nombres internos. */
export function articulacionLlana(codigo: string): string {
  const m = /^(codo|rodilla|hombro|cadera|muneca|tobillo)_(izq|der)$/.exec(codigo.trim());
  if (!m) return codigo.replace(/_/g, " ");
  const nombre = m[1] === "muneca" ? "muñeca" : m[1];
  const fem = nombre === "rodilla" || nombre === "cadera" || nombre === "muñeca";
  return `${nombre} ${(fem ? LADO_FEM : LADO_MASC)[m[2]]}`;
}

function tramoTexto(motivo: string): string {
  const m = /sin_datos_confiables:\s*(.+)$/.exec(motivo);
  return m ? m[1].split(",").map((s) => articulacionLlana(s)).join(" y ") : motivo.replace(/_/g, " ");
}

/** Hoy el cuerpo tapa el brazo que golpea cuando la cámara está del lado contrario a la mano dominante, en el saque (decisión 013). */
function elCuerpoTapaElBrazo(gesto: string, ladoCamara: string, mano: string | null): boolean {
  return gesto === "saque" && mano !== null && ladoRecomendado(mano) === ladoCamara;
}

const ladoDeLaMano = (mano: string | null): "izq" | "der" | null => (mano === "derecha" ? "der" : mano === "izquierda" ? "izq" : null);

// --- contexto de la sesión para un golpe -------------------------------------------------------------------------------------

export type ContextoSesionDeGolpe = {
  total: number;
  esTipico: boolean;
  torsion: { minimo: number; maximo: number; mediana: number } | null;
};

export function contextoDeGolpe(c: Consistencia | null, videoId: string): ContextoSesionDeGolpe | null {
  if (!c) return null;
  const s = c.separacion_cadera_hombro;
  return {
    total: c.golpes.total,
    esTipico: c.golpe_tipico === videoId,
    torsion: s.minimo !== null && s.maximo !== null && s.mediana !== null ? { minimo: s.minimo, maximo: s.maximo, mediana: s.mediana } : null,
  };
}

// --- fotos y video -----------------------------------------------------------------------------------------------------------

export function fotosDe(reporte: Json | null): FotosTexto {
  const orden = ordenDelGolpe(reporte);
  const art = artefactosDe(reporte);
  const tienePelvis = art.fotogramas.some((f) => f.segmento === "pelvis");
  const tieneTorso = art.fotogramas.some((f) => f.segmento === "torso");
  const fotoUnica = orden.tipo === "a_la_vez" && (tienePelvis || tieneTorso);
  const r0 = repeticionesDe(reporte)[0];
  const desde = r0?.desde_s ?? null;
  const ref = art.fotogramas.find((f) => f.segmento === "torso") ?? art.fotogramas.find((f) => f.segmento === "pelvis");
  const etiquetaFotoUnica =
    fotoUnica && ref ? `Cadera y tronco en su giro más rápido${desde !== null ? ` · a los ${fmt(desde + ref.instante_s, 2)} s del video` : ""}` : null;
  const ov = art.overlay;
  const tramo = ov && ov.hasta_s > ov.desde_s ? ov.hasta_s - ov.desde_s : null;
  return {
    fotoUnica,
    etiquetaFotoUnica,
    queMirarFoto:
      "La línea violeta marca tus caderas y la turquesa tus hombros. Fijate si acompañan a tu cuerpo: si el dibujo no se parece a tu cuerpo, esa medición no es confiable.",
    video: ov
      ? `Video con el esqueleto dibujado${ov.factor_lento ? `, en cámara lenta (${fmt(ov.factor_lento, 0)} veces más lento que la realidad)` : ""}${tramo ? `: es el tramo de ${fmt(tramo, 1)} s alrededor del golpe` : ""}.`
      : null,
    queMirarVideo: ov ? "Qué mirar: que las líneas sigan tu cuerpo sin saltos." : null,
  };
}

// --- el golpe ------------------------------------------------------------------------------------------------------------------

export type EntradaGolpe = {
  reporte: Json;
  gesto: string;
  encuadre: string;
  ladoCamara: string;
  manoDominante: string | null;
  /** Datos de tu sesión (de la consistencia); `null` si todavía no están. */
  contexto: ContextoSesionDeGolpe | null;
  /** Segundos de espera en la cola y de procesamiento: solo van al detalle técnico. */
  tiempos?: { espera_cola_s: number | null; procesamiento_s: number | null };
};

const dur = (s: number) => (s < 60 ? `${Math.round(s)} s` : `${Math.floor(s / 60)} min ${Math.round(s % 60)} s`);

export function textosDeGolpe(e: EntradaGolpe): TextosGolpe {
  const rep = e.reporte;
  const t = trazabilidadDe(rep);
  const g = gestoDe(e.gesto);
  const torsion = torsionDe(rep);
  const orden = ordenDelGolpe(rep);
  const articulares = articularesDe(rep);
  const rodillas = articulares.filter((a) => a.parte === "rodilla");
  const codos = articulares.filter((a) => a.parte === "codo");
  const brazo = brazoMedido(rep);
  const tapa = elCuerpoTapaElBrazo(e.gesto, e.ladoCamara, e.manoDominante);
  const tolRedondeada = fmt(t.tolerancia_orden_ms ?? 1000 / 120, 0);
  const ctx = e.contexto;

  // --- En una frase: una sola idea, sin números (decisión 039, segunda ronda); los datos van en «Qué vimos» ---
  let enUnaFrase: string;
  if (orden.tipo === "a_la_vez") enUnaFrase = `Tu cadera y tu tronco giraron casi a la vez en este ${g.uno}.`;
  else if (orden.tipo === "cadera_primero") enUnaFrase = `Tu cadera giró antes que tu tronco en este ${g.uno}.`;
  else if (orden.tipo === "tronco_primero") enUnaFrase = `Tu tronco giró antes que tu cadera en este ${g.uno}.`;
  else if (torsion !== null) enUnaFrase = `En este ${g.uno} se midió cuánto te enroscaste, pero no se pudo ver qué giró primero.`;
  else enUnaFrase = "De este golpe no se pudo medir lo suficiente como para resumirlo en una frase.";

  // --- Qué vimos: primero lo medido (máximo 3 líneas) ---
  const medido: Item[] = [];
  if (torsion !== null) {
    medido.push({
      texto: `En el momento de mayor torsión, la línea de tus hombros y la de tus caderas formaron un ángulo de ${fmt(torsion, 0)}°.`,
      ayuda: "torsion",
    });
  }
  if (orden.tipo === "a_la_vez") {
    medido.push({
      texto:
        `Tu cadera y tu tronco alcanzaron su giro más rápido casi a la vez: los separan ${milesimas(orden.ms)} y el video no permite distinguir menos de ${tolRedondeada}. ` +
        "Por eso no se puede decir cuál fue primero.",
      ayuda: "a_la_vez",
    });
  } else if (orden.tipo !== "sin_medir") {
    const primero = orden.tipo === "cadera_primero" ? ["cadera", "tronco"] : ["tronco", "cadera"];
    medido.push({
      texto:
        `Tu ${primero[0]} alcanzó su giro más rápido ${milesimas(orden.ms)} antes que tu ${primero[1]}. ` +
        "Desde otra posición de cámara, este orden podría verse distinto.",
      ayuda: "giro_rapido",
    });
  }
  const rodillaMedida = rodillas.find((a) => a.auditable);
  if (rodillaMedida && rodillaMedida.valor !== null) {
    medido.push({
      texto: `Cuando el tronco giraba más rápido, tenías ${SUJETO_ARTICULACION("rodilla", rodillaMedida.lado)} ${posturaDe("rodilla", rodillaMedida.valor)} (rodilla a ${fmt(rodillaMedida.valor, 0)}°; ${REFERENCIA_RODILLA}).`,
      ayuda: "angulo_rodilla",
    });
  } else {
    // El codo del brazo que NO golpea (el del lanzamiento) va al detalle; solo el del brazo dominante, si se midió, puede ocupar el lugar.
    const dom = ladoDeLaMano(e.manoDominante);
    const codoDom = dom ? codos.find((a) => a.lado === dom && a.auditable) : undefined;
    if (codoDom && codoDom.valor !== null) {
      medido.push({
        texto: `Cuando el tronco giraba más rápido, tenías ${SUJETO_ARTICULACION("codo", codoDom.lado)} ${posturaDe("codo", codoDom.valor)} (codo a ${fmt(codoDom.valor, 0)}°; ${REFERENCIA_CODO}).`,
        ayuda: "angulo_codo",
      });
    }
  }

  // --- lo que no se pudo medir, con el porqué en una línea ---
  const noMedido: Item[] = [];
  const nadaMedido = medido.length === 0;
  const cuerpoMedido = orden.tipo !== "sin_medir";
  const conMotivo = new Set<string>();
  for (const n of picosNoMedidosDe(rep)) {
    if (n.segmento === "brazo") continue;
    conMotivo.add(n.segmento);
    noMedido.push({ titulo: n.segmento === "pelvis" ? "La cadera:" : "El tronco:", texto: n.motivo });
  }
  if (nadaMedido && noMedido.length === 0) {
    noMedido.push({
      titulo: "Este golpe:",
      texto: "el sistema no pudo seguir tu cuerpo con confianza, así que no hay mediciones de la cadera, el tronco, el brazo ni las rodillas.",
    });
  } else if (!cuerpoMedido && conMotivo.size === 0 && !nadaMedido) {
    noMedido.push({
      titulo: "La cadera y el tronco:",
      texto: "el sistema no pudo seguirlos con confianza en este golpe, así que no hay una medición de su giro.",
    });
  }
  if (!brazo && !nadaMedido) {
    // Solo si el cuerpo sí se siguió se puede decir que lo que faltó fue el brazo, tapado por el cuerpo.
    const tapado = tapa && cuerpoMedido;
    noMedido.push({
      titulo: "El brazo con el que golpeás:",
      texto: tapado
        ? `desde la cámara, a tu ${e.ladoCamara}, el cuerpo lo tapó durante buena parte del golpe.`
        : "el sistema no pudo seguirlo con confianza durante buena parte del golpe.",
      ayuda: tapado ? "brazo_tapado" : undefined,
    });
  }
  for (const r of nadaMedido ? [] : rodillas.filter((a) => !a.auditable)) {
    noMedido.push({ titulo: `La ${articulacionTexto(r)}:`, texto: "en ese momento el sistema no la vio con suficiente seguridad." });
  }
  if (!nadaMedido && torsion === null && metricasDe(rep).some((m) => m.nombre === "separacion_cadera_hombro_max")) {
    noMedido.push({ titulo: "La torsión cadera-hombro:", texto: "no se pudo medir con suficiente seguridad durante el golpe." });
  }

  // --- Qué podés hacer con esto ---
  const medir: Item[] = [];
  if (!cuerpoMedido) {
    medir.push({
      texto: "Cuando casi no se mide nada, ayudan el cuerpo entero a la vista durante todo el golpe, buena luz y la cámara quieta, sin que nada tape al jugador.",
    });
  }
  if (!brazo && tapa && cuerpoMedido) {
    medir.push({
      texto: `Con la cámara a tu ${e.ladoCamara}, el cuerpo tapa el brazo con el que golpeás cuando armás el golpe. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que cadera y tronco de esa sesión no se podrían comparar con los de esta.`,
    });
  }
  if (esLadoDeLaMano(e.ladoCamara, e.manoDominante)) {
    medir.push({ texto: NOTA_LADO_DE_LA_MANO("este golpe") });
  }
  if (ctx && ctx.total > 1) {
    medir.push({
      texto: `Este golpe es uno de los ${ctx.total} de tu sesión. Para ver cuánto se parece a los demás, mirá la sesión.`,
      enlace: "sesion",
    });
  } else if (ctx && ctx.total === 1) {
    medir.push({ texto: "Con un solo golpe no se puede saber si lo medido es habitual en vos: una sesión de 6 o más golpes permite ver cuánto varían entre sí." });
  }
  if (!nadaMedido && rodillas.some((a) => !a.auditable)) {
    medir.push({ texto: "Un encuadre que muestre el cuerpo entero, con los pies a la vista, y buena luz pueden ayudar a que el sistema vea las rodillas con seguridad." });
  }
  const usar: Item[] = [
    {
      texto: "Para comparar con otro día, grabá desde el mismo lugar (lado y ángulo de la cámara): el mismo movimiento puede dar números distintos desde otro punto de vista.",
    },
    {
      texto: "Más que un número suelto, sirve mirar si un número se vuelve más parejo de golpe a golpe y de sesión a sesión. En Evolución se ve la variación de tu propia sesión.",
      enlace: "evolucion",
    },
  ];

  // --- Para tu entrenador o profesional ---
  const preguntas: string[] = [];
  if (orden.tipo === "a_la_vez") {
    preguntas.push(`En este ${g.uno} la cadera y el tronco giraron casi a la vez (${ms0(orden.ms)} ms). ¿Lo ves igual en el video? ¿Se parece a lo que sentís al ${g.verbo}?`);
  } else if (orden.tipo !== "sin_medir") {
    preguntas.push(
      `En este ${g.uno} ${orden.tipo === "cadera_primero" ? "la cadera" : "el tronco"} llegó a su giro más rápido ${ms0(orden.ms)} ms antes que ${orden.tipo === "cadera_primero" ? "el tronco" : "la cadera"}. ¿Lo ves igual en el video? ¿Se parece a lo que sentís al ${g.verbo}?`,
    );
  }
  if (ctx?.esTipico && ctx.torsion && torsion !== null) {
    preguntas.push(
      `Este es el golpe más cercano al valor típico de tu sesión (torsión de ${fmt(torsion, 0)}°; la sesión va de ${fmt(ctx.torsion.minimo, 0)}° a ${fmt(ctx.torsion.maximo, 0)}°). ¿Te parece representativo de tus ${g.varios}?`,
    );
  }
  if (preguntas.length === 0) preguntas.push("¿Qué ves en el video de este golpe que los números no muestran?");

  return {
    version: VERSION_TEXTOS,
    enUnaFrase,
    vimos: { medido, noMedido },
    fotos: fotosDe(rep),
    hacer: { medir, usar, literatura: literaturaDe(e.gesto) },
    profesional: { preguntas, confianza: confianzaDe(t.tolerancia_orden_ms), aviso: AVISO },
    detalle: detalleDeGolpe(e, { torsion, orden, articulares, brazo }),
  };
}

export function literaturaDe(gesto: string): Literatura {
  return {
    titulo: "Contexto de la literatura",
    aclaracion: ACLARACION_LITERATURA,
    texto: gesto === "saque" ? LITERATURA_SAQUE : LITERATURA_SIN_REFERENCIA,
  };
}

/** Cuánto se puede confiar en cada medición: el error medido contra goniometría manual (decisión 015, Criterio 2). */
export function confianzaDe(toleranciaMs: number | null): Item[] {
  const e = ERROR_VALIDADO;
  return [
    {
      titulo: "Ángulos de rodilla y codo:",
      texto:
        "se contrastaron con goniometría manual a ciegas (medición manual del ángulo sobre la imagen). " +
        `En el codo, el ángulo de KinetiQ difirió ${fmt(e.codo.media, 1)}° de media del medido a mano (en el 95 % de los casos, hasta ${fmt(e.codo.p95, 1)}°); ` +
        `en la rodilla, ${fmt(e.rodilla.media, 1)}° de media (hasta ${fmt(e.rodilla.p95, 1)}°). El codo del brazo que golpea suele tener poca cobertura.`,
    },
    {
      titulo: "Momentos:",
      texto: `el video permite distinguir diferencias de unos ${fmt(toleranciaMs ?? 1000 / 120, 0)} ms; por debajo no se sabe cuál fue primero.`,
    },
    { titulo: "Torsión cadera-hombro:", texto: "se midió que se repite entre sesiones; no se contrastó con goniometría." },
  ];
}

// --- detalle técnico del golpe -------------------------------------------------------------------------------------------------

function detalleDeGolpe(
  e: EntradaGolpe,
  d: { torsion: number | null; orden: OrdenDelGolpe; articulares: ArticularLeida[]; brazo: boolean },
): GrupoDetalle[] {
  const rep = e.reporte;
  const t = trazabilidadDe(rep);
  const r0: RepeticionLeida | null = repeticionesDe(rep)[0] ?? null;
  const metricas = metricasDe(rep);
  const conf = (c: number) => `confianza ${fmt(c, 2)}`;
  const dom = ladoDeLaMano(e.manoDominante);

  const mediciones: FilaDetalle[] = [];
  const tors = metricas.find((m) => m.nombre === "separacion_cadera_hombro_max");
  if (tors) {
    mediciones.push({
      dato: "Torsión cadera-hombro máxima",
      valor: d.torsion !== null ? `${fmt(d.torsion, 1)}° · ${conf(tors.confianza)}` : `no medida · ${conf(tors.confianza)}`,
      significa: GLOSARIO.torsion.corto,
    });
  }
  const veloc = (nombre: string, etiqueta: string, que: string) => {
    const m = metricas.find((x) => x.nombre === nombre);
    if (!m) return;
    mediciones.push({
      dato: etiqueta,
      valor: m.auditable && m.valor !== null && t.escala_conocida ? `${fmt(m.valor, 0)} °/s · ${conf(m.confianza)}` : `no medido · ${conf(m.confianza)}`,
      significa:
        m.auditable && m.valor !== null && t.escala_conocida
          ? `${que} (${fmt(m.valor, 0)} °/s son unas ${fmt(m.valor / 360, 1)} vueltas por segundo).`
          : `${que} No se informa: no hay datos suficientes o la escala de tiempo no está confirmada.`,
    });
  };
  veloc("velocidad_pico_pelvis", "Giro más rápido de la cadera", "Cuántos grados por segundo gira la línea de las caderas en su momento más rápido");
  veloc("velocidad_pico_torso", "Giro más rápido del tronco", "Lo mismo para la línea de los hombros");
  if (d.orden.tipo !== "sin_medir") {
    const tol = fmt(t.tolerancia_orden_ms ?? 1000 / 120, 1);
    mediciones.push({
      dato: "Diferencia entre los dos momentos",
      valor:
        d.orden.tipo === "a_la_vez"
          ? `${ms0(d.orden.ms)} ms (casi a la vez)`
          : `${d.orden.tipo === "cadera_primero" ? "cadera" : "tronco"} ${ms0(d.orden.ms)} ms antes`,
      significa:
        d.orden.tipo === "a_la_vez"
          ? `Es menor que los ${tol} ms necesarios para poder decir cuál fue primero.`
          : `Supera los ${tol} ms necesarios para poder decir cuál fue primero.`,
    });
  }
  for (const a of d.articulares) {
    const esDelBrazoQueNoGolpea = a.parte === "codo" && dom !== null && a.lado !== null && a.lado !== dom;
    const err = ERROR_VALIDADO[a.parte];
    mediciones.push({
      dato: `${a.parte === "rodilla" ? "Rodilla" : "Codo"}${a.lado ? ` ${(a.parte === "rodilla" ? LADO_FEM : LADO_MASC)[a.lado]}` : ""}`,
      valor: a.auditable && a.valor !== null ? `${fmt(a.valor, 1)}° · ${conf(a.confianza)}` : `no medida · ${conf(a.confianza)}`,
      significa: a.auditable
        ? `Ángulo en el instante del giro más rápido del tronco; ${a.parte === "rodilla" ? REFERENCIA_RODILLA : REFERENCIA_CODO}. ` +
          `Error medido contra goniometría manual: ${fmt(err.media, 1)}° de media.` +
          (esDelBrazoQueNoGolpea ? " Es el brazo que no golpea (el del lanzamiento de pelota)." : "")
        : `Se informa solo si las tres articulaciones del ángulo se vieron con confianza de 0,6 o más. ${a.parte === "rodilla" ? REFERENCIA_RODILLA : REFERENCIA_CODO}.`,
    });
  }
  if (!d.brazo) {
    mediciones.push({
      dato: "Brazo que golpea",
      valor: "no medido",
      significa: "Faltaron datos del brazo durante gran parte del golpe, así que no hay un momento claro de giro más rápido.",
    });
  } else {
    const pb = r0?.picos?.find((x) => x.segmento === "brazo");
    const pt = r0?.picos?.find((x) => x.segmento === "torso");
    if (pb && pt) {
      const dms = (pb.instante_s - pt.instante_s) * 1000;
      const tolB = t.tolerancia_orden_ms ?? 1000 / 120;
      mediciones.push({
        dato: "Giro más rápido del brazo que golpea",
        valor: `${Math.abs(dms) <= tolB ? "casi a la vez que el tronco" : `${ms0(Math.abs(dms))} ms ${dms > 0 ? "después" : "antes"} que el tronco`} · ${conf(pb.confianza)}`,
        significa: "Momento en que el brazo cambió más rápido de dirección, comparado con el del tronco. Es un dato del golpe: no se evalúa.",
      });
    }
  }

  const cuando: FilaDetalle[] = [];
  if (r0 && typeof r0.desde_s === "number") {
    const hasta = (rep.secuenciacion as { repeticiones?: { hasta_s?: number }[] } | undefined)?.repeticiones?.[0]?.hasta_s;
    cuando.push({
      dato: "Tramo analizado",
      valor: `${fmt(r0.desde_s, 2)} s a ${typeof hasta === "number" ? fmt(hasta, 2) : "—"} s del video`,
      significa:
        "El análisis mira un tramo corto alrededor del giro más rápido del tronco. Los momentos de cada parte se cuentan desde su inicio; el del tronco cae siempre en el centro porque el tramo se arma alrededor de él. Lo que importa es la diferencia entre los momentos.",
    });
  }
  const cob = coberturaDe(rep);
  if (cob !== null) {
    const tramos = tramosNoAuditablesDe(rep);
    const detalleTramos = tramos.length
      ? ` Sin datos confiables: ${tramos
          .slice(0, 4)
          .map((x) => `${tramoTexto(x.motivo)}, de ${fmt(x.desde_s, 2)} s a ${fmt(x.hasta_s, 2)} s del video`)
          .join("; ")}${tramos.length > 4 ? ` y ${tramos.length - 4} tramos más` : ""}.`
      : "";
    cuando.push({ dato: "Parte del golpe medida con seguridad", valor: `${fmt(cob, 1)} %`, significa: `El resto son tramos donde alguna articulación no se vio con confianza.${detalleTramos}` });
  }

  const video: FilaDetalle[] = [];
  if (t.fps_real !== null) {
    video.push({
      dato: "Fotogramas por segundo reales",
      valor: `${fmt(t.fps_real, 1)}${t.fps_nominal !== null ? ` (el teléfono anuncia ${fmt(t.fps_nominal, 0)})` : ""}`,
      significa: t.fotogramas_perdidos_pct !== null ? `Faltó el ${fmt(t.fotogramas_perdidos_pct, 1)} % de los fotogramas.` : "Es la frecuencia medida en el archivo.",
    });
    video.push({ dato: "Resolución en el tiempo", valor: `1 fotograma ≈ ${fmt(1000 / t.fps_real, 0)} ms`, significa: "Por eso hay una diferencia mínima para poder ordenar dos momentos." });
  }
  if (t.puntos_interpolados !== null && t.puntos_de_la_grilla !== null) {
    video.push({
      dato: "Fotogramas reconstruidos",
      valor: `${t.puntos_interpolados} de ${t.puntos_de_la_grilla}${t.puntos_interpolados_pct !== null ? ` (${fmt(t.puntos_interpolados_pct, 1)} %)` : ""}`,
      significa: `Para tener un muestreo parejo se estimó el punto entre dos vecinos (interpolación)${t.hueco_maximo_ms !== null ? `, con huecos de hasta ${fmt(t.hueco_maximo_ms, 1)} ms` : ""}. Un momento que cae en uno de esos puntos es una estimación, no una medición.`,
    });
  }
  const filtro = (rep.trazabilidad as { filtro?: { tipo?: string; orden?: number; corte_hz?: number; fase_cero?: boolean } } | undefined)?.filtro;
  if (filtro) {
    video.push({
      dato: "Suavizado de la señal",
      valor: `${(filtro.tipo ?? "butterworth").replace(/^./, (c) => c.toUpperCase())} de ${filtro.orden ?? "—"}.º orden, corte ${filtro.corte_hz !== undefined ? fmt(filtro.corte_hz, 0) : "—"} Hz${filtro.fase_cero ? ", sin retraso" : ""}`,
      significa: "Quita el temblor de la detección sin correr los momentos en el tiempo.",
    });
  }
  video.push({
    dato: "Tiempo del video",
    valor: t.escala_conocida ? "confirmado" : "no confirmado",
    significa: t.escala_conocida ? "Se pudo leer cuándo se tomó cada fotograma." : "Sin esto, los tiempos y las velocidades no son confiables.",
  });
  if (t.modo_captura) video.push({ dato: "Modo de captura declarado", valor: MODOS_LLANOS[t.modo_captura] ?? t.modo_captura.replace(/_/g, " "), significa: "Lo que se indicó al subir el video." });

  const versiones: FilaDetalle[] = [
    { dato: "Motor", valor: `${t.version_motor ?? "—"} · ${t.backend_pose ?? "—"}`, significa: "Versión del programa que calculó el reporte y detector de pose." },
    { dato: "Textos", valor: `v${VERSION_TEXTOS}`, significa: "Versión de las frases de este reporte; si cambian, sube el número." },
  ];
  if (e.tiempos?.espera_cola_s != null) versiones.push({ dato: "Espera en la cola", valor: dur(e.tiempos.espera_cola_s), significa: "Tiempo hasta que le tocó el turno al análisis." });
  if (e.tiempos?.procesamiento_s != null) versiones.push({ dato: "Procesamiento", valor: dur(e.tiempos.procesamiento_s), significa: "Tiempo que tardó el servidor en analizar este golpe." });

  return [
    { titulo: "Mediciones", filas: mediciones },
    { titulo: "Cuándo y con qué cobertura", filas: cuando },
    { titulo: "Cómo salió el video", filas: video },
    { titulo: "Versiones y tiempos", filas: versiones },
  ].filter((x) => x.filas.length > 0);
}

// --- la sesión ----------------------------------------------------------------------------------------------------------------

export type GolpeDeEntrada = { id: string; estado: string; reporte: Json | null };

export type EntradaSesion = {
  gesto: string;
  encuadre: string;
  ladoCamara: string;
  manoDominante: string | null;
  golpes: GolpeDeEntrada[];
  consistencia: Consistencia | null;
};

type ResumenGolpe = {
  id: string;
  numero: number;
  medido: boolean;
  torsion: number | null;
  orden: OrdenDelGolpe;
  brazo: boolean;
  articulares: ArticularLeida[];
  cobertura: number | null;
  tieneReporte: boolean;
};

function resumenDe(g: GolpeDeEntrada, numero: number): ResumenGolpe {
  const rep = g.reporte;
  const orden = ordenDelGolpe(rep);
  return {
    id: g.id,
    numero,
    medido: orden.tipo !== "sin_medir",
    torsion: torsionDe(rep),
    orden,
    brazo: brazoMedido(rep),
    articulares: articularesDe(rep),
    cobertura: coberturaDe(rep),
    tieneReporte: !!rep,
  };
}

/** "entre 29° y 42°", o "en 33°" si todos dan lo mismo. */
function entreG(valores: number[]): string {
  const a = fmt(Math.min(...valores), 0);
  const b = fmt(Math.max(...valores), 0);
  return a === b ? `en ${a}°` : `entre ${a}° y ${b}°`;
}
/** Números con coma y "y": "29° y 11°". */
function juntar(t: string[]): string {
  return t.length <= 1 ? t.join("") : `${t.slice(0, -1).join(", ")} y ${t[t.length - 1]}`;
}
const rangoMs = (v: number[]) => {
  const a = ms0(Math.min(...v));
  const b = ms0(Math.max(...v));
  return a === b ? `${a} ms` : `entre ${a} y ${b} ms`;
};

const SIN_COMPARACION =
  "La comparación entre golpes no estaba disponible al armar este reporte (se calcula en el servidor). Los datos de cada golpe están en su reporte.";

export function textosDeSesion(e: EntradaSesion): TextosSesion {
  const g = gestoDe(e.gesto);
  const c = e.consistencia;
  const resumen = e.golpes.map((x, i) => resumenDe(x, i + 1));
  const porId = new Map(resumen.map((r) => [r.id, r]));
  const medidos = resumen.filter((r) => r.medido);
  const total = e.golpes.length;
  const m = medidos.length;
  const tapa = elCuerpoTapaElBrazo(e.gesto, e.ladoCamara, e.manoDominante);
  const sep = c?.separacion_cadera_hombro ?? null;
  const apartan = (c?.golpes_que_se_apartan ?? []).map((id) => porId.get(id)).filter((r): r is ResumenGolpe => !!r);
  const idsApartan = new Set(apartan.map((r) => r.id));

  // Golpes ordenables, a la vez y con cada orden
  const caderaPrimero = medidos.filter((r) => r.orden.tipo === "cadera_primero");
  const troncoPrimero = medidos.filter((r) => r.orden.tipo === "tronco_primero");
  const aLaVez = medidos.filter((r) => r.orden.tipo === "a_la_vez");
  const ordenables = caderaPrimero.length + troncoPrimero.length;
  const msDe = (rs: ResumenGolpe[]) => rs.map((r) => (r.orden.tipo === "sin_medir" ? 0 : r.orden.ms));

  // --- En una frase ---
  const plural = g.varios;
  const PALABRA = ["cero", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce"];
  const palabra = (n: number) => PALABRA[n] ?? "varios";

  // En una frase: una sola idea, sin números (decisión 039, segunda ronda); el rango, el golpe que se aparta y los conteos van en «Qué vimos».
  let enUnaFrase: string;
  if (!c) {
    enUnaFrase = "No se pudo armar el resumen de la sesión ahora: la comparación entre golpes no estaba disponible.";
  } else if (m === 0) {
    enUnaFrase = "No se pudo medir ningún golpe de esta sesión.";
  } else {
    const medimos = m === total ? `Medimos ${palabra(m)} ${m === 1 ? g.uno : plural}.` : `Medimos ${palabra(m)} de tus ${palabra(total)} ${plural}.`;
    // «Giraste parecido» solo cuando el servidor pudo marcar qué golpe se aparta (desde 5 golpes): con menos no se afirma.
    const sepSuficiente = !!(sep && sep.n >= c.minimos.se_apartan);
    const parecido = m >= 2 && sepSuficiente ? (apartan.length > 0 ? "Giraste parecido en casi todos" : "Giraste parecido en todos") : null;
    let orden: string | null = null;
    let ordenSolo: string | null = null;
    if (ordenables === 0) ordenSolo = "En ninguno se pudo ver qué giró primero: la cadera y el tronco giraron casi a la vez.";
    else if (caderaPrimero.length > 0 && troncoPrimero.length > 0) orden = "cuando se pudo ver el orden, a veces arrancó primero la cadera y a veces el tronco";
    else orden = `cuando se pudo ver el orden, ${caderaPrimero.length > 0 ? "la cadera" : "el tronco"} arrancó primero`;
    const mayus = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
    let resto = "";
    if (ordenSolo) resto = parecido ? `${parecido}. ${ordenSolo}` : ordenSolo;
    else if (orden) resto = parecido ? `${parecido} y, ${orden}.` : `${mayus(orden)}.`;
    enUnaFrase = `${medimos} ${resto}`.trim();
  }

  // --- Qué vimos ---
  const medido: Item[] = [];
  const noMedido: Item[] = [];
  if (!c) {
    noMedido.push({ texto: SIN_COMPARACION });
  } else {
    if (sep && sep.n > 0 && sep.mediana !== null) {
      const intro = total === 1 ? "Se midió el golpe." : m === total ? `Se midieron los ${total} golpes.` : `Se midieron ${m} de los ${total} golpes.`;
      const valores = sep.valores;
      const otros = valores.filter((v) => !idsApartan.has(v.video_id)).map((v) => v.valor);
      let resto: string;
      if (valores.length === 1) resto = `: ${fmt(valores[0].valor, 0)}°.`;
      else if (apartan.length === 0) resto = `: los ${valores.length} golpes quedaron ${entreG(valores.map((v) => v.valor))}.`;
      else {
        const fueron = apartan.map((r) => `${fmt(sep.valores.find((v) => v.video_id === r.id)?.valor ?? 0, 0)}°`);
        const quienes =
          apartan.length === 1
            ? `el golpe ${apartan[0].numero} fue de ${fueron[0]}`
            : `los golpes ${lista(apartan.map((r) => r.numero))} fueron de ${juntar(fueron)}`;
        resto =
          otros.length === 0
            ? `: ${quienes}.`
            : `: ${otros.length === 1 ? "1 golpe quedó" : `${otros.length} golpes quedaron`} ${entreG(otros)} y ${quienes}.`;
      }
      medido.push({ texto: `${intro} La torsión entre tus caderas y tus hombros tuvo un valor típico de ${fmt(sep.mediana, 0)}°${resto}`, ayuda: "valor_tipico" });
    } else if (m > 0) {
      noMedido.push({ titulo: "La torsión cadera-hombro:", texto: "no se pudo medir con suficiente seguridad en esta sesión." });
    }

    if (m > 0) {
      if (ordenables === 0) {
        medido.push({
          texto: `En ningún golpe se pudo establecer cuál giró primero: la cadera y el tronco quedaron casi a la vez (${rangoMs(msDe(aLaVez))}).`,
          ayuda: "a_la_vez",
        });
      } else if (caderaPrimero.length > 0 && troncoPrimero.length > 0) {
        medido.push({
          texto:
            `En ${ordenables} de los ${m} golpes se pudo establecer cuál giró primero: en ${caderaPrimero.length} fue la cadera y en ${troncoPrimero.length}, el tronco.` +
            (aLaVez.length ? ` En ${aLaVez.length === 1 ? "el otro" : `los otros ${aLaVez.length}`} quedaron casi a la vez (${rangoMs(msDe(aLaVez))}) y no se puede decir cuál fue primero.` : "") +
            " Desde otra posición de cámara, este orden podría verse distinto.",
          ayuda: "a_la_vez",
        });
      } else {
        const quien = caderaPrimero.length > 0 ? "cadera" : "tronco";
        const grupo = caderaPrimero.length > 0 ? caderaPrimero : troncoPrimero;
        const otra = quien === "cadera" ? "tronco" : "cadera";
        const donde = ordenables === 1 ? `En 1 de los ${m} golpes (el ${grupo[0].numero})` : ordenables === m ? `En los ${m} golpes` : `En ${ordenables} de los ${m} golpes (${lista(grupo.map((r) => r.numero))})`;
        const siempre = ordenables === 1 ? `y fue la ${quien === "cadera" ? "cadera" : "tronco"}` : ordenables === m ? `y en todos fue ${quien === "cadera" ? "la cadera" : "el tronco"}` : `y en los ${ordenables} fue ${quien === "cadera" ? "la cadera" : "el tronco"}`;
        const cuanto = ordenables === 1 ? milesimas(msDe(grupo)[0]) : `${rangoMs(msDe(grupo)).replace(" ms", "")} milésimas de segundo`.replace(/^(\d)/, "$1");
        medido.push({
          texto:
            `${donde} se pudo establecer cuál giró primero, ${siempre}: llegó a su giro más rápido ${cuanto} antes que el ${otra}.` +
            (aLaVez.length ? ` En ${aLaVez.length === 1 ? "el otro" : `los otros ${aLaVez.length}`} quedaron casi a la vez (${rangoMs(msDe(aLaVez))}) y no se puede decir cuál fue primero.` : "") +
            " Desde otra posición de cámara, este orden podría verse distinto." +
            (c.orden.suficiente ? ` El mismo orden se repitió en ${c.orden.mismo_orden} de los ${c.orden.ordenables} golpes en que se pudo establecer.` : ""),
          ayuda: "a_la_vez",
        });
      }

      // La rodilla: el rango de los golpes que no se apartan
      const nombresRodilla = [...new Set(medidos.flatMap((r) => r.articulares.filter((a) => a.parte === "rodilla").map((a) => a.nombre)))];
      const nombre = nombresRodilla
        .map((n) => ({ n, k: medidos.filter((r) => r.articulares.some((a) => a.nombre === n && a.auditable)).length }))
        .sort((a, b) => b.k - a.k)[0]?.n;
      if (nombre) {
        const lado = /_(izq|der)_/.exec(nombre)?.[1] as "izq" | "der" | undefined;
        const nom = articulacionTexto({ parte: "rodilla", lado: lado ?? null });
        const vals = medidos
          .filter((r) => !idsApartan.has(r.id))
          .map((r) => r.articulares.find((a) => a.nombre === nombre && a.auditable)?.valor)
          .filter((v): v is number => typeof v === "number");
        const sujetoRodilla = SUJETO_ARTICULACION("rodilla", lado ?? null);
        if (vals.length >= 2) {
          medido.push({
            texto: `Cuando el tronco giraba más rápido, tenías ${sujetoRodilla} ${posturaDe("rodilla", Math.min(...vals))} en los ${vals.length} golpes en que se midió (rodilla ${entreG(vals)}; ${REFERENCIA_RODILLA}).`,
            ayuda: "angulo_rodilla",
          });
        } else if (vals.length === 1) {
          medido.push({
            texto: `Cuando el tronco giraba más rápido, tenías ${sujetoRodilla} ${posturaDe("rodilla", vals[0])} en el único golpe en que se midió (rodilla a ${fmt(vals[0], 0)}°; ${REFERENCIA_RODILLA}).`,
            ayuda: "angulo_rodilla",
          });
        }
        const sinRodilla = medidos.filter((r) => !r.articulares.some((a) => a.nombre === nombre && a.auditable));
        if (sinRodilla.length > 0) {
          noMedido.push({
            titulo: `La ${nom}:`,
            texto: `no se pudo medir en ${sinRodilla.length === 1 ? "1 golpe" : `${sinRodilla.length} golpes`} (${listaConEl(sinRodilla.map((r) => r.numero))}); en ese momento el sistema no la vio con suficiente seguridad.`,
          });
        }
      }

      const sinBrazo = medidos.filter((r) => !r.brazo);
      if (sinBrazo.length > 0) {
        noMedido.unshift({
          titulo: "El brazo con el que golpeás,",
          texto: `${sinBrazo.length === m ? "en ningún golpe" : `en ${sinBrazo.length} de los ${m} golpes`}: ${
            tapa ? `desde la cámara, a tu ${e.ladoCamara}, el cuerpo lo tapa.` : "el sistema no pudo seguirlo con confianza."
          }`,
          ayuda: tapa ? "brazo_tapado" : undefined,
        });
      }
    }
    const noMedibles = c.golpes.no_medibles;
    if (noMedibles > 0) noMedido.push({ texto: `${noMedibles === 1 ? "1 golpe no se pudo medir" : `${noMedibles} golpes no se pudieron medir`}.` });
    if (c.golpes.en_analisis > 0) noMedido.push({ texto: `${c.golpes.en_analisis === 1 ? "1 golpe sigue" : `${c.golpes.en_analisis} golpes siguen`} en análisis.` });
  }

  // --- Un golpe que se aparta, con lo que se aparta ---
  const seAparta: Item[] = [];
  for (const r of apartan) {
    const propio = r.torsion ?? sep?.valores.find((v) => v.video_id === r.id)?.valor ?? null;
    const extra = rodillaQueSeAparta(r, medidos.filter((x) => !idsApartan.has(x.id)));
    seAparta.push({
      titulo: `El golpe ${r.numero} se parece menos a los demás:`,
      texto:
        `${propio !== null ? `su torsión fue de ${fmt(propio, 0)}°` : "su torsión se aparta de la de los demás"}` +
        `${extra ? ` y, además, ${extra}` : ""}. Puede ser tu golpe o la medición: miralo en el video.`,
      ayuda: "se_aparta",
      golpeId: r.id,
    });
  }

  // --- Golpe típico ---
  const idTipico = c?.golpe_tipico ?? null;
  const rTipico = idTipico ? porId.get(idTipico) : undefined;
  const tipico = rTipico
    ? {
        numero: rTipico.numero,
        texto: `Golpe típico (golpe ${rTipico.numero}): el más cercano al valor típico de la sesión${rTipico.torsion !== null ? ` (${fmt(rTipico.torsion, 0)}° de torsión)` : ""}. No es un golpe ejemplar ni un juicio sobre tu técnica.`,
        queMirar: `Fijate que la línea violeta (caderas) y la turquesa (hombros) acompañen tu cuerpo.${apartan.length ? ` Después abrí ${apartan.length === 1 ? `el golpe ${apartan[0].numero}` : `los golpes ${lista(apartan.map((r) => r.numero))}`} y compará.` : ""}`,
      }
    : null;

  // --- Qué podés hacer con esto ---
  const medir: Item[] = [];
  if (c && m > 0 && ordenables < c.minimos.repetibilidad) {
    medir.push({
      texto: `El orden entre cadera y tronco se pudo establecer en ${ordenables} de ${m} golpes. Con ${c.minimos.repetibilidad} o más golpes en que se distinga, KinetiQ puede decirte cuántas veces se repitió el mismo orden; las sesiones más largas (hasta 12 golpes) ayudan.`,
    });
  }
  if (m > 0 && medidos.every((r) => !r.brazo) && tapa) {
    medir.push({
      texto: `Con la cámara a tu ${e.ladoCamara}, el cuerpo tapa el brazo con el que golpeás. Si querés intentar medirlo, podés grabar desde el otro lado; ese lado todavía no está validado en KinetiQ, así que no se podría comparar con esta sesión.`,
    });
  }
  if (esLadoDeLaMano(e.ladoCamara, e.manoDominante)) medir.push({ texto: NOTA_LADO_DE_LA_MANO("esta sesión") });
  const usar: Item[] = [
    { texto: `Para comparar esta sesión con otra, grabá desde el mismo lugar: ${g.uno}, ${ENCUADRES[e.encuadre] ?? e.encuadre}, cámara a la ${e.ladoCamara}.` },
    {
      texto:
        sep && sep.mediana !== null
          ? sep.dispersion !== null
            ? `En Evolución podés mirar si el valor típico de la torsión (hoy ${fmt(sep.mediana, 0)}°) y la variación entre golpes (hoy ±${fmt(sep.dispersion, 0)}°) se mantienen o se vuelven más parejos de una sesión a otra.`
            : `En Evolución podés mirar si el valor típico de la torsión (hoy ${fmt(sep.mediana, 0)}°) se mantiene de una sesión a otra.`
          : "En Evolución podés mirar cómo cambian tus mediciones de una sesión a otra.",
      enlace: "evolucion",
    },
  ];

  // --- Para tu entrenador o profesional ---
  const preguntas: string[] = [];
  if (apartan.length > 0) {
    const r = apartan[0];
    const otros = medidos.filter((x) => !idsApartan.has(x.id)).map((x) => x.torsion).filter((v): v is number => v !== null);
    const propio = r.torsion ?? sep?.valores.find((v) => v.video_id === r.id)?.valor ?? null;
    const extra = rodillaQueSeAparta(r, medidos.filter((x) => !idsApartan.has(x.id)));
    preguntas.push(
      `En el golpe ${r.numero} la torsión fue de ${propio !== null ? `${fmt(propio, 0)}°` : "otro valor"}${otros.length ? ` (en los otros, ${entreG(otros)})` : ""}${extra ? ` y ${extra.split(" (")[0]}` : ""}. ¿Qué ves en el video de ese golpe? ¿Fue un ${g.uno} distinto a los demás?`,
    );
  }
  if (ordenables > 0 && aLaVez.length > 0 && (caderaPrimero.length === 0 || troncoPrimero.length === 0)) {
    const quien = caderaPrimero.length > 0 ? "la cadera" : "el tronco";
    const otra = caderaPrimero.length > 0 ? "el tronco" : "la cadera";
    preguntas.push(
      `En ${ordenables} golpes ${quien} llegó antes que ${otra} y en otros ${aLaVez.length} llegaron casi juntos. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?`,
    );
  } else if (ordenables > 0 && caderaPrimero.length > 0 && troncoPrimero.length > 0) {
    preguntas.push(`En ${caderaPrimero.length} golpes la cadera llegó antes que el tronco y en ${troncoPrimero.length}, al revés. ¿Se ve esa diferencia en el video? ¿Vale la pena seguir mirándola en las próximas sesiones?`);
  }
  if (total >= 2) {
    preguntas.push(`¿Cuál de estos ${total} ${g.varios} sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?`);
  }

  const tolMs = e.golpes.map((x) => trazabilidadDe(x.reporte).tolerancia_orden_ms).find((v) => v !== null) ?? null;
  const versiones = c?.versiones_motor ?? [];

  // --- Detalle técnico ---
  const filas = resumen.map((r) => {
    const rod = r.articulares.find((a) => a.parte === "rodilla");
    const cod = r.articulares.find((a) => a.parte === "codo");
    const dom = ladoDeLaMano(e.manoDominante);
    const codoNoDom = r.articulares.find((a) => a.parte === "codo" && (dom === null || a.lado !== dom)) ?? cod;
    const que = !r.tieneReporte ? "sin reporte" : !r.medido ? "no se pudo medir" : r.brazo ? "cadera, tronco y brazo" : "cadera y tronco, sin el brazo";
    const ordenTxt =
      r.orden.tipo === "sin_medir"
        ? "—"
        : r.orden.tipo === "a_la_vez"
          ? `casi a la vez (${ms0(r.orden.ms)} ms)`
          : `${r.orden.tipo === "cadera_primero" ? "cadera" : "tronco"} ${ms0(r.orden.ms)} ms antes`;
    return [
      String(r.numero),
      r.torsion !== null ? `${fmt(r.torsion, 1)}°` : "—",
      ordenTxt,
      rod && rod.auditable && rod.valor !== null ? `${fmt(rod.valor, 0)}°` : rod ? "no medida" : "—",
      codoNoDom && codoNoDom.auditable && codoNoDom.valor !== null ? `${fmt(codoNoDom.valor, 0)}°` : codoNoDom ? "no medido" : "—",
      r.cobertura !== null ? `${fmt(r.cobertura, 1)} %` : "—",
      que,
    ];
  });
  const terminos = [
    { termino: GLOSARIO.valor_tipico.termino, significa: GLOSARIO.valor_tipico.corto },
    { termino: "Variación típica", significa: `${GLOSARIO.variacion_tipica.corto}${sep?.dispersion != null ? ` En esta sesión: ±${fmt(sep.dispersion, 1)}°.` : ""}` },
    { termino: GLOSARIO.golpe_tipico.termino, significa: GLOSARIO.golpe_tipico.corto },
    { termino: GLOSARIO.se_aparta.termino, significa: GLOSARIO.se_aparta.corto },
    { termino: GLOSARIO.a_la_vez.termino, significa: `Con la resolución de estos videos, menos de ${fmt(tolMs ?? 1000 / 120, 1)} ms de diferencia no se puede ordenar. La repetición del orden se informa desde ${c?.minimos.repetibilidad ?? 5} golpes en que se pudo establecer.` },
  ];

  return {
    version: VERSION_TEXTOS,
    enUnaFrase,
    vimos: { medido, noMedido, seAparta },
    tipico,
    hacer: { medir, usar, literatura: literaturaDe(e.gesto) },
    profesional: { preguntas, confianza: confianzaDe(tolMs), aviso: AVISO },
    detalle: {
      columnas: ["Golpe", "Torsión", "Cadera y tronco", "Rodilla (180° = estirada)", "Codo (180° = estirado)", "Parte medida", "Qué se midió"],
      filas,
      nota: "Rodilla y codo: 180° es la pierna (o el brazo) totalmente estirada. El codo que se muestra es el del brazo que no golpea (el del lanzamiento de pelota).",
      terminos,
      versiones: `Motor ${versiones.length ? versiones.join(", ") : "—"} · textos v${VERSION_TEXTOS}${c?.mezcla_de_versiones ? " · algunos golpes se calcularon con una versión anterior del motor" : ""}`,
    },
  };
}

/** Si la rodilla del golpe que se aparta cae fuera del rango de los demás por más que el error validado, se nombra (decisión 039). */
function rodillaQueSeAparta(r: ResumenGolpe, demas: ResumenGolpe[]): string | null {
  for (const a of r.articulares.filter((x) => x.parte === "rodilla" && x.auditable && x.valor !== null)) {
    const otros = demas
      .map((d) => d.articulares.find((x) => x.nombre === a.nombre && x.auditable)?.valor)
      .filter((v): v is number => typeof v === "number");
    if (otros.length < 3) continue;
    const mn = Math.min(...otros);
    const mx = Math.max(...otros);
    const v = a.valor as number;
    const margen = ERROR_VALIDADO.rodilla.p95;
    if (v < mn - margen) return `${SUJETO_ARTICULACION(a.parte, a.lado)} estaba mucho más flexionada (rodilla a ${fmt(v, 0)}°, contra ${fmt(mn, 0)}° a ${fmt(mx, 0)}° en los otros ${otros.length} con dato; ${REFERENCIA_RODILLA})`;
    if (v > mx + margen) return `${SUJETO_ARTICULACION(a.parte, a.lado)} estaba mucho menos flexionada (rodilla a ${fmt(v, 0)}°, contra ${fmt(mn, 0)}° a ${fmt(mx, 0)}° en los otros ${otros.length} con dato; ${REFERENCIA_RODILLA})`;
  }
  return null;
}

// --- «Cuándo giró cada parte»: todo relativo al tronco ----------------------------------------------------------------------------

export type PuntoDeSecuencia = {
  segmento: "pelvis" | "torso" | "brazo";
  /** Milisegundos respecto del tronco (negativo = antes). `null` si ese segmento no se midió. */
  deltaMs: number | null;
  etiqueta: string;
};

export type DatosDeSecuencia = {
  /** Diferencia mínima para poder decir cuál fue primero: la zona sombreada del gráfico (±). */
  toleranciaMs: number;
  /** Sin el tronco medido no hay referencia y no se dibuja nada. */
  sinReferencia: boolean;
  puntos: PuntoDeSecuencia[];
  resumen: string;
};

/**
 * Los momentos del giro más rápido de la cadera, el tronco y el brazo, todos respecto del tronco (tronco = 0). No usa los segundos desde el
 * inicio del tramo analizado: ese número no significa nada para el jugador (decisión 039). El brazo solo figura si se midió con confianza.
 */
export function datosDeSecuencia(reporte: Json | null): DatosDeSecuencia {
  const tolMs = trazabilidadDe(reporte).tolerancia_orden_ms ?? 1000 / 120;
  const r = repeticionesDe(reporte).find((x) => x.picos?.some((p) => p.segmento === "torso" && p.confianza >= UMBRAL_CONFIANZA_PICO));
  const pico = (s: string) => r?.picos?.find((p) => p.segmento === s && p.confianza >= UMBRAL_CONFIANZA_PICO && Number.isFinite(p.instante_s));
  const torso = pico("torso");
  if (!r || !torso) {
    return {
      toleranciaMs: tolMs,
      sinReferencia: true,
      puntos: (["pelvis", "torso", "brazo"] as const).map((s) => ({ segmento: s, deltaMs: null, etiqueta: "no medido" })),
      resumen: "No se midió el giro del tronco, que es la referencia: sin él no se puede ubicar a la cadera ni al brazo.",
    };
  }
  const nombres = { pelvis: "cadera", torso: "tronco", brazo: "brazo" } as const;
  const puntos: PuntoDeSecuencia[] = (["pelvis", "torso", "brazo"] as const).map((s) => {
    if (s === "torso") return { segmento: s, deltaMs: 0, etiqueta: "referencia" };
    const p = pico(s);
    if (!p) return { segmento: s, deltaMs: null, etiqueta: "no medido" };
    const d = (p.instante_s - torso.instante_s) * 1000;
    return { segmento: s, deltaMs: d, etiqueta: `${ms0(Math.abs(d))} ms ${d < 0 ? "antes" : "después"}` };
  });
  const resumen = puntos
    .filter((x) => x.segmento !== "torso")
    .map((x) => (x.deltaMs === null ? `${nombres[x.segmento]}: no medido` : `${nombres[x.segmento]}: ${x.etiqueta} que el tronco${Math.abs(x.deltaMs) <= tolMs ? " (dentro de la zona donde no se puede distinguir cuál fue primero)" : ""}`))
    .join("; ");
  return { toleranciaMs: tolMs, sinReferencia: false, puntos, resumen };
}

// --- «¿Qué giró primero?»: la secuencia simple del cuerpo del reporte -------------------------------------------------------------

export type SegmentoDeSecuencia = "pelvis" | "torso" | "brazo";

export type CajaDeSecuencia = {
  partes: SegmentoDeSecuencia[];
  /** «Cadera», «Cadera y tronco». */
  etiqueta: string;
  /** Más de una parte dentro de la tolerancia: van juntas, con «casi a la vez». */
  casiALaVez: boolean;
};

export type SecuenciaSimple = {
  /** De izquierda a derecha, en el orden en que llegó el giro más rápido; entre una caja y la siguiente va una flecha con «antes». */
  cajas: CajaDeSecuencia[];
  /** Las partes que no se midieron: cajas grises punteadas, «Brazo · no se vio». */
  noVistas: { segmento: SegmentoDeSecuencia; etiqueta: string }[];
  sinDatos: boolean;
  /** Para el lector de pantalla. */
  resumen: string;
};

const NOMBRE_CAJA: Record<SegmentoDeSecuencia, string> = { pelvis: "Cadera", torso: "Tronco", brazo: "Brazo" };

/**
 * Qué parte llegó primero a su giro más rápido, sin ejes ni números. Las partes cuya diferencia no supera la tolerancia del reporte
 * (8,33 ms, decisión 032) van juntas en UNA caja: a esa resolución no se puede decir cuál fue primero.
 */
export function secuenciaSimple(reporte: Json | null): SecuenciaSimple {
  const tolS = (trazabilidadDe(reporte).tolerancia_orden_ms ?? 1000 / 120) / 1000;
  const r = repeticionesDe(reporte).find((x) => x.picos?.some((p) => p.confianza >= UMBRAL_CONFIANZA_PICO && Number.isFinite(p.instante_s)));
  const orden: SegmentoDeSecuencia[] = ["pelvis", "torso", "brazo"];
  const medidas = orden
    .map((s) => ({ s, p: r?.picos?.find((p) => p.segmento === s && p.confianza >= UMBRAL_CONFIANZA_PICO && Number.isFinite(p.instante_s)) }))
    .filter((x): x is { s: SegmentoDeSecuencia; p: NonNullable<typeof x.p> } => !!x.p)
    .sort((a, b) => a.p.instante_s - b.p.instante_s);
  const noVistas = orden
    .filter((s) => !medidas.some((x) => x.s === s))
    .map((s) => ({ segmento: s, etiqueta: `${NOMBRE_CAJA[s]} · no se vio` }));
  if (medidas.length === 0) {
    return { cajas: [], noVistas, sinDatos: true, resumen: "No se pudo ver qué giró primero." };
  }
  const grupos: { s: SegmentoDeSecuencia; t: number }[][] = [];
  for (const x of medidas) {
    const ultimo = grupos[grupos.length - 1];
    if (ultimo && x.p.instante_s - ultimo[0].t <= tolS + 1e-9) ultimo.push({ s: x.s, t: x.p.instante_s });
    else grupos.push([{ s: x.s, t: x.p.instante_s }]);
  }
  const cajas: CajaDeSecuencia[] = grupos.map((gr) => {
    const partes = gr.map((x) => x.s);
    const nombres = partes.map((s) => NOMBRE_CAJA[s].toLowerCase());
    const etiqueta = partes.length === 1 ? NOMBRE_CAJA[partes[0]] : `${NOMBRE_CAJA[partes[0]]} y ${nombres.slice(1).join(" y ")}`;
    return { partes, etiqueta, casiALaVez: partes.length > 1 };
  });
  const resumen =
    cajas.map((c) => (c.casiALaVez ? `${c.etiqueta.toLowerCase()} casi a la vez` : c.etiqueta.toLowerCase())).join(", antes ") +
    (noVistas.length ? `. No se vio: ${noVistas.map((n) => NOMBRE_CAJA[n.segmento].toLowerCase()).join(" ni ")}.` : ".");
  return { cajas, noVistas, sinDatos: false, resumen: `Qué giró primero: ${resumen}` };
}

// --- título de la pantalla del golpe --------------------------------------------------------------------------------------------

/** «Saque · golpe 4 de 6». Un golpe solo en su sesión: «Saque · golpe único». Sin saber el lugar (todavía se lee): solo el golpe. */
export function tituloDeGolpe(gesto: string, posicion: { n: number; m: number } | null): { gesto: string; resto: string | null } {
  const nombre = { saque: "Saque", drive: "Drive", reves: "Revés" }[gesto] ?? "Golpe";
  if (!posicion || posicion.n < 1 || posicion.m < 1) return { gesto: nombre, resto: null };
  if (posicion.m === 1) return { gesto: nombre, resto: "golpe único" };
  return { gesto: nombre, resto: `golpe ${posicion.n} de ${posicion.m}` };
}
