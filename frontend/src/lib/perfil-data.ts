import { API_URL, getSupabase } from "@/lib/supabase";
import {
  urlCuenta,
  CONFIRMACION_ELIMINAR,
  armarExportacion,
  resumirActividad,
  type ActividadDelUsuario,
  type DatosJugador,
} from "@/lib/perfil";

/** Lecturas y escrituras del Perfil: directo a Supabase con la sesión del usuario (RLS) y, para eliminar la cuenta, la API. */

function cliente() {
  const c = getSupabase();
  if (!c) throw new Error("sin-configuracion");
  return c;
}

export type PerfilLeido = { id: string; email: string; nombre: string; rol: string; creado_en: string };
export type JugadorLeido = { id: string; nombre: string; mano_dominante: string; nivel: string };

export async function leerPerfil(): Promise<PerfilLeido | null> {
  const { data, error } = await cliente().from("usuarios").select("id, email, nombre, rol, creado_en").maybeSingle();
  if (error) throw error;
  return (data as PerfilLeido | null) ?? null;
}

export async function leerJugadores(): Promise<JugadorLeido[]> {
  const { data, error } = await cliente()
    .from("atletas")
    .select("id, nombre, mano_dominante, nivel")
    .order("creado_en", { ascending: true });
  if (error) throw error;
  return (data ?? []) as JugadorLeido[];
}

/** Cuántas sesiones y golpes tiene el usuario y cuántos se midieron (la RLS limita a lo propio). */
export async function leerActividad(): Promise<ActividadDelUsuario> {
  const { data, error } = await cliente()
    .from("sesiones")
    .select("id, videos(id, estado, reportes_biomecanicos(reporte))");
  if (error) throw error;
  return resumirActividad((data ?? []) as never);
}

/** Guarda nombre y rol. El nombre también va a los metadatos de la sesión, que es de donde lo lee la cabecera. */
export async function guardarPerfil(id: string, nombre: string, rol: string): Promise<void> {
  const c = cliente();
  const { error } = await c.from("usuarios").update({ nombre: nombre.trim(), rol }).eq("id", id);
  if (error) throw error;
  await c.auth.updateUser({ data: { nombre: nombre.trim() } });
}

export async function guardarJugador(id: string, datos: DatosJugador): Promise<void> {
  const { error } = await cliente()
    .from("atletas")
    .update({ nombre: datos.nombre.trim(), mano_dominante: datos.mano_dominante, nivel: datos.nivel })
    .eq("id", id);
  if (error) throw error;
}

/** Todo lo del usuario (la RLS limita a lo propio) listo para descargar como JSON. */
export async function leerMisDatos() {
  const c = cliente();
  const [u, a, s] = await Promise.all([
    c.from("usuarios").select("*").maybeSingle(),
    c.from("atletas").select("*").order("creado_en", { ascending: true }),
    c
      .from("sesiones")
      .select("*, videos(id, estado, fps_real, duracion_s, resolucion, creado_en, ruta_almacenamiento, reportes_biomecanicos(reporte))")
      .order("fecha", { ascending: true }),
  ]);
  if (u.error) throw u.error;
  if (a.error) throw a.error;
  if (s.error) throw s.error;
  return armarExportacion(
    {
      usuario: (u.data as Record<string, unknown> | null) ?? null,
      atletas: (a.data ?? []) as Record<string, unknown>[],
      sesiones: (s.data ?? []) as never,
    },
    new Date().toISOString(),
  );
}

export type ResultadoEliminar = { ok: true; archivos: number } | { ok: false; texto: string };

/** `DELETE /cuenta`: borra los archivos y la cuenta con todos sus datos. Si falla, la cuenta queda como estaba. */
export async function eliminarMiCuenta(accessToken: string): Promise<ResultadoEliminar> {
  const url = urlCuenta(API_URL);
  if (!url) return { ok: false, texto: "Falta configurar la dirección del servidor (VITE_API_URL)." };
  try {
    const r = await fetch(url, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({ confirmacion: CONFIRMACION_ELIMINAR }),
    });
    if (r.ok) {
      const d = (await r.json().catch(() => ({}))) as { archivos_eliminados?: number };
      return { ok: true, archivos: d.archivos_eliminados ?? 0 };
    }
    if (r.status === 401) return { ok: false, texto: "Tu sesión venció. Ingresá de nuevo y volvé a intentar." };
    return {
      ok: false,
      texto: "No pudimos eliminar la cuenta ahora. No se borró nada: tu cuenta sigue como estaba. Probá de nuevo en un momento.",
    };
  } catch {
    return { ok: false, texto: "No pudimos conectarnos con el servidor. No se borró nada: probá de nuevo." };
  }
}
