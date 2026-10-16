import { useEffect, useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowDown, ArrowUp, Equal, Loader2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { Hueco, PanelBarras, PanelLinea } from "@/components/evolucion/graficos";
import { BotonDescargarPdf, SelloDelPdf, LimitacionesDelPdf } from "@/components/reporte/pdf";
import { useSesion } from "@/lib/sesion";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA } from "@/lib/estado-video";
import { avisosDeEvolucion, etiquetaDeFecha, tarjetasDeEvolucion, type SerieDeEvolucion } from "@/lib/evolucion";
import { leerEvolucion } from "@/lib/evolucion-api";
import { gruposDeEvolucion, type GrupoDeEvolucion } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

export const Route = createFileRoute("/evolucion")({
  head: () => ({
    meta: [
      { title: "Evolución — KinetiQ" },
      { name: "description", content: "Vos frente a vos mismo: cómo cambian tus mediciones de una sesión a otra." },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: () => (
    <RutaProtegida>
      <EvolucionPage />
    </RutaProtegida>
  ),
});

const clave = (g: GrupoDeEvolucion) => `${g.atleta_id}|${g.gesto}|${g.encuadre}`;

function EvolucionPage() {
  const { sesion, cargando } = useSesion();
  const [grupos, setGrupos] = useState<GrupoDeEvolucion[] | null>(null);
  const [errorGrupos, setErrorGrupos] = useState(false);
  const [elegido, setElegido] = useState<string | null>(null);
  const [serie, setSerie] = useState<SerieDeEvolucion | null | undefined>(undefined);

  useEffect(() => {
    if (cargando) return;
    let activo = true;
    gruposDeEvolucion()
      .then((g) => {
        if (!activo) return;
        setGrupos(g);
        setElegido((previo) => previo ?? (g[0] ? clave(g[0]) : null));
      })
      .catch(() => {
        if (!activo) return;
        setErrorGrupos(true);
        setGrupos([]);
      });
    return () => {
      activo = false;
    };
  }, [cargando]);

  const grupo = useMemo(() => (grupos ?? []).find((g) => clave(g) === elegido) ?? null, [grupos, elegido]);
  const token = sesion?.access_token;

  useEffect(() => {
    if (!grupo || !token) return;
    let activo = true;
    setSerie(undefined);
    leerEvolucion(grupo.atleta_id, grupo.gesto, grupo.encuadre, token).then((s) => activo && setSerie(s));
    return () => {
      activo = false;
    };
  }, [grupo, token]);

  const cargandoTodo = grupos === null;
  const hayVariosJugadores = new Set((grupos ?? []).map((g) => g.atleta_id)).size > 1;

  return (
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-14">
      <SelloDelPdf
        titulo={grupo ? `Evolución · ${GESTO_ETIQUETA[grupo.gesto] ?? grupo.gesto} · cámara de ${ENCUADRE_ETIQUETA[grupo.encuadre] ?? grupo.encuadre} · ${grupo.atleta}` : "Evolución"}
        versiones={serie?.versiones_motor ?? []}
      />
      <nav aria-label="Ruta" className="font-mono text-xs text-muted-foreground print:hidden">
        <Link to="/videos" className="hover:text-foreground">Biblioteca</Link> / Evolución
      </nav>
      <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight md:text-6xl">
        Vos, frente a <span className="text-gradient-neon">vos mismo</span>
      </h1>
      <p className="mt-3 max-w-2xl text-muted-foreground">
        Solo se comparan sesiones del mismo jugador, golpe y encuadre. No hay comparación con otros jugadores ni con un modelo ideal, y un cambio
        no es mejor ni peor: es lo que cambió.
      </p>

      {cargandoTodo ? (
        <p role="status" className="mt-10 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando…
        </p>
      ) : (grupos ?? []).length === 0 ? (
        <div className="mt-10">
          <Hueco>
            {errorGrupos ? "No pudimos leer tus sesiones ahora. Probá de nuevo en un momento." : "Todavía no cargaste ninguna sesión. La evolución empieza con la segunda sesión de un mismo golpe y encuadre."}{" "}
            <Link to="/upload" className="underline underline-offset-4">Cargar golpes</Link>
          </Hueco>
        </div>
      ) : (
        <>
          <div role="group" aria-label="Qué comparar" className="mt-8 flex flex-wrap gap-2 print:hidden">
            {(grupos ?? []).map((g) => {
              const activo = clave(g) === elegido;
              return (
                <button
                  key={clave(g)}
                  type="button"
                  aria-pressed={activo}
                  onClick={() => setElegido(clave(g))}
                  className={
                    "min-h-11 rounded-xl border px-4 text-sm font-semibold " +
                    (activo ? "border-neon bg-neon/10 text-neon" : "border-border text-muted-foreground hover:text-foreground")
                  }
                >
                  {GESTO_ETIQUETA[g.gesto] ?? g.gesto} · {ENCUADRE_ETIQUETA[g.encuadre] ?? g.encuadre}
                  {hayVariosJugadores ? ` · ${g.atleta}` : ""}
                  <span className="ml-2 font-mono text-xs opacity-70">{g.sesiones} {g.sesiones === 1 ? "sesión" : "sesiones"}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            {grupo && (
              <p className="text-sm text-muted-foreground">
                {grupo.atleta} · {GESTO_ETIQUETA[grupo.gesto] ?? grupo.gesto} en {ENCUADRE_ETIQUETA[grupo.encuadre] ?? grupo.encuadre}
              </p>
            )}
            <BotonDescargarPdf />
          </div>

          {serie === undefined ? (
            <p role="status" className="mt-8 flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Calculando…
            </p>
          ) : serie === null ? (
            <div className="mt-8">
              <Hueco>No pudimos calcular la evolución ahora. Probá de nuevo en un momento.</Hueco>
            </div>
          ) : (
            <Serie serie={serie} />
          )}
        </>
      )}

      <LimitacionesDelPdf />
    </main>
  );
}

function Serie({ serie }: { serie: SerieDeEvolucion }) {
  const tarjetas = tarjetasDeEvolucion(serie);
  const avisos = avisosDeEvolucion(serie);
  const etiquetas = serie.sesiones.map((s) => etiquetaDeFecha(s.fecha));
  const unaSola = serie.sesiones.length === 1;
  const banda =
    serie.centro_habitual !== null && serie.variacion_habitual !== null
      ? { centro: serie.centro_habitual, semiancho: serie.variacion_habitual }
      : null;

  return (
    <div className="mt-8">
      {unaSola && (
        <p className="mb-6 rounded-2xl border border-dashed border-border px-4 py-3 text-sm">
          Tenés una sola sesión de este golpe y encuadre: es tu punto de partida. La comparación empieza con la segunda.
        </p>
      )}

      <ul className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {tarjetas.map((t) => (
          <li key={t.clave} className="rounded-2xl border border-border bg-card p-5">
            <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{t.titulo}</p>
            <p className="mt-2 flex items-center gap-2 font-display text-3xl font-bold">
              {t.direccion === "sube" && <ArrowUp className="h-5 w-5 text-acento" aria-label="Aumentó" />}
              {t.direccion === "baja" && <ArrowDown className="h-5 w-5 text-acento" aria-label="Disminuyó" />}
              {t.direccion === "igual" && <Equal className="h-5 w-5 text-acento" aria-label="Se mantuvo" />}
              {t.valor ?? "—"}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">{t.texto}</p>
          </li>
        ))}
      </ul>

      {avisos.map((a) => (
        <p key={a} className="mt-3 text-xs text-muted-foreground">{a}</p>
      ))}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <PanelLinea
          titulo="Separación cadera-hombro máxima"
          unidad="grados · mediana por sesión"
          puntos={serie.sesiones.map((s) => ({ valor: s.separacion_cadera_hombro.mediana, dispersion: s.separacion_cadera_hombro.dispersion }))}
          etiquetas={etiquetas}
          banda={banda}
          textoBanda={`tu variación habitual ±${fmt(banda?.semiancho ?? 0, 0)}°`}
          nota={
            "Cada punto es la mediana de los golpes medidos de la sesión; la línea vertical, cuánto variaron entre sí. " +
            "Una sesión sin dato queda como hueco: no se completa con una estimación."
          }
        />
        {serie.sesiones.some((s) => s.orden.suficiente) ? (
          <PanelBarras
            titulo="Golpes con el mismo orden de cadera y tronco"
            barras={serie.sesiones.map((s) => ({ mismo: s.orden.mismo_orden, ordenables: s.orden.ordenables, suficiente: s.orden.suficiente }))}
            etiquetas={etiquetas}
            nota="De los golpes en que se distingue cuál llegó primero, cuántos tuvieron el mismo orden. Mide si se repite, no cuál es el correcto. Con menos de 5 golpes ordenables no se dice."
          />
        ) : (
          <p className="rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
            <strong className="text-foreground">No hay gráfico del orden de cadera y tronco:</strong> ninguna sesión llega a 5 golpes en los que se
            distinga cuál llegó primero. Es lo habitual con la cámara en tres cuartos: la cadera y el tronco llegan a su pico con menos de 8,33 ms
            de diferencia y, a esa resolución, no se puede saber cuál fue primero. Los golpes medidos se ven en la separación de arriba.
          </p>
        )}
      </div>
    </div>
  );
}
