/**
 * De un error de Supabase Auth a un mensaje en lenguaje llano (R2: sin jerga ni códigos).
 *
 * Función pura, sin dependencias: se prueba con `bun test` (frontend/tests/auth-errores.test.ts).
 *
 * Regla de la especificación §3: sin confirmar el correo, el ingreso responde "Confirmá tu correo para
 * entrar", no un error genérico.
 */

export type ErrorAuth = { code?: string | null; message?: string | null; status?: number | null } | null | undefined;

export type Mensaje = { texto: string; tipo: "correo-sin-confirmar" | "credenciales" | "espera" | "red" | "otro" };

export function mensajeDeIngreso(error: ErrorAuth): Mensaje {
  const code = (error?.code ?? "").toLowerCase();
  const message = (error?.message ?? "").toLowerCase();

  if (code === "email_not_confirmed" || message.includes("email not confirmed")) {
    return { tipo: "correo-sin-confirmar", texto: "Confirmá tu correo para entrar. Te enviamos un enlace: revisá también la carpeta de spam o correo no deseado." };
  }
  if (code === "invalid_credentials" || message.includes("invalid login credentials")) {
    return { tipo: "credenciales", texto: "El correo o la contraseña no coinciden." };
  }
  return mensajeGeneral(code, message, error?.status ?? null);
}

export function mensajeDeRegistro(error: ErrorAuth): Mensaje {
  const code = (error?.code ?? "").toLowerCase();
  const message = (error?.message ?? "").toLowerCase();

  if (code === "weak_password" || message.includes("password should be")) {
    return { tipo: "otro", texto: "La contraseña es demasiado débil. Usá al menos 8 caracteres, con letras y números." };
  }
  if (code === "user_already_exists" || message.includes("already registered")) {
    return { tipo: "otro", texto: "Ya hay una cuenta con ese correo. Probá ingresar." };
  }
  if (code === "email_address_invalid" || message.includes("invalid email")) {
    return { tipo: "otro", texto: "Ese correo no parece válido. Revisalo." };
  }
  return mensajeGeneral(code, message, error?.status ?? null);
}

function mensajeGeneral(code: string, message: string, status: number | null): Mensaje {
  if (code.includes("rate_limit") || message.includes("rate limit") || status === 429) {
    return { tipo: "espera", texto: "Hubo demasiados intentos. Esperá unos minutos y volvé a probar." };
  }
  if (message.includes("failed to fetch") || message.includes("network") || status === 0) {
    return { tipo: "red", texto: "No pudimos conectarnos. Revisá tu conexión y volvé a probar." };
  }
  return { tipo: "otro", texto: "No pudimos completar la operación. Probá de nuevo en un momento." };
}

/** Contraseña mínima del formulario (Supabase acepta menos; acá se pide más). */
export const LARGO_MINIMO_CONTRASENA = 8;

export function contrasenaValida(contrasena: string): boolean {
  return contrasena.length >= LARGO_MINIMO_CONTRASENA && /[A-Za-z]/.test(contrasena) && /\d/.test(contrasena);
}

export const ROLES = [
  { valor: "jugador", etiqueta: "Jugador" },
  { valor: "entrenador", etiqueta: "Entrenador" },
  { valor: "profesional_salud", etiqueta: "Profesional de la salud" },
] as const;

export type Rol = (typeof ROLES)[number]["valor"];

export function esRol(valor: string): valor is Rol {
  return ROLES.some((r) => r.valor === valor);
}
