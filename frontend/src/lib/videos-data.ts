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
  atletas: { nombre: string; mano_dominante?: string | null } | null;
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
    .select("*, sesiones(id, gesto, encuadre, lado_camara, modo_captura, fecha, creado_en, atletas(nombre, mano_dominante)), reportes_biomecanicos(reporte)")
    .eq("id", videoId)
    .maybeSingle();
  if (error) throw error;
  return (data as VideoConReporte | null) ?? null;
}

/** Una sesión con sus golpes (en el orden en que se cargaron) y sus reportes. `null` si no existe o no es del usuario (la RLS lo oculta). */
export async function leerSesion(sesionId: string): Promise<SesionConVideos | null> {
  const { data, error } = await cliente()
    .from("sesiones")
    .select(
      "id, gesto, encuadre, lado_camara, modo_captura, fecha, creado_en, atletas(nombre, mano_dominante), videos(*, reportes_biomecanicos(reporte))",
    )
    .eq("id", sesionId)
    .order("creado_en", { referencedTable: "videos", ascending: true })
    .maybeSingle();
  if (error) throw error;
  return (data as unknown as SesionConVideos | null) ?? null;
}

export type GolpeDeSesion = { id: string; estado: FilaVideo["estado"] };

/** Los golpes de una sesión en orden de carga: para "golpe 2 de 6" en Procesando. */
export async function golpesDeSesion(sesionId: string): Promise<GolpeDeSesion[]> {
  const { data, error } = await cliente()
    .from("videos")
    .select("id, estado")
    .eq("sesion_id", sesionId)
    .order("creado_en", { ascending: true });
  if (error) throw error;
  return (data ?? []) as GolpeDeSesion[];
}

export async function listarSesiones(): Promise<SesionConVideos[]> {
  const { data, error } = await cliente()
    .from("sesiones")
    .select(
      "id, gesto, encuadre, lado_camara, modo_captura, fecha, creado_en, atletas(nombre, mano_dominante), videos(*, reportes_biomecanicos(reporte))",
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

/**
 * URLs firmadas de vida corta (1 h) de los artefactos del reporte (fotogramas clave y video con esqueleto). El reporte guarda
 * RUTAS, no URLs (decisión 025): una URL vence y el reporte no. El bucket es privado y la política deja leer solo la carpeta propia.
 * Si no se pueden firmar, el mapa viene vacío y la pantalla no muestra imágenes (nunca una imagen de relleno).
 */
export async function urlsDeArtefactos(rutas: readonly string[]): Promise<Record<string, string>> {
  const unicas = [...new Set(rutas.filter((r) => r.length > 0))];
  if (unicas.length === 0) return {};
  const { data, error } = await cliente().storage.from("artefactos").createSignedUrls(unicas, 3600);
  if (error || !data) return {};
  const salida: Record<string, string> = {};
  for (const d of data) {
    if (d.path && d.signedUrl && !d.error) salida[d.path] = d.signedUrl;
  }
  return salida;
}

// --- eliminar --------------------------------------------------------------------------------------------------------------------
// El derecho de supresión (Ley 25.326) cubre los archivos, no solo las filas: el video original y los artefactos (fotogramas y video con
// esqueleto) están en dos buckets privados y las políticas dejan borrar solo la carpeta propia. Mejor esfuerzo con los archivos: un
// resto huérfano no rompe nada, y que la fila quede viva por un error de Storage sí sería un borrado a medias.

type FilaConReporte = { ruta_almacenamiento?: string; reportes_biomecanicos?: unknown };

function rutasDeArtefactos(v: FilaConReporte): string[] {
  const r = v.reportes_biomecanicos;
  const fila = Array.isArray(r) ? r[0] : r;
  const rep = (fila as { reporte?: { artefactos?: { overlay_ruta?: unknown; fotogramas_clave?: { ruta?: unknown }[] } } } | null)?.reporte;
  const a = rep?.artefactos;
  const rutas: unknown[] = [a?.overlay_ruta, ...(Array.isArray(a?.fotogramas_clave) ? a.fotogramas_clave.map((f) => f?.ruta) : [])];
  return rutas.filter((x): x is string => typeof x === "string" && x.length > 0);
}

async function borrarArchivos(videos: FilaConReporte[]) {
  const c = cliente();
  const originales = videos.map((v) => v.ruta_almacenamiento).filter((x): x is string => !!x);
  const artefactos = videos.flatMap(rutasDeArtefactos);
  try {
    if (originales.length > 0) await c.storage.from("videos").remove(originales);
    if (artefactos.length > 0) await c.storage.from("artefactos").remove(artefactos);
  } catch {
    /* mejor esfuerzo: ver el comentario de arriba */
  }
}

/** Elimina un golpe: sus archivos y su fila (el reporte se va en cascada). Si era el último de la sesión, elimina también la sesión vacía. */
export async function eliminarGolpe(video: FilaConReporte & { id: string; sesion_id: string }): Promise<{ sesionEliminada: boolean }> {
  await borrarArchivos([video]);
  const c = cliente();
  const { error } = await c.from("videos").delete().eq("id", video.id);
  if (error) throw error;
  const { count } = await c.from("videos").select("id", { count: "exact", head: true }).eq("sesion_id", video.sesion_id);
  if ((count ?? 1) === 0) {
    await c.from("sesiones").delete().eq("id", video.sesion_id);
    return { sesionEliminada: true };
  }
  return { sesionEliminada: false };
}

/** Elimina una sesión con todos sus golpes y sus archivos. */
export async function eliminarSesion(sesion: { id: string; videos: FilaConReporte[] }): Promise<void> {
  await borrarArchivos(sesion.videos);
  const { error } = await cliente().from("sesiones").delete().eq("id", sesion.id);
  if (error) throw error;
}

// --- Evolución -------------------------------------------------------------------------------------------------------------------------

export type GrupoDeEvolucion = {
  atleta_id: string;
  atleta: string;
  gesto: string;
  encuadre: string;
  sesiones: number;
};

/** Los jugadores × golpe × encuadre con al menos una sesión, para elegir qué comparar. Liviano: sin videos ni reportes. */
export async function gruposDeEvolucion(): Promise<GrupoDeEvolucion[]> {
  const { data, error } = await cliente().from("sesiones").select("atleta_id, gesto, encuadre, atletas(nombre)");
  if (error) throw error;
  const mapa = new Map<string, GrupoDeEvolucion>();
  for (const s of (data ?? []) as unknown as { atleta_id: string; gesto: string; encuadre: string; atletas: { nombre: string } | null }[]) {
    const clave = `${s.atleta_id}|${s.gesto}|${s.encuadre}`;
    const previo = mapa.get(clave);
    if (previo) previo.sesiones += 1;
    else mapa.set(clave, { atleta_id: s.atleta_id, atleta: s.atletas?.nombre ?? "Jugador", gesto: s.gesto, encuadre: s.encuadre, sesiones: 1 });
  }
  return [...mapa.values()].sort((a, b) => b.sesiones - a.sesiones);
}
