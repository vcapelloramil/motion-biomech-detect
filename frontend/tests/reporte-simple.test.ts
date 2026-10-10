// Se corre con `bun test` desde frontend/. Vive fuera de src/ (no entra en el build ni en el tsconfig).
import { describe, expect, test } from "bun:test";
import {
  MAX_OBSERVACIONES,
  coberturaDe,
  fraseDeSecuencia,
  masImportantes,
  picosOrdenados,
  repeticionesDe,
  trazabilidadDe,
  tramosNoAuditablesDe,
  type RepeticionLeida,
} from "../src/lib/reporte-simple";

const obs = (severidad: string, texto = severidad) => ({ severidad, texto });

describe("lo más importante", () => {
  test("a lo sumo tres, por importancia, y el resto queda aparte", () => {
    const { visibles, ocultas } = masImportantes([
      obs("sin_evaluar"),
      obs("correcto"),
      obs("no_auditable"),
      obs("desvio_leve"),
      obs("alerta_de_carga"),
    ]);
    expect(MAX_OBSERVACIONES).toBe(3);
    expect(visibles.map((o) => o.severidad)).toEqual(["alerta_de_carga", "desvio_leve", "correcto"]);
    expect(ocultas.map((o) => o.severidad)).toEqual(["no_auditable", "sin_evaluar"]);
  });

  test("es estable: dentro de una severidad conserva el orden del motor", () => {
    const { visibles } = masImportantes([obs("correcto", "primera"), obs("correcto", "segunda")]);
    expect(visibles.map((o) => o.texto)).toEqual(["primera", "segunda"]);
  });

  test("una severidad desconocida va al final y no se descarta", () => {
    const { visibles } = masImportantes([obs("rara"), obs("correcto")]);
    expect(visibles.map((o) => o.severidad)).toEqual(["correcto", "rara"]);
  });

  test("sin observaciones, listas vacías", () => {
    expect(masImportantes([])).toEqual({ visibles: [], ocultas: [] });
  });
});

const rep = (p: Partial<RepeticionLeida>): RepeticionLeida => ({
  indice: 1, auditable: true, orden_observado: ["pelvis", "torso", "brazo"], correcto: null, motivo_no_auditable: null, picos: [], ...p,
});

describe("frase de la secuencia", () => {
  test("con orden establecido describe lo observado, sin prometer nada", () => {
    const f = fraseDeSecuencia(rep({}), 199.6);
    expect(f.tipo).toBe("orden");
    expect(f.texto).toContain("tu cadera, después tu tronco y por último tu brazo");
    expect(f.texto.startsWith("Se observa")).toBe(true);
  });

  test("simultaneidad: dice a cuántos fps no se puede saber y que no se evalúa", () => {
    const f = fraseDeSecuencia(
      rep({ auditable: false, orden_observado: null, motivo_no_auditable: "simultaneidad al límite de resolución: la cadera y el tronco quedaron a un fotograma o menos" }),
      199.63,
    );
    expect(f.tipo).toBe("simultaneo");
    expect(f.texto).toContain("A 200 fps no se puede saber cuál fue primero");
    expect(f.texto).toContain("no lo evaluamos");
  });

  test("sin repetición o sin dato: 'no se pudo medir', nunca un orden inventado", () => {
    expect(fraseDeSecuencia(null, null).tipo).toBe("sin_dato");
    const f = fraseDeSecuencia(rep({ auditable: false, orden_observado: null, motivo_no_auditable: "sin pico auditable para: torso" }), 200);
    expect(f.tipo).toBe("sin_dato");
    expect(f.texto).toContain("No se pudo medir");
  });

  test("ningún texto usa el vocabulario que R2 prohíbe", () => {
    const todo = JSON.stringify([
      fraseDeSecuencia(rep({}), 200),
      fraseDeSecuencia(rep({ auditable: false, orden_observado: null, motivo_no_auditable: "simultaneidad" }), 200),
      fraseDeSecuencia(null, null),
    ]).toLowerCase();
    for (const prohibido of ["predec", "diagnóstic", "prevenir", "lesión", "riesgo", "bandera roja"]) {
      expect(todo.includes(prohibido)).toBe(false);
    }
  });
});

describe("lectura del JSON", () => {
  const reporte = {
    cobertura: { auditable_pct: 38.86, tramos_no_auditables: [{ desde_s: 0, hasta_s: 1.52, motivo: "sin_datos_confiables: codo_der" }] },
    trazabilidad: {
      fps_real: 199.63, fps_nominal: 239.98, fotogramas_perdidos_pct: 16.81, escala_temporal_conocida: true,
      version_motor: "0.4.1", backend_pose: "mediapipe", modo_captura: "camara_lenta_240",
      regularizacion: { puntos_interpolados_pct: 16.42 },
    },
    secuenciacion: {
      repeticiones: [
        {
          indice: 1, auditable: false, orden_observado: null, correcto: null, motivo_no_auditable: "simultaneidad",
          picos: [
            { segmento: "brazo", instante_s: 0.354, velocidad: 722, confianza: 0.86, unidad: "grados/s" },
            { segmento: "pelvis", instante_s: 0.304, velocidad: 771, confianza: 1, unidad: "grados/s" },
            { segmento: "torso", instante_s: 0.3, velocidad: 520, confianza: 1, unidad: "grados/s" },
          ],
        },
      ],
    },
  };

  test("trazabilidad, cobertura y tramos", () => {
    const t = trazabilidadDe(reporte);
    expect(t).toMatchObject({ fps_real: 199.63, escala_conocida: true, puntos_interpolados_pct: 16.42, version_motor: "0.4.1" });
    expect(trazabilidadDe({ trazabilidad: { regularizacion: { fps_grilla: 240, puntos_interpolados_pct: 1 } } }).fps_grilla).toBe(240);
    expect(trazabilidadDe({ trazabilidad: {} }).fps_grilla).toBeNull();
    expect(coberturaDe(reporte)).toBe(38.86);
    expect(tramosNoAuditablesDe(reporte)).toHaveLength(1);
  });

  test("los picos salen en el orden de las filas del gráfico, no en el que llegaron", () => {
    const r = repeticionesDe(reporte)[0];
    expect(picosOrdenados(r).map((p) => p.segmento)).toEqual(["pelvis", "torso", "brazo"]);
  });

  test("un reporte vacío o sin sección no rompe", () => {
    expect(repeticionesDe(null)).toEqual([]);
    expect(trazabilidadDe(null).escala_conocida).toBe(false);
    expect(trazabilidadDe(null).puntos_interpolados_pct).toBeNull();
    expect(coberturaDe({})).toBeNull();
    expect(tramosNoAuditablesDe({})).toEqual([]);
    expect(picosOrdenados(null)).toEqual([]);
  });
});
