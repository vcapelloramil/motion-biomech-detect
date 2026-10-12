// Se corre con `bun test` desde frontend/. Vive fuera de src/ (no entra en el build ni en el tsconfig).
import { describe, expect, test } from "bun:test";
import {
  MAX_OBSERVACIONES,
  artefactosDe,
  coberturaDe,
  fraseDeSecuencia,
  fundamentosSinRepetir,
  magnitudesDe,
  masImportantes,
  picosOrdenados,
  repeticionesDe,
  resolucionTexto,
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

  test("simultaneidad: dice la resolución REAL del archivo, la tolerancia y que no se evalúa", () => {
    const f = fraseDeSecuencia(
      rep({ auditable: false, orden_observado: null, motivo_no_auditable: "simultaneidad al límite de resolución: la cadera y el tronco quedaron a un fotograma o menos" }),
      199.9,
      8.333,
    );
    expect(f.tipo).toBe("simultaneo");
    expect(f.texto).toContain("a menos de 8,3 ms uno del otro");
    expect(f.texto).toContain("A esta resolución (1 fotograma ≈ 5 ms a 200 fps reales) no se puede saber cuál fue primero");
    expect(f.texto).toContain("no lo evaluamos");
  });

  test("sin tolerancia en el reporte (versión anterior) la frase sigue siendo verdadera", () => {
    const f = fraseDeSecuencia(rep({ auditable: false, orden_observado: null, motivo_no_auditable: "simultaneidad" }), 199.9);
    expect(f.texto).not.toContain("a menos de");
    expect(f.texto).toContain("no se puede saber cuál fue primero");
  });

  test("la resolución se expresa con la tasa real y sin decimales de más", () => {
    expect(resolucionTexto(199.9)).toBe("1 fotograma ≈ 5 ms a 200 fps reales");
    expect(resolucionTexto(120)).toBe("1 fotograma ≈ 8,3 ms a 120 fps reales");
    expect(resolucionTexto(null)).toBeNull();
    expect(resolucionTexto(0)).toBeNull();
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


describe("artefactos y fundamentos", () => {
  const reporte = {
    artefactos: {
      overlay_ruta: "u/v/esqueleto.mp4",
      overlay_info: { desde_s: 1.4, hasta_s: 3.0, fps_reproduccion: 30, factor_lento: 8 },
      fotogramas_clave: [
        { segmento: "brazo", instante_s: 0.496, ruta: "u/v/clave_brazo.jpg" },
        { segmento: "pelvis", instante_s: 0.317, ruta: "u/v/clave_pelvis.jpg" },
        { segmento: "torso", instante_s: 0.3, ruta: "" },
      ],
    },
  };

  test("los fotogramas salen en el orden cadera, tronco, brazo y sin rutas vacías", () => {
    const a = artefactosDe(reporte);
    expect(a.fotogramas.map((f) => f.segmento)).toEqual(["pelvis", "brazo"]);
    expect(a.overlay).toEqual({ ruta: "u/v/esqueleto.mp4", desde_s: 1.4, hasta_s: 3.0, factor_lento: 8 });
  });

  test("sin artefactos es 'no generado': nada que mostrar, nada inventado", () => {
    expect(artefactosDe({ artefactos: {} })).toEqual({ fotogramas: [], overlay: null });
    expect(artefactosDe(null)).toEqual({ fotogramas: [], overlay: null });
  });

  test("la línea de instantes no se repite entre observaciones", () => {
    const linea = "Instantes de la velocidad máxima: tronco 0,300 s.";
    const r = fundamentosSinRepetir([
      { severidad: "sin_evaluar", texto: "a", fundamento: linea, referencia: null },
      { severidad: "sin_evaluar", texto: "b", fundamento: linea, referencia: null },
      { severidad: "correcto", texto: "c", fundamento: "otra", referencia: "Fuente (2011)" },
    ]);
    expect(r.map((x) => x.fundamento)).toEqual([linea, null, "otra"]);
    expect(r[2].referencia).toBe("Fuente (2011)");
  });
});

describe("brazo sin medir (12/10)", () => {
  test("con cadera y tronco ordenables se informa lo medido y se dice qué no se pudo medir", () => {
    const f = fraseDeSecuencia(rep({ orden_observado: ["pelvis", "torso"] }), 200.8);
    expect(f.tipo).toBe("orden");
    expect(f.texto).toContain("primero alcanzó su velocidad máxima tu cadera y después tu tronco");
    expect(f.texto).toContain("El brazo no se pudo medir");
  });

  test("el inicio de la ventana y la reconstrucción por interpolación llegan a la trazabilidad", () => {
    const t = trazabilidadDe({
      trazabilidad: { regularizacion: { puntos_interpolados: 156, puntos_de_la_grilla: 959, hueco_maximo_ms: 12.5, puntos_interpolados_pct: 16.3 } },
    });
    expect(t).toMatchObject({ puntos_interpolados: 156, puntos_de_la_grilla: 959, hueco_maximo_ms: 12.5 });
    expect(trazabilidadDe(null).hueco_maximo_ms).toBeNull();
  });
});

describe("magnitudes articulares", () => {
  const reporte = {
    metricas: [
      { nombre: "velocidad_pico_torso", valor: 450, unidad: "grados/s", confianza: 1, auditable: true },
      { nombre: "separacion_cadera_hombro_max", valor: 41.5, unidad: "grados", confianza: 0.93, auditable: true },
      { nombre: "angulo_rodilla_izq_en_pico_tronco", valor: 142.3, unidad: "grados", confianza: 0.88, auditable: true },
      { nombre: "angulo_codo_der_en_pico_tronco", valor: null, unidad: "grados", confianza: 0.41, auditable: false },
    ],
  };

  test("solo las magnitudes articulares, con su etiqueta y el error medido contra goniometría", () => {
    const m = magnitudesDe(reporte);
    expect(m.map((x) => x.nombre)).toEqual([
      "separacion_cadera_hombro_max",
      "angulo_rodilla_izq_en_pico_tronco",
      "angulo_codo_der_en_pico_tronco",
    ]);
    expect(m[0].etiqueta).toBe("Separación cadera-hombro máxima");
    expect(m[1].etiqueta).toBe("Ángulo de la rodilla izquierda en el pico del tronco");
    expect(m[1].nota).toContain("8,5° de media y hasta 19,2°");
    expect(m[2].etiqueta).toBe("Ángulo del codo derecho en el pico del tronco");
    expect(m[2].auditable).toBe(false);
    expect(m[2].nota).toContain("No se informa");
  });

  test("sin métricas no rompe", () => {
    expect(magnitudesDe(null)).toEqual([]);
    expect(magnitudesDe({ metricas: "x" })).toEqual([]);
  });
});
