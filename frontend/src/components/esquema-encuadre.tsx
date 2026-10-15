import type { Encuadre } from "@/lib/carga";
import { geometriaEsquema, type LadoCamara } from "@/lib/esquema-encuadre";

/**
 * Esquema visto desde arriba: dónde está la cámara respecto del jugador en cada encuadre.
 *
 * El jugador mira hacia la red (arriba) y el golpe va hacia la red. La cámara se dibuja del lado `lado` del jugador (por defecto, el
 * recomendado: el contrario a su mano dominante, como en todas las grabaciones de referencia, decisión 013). Perfil: a un costado,
 * a 90° de la dirección del golpe. Tres cuartos: **por delante** del jugador, en diagonal a ~45°: se lo ve un poco de frente.
 * La geometría está en `lib/esquema-encuadre.ts`.
 */
export function EsquemaEncuadre({
  encuadre,
  lado = "izquierda",
  className,
}: {
  encuadre: Encuadre;
  lado?: LadoCamara;
  className?: string;
}) {
  const perfil = encuadre === "perfil";
  const { jugador, camara, rotacion, angulo } = geometriaEsquema(encuadre, lado);
  const cara = lado === "izquierda" ? "izquierda" : "derecha";
  return (
    <svg
      viewBox="0 0 160 120"
      className={className}
      role="img"
      aria-label={
        perfil
          ? `Vista desde arriba: la cámara está a un costado del jugador, a su ${cara}, a 90 grados de la dirección del golpe`
          : `Vista desde arriba: la cámara está por delante del jugador, en diagonal hacia su ${cara}, a unos 45 grados de la dirección del golpe`
      }
    >
      {/* red */}
      <line x1="14" y1="14" x2="146" y2="14" stroke="var(--muted-foreground)" strokeWidth="2" strokeDasharray="4 4" />
      <text x="80" y="9" textAnchor="middle" fontSize="8" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
        RED
      </text>
      {/* dirección del golpe */}
      <line x1={jugador.x} y1={jugador.y - 12} x2={jugador.x} y2="30" stroke="var(--muted-foreground)" strokeWidth="1.5" />
      <polygon points={`${jugador.x - 4},34 ${jugador.x + 4},34 ${jugador.x},26`} fill="var(--muted-foreground)" />
      {/* línea de la cámara al jugador */}
      <line x1={camara.x} y1={camara.y} x2={jugador.x} y2={jugador.y} stroke="var(--neon)" strokeWidth="1.5" strokeDasharray="3 3" />
      {/* jugador */}
      <circle cx={jugador.x} cy={jugador.y} r="11" fill="var(--card)" stroke="var(--foreground)" strokeWidth="2" />
      <text x={jugador.x} y={jugador.y + 3} textAnchor="middle" fontSize="8" fill="var(--foreground)" fontFamily="var(--font-mono)">
        J
      </text>
      {/* cámara */}
      <g transform={`translate(${camara.x} ${camara.y}) rotate(${rotacion})`}>
        <rect x="-9" y="-6" width="18" height="12" rx="2" fill="var(--neon)" />
        <polygon points="-9,-3 -15,-7 -15,7 -9,3" fill="var(--neon)" />
      </g>
      <text x={camara.x} y={camara.y + 20} textAnchor="middle" fontSize="8" fill="var(--neon)" fontFamily="var(--font-mono)">
        CÁMARA
      </text>
      {/* ángulo */}
      <text x={angulo.x} y={angulo.y} textAnchor={angulo.ancla} fontSize="8" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
        {angulo.texto}
      </text>
    </svg>
  );
}
