import { getSupabase } from "@/lib/supabase";
import { pedirAnalisis } from "@/lib/cargar-video";
import type { ModoCaptura } from "@/lib/carga";
import type { FilaVideo } from "@/lib/estado-video";

/**
 * Lecturas de la Biblioteca y de Procesando (decisión 025): directo a Supabase con la sesión del usuario; la RLS
 * garantiza que cada quien ve solo lo suyo. Se pide `*` de `videos` a propósito: las columnas de tiempos llegan con
 * la migración 20261010000000 y la pantalla tiene que funcionar antes y después de aplicarla.
 */

export type SesionLeida = {
  id: string;
  gesto: string;
  encuadre: string;
  lado_camara: string;
  modo_captura: ModoCaptura;
  fecha: string;
  creado_en: string;
  atletas: { nombre: string } | null;
};

export type VideoConReporte = FilaVideo & {
  sesiones: SesionLeida | null;
  reportes_biomecanicos: unknown;
};

export type SesionConVideos = SesionLeida & { videos: (FilaVideo & { reportes_biomecanicos: unknown })[] };

function cliente() {
  const c = getSupabase();
  if (!c) throw new Error("sin-configuracion");
  return c;
}

export async function leerVideo(videoId: string): Promise<VideoConReporte | null> {
  const { data, error } = await cliente()
    .from("videos")
    .select("*, sesiones(id, gesto, encuadre, lado_camara, modo_captura, fecha, creado_en, atletas(nombre)), reportes_biomecanicos(reporte)")
    .eq("id", videoId)
    .maybeSingle();
  if (error) throw error;
  return (data as VideoConReporte | null) ?? null;
}

export async function listarSesiones(): Promise<SesionConVideos[]> {
  const { data, error } = await cliente()
    .from("sesiones")
    .select(
      "id, gesto, encuadre, lado_camara, modo_captura, fecha, creado_en, atletas(nombre), videos(*, reportes_biomecanicos(reporte))",
    )
    .order("creado_en", { ascending: false });
  if (error) throw error;
  return (data ?? []) as unknown as SesionConVideos[];
}

/** Corrige "¿Cómo lo grabaste?" de la sesión. Lo rechaza la base si ya hay golpes analizados con otra configuración (decisión 022). */
export async function corregirModo(sesionId: string, modo: ModoCaptura): Promise<{ ok: true } | { ok: false; texto: string }> {
  const { error } = await cliente().from("sesiones").update({ modo_captura: modo }).eq("id", sesionId);
  if (!error) return { ok: true };
  return {
    ok: false,
    texto:
      "Esta sesión ya tiene golpes analizados con otra configuración, así que no se puede cambiar. " +
      "Para este video, creá una sesión nueva.",
  };
}

export async function reintentar(videoId: string) {
  const token = (await cliente().auth.getSession()).data.session?.access_token;
  if (!token) return { ok: false as const, reintentable: false, texto: "Tu sesión venció. Ingresá de nuevo.", renovarSesion: true };
  return pedirAnalisis(videoId, token);
}
