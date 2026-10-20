// La matriz de casos de docs/ux/textos-reporte-039-propuesta.md como casos de prueba: cada escenario genera sus textos con las mismas reglas,
// y se verifica lo esencial de cada uno más las palabras prohibidas y la jerga.
import { describe, expect, test } from "bun:test";
import { CASOS, type Caso } from "./casos-matriz";
import { JERGA, PROHIBIDAS } from "./palabras-prohibidas";
import { LITERATURA_SAQUE, LITERATURA_SIN_REFERENCIA, textosDeGolpe, textosDeSesion, type Item } from "../src/lib/textos-reporte";

const textos = (c: Caso) => (c.tipo === "golpe" ? textosDeGolpe(c.golpe) : textosDeSesion(c.sesion));
const juntar = (items: Item[]) => items.map((i) => `${i.titulo ?? ""} ${i.texto}`).join("\n");
const caso = (id: string) => CASOS.find((c) => c.id === id)!;

describe("matriz de casos", () => {
  test("están los once escenarios pedidos", () => {
    expect(CASOS.map((c) => c.n)).toEqual(["1", "2", "3", "4a", "4b", "5", "6", "7", "8", "9", "10", "11"]);
  });

  for (const c of CASOS) {
    test(`caso ${c.n}: sin palabras prohibidas ni jerga interna`, () => {
      const t = textos(c);
      const todo = [
        t.enUnaFrase,
        juntar(t.vimos.medido),
        juntar(t.vimos.noMedido),
        "seAparta" in t.vimos ? juntar(t.vimos.seAparta) : "",
        juntar(t.hacer.medir),
        juntar(t.hacer.usar),
        `${t.hacer.literatura.aclaracion} ${t.hacer.literatura.texto}`,
        t.profesional.preguntas.join("\n"),
        juntar(t.profesional.confianza),
      ].join("\n");
      expect(PROHIBIDAS.filter((r) => r.test(todo)).map(String)).toEqual([]);
      expect(JERGA.filter((r) => r.test(todo)).map(String)).toEqual([]);
    });
    test(`caso ${c.n}: todo ángulo de rodilla o de codo trae su referencia de 180°`, () => {
      const t = textos(c);
      const lineas = [...t.vimos.medido, ...t.vimos.noMedido, ...("seAparta" in t.vimos ? t.vimos.seAparta : [])];
      for (const l of lineas) if (/(rodilla|codo)[^.]*\d+°/i.test(l.texto)) expect(l.texto).toContain("180°");
    });
  }

  test("1. cadera claramente antes", () => {
    const t = textos(caso("cadera_antes"));
    expect(t.enUnaFrase).toBe("Tu cadera giró antes que tu tronco en este saque.");
    expect(juntar(t.vimos.medido)).toContain("Tu cadera alcanzó su giro más rápido 42 milésimas de segundo antes que tu tronco.");
    expect(juntar(t.vimos.medido)).toContain("Desde otra posición de cámara, este orden podría verse distinto.");
  });

  test("2. tronco antes que la cadera", () => {
    const t = textos(caso("tronco_antes"));
    expect(t.enUnaFrase).toBe("Tu tronco giró antes que tu cadera en este saque.");
    expect(juntar(t.vimos.medido)).toContain("Tu tronco alcanzó su giro más rápido 42 milésimas de segundo antes que tu cadera.");
  });

  test("3. sin nada medido: lo dice una vez, sin culpar al brazo ni inventar una medición", () => {
    const t = textos(caso("nada_medido"));
    expect(t.enUnaFrase).toBe("De este golpe no se pudo medir lo suficiente como para resumirlo en una frase.");
    expect(t.vimos.medido).toHaveLength(0);
    expect(t.vimos.noMedido).toHaveLength(1);
    expect(juntar(t.vimos.noMedido)).not.toContain("tapó");
    expect(juntar(t.hacer.medir)).toContain("el cuerpo entero a la vista");
  });

  test("4. drive y revés: el recuadro dice que no hay referencia, y el saque sí la tiene", () => {
    expect(textos(caso("drive")).hacer.literatura.texto).toBe(LITERATURA_SIN_REFERENCIA);
    expect(textos(caso("reves")).hacer.literatura.texto).toBe(LITERATURA_SIN_REFERENCIA);
    expect(textos(caso("cadera_antes")).hacer.literatura.texto).toBe(LITERATURA_SAQUE);
    expect(textos(caso("drive")).enUnaFrase.endsWith("en este drive.")).toBe(true);
    expect(textos(caso("reves")).enUnaFrase.endsWith("en este revés.")).toBe(true);
  });

  test("5. cámara del lado de la mano dominante: el brazo visible no figura como no medido y se avisa que ese lado no está validado", () => {
    const t = textos(caso("lado_mano"));
    expect(juntar(t.vimos.noMedido)).not.toContain("brazo");
    expect(juntar(t.hacer.medir)).toContain("del lado de tu mano dominante");
    expect(juntar(t.hacer.medir)).toContain("todavía no está validado");
    // el brazo medido aparece en el detalle, comparado con el tronco, sin evaluarlo
    const filas = (t as ReturnType<typeof textosDeGolpe>).detalle.flatMap((g) => g.filas);
    expect(filas.find((f) => f.dato.startsWith("Giro más rápido del brazo"))?.valor).toContain("52 ms después que el tronco");
  });

  test("6. zurdo: los lados se espejan", () => {
    const t = textos(caso("zurdo"));
    expect(juntar(t.vimos.noMedido)).toContain("a tu derecha");
    expect(juntar(t.vimos.noMedido)).toContain("La rodilla derecha:");
    expect(juntar(t.hacer.medir)).toContain("Con la cámara a tu derecha");
  });

  test("7. orden mezclado: se cuenta cuántos de cada uno, sin hablar de un patrón", () => {
    const t = textos(caso("orden_mezclado"));
    expect(juntar(t.vimos.medido)).toContain("en 2 fue la cadera y en 1, el tronco");
    expect(t.enUnaFrase).toBe("Medimos seis saques. Giraste parecido en casi todos y, cuando se pudo ver el orden, a veces arrancó primero la cadera y a veces el tronco.");
    expect(juntar(t.vimos.medido)).not.toMatch(/se repite|se repitió/);
  });

  test("8. tres golpes: ni variación ni repetición, y se dice por qué", () => {
    const t = textos(caso("tres_golpes"));
    expect(t.enUnaFrase).toBe("Medimos tres saques. Cuando se pudo ver el orden, la cadera arrancó primero.");
    expect(t.enUnaFrase).not.toContain("parecido");
    expect(juntar(t.vimos.medido)).toContain("los 3 golpes quedaron entre 32° y 42°");
    expect(juntar(t.vimos.medido)).not.toContain("±");
    expect(juntar(t.hacer.usar)).not.toContain("variación entre golpes");
    expect(juntar(t.hacer.medir)).toContain("Con 5 o más golpes en que se distinga");
    expect(t.vimos.seAparta).toHaveLength(0);
  });

  test("9. sin ningún golpe que se aparte: el rango concreto, sin adjetivo y sin excepciones", () => {
    const t = textos(caso("sin_apartan"));
    expect(t.enUnaFrase).toBe("Medimos cinco saques. Giraste parecido en todos y, cuando se pudo ver el orden, la cadera arrancó primero.");
    expect(juntar(t.vimos.medido)).toContain("los 5 golpes quedaron entre 29° y 42°");
    expect(t.enUnaFrase).not.toContain("salvo");
    expect(t.vimos.seAparta).toHaveLength(0);
  });

  test("10. un solo golpe ordenable: el singular, sin generalizar", () => {
    const t = textos(caso("un_ordenable"));
    expect(t.enUnaFrase).toBe("Medimos cuatro saques. Cuando se pudo ver el orden, la cadera arrancó primero.");
    expect(juntar(t.vimos.medido)).toContain("En 1 de los 4 golpes (el 1) se pudo establecer cuál giró primero, y fue la cadera");
  });

  test("11. ningún golpe ordenable", () => {
    const t = textos(caso("ningun_ordenable"));
    expect(t.enUnaFrase).toBe("Medimos tres saques. En ninguno se pudo ver qué giró primero: la cadera y el tronco giraron casi a la vez.");
    expect(juntar(t.vimos.medido)).toContain("En ningún golpe se pudo establecer cuál giró primero");
  });

  test("7: el golpe que se aparta se nombra con su valor en «Qué vimos», no en la frase", () => {
    expect(juntar(textos(caso("orden_mezclado")).vimos.medido)).toContain("5 golpes quedaron entre 29° y 42° y el golpe 6 fue de 11°");
  });
});
