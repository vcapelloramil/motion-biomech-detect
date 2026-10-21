// Se corre con `bun test` desde frontend/. Los textos del reporte (decisión 039), probados con una sesión REAL: la del saque en tres cuartos
// del 25/9/2026 (6 golpes, motor 0.5.3; solo métricas, sin video). Fixture: tests/fixtures/sesion-25-9-saque-tres-cuartos.json
import { describe, expect, test } from "bun:test";
import fx from "./fixtures/sesion-25-9-saque-tres-cuartos.json";
import type { Consistencia } from "../src/lib/consistencia";
import { CAMBIO_DE_VARIACION, JERGA, PROHIBIDAS } from "./palabras-prohibidas";
import {
  AVISO,
  GLOSARIO,
  LITERATURA_SAQUE,
  LITERATURA_SIN_REFERENCIA,
  VERSION_TEXTOS,
  articulacionLlana,
  contextoDeGolpe,
  datosDeSecuencia,
  ordenDelGolpe,
  posturaDe,
  CORTES_POSTURA,
  secuenciaSimple,
  tituloDeGolpe,
  textosDeGolpe,
  textosDeSesion,
  type EntradaGolpe,
  type EntradaSesion,
  type Item,
} from "../src/lib/textos-reporte";

type Json = Record<string, unknown>;
const consistencia = fx.consistencia as unknown as Consistencia;
const golpes = fx.golpes.map((g) => ({ id: g.id, estado: g.estado, reporte: g.reporte as unknown as Json }));

const entradaGolpe = (i: number, extra: Partial<EntradaGolpe> = {}): EntradaGolpe => ({
  reporte: golpes[i].reporte as Json,
  gesto: "saque",
  encuadre: "tres_cuartos",
  ladoCamara: "izquierda",
  manoDominante: "derecha",
  contexto: contextoDeGolpe(consistencia, golpes[i].id),
  ...extra,
});
const entradaSesion = (extra: Partial<EntradaSesion> = {}): EntradaSesion => ({
  gesto: "saque",
  encuadre: "tres_cuartos",
  ladoCamara: "izquierda",
  manoDominante: "derecha",
  golpes,
  consistencia,
  ...extra,
});

const textoDe = (items: Item[]) => items.map((i) => `${i.titulo ?? ""} ${i.texto}`).join("\n");

describe("golpe 4 (el golpe típico de la sesión del 25/9)", () => {
  const t = textosDeGolpe(entradaGolpe(3));

  test("En una frase: lo que pidió Valentín", () => {
    expect(t.enUnaFrase).toBe("Tu cadera y tu tronco giraron casi a la vez en este saque.");
  });

  test("Qué vimos empieza por lo medido, y lo no medido va después con su porqué", () => {
    expect(t.vimos.medido[0].texto).toContain("34°");
    expect(t.vimos.medido[1].texto).toContain("4 milésimas de segundo");
    expect(t.vimos.medido[1].texto).toContain("no se puede decir cuál fue primero");
    expect(t.vimos.noMedido.map((n) => n.titulo)).toEqual(["El brazo con el que golpeás:", "La rodilla izquierda:"]);
    expect(t.vimos.noMedido[0].texto).toContain("a tu izquierda, el cuerpo lo tapó");
  });

  test("el codo del brazo que NO golpea no está en «Qué vimos» (pasa al detalle técnico)", () => {
    expect(textoDe(t.vimos.medido)).not.toMatch(/codo/i);
    const detalle = t.detalle.flatMap((g) => g.filas).find((f) => f.dato === "Codo izquierdo");
    expect(detalle?.valor).toContain("157,1°");
    expect(detalle?.significa).toContain("180° es el brazo recto, sin doblar");
    expect(detalle?.significa).toContain("no golpea");
  });

  test("una sola foto: cadera y tronco están a 4 ms", () => {
    expect(t.fotos.fotoUnica).toBe(true);
    expect(t.fotos.etiquetaFotoUnica).toContain("5,21 s del video");
    expect(t.fotos.queMirarFoto).toContain("violeta");
    expect(t.fotos.video).toContain("8 veces más lento");
  });

  test("las preguntas solo están en la sección para el profesional", () => {
    expect(t.profesional.preguntas.length).toBe(2);
    expect(t.profesional.preguntas[1]).toContain("la sesión va de 11° a 42°");
    expect(textoDe(t.hacer.medir)).not.toContain("¿");
    expect(textoDe(t.hacer.usar)).not.toContain("¿");
  });

  test("el aviso no trae «riesgo de lesión» y la goniometría se explica", () => {
    expect(t.profesional.aviso).toBe(AVISO);
    expect(AVISO).toBe(
      "KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.",
    );
    expect(AVISO.toLowerCase()).not.toContain("riesgo");
    expect(textoDe(t.profesional.confianza)).toContain("goniometría manual a ciegas (medición manual del ángulo sobre la imagen)");
    expect(textoDe(t.profesional.confianza)).toContain("12,5°");
  });

  test("literatura: la frase general, sin Fleisig y sin datos del jugador", () => {
    expect(t.hacer.literatura.texto).toBe(LITERATURA_SAQUE);
    expect(LITERATURA_SAQUE).toContain("Kovacs y Ellenbecker, 2011");
    expect(LITERATURA_SAQUE).not.toContain("Fleisig");
    expect(LITERATURA_SAQUE).not.toMatch(/\d°|\d ms/);
    expect(textosDeGolpe(entradaGolpe(3, { gesto: "drive" })).hacer.literatura.texto).toBe(LITERATURA_SIN_REFERENCIA);
  });

  test("lleva la versión de los textos", () => {
    expect(t.version).toBe(VERSION_TEXTOS);
    expect(t.detalle.flatMap((g) => g.filas).some((f) => f.dato === "Textos" && f.valor === `v${VERSION_TEXTOS}`)).toBe(true);
  });
});

describe("golpe con orden distinguible (golpe 1) y con rodilla medida", () => {
  const t = textosDeGolpe(entradaGolpe(0));
  test("la rodilla ocupa el lugar del codo, con su referencia", () => {
    const linea = t.vimos.medido.find((m) => /rodilla/.test(m.texto));
    expect(linea?.texto).toContain("178°");
    expect(linea?.texto).toContain("180° es la pierna recta, sin doblar");
  });
  test("el orden se dice como observación y con la salvedad de la cámara", () => {
    expect(t.enUnaFrase).toBe("Tu cadera giró antes que tu tronco en este saque.");
    const l = t.vimos.medido.find((m) => /antes que tu tronco/.test(m.texto));
    expect(l?.texto).toContain("17 milésimas de segundo");
    expect(l?.texto).toContain("Desde otra posición de cámara, este orden podría verse distinto.");
  });
});

describe("la sesión del 25/9", () => {
  const s = textosDeSesion(entradaSesion());

  test("En una frase: lo que pidió Valentín", () => {
    expect(s.enUnaFrase).toBe("Medimos seis saques. Giraste parecido en casi todos y, cuando se pudo ver el orden, la cadera arrancó primero.");
  });

  test("la torsión usa «valor típico» y el golpe 6 se explica sin contradicción", () => {
    const l = s.vimos.medido[0].texto;
    expect(l).toContain("valor típico de 33°");
    expect(l).toContain("5 golpes quedaron entre 29° y 42°");
    expect(l).toContain("el golpe 6 fue de 11°");
    expect(l).not.toContain("±");
    expect(l).not.toContain("valor central");
  });

  test("el orden: 3 de 6, siempre la cadera, 17 a 42 ms, con la salvedad de la cámara", () => {
    const l = s.vimos.medido[1].texto;
    expect(l).toContain("En 3 de los 6 golpes (1, 3 y 5)");
    expect(l).toContain("en los 3 fue la cadera");
    expect(l).toContain("entre 17 y 42 milésimas de segundo");
    expect(l).toContain("En los otros 3 quedaron casi a la vez (entre 4 y 8 ms)");
    expect(l).toContain("Desde otra posición de cámara, este orden podría verse distinto.");
    expect(l).not.toContain("Esto vale para esta posición de cámara");
    expect(l).not.toMatch(/se repite|se repitió/); // 3 ordenables: por debajo del mínimo de 5
  });

  test("el golpe 6 se aparta también en la rodilla", () => {
    expect(s.vimos.seAparta).toHaveLength(1);
    expect(s.vimos.seAparta[0].titulo).toBe("El golpe 6 se parece menos a los demás:");
    expect(s.vimos.seAparta[0].texto).toContain("101°, contra 172° a 178°");
    expect(s.vimos.seAparta[0].texto).toContain("180° es la pierna recta, sin doblar");
  });

  test("lo no medido: el brazo en ningún golpe, y la rodilla del golpe 4", () => {
    expect(s.vimos.noMedido[0].titulo).toBe("El brazo con el que golpeás,");
    expect(s.vimos.noMedido[0].texto).toContain("en ningún golpe");
    expect(textoDe(s.vimos.noMedido)).toContain("(el 4)");
  });

  test("las tres preguntas; la última es la que pidió Valentín", () => {
    expect(s.profesional.preguntas).toHaveLength(3);
    expect(s.profesional.preguntas[0]).toContain("En el golpe 6 la torsión fue de 11°");
    expect(s.profesional.preguntas[2]).toBe("¿Cuál de estos 6 saques sentiste más cómodo o más potente? Mirá sus números y su video: ¿se distingue en algo?");
  });

  test("Evolución usa «valor típico» y la variación", () => {
    expect(textoDe(s.hacer.usar)).toContain("valor típico de la torsión (hoy 33°) se mantiene de una sesión a otra. La variación entre golpes (hoy ±4°) sirve como idea general");
  });

  test("el golpe típico es el 4", () => {
    expect(s.tipico?.numero).toBe(4);
  });

  test("detalle: una fila por golpe, con la referencia de 180° en los encabezados y en la nota", () => {
    expect(s.detalle.filas).toHaveLength(6);
    expect(s.detalle.columnas.join("|")).toContain("180° = estirada");
    expect(s.detalle.nota).toContain("180° es la pierna (o el brazo) recta, sin doblar");
    expect(s.detalle.filas[5][3]).toBe("101°");
    expect(s.detalle.filas[3][3]).toBe("no medida");
  });

  test("sin la comparación del servidor, se dice y no se inventa nada", () => {
    const sin = textosDeSesion(entradaSesion({ consistencia: null }));
    expect(sin.enUnaFrase).toContain("no estaba disponible");
    expect(sin.vimos.medido).toHaveLength(0);
  });
});

describe("casos que no son los de la sesión del 25/9", () => {
  test("un orden mezclado se cuenta sin hablar de un patrón", () => {
    const c: Consistencia = JSON.parse(JSON.stringify(consistencia));
    // golpe 3: ahora el tronco llega antes (torso 42 ms antes que la cadera)
    const gs = JSON.parse(JSON.stringify(golpes)) as typeof golpes;
    const picos = ((gs[2].reporte.secuenciacion as { repeticiones: { picos: { segmento: string; instante_s: number }[] }[] }).repeticiones[0].picos);
    picos.find((p) => p.segmento === "pelvis")!.instante_s = 0.342;
    picos.find((p) => p.segmento === "torso")!.instante_s = 0.3;
    expect(ordenDelGolpe(gs[2].reporte).tipo).toBe("tronco_primero");
    const s = textosDeSesion(entradaSesion({ golpes: gs, consistencia: c }));
    expect(s.vimos.medido[1].texto).toContain("en 2 fue la cadera y en 1, el tronco");
    expect(s.enUnaFrase).toContain("a veces arrancó primero la cadera y a veces el tronco");
  });

  test("sin saber la mano dominante no se afirma que el cuerpo tapa el brazo", () => {
    const t = textosDeGolpe(entradaGolpe(3, { manoDominante: null }));
    expect(textoDe(t.vimos.noMedido)).not.toContain("el cuerpo lo tapó");
    expect(textoDe(t.vimos.noMedido)).toContain("no pudo seguirlo con confianza");
  });

  test("drive: «un drive típico», sin literatura y sin afirmar nada del brazo tapado", () => {
    const t = textosDeGolpe(entradaGolpe(3, { gesto: "drive" }));
    expect(t.enUnaFrase).toBe("Tu cadera y tu tronco giraron casi a la vez en este drive.");
    expect(t.hacer.literatura.texto).toBe(LITERATURA_SIN_REFERENCIA);
    expect(textoDe(t.vimos.noMedido)).not.toContain("el cuerpo lo tapó");
  });

  test("un golpe sin contexto de sesión no se llama típico", () => {
    const t = textosDeGolpe(entradaGolpe(3, { contexto: null }));
    expect(t.enUnaFrase).toBe("Tu cadera y tu tronco giraron casi a la vez en este saque.");
    expect(t.profesional.preguntas).toHaveLength(1);
  });

  test("los nombres internos se vuelven palabras", () => {
    expect(articulacionLlana("codo_der")).toBe("codo derecho");
    expect(articulacionLlana("rodilla_izq")).toBe("rodilla izquierda");
  });
});

// --- palabras prohibidas (R2 y decisión 039) -------------------------------------------------------------------------------------

function todasLasFrases(): { donde: string; texto: string }[] {
  const salida: { donde: string; texto: string }[] = [];
  const agregar = (donde: string, texto: string) => salida.push({ donde, texto });
  const items = (donde: string, l: Item[]) => l.forEach((i, n) => agregar(`${donde}[${n}]`, `${i.titulo ?? ""} ${i.texto}`));
  const comunes = (donde: string, t: { enUnaFrase: string; hacer: { medir: Item[]; usar: Item[]; literatura: { aclaracion: string; texto: string } }; profesional: { preguntas: string[]; confianza: Item[] } }) => {
    agregar(`${donde}.enUnaFrase`, t.enUnaFrase);
    items(`${donde}.medir`, t.hacer.medir);
    items(`${donde}.usar`, t.hacer.usar);
    agregar(`${donde}.literatura`, `${t.hacer.literatura.aclaracion} ${t.hacer.literatura.texto}`);
    t.profesional.preguntas.forEach((p, n) => agregar(`${donde}.pregunta${n}`, p));
    items(`${donde}.confianza`, t.profesional.confianza);
  };
  for (const gesto of ["saque", "drive", "reves"]) {
    for (let i = 0; i < golpes.length; i++) {
      const t = textosDeGolpe(entradaGolpe(i, { gesto }));
      const d = `golpe${i + 1}/${gesto}`;
      comunes(d, t);
      items(`${d}.medido`, t.vimos.medido);
      items(`${d}.noMedido`, t.vimos.noMedido);
      agregar(`${d}.fotos`, [t.fotos.queMirarFoto, t.fotos.etiquetaFotoUnica, t.fotos.video, t.fotos.queMirarVideo].filter(Boolean).join(" "));
      t.detalle.forEach((g) => g.filas.forEach((f) => agregar(`${d}.detalle.${f.dato}`, `${f.valor} ${f.significa}`)));
    }
    const s = textosDeSesion(entradaSesion({ gesto }));
    comunes(`sesion/${gesto}`, s);
    items(`sesion/${gesto}.medido`, s.vimos.medido);
    items(`sesion/${gesto}.noMedido`, s.vimos.noMedido);
    items(`sesion/${gesto}.seAparta`, s.vimos.seAparta);
    if (s.tipico) agregar(`sesion/${gesto}.tipico`, `${s.tipico.texto} ${s.tipico.queMirar}`);
    s.detalle.terminos.forEach((t) => agregar(`sesion/${gesto}.termino.${t.termino}`, `${t.termino} ${t.significa}`));
    agregar(`sesion/${gesto}.nota`, s.detalle.nota);
  }
  for (const [k, g] of Object.entries(GLOSARIO)) agregar(`glosario.${k}`, `${g.termino} ${g.corto}`);
  return salida;
}

describe("palabras prohibidas y jerga", () => {
  const frases = todasLasFrases();
  test("se recorren muchas frases", () => {
    expect(frases.length).toBeGreaterThan(300);
  });
  test("ninguna frase generada usa una palabra prohibida (el aviso es la única que nombra lo que KinetiQ no hace)", () => {
    const malas = frases.flatMap((f) => PROHIBIDAS.filter((r) => r.test(f.texto)).map((r) => `${f.donde}: ${r} → ${f.texto.slice(0, 90)}`));
    expect(malas).toEqual([]);
  });
  test("ninguna frase usa jerga interna", () => {
    // La interpolación y el procesamiento solo pueden aparecer en el detalle técnico, cada uno con su explicación (decisión 039).
    const malas = frases.flatMap((f) =>
      JERGA.filter((r) => !(r.source === "interpol" && f.donde.includes(".detalle.")) && r.test(f.texto)).map((r) => `${f.donde}: ${r}`),
    );
    expect(malas).toEqual([]);
  });
  test("todo ángulo de rodilla o de codo lleva su referencia de 180°", () => {
    const sinReferencia = frases.filter(
      (f) => /(rodilla|codo)[^.]*\d+(,\d)?°/i.test(f.texto) && !/180°/.test(f.texto) && !/12,5°|8,5°|19,2°|36,4°/.test(f.texto),
    );
    expect(sinReferencia.map((f) => f.donde)).toEqual([]);
  });
  test("el aviso sí nombra lo que no hace, pero sin «riesgo»", () => {
    expect(/riesgo/i.test(AVISO)).toBe(false);
  });
});

describe("«Cuándo giró cada parte»: todo respecto del tronco", () => {
  test("golpe 3: la cadera 42 ms antes, el tronco en 0 y el brazo sin medir", () => {
    const d = datosDeSecuencia(golpes[2].reporte);
    expect(d.sinReferencia).toBe(false);
    expect(d.puntos.map((p) => p.segmento)).toEqual(["pelvis", "torso", "brazo"]);
    expect(d.puntos[0].etiqueta).toBe("42 ms antes");
    expect(d.puntos[1].deltaMs).toBe(0);
    expect(d.puntos[2]).toEqual({ segmento: "brazo", deltaMs: null, etiqueta: "no medido" });
    expect(d.toleranciaMs).toBeCloseTo(8.333, 2);
  });
  test("golpe 4: la cadera a 4 ms cae dentro de la zona donde no se puede distinguir", () => {
    const d = datosDeSecuencia(golpes[3].reporte);
    expect(Math.abs(d.puntos[0].deltaMs ?? 99)).toBeLessThan(d.toleranciaMs);
    expect(d.resumen).toContain("dentro de la zona donde no se puede distinguir cuál fue primero");
  });
  test("sin el tronco medido no hay referencia", () => {
    const r = JSON.parse(JSON.stringify(golpes[0].reporte));
    r.secuenciacion.repeticiones[0].picos = [];
    expect(datosDeSecuencia(r).sinReferencia).toBe(true);
  });
  test("con el brazo medido se rotula «después»", () => {
    const r = JSON.parse(JSON.stringify(golpes[2].reporte));
    r.secuenciacion.repeticiones[0].picos.push({ segmento: "brazo", instante_s: 0.352, confianza: 0.93, velocidad: 1180, unidad: "grados/s" });
    expect(datosDeSecuencia(r).puntos[2].etiqueta).toBe("52 ms después");
  });
  test("no usa segundos desde el inicio de la ventana", () => {
    const d = datosDeSecuencia(golpes[3].reporte);
    expect(JSON.stringify(d)).not.toMatch(/\d,\d{3} s|ventana/);
  });
});

describe("«En una frase»: una sola idea, sin números y con un solo verbo", () => {
  const frases = todasLasFrases().filter((f) => f.donde.endsWith(".enUnaFrase"));
  test("se recorren las frases de los tres golpes y de la sesión", () => {
    expect(frases.length).toBeGreaterThan(20);
  });
  test("ninguna contiene dígitos", () => {
    expect(frases.filter((f) => /\d/.test(f.texto)).map((f) => `${f.donde}: ${f.texto}`)).toEqual([]);
  });
  test("ninguna mezcla «giró» con «aceleró»", () => {
    expect(frases.filter((f) => /acelera/i.test(f.texto)).map((f) => f.donde)).toEqual([]);
  });
  test("ninguna dice «como se espera», «bien», «mal» ni «correcto» (decisión 036)", () => {
    expect(frases.filter((f) => /como se espera|\bbien\b|\bmal\b|correct/i.test(f.texto))).toEqual([]);
  });
});

describe("¿Qué giró primero?", () => {
  test("golpe 3: cadera antes que tronco, en dos cajas con «antes», y el brazo «no se vio»", () => {
    const s = secuenciaSimple(golpes[2].reporte);
    expect(s.cajas.map((c) => c.etiqueta)).toEqual(["Cadera", "Tronco"]);
    expect(s.cajas.every((c) => !c.casiALaVez)).toBe(true);
    expect(s.noVistas.map((n) => n.etiqueta)).toEqual(["Brazo · no se vio"]);
  });
  test("golpe 4 (empate): cadera y tronco en UNA caja «casi a la vez»", () => {
    const s = secuenciaSimple(golpes[3].reporte);
    expect(s.cajas).toHaveLength(1);
    expect(s.cajas[0].etiqueta).toBe("Cadera y tronco");
    expect(s.cajas[0].casiALaVez).toBe(true);
  });
  test("con el tronco antes, el orden de las cajas se invierte", () => {
    const r = JSON.parse(JSON.stringify(golpes[2].reporte));
    const picos = r.secuenciacion.repeticiones[0].picos as { segmento: string; instante_s: number }[];
    picos.find((p) => p.segmento === "pelvis")!.instante_s = 0.342;
    picos.find((p) => p.segmento === "torso")!.instante_s = 0.3;
    expect(secuenciaSimple(r).cajas.map((c) => c.etiqueta)).toEqual(["Tronco", "Cadera"]);
  });
  test("con el brazo medido: tres cajas, o dos si el brazo cae junto al tronco", () => {
    const r = JSON.parse(JSON.stringify(golpes[2].reporte));
    const picos = r.secuenciacion.repeticiones[0].picos as { segmento: string; instante_s: number; confianza: number; velocidad: number; unidad: string }[];
    picos.push({ segmento: "brazo", instante_s: 0.352, confianza: 0.93, velocidad: 1180, unidad: "grados/s" });
    expect(secuenciaSimple(r).cajas.map((c) => c.etiqueta)).toEqual(["Cadera", "Tronco", "Brazo"]);
    picos[2].instante_s = 0.305;
    expect(secuenciaSimple(r).cajas.map((c) => c.etiqueta)).toEqual(["Cadera", "Tronco y brazo"]);
  });
  test("sin ningún pico, no hay datos", () => {
    const r = JSON.parse(JSON.stringify(golpes[0].reporte));
    r.secuenciacion.repeticiones[0].picos = [];
    const s = secuenciaSimple(r);
    expect(s.sinDatos).toBe(true);
    expect(s.cajas).toHaveLength(0);
  });
  test("la secuencia no lleva números en lo que se ve", () => {
    for (const g of golpes) {
      const s = secuenciaSimple(g.reporte);
      expect(JSON.stringify([s.cajas.map((c) => c.etiqueta), s.noVistas.map((n) => n.etiqueta)])).not.toMatch(/\d/);
    }
  });
});

describe("rodilla y codo dichos en palabras", () => {
  test("tres categorías, ningún corte más angosto que el error medido (decisión 039)", () => {
    expect(posturaDe("rodilla", 180)).toBe("estirada o casi estirada");
    expect(posturaDe("rodilla", 165)).toBe("estirada o casi estirada");
    expect(posturaDe("rodilla", 164.9)).toBe("algo flexionada");
    expect(posturaDe("rodilla", 135)).toBe("algo flexionada");
    expect(posturaDe("rodilla", 134.9)).toBe("flexionada");
    expect(posturaDe("rodilla", 90)).toBe("flexionada");
    expect(posturaDe("codo", 172)).toBe("estirado o casi estirado");
    expect(posturaDe("codo", 150)).toBe("algo flexionado");
    expect(posturaDe("codo", 100)).toBe("flexionado");
  });
  test("las tres categorías están separadas por más que el error medio de la rodilla y del codo", () => {
    expect(CORTES_POSTURA.estirada - CORTES_POSTURA.algoFlexionada).toBeGreaterThanOrEqual(2 * 8.5);
  });
  test("nunca «totalmente estirada» en un texto para el usuario", () => {
    expect(todasLasFrases().filter((f) => /totalmente estirad/i.test(f.texto)).map((f) => f.donde)).toEqual([]);
  });
  test("golpe 1: «la pierna izquierda casi estirada», con el ángulo y la referencia", () => {
    const l = textosDeGolpe(entradaGolpe(0)).vimos.medido.find((m) => /pierna/.test(m.texto))!;
    expect(l.texto).toBe("Cuando el tronco giraba más rápido, tenías la pierna izquierda estirada o casi estirada (rodilla a 178°; 180° es la pierna recta, sin doblar).");
  });
});

describe("título del golpe y tercera persona", () => {
  test("«Saque · golpe 4 de 6»", () => {
    expect(tituloDeGolpe("saque", { n: 4, m: 6 })).toEqual({ gesto: "Saque", resto: "golpe 4 de 6" });
    expect(tituloDeGolpe("reves", { n: 1, m: 1 })).toEqual({ gesto: "Revés", resto: "golpe único" });
    expect(tituloDeGolpe("drive", null)).toEqual({ gesto: "Drive", resto: null });
  });
  test("ninguna frase habla de «su sesión» al usuario", () => {
    expect(todasLasFrases().filter((f) => /\bsu sesión\b/i.test(f.texto)).map((f) => f.donde)).toEqual([]);
  });
});

describe("la variación entre golpes con pocos golpes (decisión 040)", () => {
  test("ningún texto presenta un cambio de la variación como un cambio del jugador ni invita a ver si «se vuelve más pareja»", () => {
    const malas = todasLasFrases().flatMap((f) => CAMBIO_DE_VARIACION.filter((r) => r.test(f.texto)).map((r) => `${f.donde}: ${r}`));
    expect(malas).toEqual([]);
  });
  test("todo texto de «Qué podés hacer» que menciona la variación entre golpes dice que con pocos golpes es una estimación gruesa", () => {
    for (const c of [entradaSesion()]) {
      const s = textosDeSesion(c);
      const usar = textoDe(s.hacer.usar);
      expect(usar).toContain("±4°");
      expect(usar).toContain("estimación gruesa");
      expect(usar).toContain("no conviene compararla entre sesiones");
    }
    const g = textoDe(textosDeGolpe(entradaGolpe(3)).hacer.usar);
    expect(g).toContain("estimación gruesa");
    expect(g).not.toMatch(/más parejo|se vuelve/i);
  });
  test("el ⓘ de la variación típica lo avisa", () => {
    expect(GLOSARIO.variacion_tipica.corto).toContain("Con pocos golpes es una estimación gruesa");
    expect(GLOSARIO.variacion_tipica.corto).toContain("con 6 golpes puede moverse varios grados");
  });
  test("la versión de los textos es 4", () => {
    expect(VERSION_TEXTOS).toBe("4");
  });
});

