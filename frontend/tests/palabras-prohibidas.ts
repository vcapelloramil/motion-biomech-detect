// Palabras que ninguna frase generada puede usar (R2 y decisión 039). Compartido por las pruebas de los textos y de la matriz de casos.
// El aviso es la única frase que nombra lo que KinetiQ NO hace: está exenta, y una prueba aparte verifica que no diga «riesgo».
export const PROHIBIDAS: RegExp[] = [
  /deber[ií]as?/i, /corregí/i, /correg[ií]r/i, /\bbien\b/i, /\bmal\b/i, /\bcorrect[oa]s?\b/i, /\bincorrect[oa]s?\b/i, /\bmejor(es)?\b/i, /\bpeor(es)?\b/i,
  /riesgo/i, /predec/i, /diagn[oó]stic/i, /prevenir|prevenci/i, /lesi[oó]n|lesiones/i, /coincid/i, /corresponde/i, /\bideal\b/i,
  /promet/i, /garantiz/i, /ATP|WTA/,
];

// Jerga interna que no puede verse fuera del detalle técnico (y, dentro, solo la interpolación, con su explicación).
export const JERGA: RegExp[] = [
  /interpol/i, /escala temporal/i, /cobertura auditable/i, /\bMAD\b/, /1,4826/, /codo_|rodilla_|_izq|_der/, /medido en parte/i, /ventana analizada/i, /no auditable/i,
];
