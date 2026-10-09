/**
 * Lógica pura de la pantalla Cargar (pieza 6): sin red ni DOM, para probarla con `bun test`
 * (frontend/tests/carga.test.ts).
 */

/** Mismo límite que el bucket `videos` (decisión 016): 50 MB por archivo. */
export const LIMITE_BYTES = 50 * 1024 * 1024;

/** Un golpe dura pocos segundos; más que esto probablemente trae varios (especificación §5). */
export const DURACION_AVISO_S = 8;

export const GESTOS = [
  { valor: "saque", etiqueta: "Saque" },
  { valor: "drive", etiqueta: "Drive" },
  { valor: "reves", etiqueta: "Revés" },
] as const;

export const ENCUADRES = [
  { valor: "perfil", etiqueta: "De perfil" },
  { valor: "tres_cuartos", etiqueta: "De tres cuartos" },
] as const;

export const LADOS_CAMARA = [
  { valor: "derecha", etiqueta: "A la derecha del jugador" },
  { valor: "izquierda", etiqueta: "A la izquierda del jugador" },
] as const;

/**
 * "¿Cómo lo grabaste?" (decisión 020 y especificación §5): se elige a propósito, ninguna viene marcada.
 * La pregunta es cómo se GRABÓ, no cómo se ve ni cómo llega el archivo.
 */
export const MODOS_CAPTURA = [
  { valor: "camara_lenta_240", etiqueta: "Cámara lenta de 240 fps (o \"slow-mo\" a la velocidad más alta)" },
  { valor: "camara_lenta_120", etiqueta: "Cámara lenta de 120 fps" },
  { valor: "normal", etiqueta: "Grabación normal (sin cámara lenta)" },
] as const;

export const MANOS = [
  { valor: "derecha", etiqueta: "Derecha" },
  { valor: "izquierda", etiqueta: "Izquierda" },
] as const;

export const NIVELES = [
  { valor: "recreativo", etiqueta: "Recreativo" },
  { valor: "intermedio", etiqueta: "Intermedio" },
  { valor: "avanzado", etiqueta: "Avanzado" },
] as const;

export type Gesto = (typeof GESTOS)[number]["valor"];
export type Encuadre = (typeof ENCUADRES)[number]["valor"];
export type LadoCamara = (typeof LADOS_CAMARA)[number]["valor"];
export type ModoCaptura = (typeof MODOS_CAPTURA)[number]["valor"];
export type Mano = (typeof MANOS)[number]["valor"];
export type Nivel = (typeof NIVELES)[number]["valor"];

export function esValor<T extends readonly { valor: string }[]>(lista: T, v: string): v is T[number]["valor"] {
  return lista.some((x) => x.valor === v);
}

// --- el archivo ----------------------------------------------------------------------------------------

const EXTENSIONES_VALIDAS = ["mp4", "mov"] as const;
const TIPOS_VALIDOS = ["video/mp4", "video/quicktime"] as const;

export function extensionDe(nombre: string): string {
  const i = nombre.lastIndexOf(".");
  return i < 0 ? "" : nombre.slice(i + 1).toLowerCase();
}

/** Tipo MIME para subir. Algunos navegadores dejan `type` vacío en un .mov: se deduce de la extensión. */
export function tipoDeContenido(nombre: string, tipoDelNavegador: string): string | null {
  if ((TIPOS_VALIDOS as readonly string[]).includes(tipoDelNavegador)) return tipoDelNavegador;
  const ext = extensionDe(nombre);
  if (ext === "mp4") return "video/mp4";
  if (ext === "mov") return "video/quicktime";
  return null;
}

export type ProblemaArchivo =
  | { tipo: "formato"; texto: string }
  | { tipo: "tamano"; texto: string }
  | { tipo: "vacio"; texto: string };

export function problemaDelArchivo(archivo: { name: string; size: number; type: string }): ProblemaArchivo | null {
  if (archivo.size === 0) return { tipo: "vacio", texto: "El archivo está vacío. Elegí otro." };
  if (tipoDeContenido(archivo.name, archivo.type) === null || !(EXTENSIONES_VALIDAS as readonly string[]).includes(extensionDe(archivo.name))) {
    return { tipo: "formato", texto: "Subí un video MP4 o MOV." };
  }
  if (archivo.size > LIMITE_BYTES) {
    const mb = (archivo.size / (1024 * 1024)).toFixed(0);
    return {
      tipo: "tamano",
      texto: `El archivo pesa ${mb} MB y el máximo es 50 MB. Recortalo para dejar solo el golpe (unos 2 a 5 segundos) y volvé a elegirlo.`,
    };
  }
  return null;
}

/**
 * Nombre seguro para la clave del objeto en Storage: solo letras ASCII, números, guion, guion bajo y punto.
 * Storage rechaza otros caracteres con `InvalidKey` (lo medido con la página de prueba del iPhone, 9/10).
 * Las tildes pasan a su letra base y todo lo demás a guion.
 */
export function nombreSeguro(nombre: string): string {
  const ext = extensionDe(nombre);
  const base = ext ? nombre.slice(0, nombre.length - ext.length - 1) : nombre;
  const limpio = base
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^A-Za-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
  return `${limpio || "video"}${ext ? "." + ext.replace(/[^a-z0-9]/g, "") : ""}`;
}

/** Ruta del objeto: `<usuario_id>/<video_id>/<nombre>` — la política de Storage exige la carpeta del usuario. */
export function rutaDelVideo(usuarioId: string, videoId: string, nombreOriginal: string): string {
  return `${usuarioId}/${videoId}/${nombreSeguro(nombreOriginal)}`;
}

// --- respuestas de la API (decisiones 022 y 025) -------------------------------------------------------

export type ResultadoApi =
  | { ok: true }
  | { ok: false; reintentable: boolean; texto: string; renovarSesion?: boolean };

/** De la respuesta de `POST /analisis/{id}/procesar` a un mensaje en lenguaje llano (R2). */
export function interpretarRespuestaApi(estado: number, cuerpo: unknown): ResultadoApi {
  if (estado === 202) return { ok: true };
  if (estado === 401) {
    return { ok: false, reintentable: false, renovarSesion: true, texto: "Tu sesión venció. Ingresá de nuevo y volvé a intentar." };
  }
  if (estado === 404) {
    return { ok: false, reintentable: false, texto: "No encontramos el video que acabás de subir. Volvé a cargarlo." };
  }
  if (estado === 409) {
    const codigo = detalleCodigo(cuerpo);
    if (codigo === "estado_no_reintentable") {
      // Ya estaba en cola o ya se analizó: para quien carga es lo mismo que haber salido bien.
      return { ok: true };
    }
    return { ok: false, reintentable: false, texto: "Este video ya no se puede volver a enviar a analizar." };
  }
  if (estado === 503 || estado >= 500) {
    return { ok: false, reintentable: true, texto: "El servidor de análisis no respondió. Tu video ya está guardado: probá enviarlo de nuevo en un momento." };
  }
  return { ok: false, reintentable: true, texto: "No pudimos enviar el video a analizar. Probá de nuevo en un momento." };
}

function detalleCodigo(cuerpo: unknown): string | null {
  if (cuerpo && typeof cuerpo === "object" && "detail" in cuerpo) {
    const d = (cuerpo as { detail: unknown }).detail;
    if (d && typeof d === "object" && "codigo" in d) {
      const c = (d as { codigo: unknown }).codigo;
      return typeof c === "string" ? c : null;
    }
  }
  return null;
}

/** Une la URL base de la API y el camino, sin barras dobles. `null` si la variable no está configurada. */
export function urlProcesar(apiUrl: string | undefined, videoId: string): string | null {
  if (!apiUrl || !apiUrl.trim()) return null;
  return `${apiUrl.trim().replace(/\/+$/, "")}/analisis/${encodeURIComponent(videoId)}/procesar`;
}
