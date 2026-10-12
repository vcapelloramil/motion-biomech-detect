/**
 * Formato de números del reporte: coma decimal en TODA la interfaz (ajuste del 12/10/2026).
 * Una sola función para que la tabla de velocidades, la trazabilidad y los textos no mezclen punto y coma.
 */
export function fmt(x: number, decimales = 1): string {
  return x.toFixed(decimales).replace(".", ",");
}
