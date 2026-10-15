// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import {
  CONFIRMACION_ELIMINAR,
  armarExportacion,
  confirmacionValida,
  nombreArchivoExportacion,
  problemaDelJugador,
  problemaDelNombre,
  problemaDelPerfil,
  resumirActividad,
  urlCuenta,
} from "../src/lib/perfil";

describe("eliminar la cuenta", () => {
  test("solo la palabra exacta confirma (la misma que exige el servidor)", () => {
    expect(CONFIRMACION_ELIMINAR).toBe("ELIMINAR");
    expect(confirmacionValida("ELIMINAR")).toBe(true);
    expect(confirmacionValida("  ELIMINAR ")).toBe(true);
    expect(confirmacionValida("eliminar")).toBe(false);
    expect(confirmacionValida("")).toBe(false);
    expect(confirmacionValida("ELIMINAR TODO")).toBe(false);
  });

  test("la dirección de la API", () => {
    expect(urlCuenta("https://api.example.com/")).toBe("https://api.example.com/cuenta");
    expect(urlCuenta("")).toBeNull();
    expect(urlCuenta(undefined)).toBeNull();
  });
});

describe("validación del perfil", () => {
  test("nombre", () => {
    expect(problemaDelNombre("Valentín")).toBeNull();
    expect(problemaDelNombre("   ")).toBe("Escribí un nombre.");
    expect(problemaDelNombre("x".repeat(81))).toContain("hasta 80");
  });

  test("perfil: nombre y rol conocido", () => {
    expect(problemaDelPerfil("Valentín", "jugador")).toBeNull();
    expect(problemaDelPerfil("Valentín", "profesional_salud")).toBeNull();
    expect(problemaDelPerfil("Valentín", "admin")).not.toBeNull();
    expect(problemaDelPerfil("", "jugador")).not.toBeNull();
  });

  test("jugador: mano y nivel del vocabulario cerrado", () => {
    expect(problemaDelJugador({ nombre: "VCR", mano_dominante: "derecha", nivel: "intermedio" })).toBeNull();
    expect(problemaDelJugador({ nombre: "VCR", mano_dominante: "ambidiestro", nivel: "intermedio" })).toBe("Elegí la mano dominante.");
    expect(problemaDelJugador({ nombre: "VCR", mano_dominante: "derecha", nivel: "pro" })).toBe("Elegí el nivel.");
  });
});

describe("descargar mis datos", () => {
  const entrada = {
    usuario: { id: "u1", email: "v@x.com", nombre: "Valentín", rol: "jugador", creado_en: "2026-09-01T00:00:00Z", vista_por_defecto: "simple" },
    atletas: [{ id: "a1", nombre: "VCR", mano_dominante: "derecha", nivel: "avanzado", edad: null, creado_en: "2026-09-01" }],
    sesiones: [
      {
        id: "s1",
        gesto: "saque",
        encuadre: "tres_cuartos",
        fecha: "2026-09-24",
        videos: [
          { id: "v1", estado: "completado", reportes_biomecanicos: [{ reporte: { version_contrato: "1.4" } }] },
          { id: "v2", estado: "fallido", reportes_biomecanicos: null },
        ],
      },
    ],
  };

  test("arma la cuenta, los jugadores y las sesiones con el reporte de cada golpe", () => {
    const d = armarExportacion(entrada, "2026-10-14T03:00:00.000Z");
    expect(d.formato).toBe("kinetiq-mis-datos/1");
    expect(d.cuenta).toEqual({ id: "u1", correo: "v@x.com", nombre: "Valentín", rol: "jugador", creado_en: "2026-09-01T00:00:00Z" });
    expect(d.jugadores[0].nombre).toBe("VCR");
    expect(d.sesiones[0].golpes).toHaveLength(2);
    expect((d.sesiones[0].golpes[0].reporte as { version_contrato: string }).version_contrato).toBe("1.4");
    expect(d.sesiones[0].golpes[1].reporte).toBeNull();
    expect("videos" in d.sesiones[0]).toBe(false);
  });

  test("dice qué no incluye y no lleva claves ni tokens", () => {
    const d = armarExportacion(entrada, "2026-10-14T03:00:00.000Z");
    expect(d.nota).toContain("No incluye los archivos de video");
    expect(JSON.stringify(d)).not.toMatch(/token|password|contrasena|secret/i);
  });

  test("sin datos no rompe", () => {
    const d = armarExportacion({ usuario: null, atletas: [], sesiones: [] }, "2026-10-14T03:00:00.000Z");
    expect(d.cuenta.id).toBeNull();
    expect(d.sesiones).toEqual([]);
  });

  test("nombre del archivo con la fecha", () => {
    expect(nombreArchivoExportacion("2026-10-14T03:00:00.000Z")).toBe("kinetiq-mis-datos-2026-10-14.json");
  });
});

describe("actividad del usuario (Perfil)", () => {
  test("sin sesiones, todo en cero", () => {
    expect(resumirActividad([])).toEqual({ sesiones: 0, golpes: 0, medidos: 0, no_medibles: 0, en_analisis: 0 });
  });

  test("cuenta sesiones, golpes cargados, medidos, no medibles y en análisis", () => {
    const medido = {
      reporte: {
        secuenciacion: {
          repeticiones: [
            { picos: [{ segmento: "pelvis", instante_s: 1, confianza: 0.9 }, { segmento: "torso", instante_s: 1.02, confianza: 0.9 }] },
          ],
        },
      },
    };
    const r = resumirActividad([
      { videos: [{ estado: "completado", reportes_biomecanicos: medido }, { estado: "fallido" }, { estado: "encolado" }] },
      { videos: [] },
      { videos: null },
    ]);
    expect(r.sesiones).toBe(3);
    expect(r.golpes).toBe(3);
    expect(r.medidos).toBe(1);
    expect(r.no_medibles).toBe(1);
    expect(r.en_analisis).toBe(1);
  });
});
