import { API_URL } from "@/lib/supabase";
import { urlConsistencia, type Consistencia } from "@/lib/consistencia";

/** `null` si no se pudo calcular ahora (sin servidor, sesión vencida, etc.): la pantalla sigue sin esa parte. */
export async function leerConsistencia(sesionId: string, accessToken: string): Promise<Consistencia | null> {
  const url = urlConsistencia(API_URL, sesionId);
  if (!url) return null;
  try {
    const r = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!r.ok) return null;
    return (await r.json()) as Consistencia;
  } catch {
    return null;
  }
}
