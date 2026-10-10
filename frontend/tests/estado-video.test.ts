// Se corre con `bun test` desde frontend/. Vive fuera de src/ (no entra en el build ni en el tsconfig).
import { describe, expect, test } from "bun:test";
import {
  ETAPAS,
  MAX_INTENTOS,
  contarObservaciones,
  enCurso,
  estadoDeSesion,
  formatearDuracion,
  latenciaDe,
  observacionesDe,
  pasoActual,
  reporteDe,
  segundosEntre,
  textoDeFallo,
} from "../src/lib/estado-video";

describe("estados en curso", () => {
  test("pendiente, encolado y procesando siguen; el resto es terminal", () => {
    expect(enCurso("pendiente") && enCurso("encolado") && enCurso("procesando")).toBe(true);
    for (const e of ["completado", "parcial", "fallido"] as const) expect(enCurso(e)).toBe(false);
  });

  test("el paso avanza con el estado", () => {
    expect(["pendiente", "encolado", "procesando", "completado", "parcial"].map((e) => pasoActual(e as never))).toEqual([0, 1, 2, 3, 3]);
  });
});

describe("mensajes de fallo", () => {
  test("archivo convertido: dice el camino que funciona y la tasa medida, y no pide revisar el modo", () => {
    const t = textoDeFallo("archivo_convertido", { fps: 100.2 });
    expect(t.texto).toContain("Opciones → Formato: Actual");
    expect(t.texto).toContain("100 fps");
    expect(t.texto).toContain("app Archivos");
    expect(t.texto.toLowerCase()).not.toContain("modo de captura");
    expect(t.accion).toBe("subir_otro");
  });

  test("sin la tasa no inventa un número", () => {
    const t = textoDeFallo("archivo_convertido", { fps: null });
    expect(t.texto).not.toMatch(/\d+ fps, por debajo/);
  });

  test("modo incompatible ofrece corregir la declaración", () => {
    expect(textoDeFallo("modo_captura_incompatible").accion).toBe("corregir_modo");
  });

  test("error inesperado se reintenta con contador hasta el tope; después, subir otro", () => {
    expect(textoDeFallo("error_inesperado", { intentos: 1 })).toMatchObject({ accion: "reintentar", contador: "Intento 1 de 3" });
    expect(textoDeFallo("error_inesperado", { intentos: MAX_INTENTOS }).accion).toBe("subir_otro");
    expect(textoDeFallo(null, { intentos: 0 }).accion).toBe("reintentar"); // fallido anterior a la decisión 022
  });

  test("ningún mensaje usa el vocabulario que R2 prohíbe", () => {
    const todo = JSON.stringify([
      textoDeFallo("archivo_convertido", { fps: 100 }),
      textoDeFallo("modo_captura_incompatible"),
      textoDeFallo("error_inesperado", { intentos: 3 }),
      ETAPAS,
    ]).toLowerCase();
    for (const prohibido of ["predec", "diagnóstic", "prevenir", "lesión", "riesgo", "bandera roja", "tendinitis"]) {
      expect(todo.includes(prohibido)).toBe(false);
    }
  });
});

describe("tiempos (Criterio 4)", () => {
  test("formato legible", () => {
    expect(formatearDuracion(42)).toBe("42 s");
    expect(formatearDuracion(60)).toBe("1 min");
    expect(formatearDuracion(200)).toBe("3 min 20 s");
  });

  test("la latencia es fin menos encolado, y sin alguno de los dos no se estima", () => {
    expect(latenciaDe({ encolado_en: "2026-10-09T23:26:00Z", fin_procesamiento_en: "2026-10-09T23:35:29Z" })).toBe(569);
    expect(latenciaDe({ encolado_en: null, fin_procesamiento_en: "2026-10-09T23:35:29Z" })).toBeNull();
    expect(segundosEntre("2026-10-09T10:00:10Z", "2026-10-09T10:00:00Z")).toBeNull(); // fin antes que inicio: dato inválido
    expect(segundosEntre("basura", "2026-10-09T10:00:00Z")).toBeNull();
  });
});

describe("reporte y observaciones", () => {
  test("cuenta por severidad, incluida 'sin evaluar', e ignora las desconocidas", () => {
    const c = contarObservaciones([
      { severidad: "correcto" },
      { severidad: "sin_evaluar" },
      { severidad: "sin_evaluar" },
      { severidad: "no_auditable" },
      { severidad: "inventada" },
    ]);
    expect(c).toEqual({ correcto: 1, desvio_leve: 0, alerta_de_carga: 0, no_auditable: 1, sin_evaluar: 2 });
    expect(contarObservaciones(null).correcto).toBe(0);
  });

  test("el reporte llega como objeto o como lista", () => {
    const rep = { observaciones: [{ severidad: "correcto", texto: "x" }] };
    expect(reporteDe({ reportes_biomecanicos: { reporte: rep } })?.reporte).toEqual(rep);
    expect(reporteDe({ reportes_biomecanicos: [{ reporte: rep }] })?.reporte).toEqual(rep);
    expect(reporteDe({ reportes_biomecanicos: null })).toBeNull();
    expect(reporteDe({ reportes_biomecanicos: { reporte: null } })?.reporte).toBeNull();
    expect(observacionesDe(rep)).toHaveLength(1);
    expect(observacionesDe(null)).toEqual([]);
  });
});

describe("estado de la sesión", () => {
  test("agrega los estados de sus videos", () => {
    expect(estadoDeSesion([])).toBe("vacia");
    expect(estadoDeSesion(["completado", "procesando"])).toBe("en_curso");
    expect(estadoDeSesion(["completado", "completado"])).toBe("completada");
    expect(estadoDeSesion(["fallido", "fallido"])).toBe("fallida");
    expect(estadoDeSesion(["completado", "parcial"])).toBe("parcial");
    expect(estadoDeSesion(["completado", "fallido"])).toBe("parcial");
  });
});
