// Evolución en el lenguaje de la decisión 039 (segunda ronda). Series reales/variantes de tests/fixtures/evolucion-matriz.json.
import { describe, expect, test } from "bun:test";
import { CASOS_EVOLUCION, type CasoEvolucion } from "./casos-matriz";
import { JERGA, PROHIBIDAS } from "./palabras-prohibidas";
import { textosDeEvolucion } from "../src/lib/textos-evolucion";

const t = (id: string) => textosDeEvolucion(CASOS_EVOLUCION.find((c) => c.id === id)!.serie);
const juntar = (id: string) => {
  const x = t(id);
  return [x.cabecera, x.enUnaFrase, ...x.vimos.medido.map((i) => `${i.titulo ?? ""} ${i.texto}`), ...x.vimos.noMedido.map((i) => `${i.titulo ?? ""} ${i.texto}`), x.pocasSesiones ?? "", ...x.avisos, ...Object.values(x.graficos).filter(Boolean)].join("\n");
};

describe("Evolución: En una frase", () => {
  test("una sola idea y sin números, en cada caso", () => {
    for (const c of CASOS_EVOLUCION as CasoEvolucion[]) {
      const f = textosDeEvolucion(c.serie).enUnaFrase;
      expect(/\d/.test(f)).toBe(false);
    }
  });
  test("las frases de cada escenario", () => {
    expect(t("una_sesion").enUnaFrase).toBe("Tenés una sola sesión de este golpe y encuadre: es tu punto de partida.");
    expect(t("dos_sesiones").enUnaFrase).toBe("Tu torsión se mantuvo de una sesión a la otra.");
    expect(t("cambio_mayor").enUnaFrase).toBe("Te enroscaste más que en tu sesión anterior.");
    expect(t("pocos_golpes").enUnaFrase).toBe("Tu torsión cambió de una sesión a la otra, pero hay pocos golpes para saber si es más de lo que variás normalmente.");
    expect(t("lados_distintos").enUnaFrase).toBe("Tu torsión se mantuvo de una sesión a la otra.");
  });
});

describe("Evolución: Qué vimos", () => {
  test("los datos van acá, con su ⓘ", () => {
    const x = t("cambio_mayor");
    expect(x.vimos.medido[0].texto).toContain("aumentó 14°: de 33° a 47°");
    expect(x.vimos.medido[0].texto).toContain("Es lo que cambió, no un juicio sobre tu técnica.");
    expect(x.vimos.medido[0].ayuda).toBe("variacion_tipica");
    expect(x.vimos.medido.some((m) => m.ayuda === "sesiones_comparadas")).toBe(true);
  });
  test("con una sola sesión, un texto simple dice qué hace falta para comparar", () => {
    const x = t("una_sesion");
    expect(x.pocasSesiones).toContain("hacen falta al menos dos sesiones tuyas del mismo golpe y encuadre");
    expect(x.vimos.medido[0].texto).toContain("Tu punto de partida");
    expect(t("dos_sesiones").pocasSesiones).toBeNull();
  });
  test("sin 4 golpes por sesión no se dice la variación", () => {
    expect(juntar("pocos_golpes")).toContain("Con menos de 4 golpes medidos por sesión no se puede decir");
    expect(juntar("pocos_golpes")).not.toContain("±");
  });
  test("lados distintos: aviso, y la comparación sigue siendo solo del mismo golpe y encuadre", () => {
    expect(t("lados_distintos").avisos.join(" ")).toContain("lados distintos del jugador");
    expect(t("dos_sesiones").avisos.join(" ")).not.toContain("lados distintos");
    expect(t("dos_sesiones").cabecera).toContain("del mismo golpe y encuadre, grabadas desde el mismo lugar");
  });
  test("orden que se repite: «solo cuenta si se repite», sin decir cuál conviene", () => {
    const x = t("orden_repetido").vimos.medido.find((m) => m.ayuda === "orden_repeticion")!;
    expect(x.texto).toContain("el mismo en 5 de 5 golpes en que se pudo ver");
    expect(x.texto).toContain("Solo cuenta si se repite.");
  });
});

describe("Evolución: palabras prohibidas y jerga", () => {
  for (const c of CASOS_EVOLUCION) {
    test(`caso ${c.n}`, () => {
      const todo = juntar(c.id);
      expect(PROHIBIDAS.filter((r) => r.test(todo)).map(String)).toEqual([]);
      expect(JERGA.filter((r) => r.test(todo)).map(String)).toEqual([]);
      expect(todo).not.toMatch(/\bsu sesión\b/i);
    });
  }
});
