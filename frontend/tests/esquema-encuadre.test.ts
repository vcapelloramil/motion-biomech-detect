// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import { esLadoDeLaMano, geometriaEsquema, geometriaRaqueta, ladoRecomendado } from "../src/lib/esquema-encuadre";

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

/** ¿El segmento (a→b) cruza el rectángulo? Muestreo fino: alcanza para un dibujo de 160 × 120. */
function segmentoCruzaRect(a: { x: number; y: number }, b: { x: number; y: number }, r: { x0: number; y0: number; x1: number; y1: number }) {
  for (let i = 0; i <= 400; i++) {
    const t = i / 400;
    const x = a.x + (b.x - a.x) * t;
    const y = a.y + (b.y - a.y) * t;
    if (x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1) return true;
  }
  return false;
}

describe("rótulo «CÁMARA» del esquema", () => {
  const ANCHO_TEXTO = 6 * 5.2; // 6 letras, fuente mono de 8 px (≈ 0,6 em por letra) con holgura
  const ALTO_TEXTO = 8;
  test("no pisa la línea punteada cámara-jugador, en ningún encuadre ni lado", () => {
    for (const enc of ["perfil", "tres_cuartos"] as const) {
      for (const lado of ["izquierda", "derecha"] as const) {
        const g = geometriaEsquema(enc, lado);
        const e = g.etiquetaCamara;
        const x0 = e.ancla === "middle" ? e.x - ANCHO_TEXTO / 2 : e.ancla === "start" ? e.x : e.x - ANCHO_TEXTO;
        const caja = { x0, x1: x0 + ANCHO_TEXTO, y0: e.y - ALTO_TEXTO, y1: e.y + 2 };
        expect(segmentoCruzaRect(g.camara, g.jugador, caja)).toBe(false);
        // y queda dentro del dibujo
        expect(caja.x0).toBeGreaterThanOrEqual(0);
        expect(caja.x1).toBeLessThanOrEqual(160);
        expect(caja.y1).toBeLessThanOrEqual(120);
      }
    }
  });
});

describe("raqueta en la mano dominante", () => {
  test("derecha: a la derecha del jugador; izquierda: espejada", () => {
    const d = geometriaRaqueta("derecha");
    const i = geometriaRaqueta("izquierda");
    const j = geometriaEsquema("perfil", "izquierda").jugador;
    expect(d.mango.x1).toBeGreaterThan(j.x);
    expect(d.cabeza.cx).toBeGreaterThan(j.x);
    expect(i.cabeza.cx).toBeCloseTo(160 - d.cabeza.cx, 9);
    expect(i.cabeza.cy).toBeCloseTo(d.cabeza.cy, 9);
    expect(i.cabeza.rotacion).toBeCloseTo(-d.cabeza.rotacion, 9);
  });
  test("la cabeza queda sobre la prolongación del mango", () => {
    const g = geometriaRaqueta("derecha");
    const dx = g.mango.x2 - g.mango.x1;
    const dy = g.mango.y2 - g.mango.y1;
    const ex = g.cabeza.cx - g.mango.x2;
    const ey = g.cabeza.cy - g.mango.y2;
    expect(dx * ey - dy * ex).toBeCloseTo(0, 9); // paralelos
    expect(dx * ex + dy * ey).toBeGreaterThan(0); // misma dirección
  });
  test("no toca la cámara ni su línea en el encuadre recomendado (cámara del otro lado)", () => {
    for (const enc of ["perfil", "tres_cuartos"] as const) {
      const g = geometriaEsquema(enc, "izquierda");
      const r = geometriaRaqueta("derecha", g.jugador);
      const caja = { x0: r.cabeza.cx - 8, x1: r.cabeza.cx + 8, y0: r.cabeza.cy - 8, y1: r.cabeza.cy + 8 };
      expect(segmentoCruzaRect(g.camara, g.jugador, caja)).toBe(false);
    }
  });
});
