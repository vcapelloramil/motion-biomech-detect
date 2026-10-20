// Rellena las zonas «GENERADO» de docs/ux/textos-reporte-039-propuesta.md con lo que producen las reglas de verdad
// (`src/lib/textos-reporte.ts`): el golpe 4, la sesión del 25/9 y la matriz de casos. Así el documento que se cita en la tesis
// no puede decir otra cosa que el programa. Uso, desde frontend/:   bun tests/generar-textos-doc.ts
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { CASOS, CASOS_EVOLUCION, consistenciaReal, golpesReales, type Incluir } from "./casos-matriz";
import { textosDeEvolucion } from "../src/lib/textos-evolucion";
import {
  VERSION_TEXTOS,
  contextoDeGolpe,
  textosDeGolpe,
  textosDeSesion,
  type Item,
  type TextosGolpe,
  type TextosSesion,
} from "../src/lib/textos-reporte";

const ruta = resolve(import.meta.dir, "../../docs/ux/textos-reporte-039-propuesta.md");

const linea = (i: Item, ayuda = true) => `${i.titulo ? `**${i.titulo}** ` : ""}${i.texto}${ayuda && i.ayuda ? " ⓘ" : ""}`;
const cita = (s: string) => s.split("\n").map((l) => `> ${l}`.trimEnd()).join("\n");
const lista = (items: Item[], ayuda = true) => items.map((i) => `- ${linea(i, ayuda)}`).join("\n");
const listaEnlaces = (items: Item[]) =>
  items.map((i) => `- ${linea(i, false)}${i.enlace === "sesion" ? " *(enlace a la sesión)*" : i.enlace === "evolucion" ? " *(enlace a Evolución)*" : ""}`).join("\n");

function vimos(t: TextosGolpe | TextosSesion): string {
  const partes: string[] = [];
  partes.push("**Lo que se midió**\n" + (t.vimos.medido.length ? lista(t.vimos.medido) : "- *(nada)*"));
  if ("seAparta" in t.vimos && t.vimos.seAparta.length) partes.push("**Un golpe que se aparta**\n" + lista(t.vimos.seAparta));
  if (t.vimos.noMedido.length) partes.push("**Lo que no se pudo medir**\n" + lista(t.vimos.noMedido));
  return cita(partes.join("\n\n"));
}

function extras(t: TextosGolpe | TextosSesion, incluir: Incluir[]): string {
  const s: string[] = [];
  if (incluir.includes("medir") && t.hacer.medir.length) s.push("**Qué podés hacer → para medir mejor**\n" + listaEnlaces(t.hacer.medir));
  if (incluir.includes("usar") && t.hacer.usar.length) s.push("**Qué podés hacer → para usar estos datos al entrenar**\n" + listaEnlaces(t.hacer.usar));
  if (incluir.includes("literatura")) s.push(`**Contexto de la literatura** *(recuadro aparte)*\n> ${t.hacer.literatura.aclaracion} ${t.hacer.literatura.texto}`);
  if (incluir.includes("preguntas")) s.push("**Para tu entrenador → preguntas**\n" + t.profesional.preguntas.map((q, i) => `${i + 1}. ${q}`).join("\n"));
  return s.length ? "\n\n" + cita(s.join("\n\n")) : "";
}

function golpeCompleto(t: TextosGolpe): string {
  const f = t.fotos;
  const fotos = [
    f.fotoUnica ? `**Una sola foto** — ${f.etiquetaFotoUnica}` : "**Tres fotos** (cadera, tronco, brazo)",
    `**Qué mirar:** ${f.queMirarFoto}`,
    f.video ? `**Video.** ${f.video} ${f.queMirarVideo}` : "",
  ].filter(Boolean);
  const detalle = t.detalle
    .map((g) => `**${g.titulo}**\n\n| Dato | Valor | Qué significa |\n| --- | --- | --- |\n${g.filas.map((x) => `| ${x.dato} | ${x.valor} | ${x.significa} |`).join("\n")}`)
    .join("\n\n");
  return [
    `**En una frase**\n\n${cita(t.enUnaFrase)}`,
    `#### 1. Qué vimos\n\n${vimos(t)}`,
    `#### 2. Fotos y video\n\n${cita(fotos.join("\n\n"))}`,
    `#### 3. Qué podés hacer con esto\n\n${cita(
      [
        t.hacer.medir.length ? "**Para medir mejor**\n" + listaEnlaces(t.hacer.medir) : "",
        "**Para usar estos datos al entrenar**\n" + listaEnlaces(t.hacer.usar),
        `**${t.hacer.literatura.titulo}** *(recuadro aparte)*\n${t.hacer.literatura.aclaracion} ${t.hacer.literatura.texto}`,
      ].filter(Boolean).join("\n\n"),
    )}`,
    `#### 4. Para tu entrenador o profesional\n\n${cita(
      [
        "**Preguntas para llevar**\n" + t.profesional.preguntas.map((q, i) => `${i + 1}. ${q}`).join("\n"),
        "**[Descargar PDF]**",
        "**Cuánto se puede confiar en cada medición**\n" + lista(t.profesional.confianza, false),
        `**Aviso**\n${t.profesional.aviso}`,
      ].join("\n\n"),
    )}`,
    `#### 5. Detalle técnico *(cerrado)*\n\n${detalle}`,
  ].join("\n\n");
}

function sesionCompleta(t: TextosSesion): string {
  const tip = t.tipico ? `**${t.tipico.texto}**\n\n**Qué mirar:** ${t.tipico.queMirar}` : "*(sin golpe típico)*";
  const d = t.detalle;
  return [
    `**En una frase**\n\n${cita(t.enUnaFrase)}`,
    `#### 1. Qué vimos\n\n${vimos(t)}`,
    `#### 2. Fotos y video\n\n${cita(tip)}`,
    `#### 3. Qué podés hacer con esto\n\n${cita(
      [
        t.hacer.medir.length ? "**Para medir mejor**\n" + listaEnlaces(t.hacer.medir) : "",
        "**Para usar estos datos al entrenar**\n" + listaEnlaces(t.hacer.usar),
        `**${t.hacer.literatura.titulo}** *(recuadro aparte)*\n${t.hacer.literatura.aclaracion} ${t.hacer.literatura.texto}`,
      ].filter(Boolean).join("\n\n"),
    )}`,
    `#### 4. Para tu entrenador o profesional\n\n${cita(
      [
        "**Preguntas para llevar**\n" + t.profesional.preguntas.map((q, i) => `${i + 1}. ${q}`).join("\n"),
        "**[Descargar PDF]**",
        "**Cuánto se puede confiar en cada medición**\n" + lista(t.profesional.confianza, false),
        `**Aviso**\n${t.profesional.aviso}`,
      ].join("\n\n"),
    )}`,
    `#### 5. Detalle técnico *(cerrado)*\n\n| ${d.columnas.join(" | ")} |\n| ${d.columnas.map(() => "---").join(" | ")} |\n${d.filas.map((f) => `| ${f.join(" | ")} |`).join("\n")}\n\n*${d.nota}*\n\n` +
      d.terminos.map((x) => `- **${x.termino}:** ${x.significa}`).join("\n") + `\n\n*${d.versiones}*`,
  ].join("\n\n");
}

function matriz(): string {
  return CASOS.map((c) => {
    const t = c.tipo === "golpe" ? textosDeGolpe(c.golpe) : textosDeSesion(c.sesion);
    return `### Caso ${c.n} — ${c.titulo}\n\n*${c.escenario}*\n\n**En una frase**\n\n${cita(t.enUnaFrase)}\n\n**Qué vimos**\n\n${vimos(t)}${extras(t, c.incluir)}`;
  }).join("\n\n---\n\n");
}

function evolucion(): string {
  return CASOS_EVOLUCION.map((c) => {
    const t = textosDeEvolucion(c.serie);
    const vimosMd = [
      "**Lo que se midió**\n" + (t.vimos.medido.length ? lista(t.vimos.medido) : "- *(nada)*"),
      t.vimos.noMedido.length ? "**Lo que no se pudo medir**\n" + lista(t.vimos.noMedido) : "",
    ]
      .filter(Boolean)
      .join("\n\n");
    const partes = [
      `### Caso ${c.n} — ${c.titulo}\n\n*${c.escenario}*`,
      `**En una frase**\n\n${cita(t.enUnaFrase)}`,
      `**Qué vimos**\n\n${cita(vimosMd)}`,
    ];
    if (t.pocasSesiones) partes.push(`**Menos de dos sesiones comparables**\n\n${cita(t.pocasSesiones)}`);
    if (t.avisos.length) partes.push(`**Avisos**\n\n${t.avisos.map((a) => `- ${a}`).join("\n")}`);
    return partes.join("\n\n");
  }).join("\n\n---\n\n");
}

function golpe4(): string {
  const g = golpesReales[3];
  return golpeCompleto(
    textosDeGolpe({
      reporte: g.reporte,
      gesto: "saque",
      encuadre: "tres_cuartos",
      ladoCamara: "izquierda",
      manoDominante: "derecha",
      contexto: contextoDeGolpe(consistenciaReal, g.id),
    }),
  );
}

function sesion(): string {
  return sesionCompleta(
    textosDeSesion({ gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: golpesReales, consistencia: consistenciaReal }),
  );
}

function rellenar(doc: string, zona: string, contenido: string): string {
  const re = new RegExp(`(<!-- GENERADO:${zona} -->)[\\s\\S]*?(<!-- /GENERADO:${zona} -->)`);
  if (!re.test(doc)) throw new Error(`falta la zona GENERADO:${zona} en el documento`);
  return doc.replace(re, (_m, a, z) => `${a}\n\n${contenido}\n\n${z}`);
}

let doc = readFileSync(ruta, "utf-8");
doc = rellenar(doc, "golpe4", golpe4());
doc = rellenar(doc, "sesion", sesion());
doc = rellenar(doc, "matriz", matriz());
doc = rellenar(doc, "evolucion", evolucion());
doc = rellenar(doc, "version", `Textos **v${VERSION_TEXTOS}** · generado con \`bun tests/generar-textos-doc.ts\` desde \`frontend/src/lib/textos-reporte.ts\` y la sesión real del 25/9/2026.`);
writeFileSync(ruta, doc, "utf-8");
console.log("documento actualizado:", ruta);
