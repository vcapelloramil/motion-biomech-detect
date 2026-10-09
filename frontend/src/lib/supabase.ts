import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Cliente de Supabase del navegador (decisión 025: carga, estado y lectura van directo, con RLS).
 *
 * Solo valores PÚBLICOS: la URL del proyecto y la clave "anon". La clave service_role no existe acá ni
 * debe existir nunca (ver frontend/.env.example).
 *
 * El cliente se crea una sola vez y solo en el navegador: en el servidor (SSR de TanStack Start sobre
 * Cloudflare) no hay sesión que leer, y crearlo allí compartiría estado entre usuarios.
 */

const URL = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const CLAVE_ANON = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

/** ¿Están cargadas las variables públicas? La pantalla de ingreso lo avisa en vez de fallar en silencio. */
export const supabaseConfigurado = Boolean(URL && CLAVE_ANON);

let cliente: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  if (typeof window === "undefined" || !supabaseConfigurado) return null;
  if (!cliente) {
    cliente = createClient(URL as string, CLAVE_ANON as string, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        // El enlace del correo de confirmación vuelve con la sesión en la URL.
        detectSessionInUrl: true,
      },
    });
  }
  return cliente;
}
