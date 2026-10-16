/**
 * Instrucciones de grabación y subida de Cargar, por dispositivo (lógica pura, probada con `bun test`:
 * frontend/tests/instrucciones-carga.test.ts). El texto está en `components/instrucciones-carga.tsx`.
 */

export const DISPOSITIVOS = [
  { valor: "iphone", etiqueta: "iPhone" },
  { valor: "android", etiqueta: "Android" },
  { valor: "computadora", etiqueta: "Computadora" },
] as const;

export type Dispositivo = (typeof DISPOSITIVOS)[number]["valor"];

/**
 * El dispositivo desde el que se está cargando, a partir del `userAgent`. Un iPad reciente se presenta como "Macintosh" con pantalla
 * táctil: se lo trata como iPhone (mismas instrucciones: app Fotos). Sin información, "computadora".
 */
export function detectarDispositivo(userAgent: string | null | undefined, puntosTactiles = 0): Dispositivo {
  const ua = userAgent ?? "";
  if (/iPhone|iPad|iPod/i.test(ua)) return "iphone";
  if (/Macintosh/i.test(ua) && puntosTactiles > 1) return "iphone";
  if (/Android/i.test(ua)) return "android";
  return "computadora";
}
