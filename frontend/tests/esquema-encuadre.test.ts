// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import { esLadoDeLaMano, geometriaEsquema, ladoRecomendado } from "../src/lib/esquema-encuadre";

describe("lado recomendado de la cámara", () => {
  test("es el contrario a la mano dominante", () => {
    expect(ladoRecomendado("derecha")).toBe("izquierda");
    expect(ladoRecomendado("izquierda")).toBe("derecha");
  });
  test("sin mano elegida no se recomienda ninguno", () => {
    expect(ladoRecomendado("")).toBeNull();
    expect(ladoRecomendado(null)).toBeNull();
    expect(ladoRecomendado("ambidiestro")).toBeNull();
  });
  test("elegir el lado de la mano se detecta", () => {
    expect(esLadoDeLaMano("derecha", "derecha")).toBe(true);
    expect(esLadoDeLaMano("izquierda", "derecha")).toBe(false);
    expect(esLadoDeLaMano("", "derecha")).toBe(false);
    expect(esLadoDeLaMano("derecha", "")).toBe(false);
  });
});

describe("geometría del esquema (jugador mira a la red, hacia arriba)", () => {
  test("perfil, cámara a la izquierda del jugador: al costado, a 90°, mirando al jugador", () => {
    const g = geometriaEsquema("perfil", "izquierda");
    expect(g.camara.x).toBeLessThan(g.jugador.x);
    expect(g.camara.y).toBe(g.jugador.y);
    expect(g.rotacion).toBe(-180); // el objetivo (que mira a -x) pasa a mirar a +x, hacia el jugador
  });
  test("tres cuartos, cámara a la izquierda: POR DELANTE (del lado de la red) y en diagonal de 45°", () => {
    const g = geometriaEsquema("tres_cuartos", "izquierda");
    expect(g.camara.x).toBeLessThan(g.jugador.x);
    expect(g.camara.y).toBeLessThan(g.jugador.y); // más cerca de la red que el jugador = por delante
    const dx = g.jugador.x - g.camara.x;
    const dy = g.jugador.y - g.camara.y;
    expect(Math.abs((Math.atan2(dy, dx) * 180) / Math.PI - 45)).toBeLessThan(1e-9);
    expect(g.rotacion).toBe(-135);
  });
  test("el esquema se espeja para el otro lado (zurdo)", () => {
    for (const enc of ["perfil", "tres_cuartos"] as const) {
      const i = geometriaEsquema(enc, "izquierda");
      const d = geometriaEsquema(enc, "derecha");
      expect(d.camara.x).toBe(160 - i.camara.x);
      expect(d.camara.y).toBe(i.camara.y);
      expect(d.camara.x).toBeGreaterThan(d.jugador.x);
    }
    expect(geometriaEsquema("perfil", "derecha").rotacion).toBe(0);
  });
});
