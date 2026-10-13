// Se corre con `bun test` desde frontend/. Vive fuera de src/ (no entra en el build ni en el tsconfig).
import { describe, expect, test } from "bun:test";
import {
  ETAPAS,
  MAX_INTENTOS,
  contarGolpes,
  contarObservaciones,
  golpeMedido,
  ordenDistinguible,
  observacionesDe,
  reporteDeVersionAnterior,
  versionAnteriorA,
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

describe("golpes medidos (Biblioteca, decisión 037)", () => {
  // Un reporte con una repetición cuyos picos de cadera y tronco están en los instantes dados (confianza 0,9).
  const reporte = (t_pelvis: number | null, t_torso: number | null, extra: Record<string, unknown> = {}) => ({
    trazabilidad: { tolerancia_orden_ms: 8.333 },
    secuenciacion: {
      repeticiones: [
        {
          auditable: false,
          picos: [
            ...(t_pelvis !== null ? [{ segmento: "pelvis", instante_s: t_pelvis, confianza: 0.9 }] : []),
            ...(t_torso !== null ? [{ segmento: "torso", instante_s: t_torso, confianza: 0.9 }] : []),
          ],
        },
      ],
    },
    ...extra,
  });
  const golpe = (r: unknown, estado: "completado" | "parcial" = "completado") => ({ estado, reportes_biomecanicos: { reporte: r } });

  test("un golpe con cadera y tronco empatados está MEDIDO, y su orden no es distinguible", () => {
    const r = reporte(0.296, 0.3); // 4 ms: dentro de 8,33 ms
    expect(golpeMedido(r)).toBe(true);
    expect(ordenDistinguible(r)).toBe(false);
  });

  test("con más de la tolerancia el orden es distinguible", () => {
    const r = reporte(0.3, 0.4);
    expect(golpeMedido(r)).toBe(true);
    expect(ordenDistinguible(r)).toBe(true);
  });

  test("sin pico de cadera o de tronco, o con baja confianza, no está medido", () => {
    expect(golpeMedido(reporte(0.3, null))).toBe(false);
    expect(golpeMedido(reporte(null, 0.3))).toBe(false);
    const baja = reporte(0.3, 0.4);
    (baja.secuenciacion.repeticiones[0].picos[1] as { confianza: number }).confianza = 0.3;
    expect(golpeMedido(baja)).toBe(false);
    expect(ordenDistinguible(baja)).toBe(false);
  });

  test("cuenta medidos, con orden distinguible, no medibles y en análisis, sin tocar el veredicto", () => {
    const c = contarGolpes([
      golpe(reporte(0.3, 0.4)),
      golpe(reporte(0.296, 0.3)),
      golpe(reporte(0.3, null), "parcial"),
      { estado: "fallido" as const },
      { estado: "procesando" as const },
      { estado: "encolado" as const },
    ]);
    expect(c).toEqual({ medidos: 2, no_medibles: 2, en_analisis: 2, con_orden: 1 });
  });

  test("un reporte con un veredicto viejo cuenta como medido y no como 'correcto'", () => {
    const r = { ...reporte(0.3, 0.4), observaciones: [{ severidad: "desvio_leve" }] };
    expect(contarGolpes([golpe(r)])).toEqual({ medidos: 1, no_medibles: 0, en_analisis: 0, con_orden: 1 });
  });

  test("sin videos, todo en cero", () => {
    expect(contarGolpes([])).toEqual({ medidos: 0, no_medibles: 0, en_analisis: 0, con_orden: 0 });
  });

  test("un reporte anterior marcaba 'no auditable' el empate: se lee como 'sin diferencia medible'", () => {
    const viejo = {
      trazabilidad: { version_motor: "0.5.3" },
      observaciones: [
        { severidad: "no_auditable", texto: "La cadera y el tronco alcanzaron su velocidad máxima casi al mismo tiempo: a esta resolución del video no se puede saber cuál fue primero." },
        { severidad: "no_auditable", texto: "No se pudo medir el instante en que el brazo alcanzó su velocidad máxima en este golpe." },
      ],
    };
    const o = observacionesDe(viejo);
    expect(o[0].severidad).toBe("sin_diferencia_medible");
    expect(o[0].texto).toContain("no hay diferencia medible");
    expect(o[1].severidad).toBe("no_auditable");     // lo del brazo sí es un dato que no se pudo medir
  });
});

describe("reportes de un motor anterior a 0.5.2 (sin veredicto)", () => {
  test("compara versiones", () => {
    expect(versionAnteriorA("0.4.1")).toBe(true);
    expect(versionAnteriorA("0.5.0")).toBe(true);
    expect(versionAnteriorA("0.5.1")).toBe(true);
    expect(versionAnteriorA("0.5.2")).toBe(false);
    expect(versionAnteriorA("0.5.10")).toBe(false);
    expect(versionAnteriorA("0.6.0")).toBe(false);
    expect(versionAnteriorA("1.0.0")).toBe(false);
  });

  test("una versión ilegible o ausente cuenta como anterior", () => {
    expect(versionAnteriorA(null)).toBe(true);
    expect(versionAnteriorA("")).toBe(true);
    expect(versionAnteriorA("dev")).toBe(true);
  });

  const viejo = {
    trazabilidad: { version_motor: "0.5.0" },
    observaciones: [
      { severidad: "desvio_leve", texto: "es distinto del orden esperado para este golpe", fundamento: "instantes", referencia: "Kovacs (2011)" },
      { severidad: "correcto", texto: "es el orden esperado" },
      { severidad: "sin_evaluar", texto: "El brazo alcanzó su velocidad máxima" },
      { severidad: "no_auditable", texto: "No se pudo medir" },
    ],
  };

  test("en un reporte viejo el veredicto pasa a 'Solo registrado', con la nota y sin la cita", () => {
    const o = observacionesDe(viejo);
    expect(o.map((x) => x.severidad)).toEqual(["sin_evaluar", "sin_evaluar", "sin_evaluar", "no_auditable"]);
    expect(o[0].anterior).toBe(true);
    expect(o[0].referencia).toBeNull();
    expect(o[0].texto).not.toMatch(/esperado|correcto|desv/i);
    expect(o[2].anterior).toBeUndefined();         // lo que ya era "sin evaluar" no se toca
    expect(o[3].texto).toBe("No se pudo medir");  // ni lo "no auditable"
  });

  test("en un reporte actual no se toca nada", () => {
    const actual = { ...viejo, trazabilidad: { version_motor: "0.5.3" } };
    expect(observacionesDe(actual)).toEqual(viejo.observaciones);
    expect(reporteDeVersionAnterior(actual)).toBe(false);
    expect(reporteDeVersionAnterior(viejo)).toBe(true);
    expect(reporteDeVersionAnterior(null)).toBe(false);
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
