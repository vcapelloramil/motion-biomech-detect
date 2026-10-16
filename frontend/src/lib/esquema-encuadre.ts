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
  /** Rótulo «CÁMARA»: del lado opuesto al de la línea punteada, para que no la pise. */
  etiquetaCamara: { x: number; y: number; ancla: "start" | "middle" | "end" };
};

export type GeometriaRaqueta = {
  /** Mango: del borde del jugador hacia afuera. */
  mango: { x1: number; y1: number; x2: number; y2: number };
  /** Cabeza (elipse): centro, radios y giro en grados (sentido horario del SVG) para que su eje mayor siga al mango. */
  cabeza: { cx: number; cy: number; rx: number; ry: number; rotacion: number };
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
      ? { texto: "90°", x: (camara.x + JUGADOR.x) / 2, y: JUGADOR.y + 14, ancla: "middle" as const } // debajo de la línea: arriba puede ir la raqueta
      : { texto: "~45°, por delante", x: ANCHO / 2, y: 114, ancla: "middle" as const };
  // Perfil: la línea sale en horizontal y el rótulo va debajo, centrado. Tres cuartos: la línea baja en diagonal hacia el jugador,
  // así que el rótulo se corre hacia afuera (su borde pegado a la cámara) y queda lejos de la línea.
  const etiquetaCamara =
    encuadre === "perfil"
      ? { x: camara.x, y: camara.y + 20, ancla: "middle" as const }
      : lado === "izquierda"
        ? { x: camara.x + 8, y: camara.y + 22, ancla: "end" as const }
        : { x: camara.x - 8, y: camara.y + 22, ancla: "start" as const };
  return { jugador: { ...JUGADOR }, camara, rotacion, angulo, etiquetaCamara };
}

/**
 * Raqueta en la mano dominante del jugador (vista desde arriba, el jugador mira hacia la red = arriba). Se calcula para la mano
 * derecha (derecha del dibujo) y se espeja en x para la izquierda. Sale hacia el costado y un poco hacia la red.
 */
export function geometriaRaqueta(mano: Mano, jugador: { x: number; y: number } = JUGADOR): GeometriaRaqueta {
  const signo = mano === "derecha" ? 1 : -1;
  const dx = 9;
  const dy = -4;
  const largo = Math.hypot(dx, dy);
  const rx = 4;
  const ry = 6.5;
  const x1 = jugador.x + signo * 11;
  const y1 = jugador.y - 3;
  const x2 = x1 + signo * dx;
  const y2 = y1 + dy;
  const cx = x2 + signo * (dx / largo) * ry;
  const cy = y2 + (dy / largo) * ry;
  const rotacion = Math.round(signo * ((Math.atan2(dx, -dy) * 180) / Math.PI) * 100) / 100;
  return { mango: { x1, y1, x2, y2 }, cabeza: { cx, cy, rx, ry, rotacion } };
}
