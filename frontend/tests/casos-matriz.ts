// La matriz de casos de docs/ux/textos-reporte-039-propuesta.md: los escenarios que Valentín pidió revisar, armados con variantes del dato REAL
// del 25/9/2026. Los usan la prueba (matriz-casos.test.ts) y el generador del documento (generar-textos-doc.ts): mismas reglas, mismos casos.
import real from "./fixtures/sesion-25-9-saque-tres-cuartos.json";
import esc from "./fixtures/escenarios-matriz.json";
import type { Consistencia } from "../src/lib/consistencia";
import { contextoDeGolpe, type EntradaGolpe, type EntradaSesion } from "../src/lib/textos-reporte";

type Json = Record<string, unknown>;
export const consistenciaReal = real.consistencia as unknown as Consistencia;
export const golpesReales = real.golpes.map((g) => ({ id: g.id, estado: g.estado, reporte: g.reporte as unknown as Json }));
const reportes = esc.reportes as unknown as Record<string, Json>;
const sesiones = esc.sesiones as unknown as Record<string, { golpes: { id: string; estado: string; reporte: Json }[]; consistencia: Consistencia }>;

/** El mismo golpe visto en un espejo: izquierda ↔ derecha en los nombres de las articulaciones (para el jugador zurdo). */
export function espejo(reporte: Json): Json {
  const s = JSON.stringify(reporte).replace(/_izq/g, "_@@").replace(/_der/g, "_izq").replace(/_@@/g, "_der");
  return JSON.parse(s) as Json;
}

const base = (reporte: Json): EntradaGolpe => ({
  reporte,
  gesto: "saque",
  encuadre: "tres_cuartos",
  ladoCamara: "izquierda",
  manoDominante: "derecha",
  contexto: null,
});

export type Incluir = "medir" | "usar" | "literatura" | "preguntas";

export type Caso =
  | { id: string; n: string; titulo: string; escenario: string; tipo: "golpe"; golpe: EntradaGolpe; incluir: Incluir[] }
  | { id: string; n: string; titulo: string; escenario: string; tipo: "sesion"; sesion: EntradaSesion; incluir: Incluir[] };

export const CASOS: Caso[] = [
  {
    id: "cadera_antes", n: "1", titulo: "Cadera claramente antes que el tronco", tipo: "golpe", incluir: [],
    escenario: "Saque de tres cuartos, cámara a la izquierda, jugador diestro. Cadera 42 ms antes que el tronco; brazo no medido.",
    golpe: base(reportes.cadera_antes),
  },
  {
    id: "tronco_antes", n: "2", titulo: "Tronco antes que la cadera", tipo: "golpe", incluir: [],
    escenario: "El mismo golpe con los instantes invertidos: tronco 42 ms antes que la cadera.",
    golpe: base(reportes.tronco_antes),
  },
  {
    id: "nada_medido", n: "3", titulo: "Golpe sin nada medido", tipo: "golpe", incluir: ["medir"],
    escenario: "Ni cadera, ni tronco, ni brazo con confianza; ninguna magnitud auditable.",
    golpe: base(reportes.vacio),
  },
  {
    id: "drive", n: "4a", titulo: "Drive (recuadro de literatura sin referencia)", tipo: "golpe", incluir: ["literatura"],
    escenario: "Drive, tres cuartos, cámara a la izquierda. (Se usa el dato del saque: solo importa el lenguaje.)",
    golpe: { ...base(reportes.cadera_antes), gesto: "drive" },
  },
  {
    id: "reves", n: "4b", titulo: "Revés (recuadro de literatura sin referencia)", tipo: "golpe", incluir: ["literatura"],
    escenario: "Revés, perfil, cámara a la izquierda.",
    golpe: { ...base(reportes.cadera_antes), gesto: "reves", encuadre: "perfil" },
  },
  {
    id: "lado_mano", n: "5", titulo: "Cámara del lado de la mano dominante (brazo visible)", tipo: "golpe", incluir: ["medir"],
    escenario: "Jugador diestro con la cámara a la derecha: el pico del brazo se midió (52 ms después del tronco).",
    golpe: { ...base(reportes.con_brazo), ladoCamara: "derecha" },
  },
  {
    id: "zurdo", n: "6", titulo: "Jugador zurdo", tipo: "golpe", incluir: ["medir"],
    escenario: "Zurdo, cámara a la derecha (el lado recomendado para él), con el golpe típico de la sesión reflejado en un espejo.",
    golpe: { ...base(espejo(golpesReales[3].reporte as Json)), ladoCamara: "derecha", manoDominante: "izquierda", contexto: contextoDeGolpe(consistenciaReal, golpesReales[3].id) },
  },
  {
    id: "orden_mezclado", n: "7", titulo: "Sesión con el orden mezclado entre golpes", tipo: "sesion", incluir: ["medir", "usar", "preguntas"],
    escenario: "Los 6 golpes del 25/9, pero en el golpe 3 el tronco llega antes que la cadera.",
    sesion: { gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: sesiones.mezclado.golpes, consistencia: sesiones.mezclado.consistencia },
  },
  {
    id: "tres_golpes", n: "8", titulo: "Sesión de 3 golpes (menos del mínimo para la variación y la repetición)", tipo: "sesion", incluir: ["medir", "usar", "preguntas"],
    escenario: "Los golpes 1, 3 y 5 del 25/9: los tres con orden distinguible. Mínimos del proyecto: variación desde 4 golpes, repetición desde 5 ordenables.",
    sesion: { gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: sesiones.tres_golpes.golpes, consistencia: sesiones.tres_golpes.consistencia },
  },
  {
    id: "sin_apartan", n: "9", titulo: "Sesión sin ningún golpe que se aparte", tipo: "sesion", incluir: ["medir", "usar", "preguntas"],
    escenario: "Los golpes 1 a 5 del 25/9 (sin el 6): 5 golpes, ninguno se aparta.",
    sesion: { gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: sesiones.sin_apartan.golpes, consistencia: sesiones.sin_apartan.consistencia },
  },
  {
    id: "un_ordenable", n: "10", titulo: "Sesión con UN solo golpe ordenable", tipo: "sesion", incluir: ["medir", "preguntas"],
    escenario: "Los golpes 1, 2, 4 y 6 del 25/9: solo el 1 tiene el orden distinguible (cadera 17 ms antes); los otros tres quedaron casi a la vez.",
    sesion: { gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: sesiones.un_ordenable.golpes, consistencia: sesiones.un_ordenable.consistencia },
  },
  {
    id: "ningun_ordenable", n: "11", titulo: "Sesión con NINGÚN golpe ordenable", tipo: "sesion", incluir: ["medir", "preguntas"],
    escenario: "Los golpes 2, 4 y 6 del 25/9: en los tres, cadera y tronco quedaron casi a la vez.",
    sesion: { gesto: "saque", encuadre: "tres_cuartos", ladoCamara: "izquierda", manoDominante: "derecha", golpes: sesiones.ningun_ordenable.golpes, consistencia: sesiones.ningun_ordenable.consistencia },
  },
];

// --- Evolución (decisión 039, segunda ronda): series calculadas por el servidor con las sesiones reales del 24 y 25/9 y variantes ---
import evo from "./fixtures/evolucion-matriz.json";
import type { SerieDeEvolucion } from "../src/lib/evolucion";

const series = evo as unknown as Record<string, SerieDeEvolucion>;

export type CasoEvolucion = { id: string; n: string; titulo: string; escenario: string; serie: SerieDeEvolucion };

export const CASOS_EVOLUCION: CasoEvolucion[] = [
  { id: "una_sesion", n: "E1", titulo: "Una sola sesión (menos de 2 comparables)", escenario: "Solo la sesión del 25/9.", serie: series.una_sesion },
  { id: "dos_sesiones", n: "E2", titulo: "Dos sesiones, el cambio está dentro de lo habitual", escenario: "Las dos sesiones reales: 24/9 y 25/9 (valor típico 32,05° y 32,95°).", serie: series.dos_sesiones },
  { id: "cambio_mayor", n: "E3", titulo: "Tres sesiones, el cambio es mayor que lo habitual", escenario: "24/9, 25/9 y una sesión del 2/10 con todas las torsiones 14° más altas (variante inventada para probar la regla).", serie: series.cambio_mayor },
  { id: "pocos_golpes", n: "E4", titulo: "Dos sesiones con menos de 4 golpes (no se puede decir la variación)", escenario: "Tres golpes por sesión: el servidor no calcula la variación (mínimo 4).", serie: series.pocos_golpes },
  { id: "lados_distintos", n: "E5", titulo: "Sesiones grabadas desde lados distintos de la cámara", escenario: "La segunda sesión se cargó con la cámara a la derecha.", serie: series.lados_distintos },
  { id: "orden_repetido", n: "E6", titulo: "Orden que se repite (5 golpes con orden distinguible por sesión)", escenario: "Dos sesiones con 5 golpes en que se distingue el orden (variante para probar la regla).", serie: series.orden_repetido },
];
