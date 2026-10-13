import { API_URL } from "@/lib/supabase";
import type { SerieDeEvolucion } from "@/lib/evolucion";

export function urlEvolucion(apiUrl: string | undefined, atletaId: string, gesto: string, encuadre: string): string | null {
  if (!apiUrl || !apiUrl.trim()) return null;
  const q = new URLSearchParams({ atleta_id: atletaId, gesto, encuadre });
  return `${apiUrl.trim().replace(/\/+$/, "")}/evolucion?${q.toString()}`;
}

/** `null` si no se pudo calcular ahora (sin servidor, sesión vencida): la pantalla lo dice y no inventa una serie. */
export async function leerEvolucion(
  atletaId: string,
  gesto: string,
  encuadre: string,
  accessToken: string,
): Promise<SerieDeEvolucion | null> {
  const url = urlEvolucion(API_URL, atletaId, gesto, encuadre);
  if (!url) return null;
  try {
    const r = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!r.ok) return null;
    return (await r.json()) as SerieDeEvolucion;
  } catch {
    return null;
  }
}
