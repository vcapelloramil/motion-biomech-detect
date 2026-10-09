// Se corre con `bun test` desde frontend/. Vive fuera de src/ (no entra en el build ni en el tsconfig).
import { describe, expect, test } from "bun:test";
import {
  GESTOS,
  LIMITE_BYTES,
  MODOS_CAPTURA,
  esValor,
  interpretarRespuestaApi,
  nombreSeguro,
  problemaDelArchivo,
  rutaDelVideo,
  tipoDeContenido,
  urlProcesar,
} from "../src/lib/carga";

describe("archivo", () => {
  test("acepta mp4 y mov, y deduce el tipo cuando el navegador lo deja vacío", () => {
    expect(problemaDelArchivo({ name: "IMG_6391.MOV", size: 8_000_000, type: "video/quicktime" })).toBeNull();
    expect(problemaDelArchivo({ name: "golpe.mp4", size: 1000, type: "video/mp4" })).toBeNull();
    expect(problemaDelArchivo({ name: "IMG_1.MOV", size: 1000, type: "" })).toBeNull();
    expect(tipoDeContenido("IMG_1.MOV", "")).toBe("video/quicktime");
  });

  test("rechaza otros formatos y archivos vacíos", () => {
    expect(problemaDelArchivo({ name: "clip.avi", size: 1000, type: "video/x-msvideo" })?.tipo).toBe("formato");
    expect(problemaDelArchivo({ name: "foto.jpg", size: 1000, type: "image/jpeg" })?.tipo).toBe("formato");
    expect(problemaDelArchivo({ name: "a.mp4", size: 0, type: "video/mp4" })?.tipo).toBe("vacio");
  });

  test("el límite es 50 MB, igual que el bucket", () => {
    expect(LIMITE_BYTES).toBe(50 * 1024 * 1024);
    expect(problemaDelArchivo({ name: "a.mp4", size: LIMITE_BYTES, type: "video/mp4" })).toBeNull();
    const p = problemaDelArchivo({ name: "a.mp4", size: LIMITE_BYTES + 1, type: "video/mp4" });
    expect(p?.tipo).toBe("tamano");
    expect(p?.texto).toContain("50 MB");
  });
});

describe("clave segura de Storage", () => {
  test("solo letras ASCII, números, guion, guion bajo y punto", () => {
    const hostil = ["Saque ñandú – prueba (1)~final.MOV", "../../etc/passwd.mp4", "🎾 tenis.mp4", "a/b\\c.mov", "   .mov"];
    for (const n of hostil) {
      expect(nombreSeguro(n)).toMatch(/^[A-Za-z0-9_-]+\.(mov|mp4)$/);
    }
  });

  test("las tildes pasan a su letra base y el nombre vacío queda como 'video'", () => {
    expect(nombreSeguro("Revés año.mp4")).toBe("Reves-ano.mp4");
    expect(nombreSeguro("~~~.mov")).toBe("video.mov");
  });

  test("un nombre muy largo se acota", () => {
    expect(nombreSeguro("a".repeat(500) + ".mp4").length).toBeLessThanOrEqual(64);
  });

  test("la ruta empieza por la carpeta del usuario (lo que exige la política de Storage)", () => {
    const r = rutaDelVideo("11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222", "Mi golpe.MOV");
    expect(r).toBe("11111111-1111-4111-8111-111111111111/22222222-2222-4222-8222-222222222222/Mi-golpe.mov");
  });
});

describe("vocabulario", () => {
  test("coincide con los CHECK de la base", () => {
    // sesiones: gesto in ('saque','drive','reves'); modo_captura in ('normal','camara_lenta_120','camara_lenta_240')
    expect(GESTOS.map((g) => g.valor)).toEqual(["saque", "drive", "reves"]);
    expect(MODOS_CAPTURA.map((m) => m.valor).sort()).toEqual(["camara_lenta_120", "camara_lenta_240", "normal"]);
    expect(esValor(GESTOS, "saque")).toBe(true);
    expect(esValor(GESTOS, "volea")).toBe(false);
  });

  test("ningún texto usa el vocabulario que R2 prohíbe", () => {
    const todo = JSON.stringify([GESTOS, MODOS_CAPTURA]).toLowerCase();
    for (const prohibido of ["predec", "diagnóstic", "prevenir", "lesión", "riesgo"]) {
      expect(todo.includes(prohibido)).toBe(false);
    }
  });
});

describe("respuesta de la API", () => {
  test("202 es éxito", () => {
    expect(interpretarRespuestaApi(202, { video_id: "x", estado: "encolado" })).toEqual({ ok: true });
  });

  test("409 estado_no_reintentable cuenta como éxito: ya estaba en cola o analizado", () => {
    const r = interpretarRespuestaApi(409, { detail: { codigo: "estado_no_reintentable", estado_actual: "encolado" } });
    expect(r.ok).toBe(true);
  });

  test("401 pide renovar la sesión y no es reintentable", () => {
    const r = interpretarRespuestaApi(401, { detail: "Token de sesión inválido." });
    expect(r).toMatchObject({ ok: false, renovarSesion: true, reintentable: false });
  });

  test("404, 409 distinto y errores del servidor", () => {
    expect(interpretarRespuestaApi(404, {})).toMatchObject({ ok: false, reintentable: false });
    expect(interpretarRespuestaApi(409, { detail: { codigo: "declaracion_sin_cambios" } })).toMatchObject({ ok: false, reintentable: false });
    expect(interpretarRespuestaApi(503, {})).toMatchObject({ ok: false, reintentable: true });
    expect(interpretarRespuestaApi(500, null)).toMatchObject({ ok: false, reintentable: true });
  });

  test("los mensajes no filtran detalles técnicos", () => {
    const r = interpretarRespuestaApi(500, { detail: "Traceback (most recent call last): File app/x.py" });
    expect(r.ok === false && r.texto.includes("Traceback")).toBe(false);
  });

  test("la URL de la API se arma sin barras dobles y exige estar configurada", () => {
    expect(urlProcesar("https://kinetiq-motor.onrender.com/", "abc")).toBe("https://kinetiq-motor.onrender.com/analisis/abc/procesar");
    expect(urlProcesar("", "abc")).toBeNull();
    expect(urlProcesar(undefined, "abc")).toBeNull();
  });
});
