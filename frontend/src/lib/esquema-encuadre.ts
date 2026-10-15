/**
 * Geometría del esquema de encuadre de Cargar (vista desde arriba): lógica pura, probada con `bun test`
 * (frontend/tests/esquema-encuadre.test.ts). El dibujo está en `components/esquema-encuadre.tsx`.
 *
 * El jugador mira hacia la red (arriba en el dibujo), así que **su izquierda es la izquierda de quien mira el dibujo**.
 * La cámara va del lado **contrario a la mano dominante** (a la izquierda de un diestro): es el lado de todas las
 * grabaciones de referencia (decisión 013) y el que permite comparar sesiones entre sí.
 * - Perfil: a un costado, a 90° de la dirección del golpe.
 * - Tres cuartos: **por delante** del jugador, en diagonal (~45°): se lo ve un poco de frente.
 */

export type Mano = "derecha" | "izquierda";
export type LadoCamara = "derecha" | "izquierda";
export type EncuadreEsquema = "perfil" | "tres_cuartos";

/** El lado recomendado: el contrario a la mano dominante. `null` si todavía no se sabe la mano. */
export function ladoRecomendado(mano: string | null | undefined): LadoCamara | null {
  if (mano === "derecha") return "izquierda";
  if (mano === "izquierda") return "derecha";
  return null;
}

/** ¿El lado elegido es el de la mano dominante (el brazo que golpea queda cerca de la cámara)? */
export function esLadoDeLaMano(lado: string, mano: string | null | undefined): boolean {
  return (lado === "derecha" || lado === "izquierda") && lado === mano;
}

export type GeometriaEsquema = {
  jugador: { x: number; y: number };
  camara: { x: number; y: number };
  /** Grados (sentido horario del SVG) que hay que girar el ícono de la cámara, cuyo objetivo mira hacia -x, para que apunte al jugador. */
  rotacion: number;
  /** Texto del ángulo y su posición. */
  angulo: { texto: string; x: number; y: number; ancla: "start" | "middle" | "end" };
};

const ANCHO = 160;
const JUGADOR = { x: 80, y: 78 };

export function geometriaEsquema(encuadre: EncuadreEsquema, lado: LadoCamara): GeometriaEsquema {
  // Se calcula para la izquierda del jugador y se espeja en x para la derecha.
  const izq =
    encuadre === "perfil"
      ? { x: JUGADOR.x - 52, y: JUGADOR.y }
      : { x: JUGADOR.x - 40, y: JUGADOR.y - 40 }; // 45° exactos, por delante (del lado de la red)
  const camara = lado === "izquierda" ? izq : { x: ANCHO - izq.x, y: izq.y };

  const dx = JUGADOR.x - camara.x;
  const dy = JUGADOR.y - camara.y;
  const direccion = (Math.atan2(dy, dx) * 180) / Math.PI; // hacia dónde mira la cámara, desde +x en sentido horario
  const rotacion = Math.round((direccion - 180) * 100) / 100;

  const angulo =
    encuadre === "perfil"
      ? { texto: "90°", x: (camara.x + JUGADOR.x) / 2, y: JUGADOR.y - 6, ancla: "middle" as const }
      : { texto: "~45°, por delante", x: ANCHO / 2, y: 114, ancla: "middle" as const };
  return { jugador: { ...JUGADOR }, camara, rotacion, angulo };
}
