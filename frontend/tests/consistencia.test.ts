// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import {
  fraseGolpeQueSeAparta,
  tarjetasDeConsistencia,
  urlConsistencia,
  type Consistencia,
} from "../src/lib/consistencia";
import { tiemposDe } from "../src/lib/estado-video";

const base: Consistencia = {
  sesion_id: "s1",
  gesto: "saque",
  encuadre: "tres_cuartos",
  fecha: "2026-09-24",
  version_regla: "1",
  golpes: { total: 6, medidos: 6, no_medibles: 0, en_analisis: 0, con_orden_distinguible: 5 },
  separacion_cadera_hombro: { n: 6, unidad: "grados", mediana: 30.4, dispersion: 2.6, minimo: 26.1, maximo: 34.9, valores: [] },
  orden: { medidos: 6, ordenables: 5, mismo_orden: 4, orden_modal: ["pelvis", "torso"], suficiente: true },
  golpe_tipico: "v1",
  golpes_que_se_apartan: [],
  versiones_motor: ["0.5.3"],
  mezcla_de_versiones: false,
  minimos: { dispersion: 4, repetibilidad: 5, se_apartan: 5 },
};

const texto = (c: Consistencia) => tarjetasDeConsistencia(c).map((t) => `${t.titulo} ${t.valor ?? ""} ${t.texto}`).join(" | ");

describe("tarjetas de consistencia", () => {
  test("siempre las tres, con coma decimal y sin juicio", () => {
    const t = tarjetasDeConsistencia(base);
    expect(t.map((x) => x.clave)).toEqual(["separacion", "orden", "golpes"]);
    expect(t[0].valor).toBe("30° ± 3°");
    expect(t[1].valor).toBe("4 de 5");
    expect(t[2].valor).toBe("6 de 6");
    // la única mención de "correcto" es el descargo ("no cuál es el correcto"): se descarta antes de buscar juicios
    expect(texto(base).replace("no cuál es el correcto", "")).not.toMatch(/correct|desv|mejor|peor|alerta|esperado/i);
  });

  test("con pocos golpes dice por qué no se puede decir cuánto varía", () => {
    const c = { ...base, separacion_cadera_hombro: { ...base.separacion_cadera_hombro, n: 3, dispersion: null } };
    const t = tarjetasDeConsistencia(c)[0];
    expect(t.valor).toBe("30°");
    expect(t.texto).toContain("Con menos de 4 golpes");
  });

  test("sin ordenables no inventa un porcentaje", () => {
    const c = { ...base, orden: { ...base.orden, ordenables: 0, mismo_orden: 0, orden_modal: null, suficiente: false } };
    const t = tarjetasDeConsistencia(c)[1];
    expect(t.valor).toBeNull();
    expect(t.texto).toContain("casi al mismo tiempo");
  });

  test("con ordenables insuficientes dice cuántos hacen falta", () => {
    const c = { ...base, orden: { ...base.orden, ordenables: 3, mismo_orden: 3, suficiente: false } };
    const t = tarjetasDeConsistencia(c)[1];
    expect(t.valor).toBeNull();
    expect(t.texto).toContain("con menos de 5");
  });

  test("el conteo de golpes nombra los no medibles y los que siguen en análisis", () => {
    const c = { ...base, golpes: { total: 6, medidos: 3, no_medibles: 1, en_analisis: 2, con_orden_distinguible: 1 } };
    expect(tarjetasDeConsistencia(c)[2].texto).toBe(
      "Se midieron 3 de 6 golpes; 1 no se pudo medir y 2 siguen en análisis. En 1 se distingue cuál llegó primero, la cadera o el tronco.",
    );
  });

  test("un empate no es un golpe perdido: se mide y se dice que no se distingue el orden", () => {
    const c = { ...base, golpes: { total: 6, medidos: 6, no_medibles: 0, en_analisis: 0, con_orden_distinguible: 0 } };
    const t = tarjetasDeConsistencia(c)[2];
    expect(t.valor).toBe("6 de 6");
    expect(t.texto).toContain("En ninguno se distingue");
    expect(t.texto).not.toMatch(/no se pudo medir/i);
  });

  test("sin separación medida lo dice", () => {
    const c = { ...base, separacion_cadera_hombro: { ...base.separacion_cadera_hombro, n: 0, mediana: null, dispersion: null } };
    expect(tarjetasDeConsistencia(c)[0].valor).toBeNull();
  });

  test("el golpe que se aparta no se llama 'malo'", () => {
    expect(fraseGolpeQueSeAparta(4)).toBe("El golpe 4 se pareció menos a los demás. Puede ser tu golpe o la medición: miralo en el video.");
  });
});

describe("dirección de la API", () => {
  test("une la base y la sesión sin barras dobles", () => {
    expect(urlConsistencia("https://api.example.com/", "abc")).toBe("https://api.example.com/sesiones/abc/consistencia");
    expect(urlConsistencia("", "abc")).toBeNull();
    expect(urlConsistencia(undefined, "abc")).toBeNull();
  });
});

describe("tiempos: la espera en la cola no es procesamiento (Criterio 4)", () => {
  test("los separa", () => {
    const t = tiemposDe({
      encolado_en: "2026-10-13T10:00:00Z",
      inicio_procesamiento_en: "2026-10-13T10:08:00Z",
      fin_procesamiento_en: "2026-10-13T10:10:30Z",
    });
    expect(t.espera_cola_s).toBe(480);
    expect(t.procesamiento_s).toBe(150);
    expect(t.total_s).toBe(630);
  });

  test("lo que no se puede calcular es null, no cero", () => {
    const t = tiemposDe({ encolado_en: null, inicio_procesamiento_en: "2026-10-13T10:08:00Z", fin_procesamiento_en: null });
    expect(t).toEqual({ espera_cola_s: null, procesamiento_s: null, total_s: null });
  });
});
