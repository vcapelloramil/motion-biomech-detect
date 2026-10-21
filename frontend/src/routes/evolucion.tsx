import { useEffect, useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { Hueco, PanelBarras, PanelLinea } from "@/components/evolucion/graficos";
import { BotonDescargarPdf, SelloDelPdf, LimitacionesDelPdf } from "@/components/reporte/pdf";
import { useSesion } from "@/lib/sesion";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA } from "@/lib/estado-video";
import { etiquetasDeSesiones, type SerieDeEvolucion } from "@/lib/evolucion";
import { CABECERA_EVOLUCION, textosDeEvolucion } from "@/lib/textos-evolucion";
import { DetalleTecnico, EnUnaFrase, PieDeTextos, QueVimos } from "@/components/reporte/bloques";
import { leerEvolucion } from "@/lib/evolucion-api";
import { gruposDeEvolucion, type GrupoDeEvolucion } from "@/lib/videos-data";

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
      <p className="mt-3 max-w-2xl text-muted-foreground">{CABECERA_EVOLUCION}</p>

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
  const textos = textosDeEvolucion(serie);
  const etiquetas = etiquetasDeSesiones(serie.sesiones);
  const banda =
    serie.centro_habitual !== null && serie.variacion_habitual !== null
      ? { centro: serie.centro_habitual, semiancho: serie.variacion_habitual }
      : null;

  return (
    <div className="mt-2">
      <EnUnaFrase texto={textos.enUnaFrase} />
      {textos.pocasSesiones && (
        <p className="mt-4 rounded-2xl border border-dashed border-border px-4 py-3 text-sm">{textos.pocasSesiones}</p>
      )}
      <QueVimos medido={textos.vimos.medido} noMedido={textos.vimos.noMedido} />

      {textos.avisos.map((a) => (
        <p key={a} className="mt-3 text-xs text-muted-foreground">{a}</p>
      ))}

      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <PanelLinea
          titulo={textos.graficos.tituloLinea}
          unidad={textos.graficos.unidadLinea}
          puntos={serie.sesiones.map((s) => ({ valor: s.separacion_cadera_hombro.mediana, dispersion: s.separacion_cadera_hombro.dispersion }))}
          etiquetas={etiquetas}
          banda={banda}
          textoBanda={textos.graficos.textoBanda ?? ""}
          nota={textos.graficos.notaLinea}
        />
        {serie.sesiones.some((s) => s.orden.suficiente) ? (
          <PanelBarras
            titulo={textos.graficos.tituloBarras}
            barras={serie.sesiones.map((s) => ({ mismo: s.orden.mismo_orden, ordenables: s.orden.ordenables, suficiente: s.orden.suficiente }))}
            etiquetas={etiquetas}
            nota={textos.graficos.notaBarras}
          />
        ) : (
          <p className="rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">{textos.graficos.sinBarras}</p>
        )}
      </div>

      <DetalleTecnico>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[34rem] text-left text-sm">
            <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              <tr>
                {textos.detalle.columnas.map((c) => (
                  <th key={c} className="py-2 pr-4">{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {textos.detalle.filas.map((f, i) => (
                <tr key={i} className="border-t border-border align-top">
                  {f.map((c, k) => (
                    <td key={k} className={"py-2 pr-4 " + (k === 0 ? "font-semibold" : "font-mono")}>{c}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted-foreground">{textos.detalle.nota}</p>
        <PieDeTextos />
      </DetalleTecnico>
    </div>
  );
}
