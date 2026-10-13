// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import {
  avisosDeEvolucion,
  etiquetaDeFecha,
  tarjetasDeEvolucion,
  type ResumenDeSesion,
  type SerieDeEvolucion,
} from "../src/lib/evolucion";
import { urlEvolucion } from "../src/lib/evolucion-api";

const sesion = (id: string, fecha: string, mediana: number | null, extra: Partial<ResumenDeSesion> = {}): ResumenDeSesion => ({
  sesion_id: id,
  fecha,
  lado_camara: "derecha",
  golpes: { total: 6, medidos: 6, no_medibles: 0, en_analisis: 0, con_orden_distinguible: 4 },
  separacion_cadera_hombro: { n: mediana === null ? 0 : 6, mediana, dispersion: mediana === null ? null : 2.6, minimo: null, maximo: null },
  orden: { medidos: 6, ordenables: 5, mismo_orden: 4, suficiente: true },
  versiones_motor: ["0.5.3"],
  golpes_que_se_apartan: 0,
  ...extra,
});

const serie = (sesiones: ResumenDeSesion[], resto: Partial<SerieDeEvolucion> = {}): SerieDeEvolucion => ({
  atleta_id: "a1",
  gesto: "saque",
  encuadre: "tres_cuartos",
  version_regla: "1",
  sesiones,
  variacion_habitual: 2.6,
  centro_habitual: null,
  cambio_separacion: null,
  lados_de_camara: ["derecha"],
  versiones_motor: ["0.5.3"],
  mezcla_de_versiones: false,
  ...resto,
});

const texto = (s: SerieDeEvolucion) => tarjetasDeEvolucion(s).map((t) => `${t.titulo} ${t.valor ?? ""} ${t.texto}`).join(" | ");

describe("tarjetas de evolución", () => {
  test("una sola sesión: punto de partida, sin cambio inventado", () => {
    const t = tarjetasDeEvolucion(serie([sesion("s1", "2026-09-24", 30.4)]));
    expect(t.map((x) => x.clave)).toEqual(["separacion", "orden", "golpes", "sesiones"]);
    expect(t[0].valor).toBe("30°");
    expect(t[0].direccion).toBeNull();
    expect(t[0].texto).toContain("punto de partida");
    expect(t[3].valor).toBe("1");
  });

  test("dos sesiones dentro de la variación habitual: se mantuvo", () => {
    const s = serie([sesion("s1", "2026-09-24", 30.4), sesion("s2", "2026-09-25", 31.2)], {
      cambio_separacion: { anterior: 30.4, actual: 31.2, delta: 0.8, dentro_de_lo_habitual: true },
    });
    const t = tarjetasDeEvolucion(s)[0];
    expect(t.direccion).toBe("igual");
    expect(t.texto).toContain("Se mantuvo");
    expect(t.texto).toContain("±3°");
  });

  test("un cambio mayor: aumentó o disminuyó, sin decir si es bueno", () => {
    const sube = serie([sesion("s1", "2026-09-24", 25), sesion("s2", "2026-09-30", 31)], {
      cambio_separacion: { anterior: 25, actual: 31, delta: 6, dentro_de_lo_habitual: false },
    });
    const t = tarjetasDeEvolucion(sube)[0];
    expect(t.direccion).toBe("sube");
    expect(t.texto).toContain("Aumentó 6°");
    expect(t.texto).toContain("No es mejor ni peor");
    const baja = serie([sesion("s1", "2026-09-24", 31), sesion("s2", "2026-09-30", 25)], {
      cambio_separacion: { anterior: 31, actual: 25, delta: -6, dentro_de_lo_habitual: false },
    });
    expect(tarjetasDeEvolucion(baja)[0].texto).toContain("Disminuyó 6°");
    expect(tarjetasDeEvolucion(baja)[0].direccion).toBe("baja");
  });

  test("sin variación habitual (menos de 4 golpes) no afirma que sea más que lo habitual", () => {
    const s = serie([sesion("s1", "2026-09-24", 25), sesion("s2", "2026-09-30", 31)], {
      variacion_habitual: null,
      cambio_separacion: { anterior: 25, actual: 31, delta: 6, dentro_de_lo_habitual: null },
    });
    const t = tarjetasDeEvolucion(s)[0];
    expect(t.texto).toContain("no se puede decir si es más que tu variación habitual");
  });

  test("ninguna tarjeta usa vocabulario de juicio", () => {
    const s = serie([sesion("s1", "2026-09-24", 25), sesion("s2", "2026-09-30", 31)], {
      cambio_separacion: { anterior: 25, actual: 31, delta: 6, dentro_de_lo_habitual: false },
    });
    // "No es mejor ni peor" es el descargo; se saca antes de buscar juicios
    expect(texto(s).replace("No es mejor ni peor: es lo que cambió.", "").replace("no cuál es el correcto", "")).not.toMatch(
      /mejor|peor|mejoró|empeoró|correct|desv|alerta/i,
    );
  });

  test("el orden necesita al menos 5 ordenables; si no, dice cuántos y por qué", () => {
    const poco = serie([sesion("s1", "2026-09-24", 30, { orden: { medidos: 6, ordenables: 3, mismo_orden: 3, suficiente: false } })]);
    const t = tarjetasDeEvolucion(poco)[1];
    expect(t.valor).toBeNull();
    expect(t.texto).toContain("con menos de 5");
    const ninguno = serie([sesion("s1", "2026-09-24", 30, { orden: { medidos: 6, ordenables: 0, mismo_orden: 0, suficiente: false } })]);
    expect(tarjetasDeEvolucion(ninguno)[1].texto).toContain("casi al mismo tiempo");
  });

  test("el orden con suficientes muestra k de m y el anterior", () => {
    const s = serie([sesion("s1", "2026-09-24", 30), sesion("s2", "2026-09-25", 31, { orden: { medidos: 6, ordenables: 6, mismo_orden: 5, suficiente: true } })]);
    const t = tarjetasDeEvolucion(s)[1];
    expect(t.valor).toBe("5 de 6");
    expect(t.texto).toContain("Antes: 4 de 5");
  });

  test("una sesión sin dato no inventa la separación", () => {
    const t = tarjetasDeEvolucion(serie([sesion("s1", "2026-09-24", null)]))[0];
    expect(t.valor).toBeNull();
    expect(t.texto).toContain("Todavía no hay una sesión con la separación medida");
  });

  test("sin sesiones, todo dice por qué falta", () => {
    const t = tarjetasDeEvolucion(serie([]));
    expect(t[1].valor).toBeNull();
    expect(t[2].valor).toBeNull();
    expect(t[3].valor).toBe("0");
  });
});

describe("avisos y utilidades", () => {
  test("avisa un lado de cámara distinto y la mezcla de versiones", () => {
    const a = avisosDeEvolucion(serie([sesion("s1", "2026-09-24", 30)], { lados_de_camara: ["derecha", "izquierda"], mezcla_de_versiones: true }));
    expect(a).toHaveLength(2);
    expect(a[0]).toContain("lados distintos");
    expect(a[1]).toContain("versión anterior del motor");
  });

  test("sin nada dudoso no avisa", () => {
    expect(avisosDeEvolucion(serie([sesion("s1", "2026-09-24", 30)]))).toEqual([]);
  });

  test("la fecha sin hora no se corre por la zona horaria", () => {
    expect(etiquetaDeFecha("2026-09-24")).toBe("24 sep");
    expect(etiquetaDeFecha("2026-01-01")).toBe("1 ene");
  });

  test("la dirección de la API", () => {
    expect(urlEvolucion("https://api.example.com/", "a1", "saque", "tres_cuartos")).toBe(
      "https://api.example.com/evolucion?atleta_id=a1&gesto=saque&encuadre=tres_cuartos",
    );
    expect(urlEvolucion("", "a1", "saque", "perfil")).toBeNull();
  });
});
