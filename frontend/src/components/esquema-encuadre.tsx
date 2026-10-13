import type { Encuadre } from "@/lib/carga";

/**
 * Esquema visto desde arriba: dónde está la cámara respecto del jugador en cada encuadre.
 *
 * El jugador mira hacia la red (arriba) y el golpe va hacia la red. Perfil: la cámara está a un costado, a 90° de esa dirección.
 * Tres cuartos: la cámara está en diagonal, por detrás de un costado del jugador, a ~45° (el protocolo de grabación,
 * `docs/protocolo-grabacion.md`). El esquema es del lado de la raqueta de un jugador diestro; con el lado de la cámara se elige el otro.
 */
export function EsquemaEncuadre({ encuadre, className }: { encuadre: Encuadre; className?: string }) {
  const perfil = encuadre === "perfil";
  // Cámara: perfil a la derecha del jugador; tres cuartos en diagonal por detrás a la derecha.
  const cam = perfil ? { x: 118, y: 58 } : { x: 108, y: 100 };
  const jugador = { x: 60, y: 58 };
  const rotacion = perfil ? 0 : 45; // el objetivo (a la izquierda en reposo) apunta al jugador
  return (
    <svg
      viewBox="0 0 160 120"
      className={className}
      role="img"
      aria-label={
        perfil
          ? "Vista desde arriba: la cámara está a un costado del jugador, a 90 grados de la dirección del golpe"
          : "Vista desde arriba: la cámara está en diagonal, por detrás de un costado del jugador, a unos 45 grados de la dirección del golpe"
      }
    >
      {/* red */}
      <line x1="14" y1="14" x2="146" y2="14" stroke="var(--muted-foreground)" strokeWidth="2" strokeDasharray="4 4" />
      <text x="80" y="9" textAnchor="middle" fontSize="8" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
        RED
      </text>
      {/* dirección del golpe */}
      <line x1={jugador.x} y1={jugador.y - 12} x2={jugador.x} y2="26" stroke="var(--muted-foreground)" strokeWidth="1.5" />
      <polygon points={`${jugador.x - 4},30 ${jugador.x + 4},30 ${jugador.x},22`} fill="var(--muted-foreground)" />
      {/* línea de la cámara al jugador */}
      <line x1={cam.x} y1={cam.y} x2={jugador.x + (perfil ? 12 : 9)} y2={jugador.y + (perfil ? 0 : 9)} stroke="var(--neon)" strokeWidth="1.5" strokeDasharray="3 3" />
      {/* jugador */}
      <circle cx={jugador.x} cy={jugador.y} r="11" fill="var(--card)" stroke="var(--foreground)" strokeWidth="2" />
      <text x={jugador.x} y={jugador.y + 3} textAnchor="middle" fontSize="8" fill="var(--foreground)" fontFamily="var(--font-mono)">
        J
      </text>
      {/* cámara */}
      <g transform={`translate(${cam.x} ${cam.y}) rotate(${rotacion})`}>
        <rect x="-9" y="-6" width="18" height="12" rx="2" fill="var(--neon)" />
        <polygon points="-9,-3 -15,-7 -15,7 -9,3" fill="var(--neon)" />
      </g>
      <text x={cam.x} y={cam.y + 20} textAnchor="middle" fontSize="8" fill="var(--neon)" fontFamily="var(--font-mono)">
        CÁMARA
      </text>
      {/* ángulo */}
      {perfil ? (
        <text x="86" y="52" fontSize="8" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
          90°
        </text>
      ) : (
        <text x="10" y="112" fontSize="8" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
          ~45° por detrás
        </text>
      )}
    </svg>
  );
}
