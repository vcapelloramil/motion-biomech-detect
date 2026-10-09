// Se corre con `bun test` desde frontend/. Vive fuera de src/ para que no entre en el build ni en el tsconfig.
import { describe, expect, test } from "bun:test";
import {
  contrasenaValida,
  esRol,
  mensajeDeIngreso,
  mensajeDeRegistro,
  ROLES,
} from "../src/lib/auth-errores";

describe("ingreso", () => {
  test("sin confirmar el correo NO es un error genérico (especificación §3)", () => {
    const m = mensajeDeIngreso({ code: "email_not_confirmed", message: "Email not confirmed", status: 400 });
    expect(m.tipo).toBe("correo-sin-confirmar");
    expect(m.texto).toContain("Confirmá tu correo para entrar");
    expect(m.texto.toLowerCase()).toContain("spam");
  });

  test("también se reconoce por el texto, sin código", () => {
    expect(mensajeDeIngreso({ message: "Email not confirmed" }).tipo).toBe("correo-sin-confirmar");
  });

  test("credenciales incorrectas no distingue entre correo y contraseña", () => {
    const m = mensajeDeIngreso({ code: "invalid_credentials", message: "Invalid login credentials", status: 400 });
    expect(m.tipo).toBe("credenciales");
    expect(m.texto).toBe("El correo o la contraseña no coinciden.");
  });

  test("demasiados intentos y falla de red", () => {
    expect(mensajeDeIngreso({ code: "over_request_rate_limit", status: 429 }).tipo).toBe("espera");
    expect(mensajeDeIngreso({ message: "Failed to fetch" }).tipo).toBe("red");
  });

  test("un error desconocido no filtra el texto técnico", () => {
    const m = mensajeDeIngreso({ code: "algo_raro", message: "AuthRetryableFetchError: ECONNRESET 10.0.0.3" });
    expect(m.texto).not.toContain("ECONNRESET");
    expect(m.texto).not.toContain("10.0.0.3");
  });

  test("sin error, mensaje neutro", () => {
    expect(mensajeDeIngreso(null).tipo).toBe("otro");
  });
});

describe("registro", () => {
  test("contraseña débil, correo repetido, correo inválido", () => {
    expect(mensajeDeRegistro({ code: "weak_password" }).texto).toContain("débil");
    expect(mensajeDeRegistro({ code: "user_already_exists" }).texto).toContain("Ya hay una cuenta");
    expect(mensajeDeRegistro({ code: "email_address_invalid" }).texto).toContain("correo");
  });

  test("límite de envíos de correo", () => {
    expect(mensajeDeRegistro({ code: "over_email_send_rate_limit" }).tipo).toBe("espera");
  });
});

describe("contraseña y rol", () => {
  test("exige 8 caracteres con letras y números", () => {
    expect(contrasenaValida("abc12")).toBe(false);
    expect(contrasenaValida("sololetras")).toBe(false);
    expect(contrasenaValida("12345678")).toBe(false);
    expect(contrasenaValida("tenis2026ok")).toBe(true);
  });

  test("los roles son exactamente los de usuarios.rol en la base", () => {
    // supabase/migrations/20261001090000_esquema_inicial.sql: check (rol in ('jugador','entrenador','profesional_salud'))
    expect(ROLES.map((r) => r.valor)).toEqual(["jugador", "entrenador", "profesional_salud"]);
    expect(esRol("jugador")).toBe(true);
    expect(esRol("admin")).toBe(false);
  });
});
