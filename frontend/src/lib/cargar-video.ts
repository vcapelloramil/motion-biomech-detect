import { API_URL, SUPABASE_CLAVE_ANON, SUPABASE_URL_PUBLICA, getSupabase } from "@/lib/supabase";
import {
  interpretarRespuestaApi,
  urlProcesar,
  type Encuadre,
  type Gesto,
  type LadoCamara,
  type Mano,
  type ModoCaptura,
  type Nivel,
  type ResultadoApi,
} from "@/lib/carga";

/**
 * Operaciones de la pantalla Cargar (decisión 025): todo va directo a Supabase con la sesión del usuario
 * (RLS + permisos por columna). La API solo recibe la orden de analizar.
 */

export type Atleta = { id: string; nombre: string; mano_dominante: Mano; nivel: Nivel };

function cliente() {
  const c = getSupabase();
  if (!c) throw new Error("sin-configuracion");
  return c;
}

export async function listarAtletas(): Promise<Atleta[]> {
  const { data, error } = await cliente()
    .from("atletas")
    .select("id, nombre, mano_dominante, nivel")
    .order("creado_en", { ascending: true });
  if (error) throw error;
  return (data ?? []) as Atleta[];
}

export async function crearAtleta(
  usuarioId: string,
  datos: { nombre: string; mano_dominante: Mano; nivel: Nivel },
): Promise<Atleta> {
  const { data, error } = await cliente()
    .from("atletas")
    .insert({ usuario_id: usuarioId, ...datos })
    .select("id, nombre, mano_dominante, nivel")
    .single();
  if (error) throw error;
  return data as Atleta;
}

export async function crearSesion(
  usuarioId: string,
  datos: { atleta_id: string; gesto: Gesto; encuadre: Encuadre; lado_camara: LadoCamara; modo_captura: ModoCaptura; fecha: string },
): Promise<string> {
  const { data, error } = await cliente()
    .from("sesiones")
    .insert({ usuario_id: usuarioId, ...datos })
    .select("id")
    .single();
  if (error) throw error;
  return (data as { id: string }).id;
}

/** El alta del video: solo las cuatro columnas que el usuario puede escribir (decisión 022). */
export async function crearVideo(datos: { id: string; sesion_id: string; usuario_id: string; ruta_almacenamiento: string }) {
  const { error } = await cliente().from("videos").insert(datos);
  if (error) throw error;
}

/** Deshace una carga a medias: borrar la sesión se lleva sus videos en cascada. Mejor esfuerzo. */
export async function descartarCarga(sesionId: string | null, ruta: string | null) {
  const c = getSupabase();
  if (!c) return;
  try {
    if (ruta) await c.storage.from("videos").remove([ruta]);
    if (sesionId) await c.from("sesiones").delete().eq("id", sesionId);
  } catch {
    /* mejor esfuerzo: un resto huérfano no rompe nada y lo limpia el usuario al eliminar su cuenta */
  }
}

/**
 * Sube el archivo al bucket privado `videos`, en la carpeta del usuario, con progreso real.
 * Se usa XMLHttpRequest porque `fetch` no informa el avance de la subida.
 */
export function subirVideo(opciones: {
  ruta: string;
  archivo: File;
  tipo: string;
  accessToken: string;
  alProgresar: (fraccion: number) => void;
}): Promise<void> {
  const { ruta, archivo, tipo, accessToken, alProgresar } = opciones;
  return new Promise((resolver, rechazar) => {
    if (!SUPABASE_URL_PUBLICA || !SUPABASE_CLAVE_ANON) return rechazar(new Error("sin-configuracion"));
    const xhr = new XMLHttpRequest();
    const destino = ruta.split("/").map(encodeURIComponent).join("/");
    xhr.open("POST", `${SUPABASE_URL_PUBLICA}/storage/v1/object/videos/${destino}`);
    xhr.setRequestHeader("Authorization", `Bearer ${accessToken}`);
    xhr.setRequestHeader("apikey", SUPABASE_CLAVE_ANON);
    xhr.setRequestHeader("Content-Type", tipo);
    xhr.setRequestHeader("x-upsert", "false");
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) alProgresar(e.loaded / e.total);
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) return resolver();
      rechazar(Object.assign(new Error("subida-rechazada"), { estado: xhr.status }));
    };
    xhr.onerror = () => rechazar(new Error("red"));
    xhr.ontimeout = () => rechazar(new Error("red"));
    xhr.send(archivo);
  });
}

/** `POST /analisis/{id}/procesar` con el JWT de la sesión (decisión 025). */
export async function pedirAnalisis(videoId: string, accessToken: string): Promise<ResultadoApi> {
  const url = urlProcesar(API_URL, videoId);
  if (!url) {
    return { ok: false, reintentable: false, texto: "Falta configurar la dirección del servidor de análisis (VITE_API_URL)." };
  }
  try {
    const resp = await fetch(url, { method: "POST", headers: { Authorization: `Bearer ${accessToken}` } });
    let cuerpo: unknown = null;
    try {
      cuerpo = await resp.json();
    } catch {
      /* sin cuerpo JSON */
    }
    return interpretarRespuestaApi(resp.status, cuerpo);
  } catch {
    return { ok: false, reintentable: true, texto: "No pudimos conectarnos con el servidor de análisis. Tu video ya está guardado: probá enviarlo de nuevo." };
  }
}
