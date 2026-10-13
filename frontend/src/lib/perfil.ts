/**
 * Perfil (paso 5 del plan §8): lógica pura, sin red ni DOM, para probarla con `bun test` (frontend/tests/perfil.test.ts).
 * Las lecturas y escrituras están en `perfil-data.ts`.
 */

import { MANOS, NIVELES, esValor } from "@/lib/carga";
import { esRol } from "@/lib/auth-errores";

/** La palabra que hay que escribir para eliminar la cuenta. El servidor exige la misma (`routers/cuenta.py`). */
export const CONFIRMACION_ELIMINAR = "ELIMINAR";

export function confirmacionValida(texto: string): boolean {
  return texto.trim() === CONFIRMACION_ELIMINAR;
}

export function urlCuenta(apiUrl: string | undefined): string | null {
  if (!apiUrl || !apiUrl.trim()) return null;
  return `${apiUrl.trim().replace(/\/+$/, "")}/cuenta`;
}

export const LARGO_MAXIMO_NOMBRE = 80;

/** `null` si el nombre sirve; si no, el motivo en lenguaje llano. */
export function problemaDelNombre(nombre: string): string | null {
  const n = nombre.trim();
  if (n.length === 0) return "Escribí un nombre.";
  if (n.length > LARGO_MAXIMO_NOMBRE) return `El nombre admite hasta ${LARGO_MAXIMO_NOMBRE} caracteres.`;
  return null;
}

export type DatosJugador = { nombre: string; mano_dominante: string; nivel: string };

export function problemaDelJugador(j: DatosJugador): string | null {
  const nombre = problemaDelNombre(j.nombre);
  if (nombre) return nombre;
  if (!esValor(MANOS, j.mano_dominante)) return "Elegí la mano dominante.";
  if (!esValor(NIVELES, j.nivel)) return "Elegí el nivel.";
  return null;
}

export function problemaDelPerfil(nombre: string, rol: string): string | null {
  return problemaDelNombre(nombre) ?? (esRol(rol) ? null : "Elegí cómo usás KinetiQ.");
}

// --- "Descargar mis datos" (derecho de acceso, Ley 25.326) -----------------------------------------------------------------------------

export type EntradaExportacion = {
  usuario: Record<string, unknown> | null;
  atletas: Record<string, unknown>[];
  /** Cada sesión con sus golpes (videos) y el reporte de cada uno. */
  sesiones: (Record<string, unknown> & { videos?: (Record<string, unknown> & { reportes_biomecanicos?: unknown })[] })[];
};

const SIN_ARCHIVOS =
  "Esta descarga incluye tus datos y los reportes. No incluye los archivos de video ni las imágenes: están guardados y se eliminan con la cuenta.";

/** El JSON que se descarga: la cuenta, los jugadores y las sesiones con sus golpes y reportes. Sin claves ni tokens. */
export function armarExportacion(entrada: EntradaExportacion, generadoEn: string) {
  const u = entrada.usuario ?? {};
  return {
    generado_en: generadoEn,
    formato: "kinetiq-mis-datos/1",
    nota: SIN_ARCHIVOS,
    cuenta: { id: u.id ?? null, correo: u.email ?? null, nombre: u.nombre ?? null, rol: u.rol ?? null, creado_en: u.creado_en ?? null },
    jugadores: entrada.atletas.map((a) => ({
      id: a.id,
      nombre: a.nombre,
      mano_dominante: a.mano_dominante,
      nivel: a.nivel,
      edad: a.edad ?? null,
      creado_en: a.creado_en ?? null,
    })),
    sesiones: entrada.sesiones.map((s) => {
      const { videos, ...resto } = s;
      return {
        ...resto,
        golpes: (videos ?? []).map((v) => {
          const { reportes_biomecanicos, ...v2 } = v;
          const r = Array.isArray(reportes_biomecanicos) ? reportes_biomecanicos[0] : reportes_biomecanicos;
          return { ...v2, reporte: (r as { reporte?: unknown } | null | undefined)?.reporte ?? null };
        }),
      };
    }),
  };
}

export function nombreArchivoExportacion(generadoEn: string): string {
  return `kinetiq-mis-datos-${generadoEn.slice(0, 10)}.json`;
}
